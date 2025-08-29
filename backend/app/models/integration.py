"""
Integration model for storing OAuth credentials and integration metadata.
"""

from enum import Enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base


class IntegrationType(str, Enum):
    """Types of integrations available."""
    GOOGLE_ANALYTICS = "google-analytics"
    SEARCH_CONSOLE = "search-console"
    GOOGLE_ADS = "google-ads"
    META_ADS = "meta-ads"
    LINKEDIN_ADS = "linkedin-ads"


class Integration(Base):
    """Store user integrations with external services."""
    __tablename__ = "integrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)  # Removed ForeignKey as users table doesn't exist
    
    # Integration details
    type = Column(SQLEnum(IntegrationType), nullable=False)
    name = Column(String(255), nullable=False)  # User-friendly name
    
    # Encrypted OAuth credentials
    credentials = Column(Text, nullable=True)  # Encrypted JSON
    
    # Status
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    
    # Additional metadata (account info, etc.)
    meta_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - commented out as User model doesn't exist yet
    # user = relationship("User", back_populates="integrations")