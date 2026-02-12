#nodes/market_data_collection.py
# 

from classes.state import MarketAnalysisState
from tools.market_data import fetch_market_data
from utils.time import resolve_time_window


def market_data_collection_node(state: MarketAnalysisState) -> dict:
    """
    Collects raw market time series data based on AnalysisPlan.
    Safe for re-execution and looping.
    """

    plan = state["analysis_plan"]

    if plan is None:
        raise ValueError("analysis_plan is required before data collection")

    # Resolve structured time window
    start_date, end_date = resolve_time_window(plan.time_window)

    # Extract assets only (benchmarks handled separately later)
    symbols = plan.universe.assets

    raw_data = fetch_market_data(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        frequency=plan.frequency
    )

    return {
        "raw_market_data": raw_data
    }
