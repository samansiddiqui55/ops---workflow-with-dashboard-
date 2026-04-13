import base64
import requests
from jira import JIRA
from jira.exceptions import JIRAError
from config import get_settings
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class JiraService:
    """Service for Jira REST API operations."""
    
    def __init__(self):
        settings = get_settings()
        self.base_url = settings.jira_base_url
        self.email = settings.jira_email
        self.api_token = settings.jira_api_token
        self.project_key = settings.jira_project_key
        
        if self.base_url and self.email and self.api_token:
            try:
                self.jira_client = JIRA(
                    options={"server": self.base_url, "verify": True},
                    basic_auth=(self.email, self.api_token)
                )
                
                credentials = f"{self.email}:{self.api_token}"
                encoded = base64.b64encode(credentials.encode()).decode()
                self.headers = {
                    "Authorization": f"Basic {encoded}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                logger.info(f"Jira service initialized for project: {self.project_key}")
            except Exception as e:
                logger.error(f"Failed to initialize Jira client: {str(e)}")
                self.jira_client = None
                self.headers = {}
        else:
            logger.warning("Jira credentials not configured. Using mock mode.")
            self.jira_client = None
            self.headers = {}
    
    async def create_issue(
        self,
        project_key: str,
        summary: str,
        description: str,
        issue_type: str = "Task",
        priority: str = "Medium",
        metadata: Optional[Dict] = None
    ) -> Dict[str, str]:
        """Create a Jira issue."""
        # Use configured project key if not provided
        if not project_key:
            project_key = self.project_key
            
        if not self.jira_client:
            logger.info(f"MOCK: Creating Jira issue in {project_key} - {summary}")
            mock_id = abs(hash(summary)) % 10000
            return {
                "issue_key": f"{project_key}-{mock_id}",
                "issue_id": str(mock_id),
                "jira_url": f"{self.base_url or 'https://jira.example.com'}/browse/{project_key}-{mock_id}"
            }
        
        try:
            fields = {
                "project": {"key": project_key},
                "summary": str(summary)[:255],  # Jira has 255 char limit
                "description": str(description) if description else "",
                "issuetype": {"name": str(issue_type)},
                "priority": {"name": str(priority)}
            }
            
            issue = self.jira_client.create_issue(fields=fields)
            logger.info(f"Jira issue created: {issue.key}")
            
            return {
                "issue_key": issue.key,
                "issue_id": issue.id,
                "jira_url": f"{self.base_url}/browse/{issue.key}"
            }
        except JIRAError as e:
            logger.error(f"Failed to create Jira issue: {str(e)}")
            raise Exception(f"Jira API error: {str(e)}")
    
    async def add_comment(self, issue_key: str, comment_text: str) -> bool:
        """Add comment to Jira issue."""
        if not self.jira_client:
            logger.info(f"MOCK: Adding comment to {issue_key}")
            return True
        
        try:
            self.jira_client.add_comment(issue_key, comment_text)
            logger.info(f"Comment added to {issue_key}")
            return True
        except JIRAError as e:
            logger.error(f"Failed to add comment: {str(e)}")
            return False
    
    async def get_issue_details(self, issue_key: str) -> Optional[Dict]:
        """Get issue details."""
        if not self.jira_client:
            logger.info(f"MOCK: Getting issue {issue_key}")
            return {
                "key": issue_key,
                "status": "Open",
                "summary": "Mock issue"
            }
        
        try:
            issue = self.jira_client.issue(issue_key)
            return {
                "key": issue.key,
                "id": issue.id,
                "summary": issue.fields.summary,
                "description": issue.fields.description,
                "status": issue.fields.status.name,
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None
            }
        except JIRAError as e:
            logger.error(f"Failed to get issue: {str(e)}")
            return None
    
    async def get_latest_comment(self, issue_key: str) -> Optional[str]:
        """Get the latest public comment from an issue."""
        if not self.jira_client:
            return "Issue has been resolved."
        
        try:
            issue = self.jira_client.issue(issue_key)
            comments = issue.fields.comment.comments
            if comments:
                return comments[-1].body
            return None
        except JIRAError as e:
            logger.error(f"Failed to get comments: {str(e)}")
            return None


jira_service = JiraService()
