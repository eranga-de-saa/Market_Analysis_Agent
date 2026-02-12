# state.py
from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
import os
from dotenv import load_dotenv
from classes.AnalysisPlan import AnalysisPlan


load_dotenv()


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
