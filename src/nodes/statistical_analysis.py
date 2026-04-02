# nodes/statistical_analysis.py

from ..classes.state import MarketAnalysisState
from ..tools.compute_market_metrics import compute_market_metrics
from ..utils.helper import make_json_safe


def statistical_analysis_node(state: MarketAnalysisState) -> dict:
    """
    Computes all requested metrics from cleaned market data.
    """

    plan = state["analysis_plan"]
    cleaned_data = state["cleaned_market_data"]

    if plan is None or cleaned_data is None:
        raise ValueError("analysis_plan and cleaned_market_data are required")

    results = compute_market_metrics(
        cleaned_data=cleaned_data,
        metrics=plan.metrics,
        benchmark=plan.universe.benchmark
    )

    results = make_json_safe(results)

    return {
        "computed_metrics": results.to_dict(),
         "progress": ["Data anlysis completed"]
    }
