from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.analysis import Industry, AnalysisStatus


class IssueFound(BaseModel):
    category: str  # conversion, performance, seo, mobile, etc.
    severity: str  # critical, high, medium, low
    title: str
    description: str
    revenue_impact: float  # Monthly revenue impact in dollars
    fix_difficulty: str  # easy, medium, hard
    fix_description: str
    estimated_fix_time: str  # "2 hours", "1 day", etc.


class QuickWin(BaseModel):
    title: str
    current_state: str
    recommended_state: str
    revenue_impact: float
    implementation_time: str
    implementation_steps: List[str]


class CompetitorInsight(BaseModel):
    competitor_domain: str
    insight: str
    advantage: str
    how_to_compete: str


class AnalysisRequest(BaseModel):
    domain: str = Field(..., description="Domain to analyze")
    conversation_id: Optional[UUID] = None
    deep_analysis: bool = False


class AnalysisResponse(BaseModel):
    id: UUID
    domain: str
    industry: Industry
    status: AnalysisStatus
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    
    # Core metrics
    performance_score: Optional[int]
    conversion_score: Optional[int]
    mobile_score: Optional[int]
    seo_score: Optional[int]
    
    # Revenue impact
    total_revenue_impact: Optional[float]
    issues_found: List[IssueFound]
    quick_wins: List[QuickWin]
    
    # Competitor insights
    competitor_insights: List[CompetitorInsight] = []
    
    # Raw results for detailed view
    raw_results: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True