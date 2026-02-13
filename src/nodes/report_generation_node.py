# nodes/report_generation.py
from ..classes.state import MarketAnalysisState
from ..classes.report_schema import ResearchReport

from langchain_openai import ChatOpenAI
from langsmith import traceable


llm = ChatOpenAI(
    model="gpt-5-nano",
    temperature=0
)

report_llm = llm.with_structured_output(ResearchReport)


@traceable(run_type="llm")
def report_generation_node(state: MarketAnalysisState) -> dict:
    """
    Generate a comprehensive research report from computed metrics
    and external qualitative context.
    """

    plan = state.get("analysis_plan")
    computed_metrics = state.get("computed_metrics")
    external_context = state.get("external_context", [])

    if plan is None or computed_metrics is None:
        raise ValueError("analysis_plan and computed_metrics are required")

    prompt = f"""
You are a financial research analyst.

Create a comprehensive research report based on the following information.

Topic:
{plan.topic}

Computed quantitative metrics:
{computed_metrics}

Qualitative external context:
{external_context}

Instructions:
- Base conclusions strictly on the provided data.
- Do not invent metrics or facts.
- Integrate quantitative results with qualitative context where relevant.
- Keep the report concise, analytical, and professional.

Generate a well-structured report with:
1. Executive Summary
2. Key Findings
3. Conclusion
"""

    report: ResearchReport = report_llm.invoke(prompt)

    return {
        "final_report": report.model_dump(),
        "progress": ["Report generation completed"]
    }
