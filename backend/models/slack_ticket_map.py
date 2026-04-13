from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class SlackTicketMap(BaseModel):
    slack_thread_ts: str
    slack_message_ts: str
    channel_id: str
    channel_name: Optional[str] = None
    jira_ticket_id: str
    jira_ticket_key: str
    created_by_slack_id: str
    created_by_name: Optional[str] = None
    original_message: str
    extracted_ids: dict = {}
    tagged_users: List[str] = []
    status: str = "open"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SlackTicketMapCreate(BaseModel):
    slack_thread_ts: str
    slack_message_ts: str
    channel_id: str
    channel_name: Optional[str] = None
    jira_ticket_id: str
    jira_ticket_key: str
    created_by_slack_id: str
    created_by_name: Optional[str] = None
    original_message: str
    extracted_ids: dict = {}
    tagged_users: List[str] = []
