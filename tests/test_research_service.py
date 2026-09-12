from copy import deepcopy

from tradingagents.dataflows.config import get_config, set_config
from tradingagents.service import RESEARCH_DEPTHS, capabilities


def test_completed_service_checkpoint_returns_without_model_or_memory_calls():
    from contextlib import nullcontext
    from types import SimpleNamespace
    from unittest.mock import Mock

    from tradingagents.graph.trading_graph import TradingAgentsGraph

    graph = TradingAgentsGraph.__new__(TradingAgentsGraph)
    graph.config = {"preserve_completed_checkpoint": True}
    graph._resuming = True
    state = {"final_trade_decision": "Hold", "news_report": "Saved evidence"}
    graph.graph = Mock()
    graph.graph.get_state.return_value = SimpleNamespace(next=(), values=state)
    graph.checkpoint_scope = Mock(return_value=nullcontext("task-checkpoint"))
    graph._resolve_pending_entries = Mock()
    graph._run_graph = Mock()
    graph.process_signal = Mock(return_value="Hold")
    graph.progress_callback = Mock()
    assert graph.propagate("AAPL", "2026-09-11") == (state, "Hold")
    graph._resolve_pending_entries.assert_not_called()
    graph._run_graph.assert_not_called()
    graph.progress_callback.assert_called_once_with(state)


def test_service_retains_checkpoint_but_cli_still_clears_it():
    from unittest.mock import Mock, patch

    from tradingagents.graph.trading_graph import TradingAgentsGraph

    graph = TradingAgentsGraph.__new__(TradingAgentsGraph)
    graph.config = {"checkpoint_enabled": True, "data_cache_dir": "/unused", "preserve_completed_checkpoint": True}
    graph._run_signature = Mock(return_value="signature")
    with patch("tradingagents.graph.trading_graph.clear_checkpoint") as clear:
        graph.clear_checkpoint_on_success("AAPL", "2026-09-11")
        clear.assert_not_called()
        graph.config.pop("preserve_completed_checkpoint")
        graph.clear_checkpoint_on_success("AAPL", "2026-09-11")
        clear.assert_called_once_with("/unused", "AAPL", "2026-09-11", "signature")


def test_headless_catalog_matches_cli_depths():
    assert [value for _, value in RESEARCH_DEPTHS] == [1, 3, 5]
    assert capabilities()["analysts"] == ["market", "social", "news", "fundamentals"]
    assert "ollama" in capabilities()["models"]


def test_etf_and_index_never_bind_company_statement_tools():
    from langchain_core.messages import AIMessage
    from langchain_core.runnables import RunnableLambda

    from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst

    class FakeLLM:
        def bind_tools(self, tools):
            assert [tool.name for tool in tools] == ["get_fund_or_index_profile"]
            return RunnableLambda(lambda _: AIMessage(content="Evidence is incomplete."))

    original = deepcopy(get_config())
    try:
        for kind in ("etf", "index"):
            set_config({"security_type": kind, "instrument_profile": {"status": "unavailable"}})
            node = create_fundamentals_analyst(FakeLLM())
            result = node({"trade_date": "2026-09-11", "company_of_interest": "SPY", "messages": []})
            assert result["fundamentals_report"] == "Evidence is incomplete."
    finally:
        set_config({**original, "security_type": original.get("security_type"), "instrument_profile": original.get("instrument_profile")})
