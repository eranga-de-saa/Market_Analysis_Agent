from typing import List, Literal, Optional, TypedDict
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from ..classes.AnalysisPlan import AnalysisPlan
from ..classes.state import MarketAnalysisState

# ------------------------
# 1. LLM INITIALIZATION
# ------------------------
llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0
)


# ------------------------
# 3. STRUCTURED LLM
# ------------------------
planner_llm = llm.with_structured_output(AnalysisPlan)

# ------------------------
# 5. PLANNER NODE
# ------------------------
def analysis_planner_node(state: MarketAnalysisState) -> dict:
    plan = planner_llm.invoke(
        f"""
        You are a financial analysis planner.
        Produce a valid AnalysisPlan.

        User prompt:
        {state["user_prompt"]}
        """
    )

    return {
        **state,
        "analysis_plan": plan,
        "progress": ["Planning completed"]
    }
