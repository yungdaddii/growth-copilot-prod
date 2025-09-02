"""Authentication schemas for request/response validation."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID

from app.models.user import SubscriptionTier, SubscriptionStatus


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    display_name: Optional[str] = None
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    role: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    display_name: Optional[str] = None
    phone_number: Optional[str] = None
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    role: Optional[str] = None
    email_notifications: Optional[bool] = None
    weekly_report: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    email: str
    display_name: Optional[str]
    photo_url: Optional[str]
    phone_number: Optional[str]
    company_name: Optional[str]
    company_website: Optional[str]
    company_size: Optional[str]
    industry: Optional[str]
    role: Optional[str]
    subscription_tier: SubscriptionTier
    subscription_status: SubscriptionStatus
    trial_ends_at: Optional[datetime]
    monthly_analyses_limit: int
    monthly_analyses_used: int
    can_use_ai_chat: bool
    can_export_data: bool
    can_use_api: bool
    email_verified: bool
    email_notifications: bool
    weekly_report: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = 3600
    refresh_token: Optional[str] = None


class LoginRequest(BaseModel):
    """Schema for login request."""
    id_token: str = Field(..., description="Firebase ID token from client-side auth")


class SubscriptionUpdate(BaseModel):
    """Schema for updating subscription."""
    tier: SubscriptionTier
    status: SubscriptionStatus
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    trial_ends_at: Optional[datetime] = None