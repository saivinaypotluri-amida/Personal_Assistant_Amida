from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    is_admin: bool = False


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_admin: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# OAuth Configuration
class OAuthConfig(BaseModel):
    service: str  # 'google', 'slack', 'azure_openai'
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    additional_config: Optional[Dict[str, Any]] = None


# Email Summary Request
class EmailSummaryRequest(BaseModel):
    days: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    source: str = "portal"  # 'portal' or 'slack'
    slack_channel: Optional[str] = None
    slack_thread_ts: Optional[str] = None


class EmailSummary(BaseModel):
    subject: str
    from_email: str
    date: str
    summary: str
    meeting_links: List[str]


class EmailSummaryResponse(BaseModel):
    summaries: List[EmailSummary]
    total_emails: int
    digest_sent: bool


# Meeting Schedule Request
class MeetingScheduleRequest(BaseModel):
    attendees: List[str]
    duration_minutes: int
    title: Optional[str] = "Meeting"
    description: Optional[str] = ""
    next_available: bool = True
    date: Optional[str] = None
    time: Optional[str] = None
    source: str = "portal"  # 'portal' or 'slack'
    slack_channel: Optional[str] = None
    slack_thread_ts: Optional[str] = None


class MeetingScheduleResponse(BaseModel):
    success: bool
    message: str
    meeting_link: Optional[str] = None
    conflicts: Optional[List[str]] = None


# Activity Log
class ActivityLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    source: str
    status: str
    details: Optional[Dict[str, Any]]
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Cost Tracking
class CostTrackingResponse(BaseModel):
    id: int
    user_id: int
    service: str
    operation: str
    tokens_used: int
    estimated_cost: float
    timestamp: datetime
    
    class Config:
        from_attributes = True


class UserStats(BaseModel):
    total_operations: int
    total_cost: float
    operations_by_type: Dict[str, int]
