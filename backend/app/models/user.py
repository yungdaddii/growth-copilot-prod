"""User model for authentication and user management."""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.models.base import Base


class SubscriptionTier(str, enum.Enum):
    """User subscription tiers."""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status."""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    INACTIVE = "inactive"


class User(Base):
    """User model for authenticated users."""
    
    __tablename__ = "users"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firebase_uid = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    
    # Profile information
    display_name = Column(String)
    photo_url = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    
    # Company information
    company_name = Column(String, nullable=True)
    company_website = Column(String, nullable=True)
    company_size = Column(String, nullable=True)  # "1-10", "11-50", "51-200", etc.
    industry = Column(String, nullable=True)
    role = Column(String, nullable=True)  # "Founder", "Marketing", "Growth", etc.
    
    # Subscription details
    subscription_tier = Column(
        SQLEnum(SubscriptionTier),
        default=SubscriptionTier.FREE,
        nullable=False
    )
    subscription_status = Column(
        SQLEnum(SubscriptionStatus),
        default=SubscriptionStatus.ACTIVE,
        nullable=False
    )
    trial_ends_at = Column(DateTime, nullable=True)
    stripe_customer_id = Column(String, nullable=True, unique=True)
    stripe_subscription_id = Column(String, nullable=True)
    
    # Feature flags and limits
    monthly_analyses_limit = Column(Integer, default=10)
    monthly_analyses_used = Column(Integer, default=0)
    can_use_ai_chat = Column(Boolean, default=True)
    can_export_data = Column(Boolean, default=False)
    can_use_api = Column(Boolean, default=False)
    
    # Account settings
    email_verified = Column(Boolean, default=False)
    email_notifications = Column(Boolean, default=True)
    weekly_report = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    last_active_at = Column(DateTime, nullable=True)
    
    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    contexts = relationship(
        "UserContext",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="UserContext.user_id"
    )
    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="Conversation.user_id"
    )
    analyses = relationship(
        "Analysis",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="Analysis.user_id"
    )
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    @property
    def is_trial(self) -> bool:
        """Check if user is in trial period."""
        if self.subscription_status == SubscriptionStatus.TRIALING:
            return self.trial_ends_at > datetime.utcnow() if self.trial_ends_at else False
        return False
    
    @property
    def is_paid(self) -> bool:
        """Check if user has a paid subscription."""
        return self.subscription_tier != SubscriptionTier.FREE
    
    @property
    def can_analyze(self) -> bool:
        """Check if user can perform analysis."""
        if self.subscription_tier == SubscriptionTier.FREE:
            return self.monthly_analyses_used < self.monthly_analyses_limit
        return True
    
    def increment_analysis_count(self):
        """Increment the monthly analysis count."""
        self.monthly_analyses_used += 1
        self.last_active_at = datetime.utcnow()
    
    def reset_monthly_usage(self):
        """Reset monthly usage counters."""
        self.monthly_analyses_used = 0