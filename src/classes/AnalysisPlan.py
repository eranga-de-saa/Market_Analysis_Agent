from typing import List, Optional, Literal
from enum import Enum
from datetime import date
from pydantic import BaseModel, Field, model_validator
import re

class AnalysisIntent(str, Enum):
    PERFORMANCE = "performance"
    RISK = "risk"
    VOLATILITY = "volatility"
    LIQUIDITY = "liquidity"
    CORRELATION = "correlation"
    VALUATION = "valuation"
    EVENT_IMPACT = "event_impact"
    REGIME_DETECTION = "regime_detection"
    EXPLORATORY = "exploratory"

class MarketType(str, Enum):
    EQUITIES = "equities"
    CRYPTO = "crypto"
    RATES = "rates"
    FX = "fx"
    COMMODITIES = "commodities"
    MIXED = "mixed"


class Metric(str, Enum):
    TOTAL_RETURN = "total_return"
    CAGR = "cagr"
    SHARPE_RATIO = "sharpe_ratio"
    MAX_DRAWDOWN = "max_drawdown"

    REALIZED_VOLATILITY = "realized_volatility"
    ROLLING_VOLATILITY = "rolling_volatility"

    ROLLING_CORRELATION = "rolling_correlation"
    BETA = "beta"

    VOLUME = "volume"
    AMIHUD_ILLIQUIDITY = "amihud_illiquidity"

    REGIME_SWITCHING = "regime_switching"


class Universe(BaseModel):
    assets: List[str] = Field(min_length=1)
    benchmark: Optional[str] = None

    @model_validator(mode="before")
    def normalize_symbols(cls, v):
        def normalize(s: str) -> str:
            m = re.search(r"\(([A-Z\.]+)\)", s)
            return m.group(1) if m else s.upper().strip()

        v["assets"] = [normalize(a) for a in v.get("assets", [])]

        if v.get("benchmark"):
            v["benchmark"] = normalize(v["benchmark"])

        return v
    
class TimeWindow(BaseModel):
    start: Optional[date] = None
    end: Optional[date] = None
    lookback_years: Optional[int] = Field(gt=0)

    @model_validator(mode="after")
    def validate_time_window(self):
        explicit = self.start is not None or self.end is not None
        relative = self.lookback_years is not None

        if explicit and relative:
            raise ValueError("Use either start/end or lookback_years, not both")

        if not explicit and not relative:
            raise ValueError("Time window must be specified")

        if explicit and not (self.start and self.end):
            raise ValueError("Both start and end must be provided")

        return self

class ConfidenceRequirements(BaseModel):
    confidence_level: float = Field(default=0.95, gt=0.5, lt=1.0)
    alpha: float = Field(default=0.05, gt=0.0, lt=0.2)
    require_confidence_intervals: bool = True



class AnalysisPlan(BaseModel):
    topic: str = Field(min_length=10)

    intent: AnalysisIntent
    market: MarketType

    universe: Universe
    metrics: List[Metric] = Field(min_length=1)

    time_window: TimeWindow
    frequency: Literal["daily", "weekly", "monthly"]

    confidence_requirements: Optional[ConfidenceRequirements] = None


