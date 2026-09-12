import json

from langchain_core.tools import tool

from tradingagents.dataflows.config import get_config


@tool
def get_fund_or_index_profile() -> str:
    """Read the run's dated ETF/index evidence snapshot, not corporate financial statements."""
    config = get_config()
    profile = config.get("instrument_profile")
    return json.dumps(profile or {"status": "unavailable", "note": "No fund/index profile evidence supplied. Do not invent constituents, weights, expenses or company financials."}, ensure_ascii=False, default=str)
