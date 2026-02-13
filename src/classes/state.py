# state.py
from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
import os
from .AnalysisPlan import AnalysisPlan
from typing_extensions import Annotated
from langgraph.graph.message import add_messages



class MarketAnalysisState(TypedDict):
    # User input
    user_prompt: str

    # Planning output
    analysis_plan: Optional[AnalysisPlan]

    # Market data
    raw_market_data: Optional[Any]
    cleaned_market_data: Optional[Any]

    # Statistics
    computed_metrics: Optional[Dict[str, Any]]

    # Qualitative context
    external_context: List[str]

    # Validation
    validation_results: Optional[Dict[str, Any]]
    sufficient_data: Optional[bool]

    # Control flow
    iteration_count: int

    # Outputs
    final_report: Optional[Dict[str, Any]]
    pdf_path: Optional[str]

    progress: Annotated[List[str], add_messages]
