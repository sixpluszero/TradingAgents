"""Headless capability definitions shared by the interactive CLI and services."""

ANALYSTS = ("market", "social", "news", "fundamentals")
RESEARCH_DEPTHS = (
    ("Shallow - Quick research, few debate and strategy discussion rounds", 1),
    ("Medium - Middle ground, moderate debate rounds and strategy discussion", 3),
    ("Deep - Comprehensive research, in depth debate and strategy discussion", 5),
)


def capabilities():
    from tradingagents.llm_clients.model_catalog import MODEL_OPTIONS

    return {"analysts": list(ANALYSTS), "depths": [n for _, n in RESEARCH_DEPTHS],
            "models": MODEL_OPTIONS, "security_types": ["stock", "etf", "index", "crypto"]}
