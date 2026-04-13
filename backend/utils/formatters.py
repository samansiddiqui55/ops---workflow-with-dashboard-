from datetime import datetime
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def format_jira_description_from_email(
    sender_name: Optional[str],
    sender_email: str,
    brand: str,
    subject: str,
    body: str,
    cc_emails: list,
    timestamp: datetime
) -> str:
    """Format email data into Jira issue description."""
    description = f"""**Email Issue Report**

**From:** {sender_name or 'Unknown'} <{sender_email}>
**Brand:** {brand}
**Original Subject:** {subject}
**Received:** {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

{'**CC:** ' + ', '.join(cc_emails) if cc_emails else ''}

---

**Issue Description:**

{body}
"""
    return description

def format_jira_description_from_slack(
    user_name: str,
    user_id: str,
    channel_name: str,
    message: str,
    extracted_ids: dict,
    tagged_users: list,
    timestamp: datetime
) -> str:
    """Format Slack message into Jira issue description."""
    ids_text = ""
    if extracted_ids:
        ids_list = [f"- **{k.upper()}:** {v}" for k, v in extracted_ids.items() if v]
        ids_text = "\n".join(ids_list)
    
    description = f"""**Slack Bug Report**

**Reporter:** {user_name} (ID: {user_id})
**Channel:** #{channel_name}
**Reported:** {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

{'**Tagged Users:** ' + ', '.join(tagged_users) if tagged_users else ''}

**Extracted IDs:**
{ids_text if ids_text else 'No IDs extracted'}

---

**Issue Description:**

{message}
"""
    return description

def format_resolution_email(
    ticket_key: str,
    ticket_summary: str,
    resolution_comment: str,
    timestamp: datetime
) -> tuple[str, str]:
    """Format resolution email (returns subject and body)."""
    subject = f"Resolved: {ticket_summary} | {ticket_key}"
    
    body = f"""Dear Customer,

We are pleased to inform you that your support issue has been resolved.

**Ticket ID:** {ticket_key}
**Issue:** {ticket_summary}
**Resolved On:** {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

**Resolution:**
{resolution_comment}

If you have any further questions or concerns, please don't hesitate to reach out.

Thank you for your patience.

Best regards,
OpsFlow Support Team
"""
    return subject, body

def format_slack_resolution_message(
    ticket_key: str,
    ticket_summary: str,
    resolution_comment: str
) -> str:
    """Format resolution message for Slack."""
    return f""":white_check_mark: **Resolved: {ticket_key}**

**Summary:** {ticket_summary}

**Resolution:** {resolution_comment}
"""
