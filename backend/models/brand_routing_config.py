from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List

class BrandRoutingConfig(BaseModel):
    brand_name: str
    sender_domains: List[str] = []
    sender_emails: List[EmailStr] = []
    jira_project_key: str
    jira_issue_type: str = "Task"
    default_assignee: Optional[str] = None
    priority: str = "Medium"
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BrandRoutingConfigCreate(BaseModel):
    brand_name: str
    sender_domains: List[str] = []
    sender_emails: List[EmailStr] = []
    jira_project_key: str
    jira_issue_type: str = "Task"
    default_assignee: Optional[str] = None
    priority: str = "Medium"
    active: bool = True
