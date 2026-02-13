#tools/compute_market_metrics.py
from typing import Dict, Any, List, Optional
import pandas as pd
from ..classes.AnalysisPlan import Metric
from ..tools.market_metrics import METRIC_FUNCTIONS, compute_rolling_correlation, compute_beta # Assume this is defined elsewhere with the appropriate mapping of Metric to functions
# Metric and metric functions are defined elsewhere in the notebook (Metric, METRIC_FUNCTIONS, compute_rolling_correlation, compute_beta)

def compute_market_metrics(
    cleaned_data: Dict[str, pd.DataFrame],
    metrics: List[Metric],
    benchmark: Optional[str] = None
) -> Dict[str, Any]:

    results: Dict[str, Any] = {}

    # Per-asset metrics
    for symbol, df in cleaned_data.items():
        symbol_results = {}

        for metric in metrics:
            if metric in METRIC_FUNCTIONS:
                symbol_results[metric.value] = METRIC_FUNCTIONS[metric](df)

        results[symbol] = symbol_results

    # Cross-asset metrics
    if Metric.ROLLING_CORRELATION in metrics:
        results["rolling_correlation"] = compute_rolling_correlation(cleaned_data)

    if Metric.BETA in metrics:
        if benchmark is None:
            raise ValueError("Benchmark required for beta")

        for symbol in cleaned_data:
            if symbol == benchmark:
                continue

            results[symbol]["beta"] = compute_beta(
                cleaned_data[symbol],
                cleaned_data[benchmark]
            )

    return results

