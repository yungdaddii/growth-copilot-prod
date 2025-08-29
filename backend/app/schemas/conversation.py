from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.conversation import MessageRole, MessageType


class MessageCreate(BaseModel):
    role: MessageRole
    content: str
    message_type: MessageType = MessageType.TEXT
    metadata: Optional[Dict[str, Any]] = {}


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    message_type: MessageType
    metadata: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    metadata: Optional[Dict[str, Any]] = {}


class ConversationResponse(BaseModel):
    id: UUID
    share_slug: str
    created_at: datetime
    updated_at: Optional[datetime]
    metadata: Dict[str, Any]
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True