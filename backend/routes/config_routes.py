from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from services.mapping_service import mapping_service
import logging

router = APIRouter(prefix="/config", tags=["configuration"])
logger = logging.getLogger(__name__)

class BrandConfigRequest(BaseModel):
    brand_name: str
    sender_domains: List[str] = []
    sender_emails: List[EmailStr] = []
    jira_project_key: str
    jira_issue_type: str = "Task"
    default_assignee: Optional[str] = None
    priority: str = "Medium"
    active: bool = True

@router.post("/brands")
async def create_brand_config(config: BrandConfigRequest):
    """Create a new brand routing configuration."""
    try:
        from datetime import datetime
        config_data = config.model_dump()
        config_data["created_at"] = datetime.utcnow()
        config_data["updated_at"] = datetime.utcnow()
        
        config_id = await mapping_service.create_brand_config(config_data)
        return {
            "status": "success",
            "config_id": config_id,
            "brand_name": config.brand_name
        }
    except Exception as e:
        logger.error(f"Error creating brand config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brands/{domain}")
async def get_brand_config(domain: str):
    """Get brand configuration by domain."""
    try:
        config = await mapping_service.get_brand_config_by_domain(domain)
        if not config:
            raise HTTPException(status_code=404, detail="Brand config not found")
        return config
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting brand config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
