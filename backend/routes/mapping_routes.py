from fastapi import APIRouter, HTTPException
from services.mapping_service import mapping_service
import logging

router = APIRouter(prefix="/mappings", tags=["mappings"])
logger = logging.getLogger(__name__)

@router.get("/email/{thread_id}")
async def get_email_mapping(thread_id: str):
    """Get email to Jira mapping by thread ID."""
    try:
        mapping = await mapping_service.get_email_mapping_by_thread(thread_id)
        if not mapping:
            raise HTTPException(status_code=404, detail="Mapping not found")
        return mapping
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting email mapping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/slack/{thread_ts}")
async def get_slack_mapping(thread_ts: str):
    """Get Slack to Jira mapping by thread timestamp."""
    try:
        mapping = await mapping_service.get_slack_mapping_by_thread(thread_ts)
        if not mapping:
            raise HTTPException(status_code=404, detail="Mapping not found")
        return mapping
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Slack mapping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jira/{ticket_key}/email")
async def get_email_mapping_by_jira(ticket_key: str):
    """Get email mapping by Jira ticket key."""
    try:
        mapping = await mapping_service.get_email_mapping_by_jira(ticket_key)
        if not mapping:
            raise HTTPException(status_code=404, detail="Email mapping not found for this ticket")
        return mapping
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jira/{ticket_key}/slack")
async def get_slack_mapping_by_jira(ticket_key: str):
    """Get Slack mapping by Jira ticket key."""
    try:
        mapping = await mapping_service.get_slack_mapping_by_jira(ticket_key)
        if not mapping:
            raise HTTPException(status_code=404, detail="Slack mapping not found for this ticket")
        return mapping
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
