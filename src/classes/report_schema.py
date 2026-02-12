# report_schema.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any


class ResearchReport(BaseModel):
    topic: str = Field(description="Research topic")

    executive_summary: str = Field(
        min_length=100,
        description="High-level summary of findings and implications"
    )

    key_findings: List[str] = Field(
        min_items=1,
        description="Bullet-point list of key quantitative and qualitative findings"
    )

    conclusion: str = Field(
        min_length=50,
        description="Concise concluding assessment"
    )


