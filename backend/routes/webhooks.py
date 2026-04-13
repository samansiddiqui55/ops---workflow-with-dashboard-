from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import json
import logging
from datetime import datetime
from services.jira_service import jira_service
from services.slack_service import slack_service
from services.email_service import email_service
from services.mapping_service import mapping_service
from services.ai_service import ai_service
from utils.formatters import format_resolution_email, format_slack_resolution_message
from config import get_settings

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)

@router.post("/jira")
async def jira_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle Jira webhook events."""
    try:
        body = await request.body()
        payload = json.loads(body.decode())
        
        event_type = payload.get("webhookEvent")
        issue = payload.get("issue", {})
        issue_key = issue.get("key")
        
        logger.info(f"Jira webhook received: {event_type} - {issue_key}")
        
        if not event_type or not issue_key:
            return JSONResponse(status_code=200, content={"status": "ignored"})
        
        if event_type in ["jira:issue_updated", "issue_status_changed"]:
            changelog = payload.get("changelog", {})
            items = changelog.get("items", [])
            
            for item in items:
                if item.get("field") == "status":
                    new_status = item.get("toString", "")
                    
                    if new_status.lower() in ["done", "closed", "resolved"]:
                        background_tasks.add_task(
                            handle_jira_close,
                            issue_key,
                            issue.get("fields", {}).get("summary", ""),
                            new_status
                        )
        
        return JSONResponse(status_code=200, content={"status": "received"})
    
    except Exception as e:
        logger.error(f"Jira webhook error: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

async def handle_jira_close(issue_key: str, summary: str, status: str):
    """Handle Jira issue closure - send email or Slack notification."""
    try:
        logger.info(f"Processing closure for {issue_key}")
        
        resolution_comment = await jira_service.get_latest_comment(issue_key) or "Issue has been resolved."
        
        email_mapping = await mapping_service.get_email_mapping_by_jira(issue_key)
        if email_mapping:
            logger.info(f"Found email mapping for {issue_key}")
            
            subject, body = format_resolution_email(
                issue_key,
                summary,
                resolution_comment,
                datetime.utcnow()
            )
            
            ai_body = await ai_service.generate_resolution_email(summary, resolution_comment)
            
            await email_service.send_email(
                to_address=email_mapping.get("sender_email"),
                subject=subject,
                body_plain=ai_body or body,
                in_reply_to=email_mapping.get("message_id"),
                cc_addresses=email_mapping.get("cc_emails", [])
            )
            
            await mapping_service.update_email_mapping_status(issue_key, "closed")
            logger.info(f"Resolution email sent for {issue_key}")
        
        slack_mapping = await mapping_service.get_slack_mapping_by_jira(issue_key)
        if slack_mapping:
            logger.info(f"Found Slack mapping for {issue_key}")
            
            message = format_slack_resolution_message(
                issue_key,
                summary,
                resolution_comment
            )
            
            await slack_service.post_message(
                channel_id=slack_mapping.get("channel_id"),
                text=message,
                thread_ts=slack_mapping.get("slack_thread_ts")
            )
            
            await mapping_service.update_slack_mapping_status(issue_key, "closed")
            logger.info(f"Resolution message posted to Slack for {issue_key}")
    
    except Exception as e:
        logger.error(f"Error handling Jira close: {str(e)}")

@router.post("/slack/events")
async def slack_events(request: Request, background_tasks: BackgroundTasks):
    """Handle Slack events."""
    try:
        body = await request.body()
        payload = json.loads(body.decode())
        
        if payload.get("type") == "url_verification":
            return JSONResponse(content={"challenge": payload["challenge"]})
        
        if payload.get("type") == "event_callback":
            event = payload.get("event", {})
            event_type = event.get("type")
            
            if event_type == "app_mention":
                background_tasks.add_task(handle_slack_app_mention, event)
            elif event_type == "message" and event.get("channel_type") == "channel":
                channel_info = await slack_service.get_channel_info(event.get("channel"))
                if channel_info and channel_info.get("name") == get_settings().slack_bug_channel:
                    background_tasks.add_task(handle_slack_bug_message, event)
        
        return JSONResponse(status_code=200, content={"status": "ok"})
    
    except Exception as e:
        logger.error(f"Slack webhook error: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

async def handle_slack_app_mention(event: dict):
    """Handle app mention in Slack."""
    logger.info(f"App mention: {event}")

async def handle_slack_bug_message(event: dict):
    """Handle message in #bug-reporting channel."""
    from services.parser_service import ParserService
    from utils.formatters import format_jira_description_from_slack
    
    try:
        text = event.get("text", "")
        user_id = event.get("user")
        channel_id = event.get("channel")
        message_ts = event.get("ts")
        
        if event.get("subtype") == "bot_message":
            return
        
        parser = ParserService()
        is_valid, validation_message = parser.is_valid_slack_message(text)
        
        if not is_valid:
            await slack_service.post_message(
                channel_id=channel_id,
                text=f":warning: {validation_message}",
                thread_ts=message_ts
            )
            return
        
        user_info = await slack_service.get_user_info(user_id)
        channel_info = await slack_service.get_channel_info(channel_id)
        
        extracted_ids = parser.extract_tracking_ids(text)
        tagged_users = parser.parse_slack_user_mentions(text)
        
        summary = f"Slack Bug: {text[:100]}"
        description = format_jira_description_from_slack(
            user_name=user_info.get("real_name", "Unknown") if user_info else "Unknown",
            user_id=user_id,
            channel_name=channel_info.get("name", "unknown") if channel_info else "unknown",
            message=text,
            extracted_ids=extracted_ids,
            tagged_users=tagged_users,
            timestamp=datetime.utcnow()
        )
        
        ai_category = await ai_service.categorize_issue(text, "slack")
        
        jira_result = await jira_service.create_issue(
            project_key="OPS",
            summary=summary,
            description=description,
            issue_type="Bug",
            priority=ai_category.get("priority", "Medium")
        )
        
        mapping_data = {
            "slack_thread_ts": message_ts,
            "slack_message_ts": message_ts,
            "channel_id": channel_id,
            "channel_name": channel_info.get("name") if channel_info else None,
            "jira_ticket_id": jira_result["issue_id"],
            "jira_ticket_key": jira_result["issue_key"],
            "created_by_slack_id": user_id,
            "created_by_name": user_info.get("real_name") if user_info else None,
            "original_message": text,
            "extracted_ids": extracted_ids,
            "tagged_users": tagged_users,
            "status": "open",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await mapping_service.create_slack_mapping(mapping_data)
        
        await slack_service.post_message(
            channel_id=channel_id,
            text=f":white_check_mark: Jira ticket created: *{jira_result['issue_key']}*\n{jira_result.get('self_url', '')}",
            thread_ts=message_ts
        )
        
        logger.info(f"Slack bug report processed: {jira_result['issue_key']}")
    
    except Exception as e:
        logger.error(f"Error handling Slack bug message: {str(e)}")
        await slack_service.post_message(
            channel_id=channel_id,
            text=f":x: Error creating ticket: {str(e)}",
            thread_ts=message_ts
        )
