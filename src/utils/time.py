# utils/time.py.  This will evolve later. For now, it is enough.
from datetime import datetime, timedelta
from typing import Tuple
from ..classes.AnalysisPlan import TimeWindow
# from analysis_plan import TimeWindow  # wherever your model lives


def resolve_time_window(time_window: TimeWindow) -> Tuple[str, str]:
    """
    Resolve a structured TimeWindow into ISO start and end dates.
    """

    end = datetime.today()

    # Relative window
    if time_window.lookback_years is not None:
        start = end - timedelta(days=365 * time_window.lookback_years)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    # Explicit window
    if time_window.start and time_window.end:
        return (
            time_window.start.isoformat(),
            time_window.end.isoformat(),
        )

    # This should never happen due to model validation
    raise ValueError("Invalid TimeWindow state")


# from analysis_plan import TimeWindow


def format_time_window_for_context(time_window: TimeWindow) -> str:
    """
    Convert TimeWindow into human-readable phrasing for search queries.
    """

    if time_window.lookback_years is not None:
        return f"last {time_window.lookback_years} years"

    if time_window.start and time_window.end:
        return f"from {time_window.start.isoformat()} to {time_window.end.isoformat()}"

    return ""


