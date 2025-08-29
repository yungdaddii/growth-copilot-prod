"""User context and monitoring models for persistent memory."""

from sqlalchemy import Column, String, JSON, DateTime, Text, Float, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.models.base import Base


class UserContext(Base):
    """Stores user context for personalized experience."""
    
    __tablename__ = "user_contexts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String, unique=True, index=True)  # From cookie/session
    primary_domain = Column(String)  # User's main website
    competitors = Column(JSON, default=list)  # ["stripe.com", "square.com"]
    industry = Column(String)  # Detected or user-specified
    company_size = Column(String)  # SMB, Mid-market, Enterprise
    monitoring_sites = Column(JSON, default=list)  # Sites to track changes
    preferences = Column(JSON, default=dict)  # User preferences
    last_analysis = Column(JSON)  # Cache of last analysis
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SiteSnapshot(Base):
    """Stores periodic snapshots of websites for change detection."""
    
    __tablename__ = "site_snapshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain = Column(String, index=True)
    url = Column(String)
    snapshot_date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Content and structure
    page_title = Column(String)
    meta_description = Column(Text)
    headlines = Column(JSON)  # H1, H2, etc.
    cta_buttons = Column(JSON)  # Text and count of CTAs
    form_fields = Column(JSON)  # Number and types of form fields
    images_count = Column(Integer)
    testimonials_count = Column(Integer)
    
    # Performance metrics
    load_time = Column(Float)  # Seconds
    page_size = Column(Float)  # MB
    requests_count = Column(Integer)
    
    # SEO metrics
    word_count = Column(Integer)
    internal_links = Column(Integer)
    external_links = Column(Integer)
    
    # Technology stack
    technologies = Column(JSON)  # Detected frameworks, analytics tools
    
    # Full content for diff comparison
    content_hash = Column(String)  # MD5 of content for quick change detection
    full_content = Column(Text)  # Cleaned HTML/text content
    
    # Changes detected from previous snapshot
    changes_detected = Column(JSON)  # List of changes from last snapshot
    change_score = Column(Float)  # 0-100 significance of changes
    
    created_at = Column(DateTime, default=datetime.utcnow)


class CompetitorIntelligence(Base):
    """Aggregated intelligence about competitors."""
    
    __tablename__ = "competitor_intelligence"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain = Column(String, index=True)
    industry = Column(String, index=True)
    
    # Growth metrics
    estimated_traffic = Column(Integer)  # Monthly visitors
    traffic_growth = Column(Float)  # % change MoM
    domain_authority = Column(Integer)  # 0-100
    
    # Conversion optimization
    conversion_score = Column(Float)  # Our calculated score
    conversion_elements = Column(JSON)  # What they have/don't have
    
    # Recent changes
    recent_updates = Column(JSON)  # Last 30 days of changes
    new_features = Column(JSON)  # Detected new functionality
    ab_tests = Column(JSON)  # Detected A/B tests
    
    # Best practices they follow
    best_practices = Column(JSON)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GrowthBenchmark(Base):
    """Industry benchmarks for predictive scoring."""
    
    __tablename__ = "growth_benchmarks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    industry = Column(String, index=True)
    metric_name = Column(String)  # e.g., "conversion_rate", "bounce_rate"
    
    # Statistical data
    p10_value = Column(Float)  # 10th percentile
    p25_value = Column(Float)  # 25th percentile  
    median_value = Column(Float)  # 50th percentile
    p75_value = Column(Float)  # 75th percentile
    p90_value = Column(Float)  # 90th percentile
    
    # Context
    sample_size = Column(Integer)  # Number of sites in benchmark
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Impact correlations
    impact_on_conversion = Column(Float)  # How much this affects conversion
    implementation_difficulty = Column(String)  # Easy, Medium, Hard


class GrowthExperiment(Base):
    """Suggested and tracked growth experiments."""
    
    __tablename__ = "growth_experiments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String, index=True)  # Link to user context
    domain = Column(String)
    
    # Experiment details
    experiment_type = Column(String)  # A/B test, Feature add, Copy change
    title = Column(String)
    description = Column(Text)
    hypothesis = Column(Text)
    
    # Predicted impact
    predicted_impact = Column(Float)  # % improvement expected
    confidence_level = Column(Float)  # 0-100% confidence in prediction
    impact_metric = Column(String)  # What we're measuring
    
    # Implementation
    implementation_code = Column(Text)  # Actual code/changes to make
    implementation_difficulty = Column(String)
    estimated_hours = Column(Float)
    
    # Tracking
    status = Column(String, default="suggested")  # suggested, running, completed
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    actual_impact = Column(Float)  # Measured after implementation
    
    # Learning
    similar_experiments = Column(JSON)  # Links to similar experiments that worked
    success_rate = Column(Float)  # % of similar experiments that succeeded
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)