from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class IssueLog(BaseModel):
    source: str
    event_type: str
    jira_ticket_key: Optional[str] = None
    message: str
    metadata: dict = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class IssueLogCreate(BaseModel):
    source: str
    event_type: str
    jira_ticket_key: Optional[str] = None
    message: str
    metadata: dict = {}
