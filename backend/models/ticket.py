from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime, timezone
import uuid


# Issue type categories for logistics support (derived from real ops data)
ISSUE_TYPES = [
    "Pincode Serviceability",
    "Webhook Issue",
    "Order Creation Failure",
    "Delay / TAT Issue",
    "Alias Mapping",
    "API / Integration Issue",
    "Cost Policy Issue",
    "Warehouse Issue",
    "Shipment / AWB Issue",
    "Panel / UI Issue",
    "Other"
]


class TicketCreate(BaseModel):
    brand: str
    sender_email: str
    summary: str
    full_message: str
    source: str
    awb: Optional[str] = None
    issue_type: Optional[str] = "Other"


class TicketUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    latest_comment: Optional[str] = None
    resolution_notes: Optional[str] = None
    issue_type: Optional[str] = None


class Ticket(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    brand: str
    sender_email: str
    summary: str
    full_message: str
    source: str
    awb: Optional[str] = None
    issue_type: str = "Other"

    status: str = "open"
    assigned_to: Optional[str] = None  # Changed default to None instead of "Unassigned"
    latest_comment: Optional[str] = "No comments yet."
    resolution_notes: Optional[str] = None

    jira_issue_key: Optional[str] = None
    jira_issue_id: Optional[str] = None
    jira_url: Optional[str] = None
    
    # TAT tracking
    resolved_at: Optional[datetime] = None
    tat_hours: Optional[float] = None  # Turnaround time in hours

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def classify_issue_type(subject: str, body: str) -> str:
    """
    Rule-based issue type classification.
    Analyzes subject and body to determine issue category.
    Based on real ops data taxonomy.
    """
    text = f"{subject} {body}".lower()
    
    # Pincode Serviceability
    if any(kw in text for kw in [
        "pincode", "pin code", "not serviceable", "serviceability", 
        "area not covered", "location not available", "drop pincode",
        "non serviceable", "pincode issue", "sdd pincode", "ndd pincode"
    ]):
        return "Pincode Serviceability"
    
    # Webhook Issue
    if any(kw in text for kw in [
        "webhook", "callback", "hook failed", "webhook failure", 
        "webhook error", "callback failure", "webhook not triggered",
        "webhook activation", "webhook setup"
    ]):
        return "Webhook Issue"
    
    # Order Creation Failure
    if any(kw in text for kw in [
        "order creation", "order failed", "create order", "order not created", 
        "order error", "cannot create order", "orders not getting created",
        "order sync", "order allocation", "order booking failure"
    ]):
        return "Order Creation Failure"
    
    # Delay / TAT Issue
    if any(kw in text for kw in [
        "delay", "delayed", "late", "tat", "turn around time", 
        "not delivered", "delivery delay", "shipment stuck",
        "pending", "stuck shipment", "tat change", "tat issue"
    ]):
        return "Delay / TAT Issue"
    
    # Alias Mapping
    if any(kw in text for kw in [
        "alias", "mapping", "alias mapping", "incorrect mapping", 
        "wrong alias", "wh mapping", "warehouse mapping",
        "alias issue", "mapping request"
    ]):
        return "Alias Mapping"
    
    # API / Integration Issue
    if any(kw in text for kw in [
        "api", "api failure", "api error", "endpoint", "500 error", 
        "timeout", "connection error", "integration", "token",
        "invalid token", "api timeout", "integration error"
    ]):
        return "API / Integration Issue"
    
    # Cost Policy Issue
    if any(kw in text for kw in [
        "cost policy", "pricing", "rate", "charges", "cost",
        "commercial", "billing", "invoice", "payment"
    ]):
        return "Cost Policy Issue"
    
    # Warehouse Issue
    if any(kw in text for kw in [
        "warehouse", "wh", "warehouse address", "warehouse update",
        "new warehouse", "warehouse issue", "scanning issue"
    ]):
        return "Warehouse Issue"
    
    # Shipment / AWB Issue
    if any(kw in text for kw in [
        "awb", "tracking number", "waybill", "shipment id", "awb error", 
        "wrong awb", "shipment", "shipment not getting created",
        "duplicate awb", "awb not sent", "shipment issue"
    ]):
        return "Shipment / AWB Issue"
    
    # Panel / UI Issue
    if any(kw in text for kw in [
        "panel", "ui", "dashboard", "unable to log", "login issue",
        "interface", "display", "screen", "page not loading"
    ]):
        return "Panel / UI Issue"
    
    return "Other"
