# nodes/context_research.py
from classes.state import MarketAnalysisState
from tools.context_research import (
    generate_symbol_topic,
    research_market_context_for_symbol
)
from utils.time import format_time_window_for_context


def context_research_node(state: MarketAnalysisState) -> dict:
    """
    Collects qualitative market context per symbol
    and appends results to external_context.
    """

    plan = state["analysis_plan"]

    if plan is None:
        raise ValueError("analysis_plan is required before context research")

    time_phrase = format_time_window_for_context(plan.time_window)

    new_entries = []

    for symbol in plan.universe.assets:
        symbol_topic = generate_symbol_topic(
            global_topic=plan.topic,
            symbol=symbol,
            market=plan.market.value
        )

        summary = research_market_context_for_symbol(
            topic=symbol_topic,
            symbol=symbol,
            time_phrase=time_phrase
        )

        new_entries.append(
            {
                "symbol": symbol,
                "topic": symbol_topic,
                "summary": summary
            }
        )

    return {
        "external_context": new_entries
    }
