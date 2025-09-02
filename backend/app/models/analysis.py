from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, JSON, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class Industry(str, enum.Enum):
    SAAS = "saas"
    ECOMMERCE = "ecommerce"
    ENTERPRISE = "enterprise"
    MARKETPLACE = "marketplace"
    AGENCY = "agency"
    FINTECH = "fintech"
    HEALTHTECH = "healthtech"
    EDTECH = "edtech"
    OTHER = "other"


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"))
    domain = Column(String(255), nullable=False, index=True)
    industry = Column(SQLEnum(Industry), default=Industry.OTHER)
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Float)
    
    # Results
    results = Column(JSON, default=dict)
    issues_found = Column(JSON, default=list)
    revenue_impact = Column(Float)  # Total monthly revenue impact
    quick_wins = Column(JSON, default=list)
    
    # Metrics
    performance_score = Column(Integer)  # 0-100
    conversion_score = Column(Integer)  # 0-100
    mobile_score = Column(Integer)  # 0-100
    seo_score = Column(Integer)  # 0-100
    
    # Relationships
    user = relationship("User", back_populates="analyses", foreign_keys=[user_id])
    conversation = relationship("Conversation", back_populates="analyses")


class CompetitorCache(Base):
    __tablename__ = "competitor_cache"
    
    domain = Column(String(255), primary_key=True)
    industry = Column(SQLEnum(Industry), nullable=False)
    last_analyzed = Column(DateTime(timezone=True), server_default=func.now())
    
    # Cached metrics
    metrics = Column(JSON, default=dict)
    features = Column(JSON, default=list)
    pricing_model = Column(String(100))
    traffic_estimate = Column(Integer)
    
    # Update tracking
    update_frequency = Column(Integer, default=86400)  # seconds
    analysis_count = Column(Integer, default=0)