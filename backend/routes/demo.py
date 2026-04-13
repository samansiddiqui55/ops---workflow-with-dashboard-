from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

router = APIRouter()

# In-memory storage (for demo)
TICKETS = []

class EmailTicketRequest(BaseModel):
    brand: str
    sender: str
    subject: str
    body: str
    cc: Optional[List[str]] = []

class SlackTicketRequest(BaseModel):
    username: str
    message: str
    tagged_users: Optional[List[str]] = []

# -------- CREATE EMAIL TICKET --------
@router.post("/create-email-ticket")
def create_email_ticket(data: EmailTicketRequest):
    ticket_id = f"TICKET-{str(uuid.uuid4())[:8]}"

    ticket = {
        "id": ticket_id,
        "source": "email",
        "brand": data.brand,
        "sender": data.sender,
        "summary": data.subject,
        "description": data.body,
        "status": "OPEN",
        "created_at": str(datetime.now()),
        "comments": []
    }

    TICKETS.append(ticket)

    return {"message": "Email ticket created", "ticket": ticket}


# -------- CREATE SLACK TICKET --------
@router.post("/create-slack-ticket")
def create_slack_ticket(data: SlackTicketRequest):
    message = data.message.lower()

    keywords = ["awb", "tracking", "shipment", "order", "delayed", "error"]

    if not any(word in message for word in keywords):
        return {"error": "Invalid message. Include AWB / tracking / shipment info."}

    ticket_id = f"TICKET-{str(uuid.uuid4())[:8]}"

    ticket = {
        "id": ticket_id,
        "source": "slack",
        "username": data.username,
        "summary": data.message[:50],
        "description": data.message,
        "status": "OPEN",
        "created_at": str(datetime.now()),
        "comments": []
    }

    TICKETS.append(ticket)

    return {"message": "Slack ticket created", "ticket": ticket}


# -------- GET ALL TICKETS --------
@router.get("/tickets")
def get_tickets():
    return {"tickets": TICKETS}


# -------- CLOSE TICKET --------
@router.post("/close-ticket/{ticket_id}")
def close_ticket(ticket_id: str):
    for ticket in TICKETS:
        if ticket["id"] == ticket_id:
            ticket["status"] = "CLOSED"

            if ticket["source"] == "email":
                response = f"Email sent: Issue {ticket_id} resolved."
            else:
                response = f"Slack reply: Issue {ticket_id} resolved."

            return {
                "message": "Ticket closed",
                "ticket": ticket,
                "response": response
            }

    return {"error": "Ticket not found"}