from motor.motor_asyncio import AsyncIOMotorClient
from config import get_settings
import logging
from typing import Optional, Dict
import os

logger = logging.getLogger(__name__)

class MappingService:
    """Service for managing ticket mappings in MongoDB."""
    
    def __init__(self):
        settings = get_settings()
        self.client = AsyncIOMotorClient(settings.mongo_url)
        self.db = self.client[settings.db_name]
    
    async def create_email_mapping(self, mapping_data: Dict) -> str:
        """Create email-to-Jira ticket mapping."""
        try:
            result = await self.db.email_ticket_maps.insert_one(mapping_data)
            logger.info(f"Email mapping created: {mapping_data['email_thread_id']} -> {mapping_data['jira_ticket_key']}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create email mapping: {str(e)}")
            raise
    
    async def get_email_mapping_by_thread(self, email_thread_id: str) -> Optional[Dict]:
        """Get mapping by email thread ID."""
        try:
            mapping = await self.db.email_ticket_maps.find_one(
                {"email_thread_id": email_thread_id},
                {"_id": 0}
            )
            return mapping
        except Exception as e:
            logger.error(f"Failed to get email mapping: {str(e)}")
            return None
    
    async def get_email_mapping_by_jira(self, jira_ticket_key: str) -> Optional[Dict]:
        """Get mapping by Jira ticket key."""
        try:
            mapping = await self.db.email_ticket_maps.find_one(
                {"jira_ticket_key": jira_ticket_key},
                {"_id": 0}
            )
            return mapping
        except Exception as e:
            logger.error(f"Failed to get email mapping by Jira: {str(e)}")
            return None
    
    async def update_email_mapping_status(self, jira_ticket_key: str, status: str) -> bool:
        """Update mapping status."""
        try:
            result = await self.db.email_ticket_maps.update_one(
                {"jira_ticket_key": jira_ticket_key},
                {"$set": {"status": status}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update email mapping: {str(e)}")
            return False
    
    async def create_slack_mapping(self, mapping_data: Dict) -> str:
        """Create Slack-to-Jira ticket mapping."""
        try:
            result = await self.db.slack_ticket_maps.insert_one(mapping_data)
            logger.info(f"Slack mapping created: {mapping_data['slack_thread_ts']} -> {mapping_data['jira_ticket_key']}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create Slack mapping: {str(e)}")
            raise
    
    async def get_slack_mapping_by_thread(self, slack_thread_ts: str) -> Optional[Dict]:
        """Get mapping by Slack thread timestamp."""
        try:
            mapping = await self.db.slack_ticket_maps.find_one(
                {"slack_thread_ts": slack_thread_ts},
                {"_id": 0}
            )
            return mapping
        except Exception as e:
            logger.error(f"Failed to get Slack mapping: {str(e)}")
            return None
    
    async def get_slack_mapping_by_jira(self, jira_ticket_key: str) -> Optional[Dict]:
        """Get mapping by Jira ticket key."""
        try:
            mapping = await self.db.slack_ticket_maps.find_one(
                {"jira_ticket_key": jira_ticket_key},
                {"_id": 0}
            )
            return mapping
        except Exception as e:
            logger.error(f"Failed to get Slack mapping by Jira: {str(e)}")
            return None
    
    async def update_slack_mapping_status(self, jira_ticket_key: str, status: str) -> bool:
        """Update Slack mapping status."""
        try:
            result = await self.db.slack_ticket_maps.update_one(
                {"jira_ticket_key": jira_ticket_key},
                {"$set": {"status": status}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update Slack mapping: {str(e)}")
            return False
    
    async def get_brand_config_by_domain(self, domain: str) -> Optional[Dict]:
        """Get brand routing config by sender domain."""
        try:
            config = await self.db.brand_routing_configs.find_one(
                {"sender_domains": domain, "active": True},
                {"_id": 0}
            )
            return config
        except Exception as e:
            logger.error(f"Failed to get brand config: {str(e)}")
            return None
    
    async def get_brand_config_by_email(self, email: str) -> Optional[Dict]:
        """Get brand routing config by sender email."""
        try:
            config = await self.db.brand_routing_configs.find_one(
                {"sender_emails": email, "active": True},
                {"_id": 0}
            )
            return config
        except Exception as e:
            logger.error(f"Failed to get brand config by email: {str(e)}")
            return None
    
    async def create_brand_config(self, config_data: Dict) -> str:
        """Create brand routing configuration."""
        try:
            result = await self.db.brand_routing_configs.insert_one(config_data)
            logger.info(f"Brand config created: {config_data['brand_name']}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create brand config: {str(e)}")
            raise
    
    async def log_issue_event(self, log_data: Dict) -> str:
        """Log an issue event."""
        try:
            result = await self.db.issue_logs.insert_one(log_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to log issue event: {str(e)}")
            raise

mapping_service = MappingService()
