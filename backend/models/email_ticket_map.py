from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class EmailTicketMap(BaseModel):
    email_thread_id: str
    message_id: str
    jira_ticket_id: str
    jira_ticket_key: str
    brand: str
    sender_email: str
    sender_name: Optional[str] = None
    original_subject: str
    cc_emails: List[str] = []
    status: str = "open"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class EmailTicketMapCreate(BaseModel):
    email_thread_id: str
    message_id: str
    jira_ticket_id: str
    jira_ticket_key: str
    brand: str
    sender_email: str
    sender_name: Optional[str] = None
    original_subject: str
    cc_emails: List[str] = []
