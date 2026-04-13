import re
from typing import Dict, List, Optional, Tuple
from email.utils import parseaddr
import hashlib
import logging

logger = logging.getLogger(__name__)

class ParserService:
    """Service for parsing and extracting information from emails and Slack messages."""
    
    @staticmethod
    def extract_sender_info(from_header: str) -> Tuple[Optional[str], str]:
        """Extract sender name and email from From header."""
        display_name, email_address = parseaddr(from_header)
        return display_name or None, email_address
    
    @staticmethod
    def extract_email_domain(email: str) -> str:
        """Extract domain from email address."""
        return email.split('@')[-1].lower() if '@' in email else ""
    
    @staticmethod
    def generate_thread_id(subject: str, participants: List[str]) -> str:
        """Generate stable thread ID from subject and participants."""
        normalized_subject = re.sub(r'^(re:|fwd:)\s*', '', subject, flags=re.IGNORECASE).strip().lower()
        sorted_participants = sorted(set(participants))
        thread_seed = f"{normalized_subject}:{''.join(sorted_participants)}"
        return hashlib.md5(thread_seed.encode()).hexdigest()[:16]
    
    @staticmethod
    def extract_tracking_ids(text: str) -> Dict[str, Optional[str]]:
        """Extract various tracking IDs from text (AWB, Shipment ID, Order ID, Tracking ID)."""
        ids = {
            'awb': None,
            'shipment_id': None,
            'order_id': None,
            'tracking_id': None
        }
        
        awb_pattern = r'\b(?:AWB|awb)[:\s#-]*([A-Z0-9]{10,15})\b'
        awb_match = re.search(awb_pattern, text, re.IGNORECASE)
        if awb_match:
            ids['awb'] = awb_match.group(1)
        
        shipment_pattern = r'\b(?:SHIPMENT|shipment|ship)[\s_-]*(?:ID|id)[:\s#-]*([A-Z0-9]{8,20})\b'
        shipment_match = re.search(shipment_pattern, text, re.IGNORECASE)
        if shipment_match:
            ids['shipment_id'] = shipment_match.group(1)
        
        order_pattern = r'\b(?:ORDER|order)[\s_-]*(?:ID|id)[:\s#-]*([A-Z0-9]{6,15})\b'
        order_match = re.search(order_pattern, text, re.IGNORECASE)
        if order_match:
            ids['order_id'] = order_match.group(1)
        
        tracking_pattern = r'\b(?:TRACKING|tracking|track)[\s_-]*(?:ID|id|number|#)[:\s#-]*([A-Z0-9]{10,25})\b'
        tracking_match = re.search(tracking_pattern, text, re.IGNORECASE)
        if tracking_match:
            ids['tracking_id'] = tracking_match.group(1)
        
        return ids
    
    @staticmethod
    def has_issue_keywords(text: str) -> bool:
        """Check if text contains issue-related keywords."""
        keywords = [
            'issue', 'delayed', 'stuck', 'failed', 'error',
            'not updated', 'missing', 'problem', 'urgent',
            'help', 'wrong', 'incorrect', 'damaged', 'lost'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)
    
    @staticmethod
    def is_valid_slack_message(text: str) -> Tuple[bool, str]:
        """Validate if Slack message is valid for ticket creation."""
        has_ids = any(ParserService.extract_tracking_ids(text).values())
        has_issue = ParserService.has_issue_keywords(text)
        
        if not has_ids and not has_issue:
            return False, "Please share AWB / Tracking ID / Shipment ID / Order ID or describe the issue clearly."
        
        if not has_ids:
            return False, "Please provide at least one of: AWB, Tracking ID, Shipment ID, or Order ID."
        
        return True, ""
    
    @staticmethod
    def parse_slack_user_mentions(text: str) -> List[str]:
        """Extract user mentions from Slack message (format: <@U1234567890>)."""
        return re.findall(r'<@(U[A-Z0-9]+)>', text)
    
    @staticmethod
    def extract_cc_emails(cc_header: str) -> List[str]:
        """Extract list of email addresses from CC header."""
        if not cc_header:
            return []
        from email.utils import getaddresses
        addresses = getaddresses([cc_header])
        return [email for _, email in addresses if email]
