import re
import asyncio
from datetime import datetime, timezone
from typing import List, Optional
from models.ticket import TicketCreate, Ticket, TicketUpdate, classify_issue_type
from config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient
from services.jira_service import jira_service
import logging

logger = logging.getLogger(__name__)

settings = get_settings()
mongo_client = AsyncIOMotorClient(settings.mongo_url)
db = mongo_client[settings.db_name]
tickets_collection = db["tickets"]


def normalize_subject(subject: str) -> str:
    """Normalize subject for deduplication (remove RE:, FW:, etc.)"""
    subject = re.sub(r'^(re:|fw:|fwd:|aw:)\s*', '', subject.lower().strip(), flags=re.IGNORECASE)
    subject = re.sub(r'\s+', ' ', subject)
    return subject.strip()


def serialize_ticket(ticket: dict) -> dict:
    if not ticket:
        return ticket

    if "_id" in ticket:
        ticket["_id"] = str(ticket["_id"])

    for field in ["created_at", "updated_at", "resolved_at"]:
        if field in ticket and isinstance(ticket[field], datetime):
            ticket[field] = ticket[field].isoformat()

    return ticket


class TicketService:
    async def find_existing_open_ticket(self, sender_email: str, subject: str) -> Optional[dict]:
        """
        Prevent duplicate tickets:
        same sender + normalized subject + still unresolved = do not create again
        """
        try:
            normalized = normalize_subject(subject)
            
            # Check all open tickets from same sender
            cursor = tickets_collection.find({
                "sender_email": sender_email.lower().strip(),
                "status": {"$ne": "resolved"}
            })
            
            async for ticket in cursor:
                ticket_subject_normalized = normalize_subject(ticket.get("summary", ""))
                if ticket_subject_normalized == normalized:
                    logger.info(
                        f"Duplicate open ticket found for sender={sender_email}, subject={subject}"
                    )
                    return ticket

            return None

        except Exception as e:
            logger.error(f"Error checking duplicate ticket: {str(e)}")
            return None

    async def create_ticket(self, payload: TicketCreate) -> dict:
        """
        Create ticket in Mongo + Jira
        Includes issue_type classification
        """

        # 1. Check duplicate before creating
        existing_ticket = await self.find_existing_open_ticket(
            sender_email=payload.sender_email,
            subject=payload.summary
        )

        if existing_ticket:
            logger.info(
                f"Skipping duplicate ticket creation for {payload.sender_email} | {payload.summary}"
            )
            return serialize_ticket(existing_ticket)

        # 2. Classify issue type
        issue_type = classify_issue_type(payload.summary, payload.full_message)
        logger.info(f"Classified issue type: {issue_type}")

        jira_issue_key = None
        jira_issue_id = None
        jira_url = None

        # 3. Try Jira creation
        try:
            jira_result = await jira_service.create_issue(
                project_key=settings.jira_project_key,
                summary=payload.summary,
                description=f"[{issue_type}]\n\n{payload.full_message}",
                issue_type="Task",
                priority="Medium"
            )

            jira_issue_key = jira_result.get("issue_key")
            jira_issue_id = jira_result.get("issue_id")
            jira_url = jira_result.get("jira_url")

            logger.info(f"Jira issue linked successfully: {jira_issue_key}")

        except Exception as e:
            logger.warning(
                f"Jira issue creation failed. Continuing in local-only mode. Error: {str(e)}"
            )

        # 4. Create local ticket
        ticket = Ticket(
            brand=payload.brand,
            sender_email=payload.sender_email.lower().strip(),
            summary=payload.summary,
            full_message=payload.full_message,
            source=payload.source,
            awb=payload.awb,
            issue_type=issue_type,
            jira_issue_key=jira_issue_key,
            jira_issue_id=jira_issue_id,
            jira_url=jira_url
        )

        ticket_dict = ticket.model_dump()
        await tickets_collection.insert_one(ticket_dict)

        saved_ticket = await tickets_collection.find_one({"id": ticket.id})
        serialized = serialize_ticket(saved_ticket)
        
        # Broadcast new ticket via WebSocket
        try:
            import builtins
            if hasattr(builtins, 'ws_manager'):
                import asyncio
                asyncio.ensure_future(builtins.ws_manager.broadcast({
                    "type": "new_ticket",
                    "ticket": serialized
                }))
        except Exception as e:
            logger.warning(f"WebSocket broadcast failed: {e}")
        
        return serialized

    async def get_all_tickets(self) -> List[dict]:
        tickets = []
        async for ticket in tickets_collection.find().sort("created_at", -1):
            tickets.append(serialize_ticket(ticket))
        return tickets

    async def create_display_ticket(self, payload: TicketCreate, email_date=None) -> Optional[dict]:
        """
        Create a display-only ticket (NO Jira creation).
        Used for historical email import - shows in dashboard but doesn't create Jira tickets.
        """
        # Check for duplicate
        existing_ticket = await self.find_existing_open_ticket(
            sender_email=payload.sender_email,
            subject=payload.summary
        )
        if existing_ticket:
            return None  # Skip duplicates silently

        # Classify issue type
        issue_type = classify_issue_type(payload.summary, payload.full_message)

        ticket = Ticket(
            brand=payload.brand,
            sender_email=payload.sender_email.lower().strip(),
            summary=payload.summary,
            full_message=payload.full_message,
            source=payload.source,
            awb=payload.awb,
            issue_type=issue_type,
            jira_issue_key=None,
            jira_issue_id=None,
            jira_url=None,
            status="open"
        )

        # Use email date if provided for historical accuracy
        if email_date:
            ticket.created_at = email_date
            ticket.updated_at = email_date

        ticket_dict = ticket.model_dump()
        await tickets_collection.insert_one(ticket_dict)
        
        return serialize_ticket(ticket_dict)

    async def get_ticket_by_id(self, ticket_id: str) -> Optional[dict]:
        ticket = await tickets_collection.find_one({"id": ticket_id})
        return serialize_ticket(ticket) if ticket else None

    async def update_ticket(self, ticket_id: str, payload: TicketUpdate) -> Optional[dict]:
        update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc)

        await tickets_collection.update_one(
            {"id": ticket_id},
            {"$set": update_data}
        )

        updated_ticket = await tickets_collection.find_one({"id": ticket_id})
        return serialize_ticket(updated_ticket) if updated_ticket else None

    async def resolve_ticket(
        self,
        ticket_id: str,
        latest_comment: str = "",
        resolution_notes: str = ""
    ) -> Optional[dict]:
        ticket = await tickets_collection.find_one({"id": ticket_id})
        if not ticket:
            return None

        # Calculate TAT (turnaround time)
        resolved_at = datetime.now(timezone.utc)
        created_at = ticket.get("created_at")
        tat_hours = None
        
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            
            delta = resolved_at - created_at
            tat_hours = round(delta.total_seconds() / 3600, 2)  # Convert to hours

        await tickets_collection.update_one(
            {"id": ticket_id},
            {
                "$set": {
                    "status": "resolved",
                    "latest_comment": latest_comment,
                    "resolution_notes": resolution_notes,
                    "resolved_at": resolved_at,
                    "tat_hours": tat_hours,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )

        jira_issue_key = ticket.get("jira_issue_key")
        if jira_issue_key and latest_comment:
            try:
                await jira_service.add_comment(jira_issue_key, latest_comment)
            except Exception as e:
                logger.warning(f"Failed to add Jira comment for {jira_issue_key}: {str(e)}")

        updated_ticket = await tickets_collection.find_one({"id": ticket_id})
        serialized = serialize_ticket(updated_ticket) if updated_ticket else None
        
        # Broadcast ticket resolved via WebSocket
        if serialized:
            try:
                import builtins
                if hasattr(builtins, 'ws_manager'):
                    asyncio.ensure_future(builtins.ws_manager.broadcast({
                        "type": "ticket_resolved",
                        "ticket": serialized
                    }))
            except Exception as e:
                logger.warning(f"WebSocket broadcast failed: {e}")
        
        return serialized

    async def delete_ticket(self, ticket_id: str) -> bool:
        result = await tickets_collection.delete_one({"id": ticket_id})
        return result.deleted_count > 0
    
    # Analytics methods
    async def get_issues_by_client(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[dict]:
        """Aggregate issues by client/brand."""
        pipeline = []
        
        match_stage = {}
        if start_date or end_date:
            match_stage["created_at"] = {}
            if start_date:
                match_stage["created_at"]["$gte"] = start_date
            if end_date:
                match_stage["created_at"]["$lte"] = end_date
        
        if match_stage:
            pipeline.append({"$match": match_stage})
        
        pipeline.extend([
            {
                "$group": {
                    "_id": {
                        "brand": "$brand",
                        "issue_type": "$issue_type"
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$group": {
                    "_id": "$_id.brand",
                    "total": {"$sum": "$count"},
                    "by_type": {
                        "$push": {
                            "issue_type": "$_id.issue_type",
                            "count": "$count"
                        }
                    }
                }
            },
            {"$sort": {"total": -1}}
        ])
        
        results = []
        async for doc in tickets_collection.aggregate(pipeline):
            results.append({
                "brand": doc["_id"] or "Unknown",
                "total": doc["total"],
                "by_type": doc["by_type"]
            })
        return results
    
    async def get_issue_type_distribution(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[dict]:
        """Aggregate issues by type."""
        pipeline = []
        
        match_stage = {}
        if start_date or end_date:
            match_stage["created_at"] = {}
            if start_date:
                match_stage["created_at"]["$gte"] = start_date
            if end_date:
                match_stage["created_at"]["$lte"] = end_date
        
        if match_stage:
            pipeline.append({"$match": match_stage})
        
        pipeline.extend([
            {
                "$group": {
                    "_id": "$issue_type",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ])
        
        results = []
        async for doc in tickets_collection.aggregate(pipeline):
            results.append({
                "issue_type": doc["_id"] or "Other",
                "count": doc["count"]
            })
        return results
    
    async def get_time_series(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[dict]:
        """Aggregate issues by date."""
        pipeline = []
        
        match_stage = {}
        if start_date or end_date:
            match_stage["created_at"] = {}
            if start_date:
                match_stage["created_at"]["$gte"] = start_date
            if end_date:
                match_stage["created_at"]["$lte"] = end_date
        
        if match_stage:
            pipeline.append({"$match": match_stage})
        
        pipeline.extend([
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ])
        
        results = []
        async for doc in tickets_collection.aggregate(pipeline):
            results.append({
                "date": doc["_id"],
                "count": doc["count"]
            })
        return results
    
    async def get_tat_by_client(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[dict]:
        """Get average TAT (turnaround time) per client."""
        pipeline = []
        
        match_stage = {"status": "resolved", "tat_hours": {"$ne": None}}
        if start_date or end_date:
            match_stage["created_at"] = {}
            if start_date:
                match_stage["created_at"]["$gte"] = start_date
            if end_date:
                match_stage["created_at"]["$lte"] = end_date
        
        pipeline.append({"$match": match_stage})
        
        pipeline.extend([
            {
                "$group": {
                    "_id": "$brand",
                    "avg_tat_hours": {"$avg": "$tat_hours"},
                    "min_tat_hours": {"$min": "$tat_hours"},
                    "max_tat_hours": {"$max": "$tat_hours"},
                    "resolved_count": {"$sum": 1}
                }
            },
            {"$sort": {"avg_tat_hours": 1}}
        ])
        
        results = []
        async for doc in tickets_collection.aggregate(pipeline):
            results.append({
                "brand": doc["_id"] or "Unknown",
                "avg_tat_hours": round(doc["avg_tat_hours"], 2) if doc["avg_tat_hours"] else 0,
                "min_tat_hours": round(doc["min_tat_hours"], 2) if doc["min_tat_hours"] else 0,
                "max_tat_hours": round(doc["max_tat_hours"], 2) if doc["max_tat_hours"] else 0,
                "resolved_count": doc["resolved_count"]
            })
        return results
    
    async def get_tat_by_issue_type(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[dict]:
        """Get average TAT per issue type."""
        pipeline = []
        
        match_stage = {"status": "resolved", "tat_hours": {"$ne": None}}
        if start_date or end_date:
            match_stage["created_at"] = {}
            if start_date:
                match_stage["created_at"]["$gte"] = start_date
            if end_date:
                match_stage["created_at"]["$lte"] = end_date
        
        pipeline.append({"$match": match_stage})
        
        pipeline.extend([
            {
                "$group": {
                    "_id": "$issue_type",
                    "avg_tat_hours": {"$avg": "$tat_hours"},
                    "min_tat_hours": {"$min": "$tat_hours"},
                    "max_tat_hours": {"$max": "$tat_hours"},
                    "resolved_count": {"$sum": 1}
                }
            },
            {"$sort": {"avg_tat_hours": 1}}
        ])
        
        results = []
        async for doc in tickets_collection.aggregate(pipeline):
            results.append({
                "issue_type": doc["_id"] or "Other",
                "avg_tat_hours": round(doc["avg_tat_hours"], 2) if doc["avg_tat_hours"] else 0,
                "min_tat_hours": round(doc["min_tat_hours"], 2) if doc["min_tat_hours"] else 0,
                "max_tat_hours": round(doc["max_tat_hours"], 2) if doc["max_tat_hours"] else 0,
                "resolved_count": doc["resolved_count"]
            })
        return results


ticket_service = TicketService()
