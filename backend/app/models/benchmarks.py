from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
import enum

from app.database import Base
from app.models.analysis import Industry


class MetricType(str, enum.Enum):
    CONVERSION_RATE = "conversion_rate"
    FORM_FIELDS = "form_fields"
    PAGE_SPEED = "page_speed"
    MOBILE_SCORE = "mobile_score"
    TIME_TO_VALUE = "time_to_value"
    TRIAL_LENGTH = "trial_length"
    PRICING_TRANSPARENCY = "pricing_transparency"
    SUPPORT_RESPONSE = "support_response"


class IndustryBenchmark(Base):
    __tablename__ = "industry_benchmarks"
    
    id = Column(String(100), primary_key=True)  # industry_metric combo
    industry = Column(SQLEnum(Industry), nullable=False, index=True)
    metric_type = Column(SQLEnum(MetricType), nullable=False)
    
    # Benchmark values
    p25_value = Column(Float)  # 25th percentile
    p50_value = Column(Float)  # Median
    p75_value = Column(Float)  # 75th percentile
    p90_value = Column(Float)  # 90th percentile
    
    # Metadata
    sample_size = Column(Float)
    source = Column(String(255))
    notes = Column(JSON, default=dict)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())