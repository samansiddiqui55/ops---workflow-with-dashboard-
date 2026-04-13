from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import get_settings
import logging
from typing import Dict, Optional, List
import hmac
import hashlib
import time

logger = logging.getLogger(__name__)

class SlackService:
    """Service for Slack Bot API operations."""
    
    def __init__(self):
        settings = get_settings()
        self.bot_token = settings.slack_bot_token
        self.signing_secret = settings.slack_signing_secret
        self.bug_channel = settings.slack_bug_channel
        
        if self.bot_token:
            self.client = WebClient(token=self.bot_token)
            self.is_configured = True
        else:
            logger.warning("Slack not configured. Using mock mode.")
            self.client = None
            self.is_configured = False
    
    def verify_signature(self, timestamp: str, body: str, signature: str) -> bool:
        """Verify Slack request signature."""
        if abs(time.time() - int(timestamp)) > 60 * 5:
            return False
        
        sig_basestring = f"v0:{timestamp}:{body}".encode()
        computed_sig = 'v0=' + hmac.new(
            self.signing_secret.encode(),
            sig_basestring,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(computed_sig, signature)
    
    async def post_message(self, channel_id: str, text: str, thread_ts: Optional[str] = None) -> bool:
        """Post a message to Slack channel or thread."""
        if not self.is_configured:
            logger.info(f"MOCK: Posting to Slack channel {channel_id}: {text}")
            return True
        
        try:
            response = self.client.chat_postMessage(
                channel=channel_id,
                text=text,
                thread_ts=thread_ts
            )
            logger.info(f"Message posted to {channel_id}")
            return True
        except SlackApiError as e:
            logger.error(f"Slack API error: {str(e)}")
            return False
    
    async def get_user_info(self, user_id: str) -> Optional[Dict]:
        """Get Slack user information."""
        if not self.is_configured:
            return {"id": user_id, "name": "mock_user", "real_name": "Mock User"}
        
        try:
            response = self.client.users_info(user=user_id)
            user = response['user']
            return {
                "id": user['id'],
                "name": user['name'],
                "real_name": user.get('real_name', ''),
                "email": user.get('profile', {}).get('email', '')
            }
        except SlackApiError as e:
            logger.error(f"Failed to get user info: {str(e)}")
            return None
    
    async def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """Get Slack channel information."""
        if not self.is_configured:
            return {"id": channel_id, "name": "mock-channel"}
        
        try:
            response = self.client.conversations_info(channel=channel_id)
            channel = response['channel']
            return {
                "id": channel['id'],
                "name": channel['name'],
                "is_private": channel.get('is_private', False)
            }
        except SlackApiError as e:
            logger.error(f"Failed to get channel info: {str(e)}")
            return None
    
    async def get_permalink(self, channel_id: str, message_ts: str) -> Optional[str]:
        """Get permalink for a Slack message."""
        if not self.is_configured:
            return f"https://slack.com/mock/{channel_id}/{message_ts}"
        
        try:
            response = self.client.chat_getPermalink(
                channel=channel_id,
                message_ts=message_ts
            )
            return response['permalink']
        except SlackApiError as e:
            logger.error(f"Failed to get permalink: {str(e)}")
            return None

slack_service = SlackService()
