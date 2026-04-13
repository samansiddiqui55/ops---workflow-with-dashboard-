import re
from typing import Tuple

def is_valid_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_valid_jira_key(key: str) -> bool:
    """Validate Jira issue key format (e.g., PROJ-123)."""
    pattern = r'^[A-Z]+-\d+$'
    return bool(re.match(pattern, key))

def is_valid_slack_ts(timestamp: str) -> bool:
    """Validate Slack timestamp format."""
    pattern = r'^\d+\.\d+$'
    return bool(re.match(pattern, timestamp))

def sanitize_text(text: str, max_length: int = 5000) -> str:
    """Sanitize and truncate text for storage."""
    if not text:
        return ""
    
    text = text.strip()
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text

def extract_domain_from_email(email: str) -> str:
    """Extract domain from email address."""
    if '@' in email:
        return email.split('@')[-1].lower()
    return ""
