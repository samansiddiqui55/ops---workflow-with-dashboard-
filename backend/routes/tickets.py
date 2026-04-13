# from fastapi import APIRouter, HTTPException
# from models.ticket import TicketCreate, TicketUpdate
# from services.ticket_service import ticket_service

# router = APIRouter(prefix="/tickets", tags=["Tickets"])


# @router.get("/")
# async def get_all_tickets():
#     tickets = await db.issue_logs.find().to_list(length=100)

#     for ticket in tickets:
#         ticket["_id"] = str(ticket["_id"])  # 🔥 FIX HERE

#     return tickets


# @router.get("/{ticket_id}")
# async def get_ticket(ticket_id: str):
#     ticket = await ticket_service.get_ticket_by_id(ticket_id)
#     if not ticket:
#         raise HTTPException(status_code=404, detail="Ticket not found")
#     return ticket


# @router.post("/")
# async def create_ticket(payload: TicketCreate):
#     return await ticket_service.create_ticket(payload)


# @router.patch("/{ticket_id}")
# async def update_ticket(ticket_id: str, payload: TicketUpdate):
#     ticket = await ticket_service.update_ticket(ticket_id, payload)
#     if not ticket:
#         raise HTTPException(status_code=404, detail="Ticket not found")
#     return ticket


# @router.post("/{ticket_id}/resolve")
# async def resolve_ticket(ticket_id: str, payload: TicketUpdate):
#     ticket = await ticket_service.resolve_ticket(
#         ticket_id=ticket_id,
#         latest_comment=payload.latest_comment or "",
#         resolution_notes=payload.resolution_notes or ""
#     )
#     if not ticket:
#         raise HTTPException(status_code=404, detail="Ticket not found")
#     return ticket

from fastapi import APIRouter, HTTPException
from typing import List

from models.ticket import TicketCreate, TicketUpdate
from services.ticket_service import ticket_service

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("/")
async def create_ticket(payload: TicketCreate):
    return await ticket_service.create_ticket(payload)


@router.get("/")
async def get_all_tickets():
    return await ticket_service.get_all_tickets()


@router.get("/{ticket_id}")
async def get_ticket(ticket_id: str):
    ticket = await ticket_service.get_ticket_by_id(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.put("/{ticket_id}")
async def update_ticket(ticket_id: str, payload: TicketUpdate):
    ticket = await ticket_service.update_ticket(ticket_id, payload)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.post("/{ticket_id}/resolve")
async def resolve_ticket(ticket_id: str, payload: TicketUpdate):
    ticket = await ticket_service.resolve_ticket(
        ticket_id=ticket_id,
        latest_comment=payload.latest_comment or "",
        resolution_notes=payload.resolution_notes or ""
    )

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return {
        "message": f"Ticket {ticket_id} resolved successfully",
        "ticket": ticket
    }