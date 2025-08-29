from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime, timezone
from uuid import UUID


class WebSocketMessage(BaseModel):
    type: Literal["chat", "analysis_update", "error", "connection", "typing"]
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MessagePayload(BaseModel):
    content: str
    conversation_id: Optional[UUID] = None
    message_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = {}


class AnalysisUpdatePayload(BaseModel):
    status: str
    message: str
    progress: Optional[int] = None  # 0-100
    data: Optional[Dict[str, Any]] = {}


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = {}