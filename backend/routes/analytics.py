from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime, timedelta, timezone
from services.ticket_service import ticket_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def parse_date_filter(period: str) -> tuple:
    """Parse time period filter and return start/end dates."""
    now = datetime.now(timezone.utc)
    
    if period == "1w":
        start_date = now - timedelta(days=7)
    elif period == "1m":
        start_date = now - timedelta(days=30)
    elif period == "3m":
        start_date = now - timedelta(days=90)
    elif period == "6m":
        start_date = now - timedelta(days=180)
    elif period == "1y":
        start_date = now - timedelta(days=365)
    else:
        start_date = None
    
    return start_date, now


@router.get("/issues-by-client")
async def get_issues_by_client(
    period: Optional[str] = Query(None, description="Time period: 1w, 1m, 3m, 6m, 1y"),
    start_date: Optional[str] = Query(None, description="Custom start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Custom end date (ISO format)")
):
    """
    Get issue distribution by client/brand.
    Returns count of issues per brand, broken down by issue type.
    """
    # Parse dates
    if period:
        sd, ed = parse_date_filter(period)
    elif start_date or end_date:
        sd = datetime.fromisoformat(start_date) if start_date else None
        ed = datetime.fromisoformat(end_date) if end_date else None
    else:
        sd, ed = None, None
    
    data = await ticket_service.get_issues_by_client(sd, ed)
    
    return {
        "status": "success",
        "period": period or "all_time",
        "data": data
    }


@router.get("/issue-types")
async def get_issue_types(
    period: Optional[str] = Query(None, description="Time period: 1w, 1m, 3m, 6m, 1y"),
    start_date: Optional[str] = Query(None, description="Custom start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Custom end date (ISO format)")
):
    """
    Get issue type distribution.
    Returns count of issues by type.
    """
    # Parse dates
    if period:
        sd, ed = parse_date_filter(period)
    elif start_date or end_date:
        sd = datetime.fromisoformat(start_date) if start_date else None
        ed = datetime.fromisoformat(end_date) if end_date else None
    else:
        sd, ed = None, None
    
    data = await ticket_service.get_issue_type_distribution(sd, ed)
    
    return {
        "status": "success", 
        "period": period or "all_time",
        "data": data
    }


@router.get("/time-series")
async def get_time_series(
    period: Optional[str] = Query(None, description="Time period: 1w, 1m, 3m, 6m, 1y"),
    start_date: Optional[str] = Query(None, description="Custom start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Custom end date (ISO format)")
):
    """
    Get issue frequency over time.
    Returns count of issues per day.
    """
    # Parse dates
    if period:
        sd, ed = parse_date_filter(period)
    elif start_date or end_date:
        sd = datetime.fromisoformat(start_date) if start_date else None
        ed = datetime.fromisoformat(end_date) if end_date else None
    else:
        sd, ed = None, None
    
    data = await ticket_service.get_time_series(sd, ed)
    
    return {
        "status": "success",
        "period": period or "all_time",
        "data": data
    }


@router.get("/summary")
async def get_analytics_summary(
    period: Optional[str] = Query(None, description="Time period: 1w, 1m, 3m, 6m, 1y")
):
    """
    Get a summary of analytics for the dashboard.
    """
    if period:
        sd, ed = parse_date_filter(period)
    else:
        sd, ed = None, None
    
    issues_by_client = await ticket_service.get_issues_by_client(sd, ed)
    issue_types = await ticket_service.get_issue_type_distribution(sd, ed)
    time_series = await ticket_service.get_time_series(sd, ed)
    tat_by_client = await ticket_service.get_tat_by_client(sd, ed)
    tat_by_issue_type = await ticket_service.get_tat_by_issue_type(sd, ed)
    
    # Calculate totals
    total_issues = sum(item["count"] for item in issue_types)
    total_clients = len(issues_by_client)
    
    # Top issue type
    top_issue = issue_types[0] if issue_types else {"issue_type": "N/A", "count": 0}
    
    # Top client
    top_client = issues_by_client[0] if issues_by_client else {"brand": "N/A", "total": 0}
    
    # Average TAT
    total_tat_hours = sum(item.get("avg_tat_hours", 0) * item.get("resolved_count", 0) for item in tat_by_client)
    total_resolved = sum(item.get("resolved_count", 0) for item in tat_by_client)
    avg_tat = round(total_tat_hours / total_resolved, 2) if total_resolved > 0 else 0
    
    return {
        "status": "success",
        "period": period,
        "summary": {
            "total_issues": total_issues,
            "total_clients": total_clients,
            "top_issue_type": top_issue,
            "top_client": top_client,
            "avg_tat_hours": avg_tat,
            "total_resolved": total_resolved
        },
        "issues_by_client": issues_by_client,
        "issue_types": issue_types,
        "time_series": time_series,
        "tat_by_client": tat_by_client,
        "tat_by_issue_type": tat_by_issue_type
    }


@router.get("/tat-by-client")
async def get_tat_by_client(
    period: Optional[str] = Query(None, description="Time period: 1w, 1m, 3m, 6m, 1y"),
    start_date: Optional[str] = Query(None, description="Custom start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Custom end date (ISO format)")
):
    """
    Get average TAT (turnaround time) per client.
    """
    if period:
        sd, ed = parse_date_filter(period)
    elif start_date or end_date:
        sd = datetime.fromisoformat(start_date) if start_date else None
        ed = datetime.fromisoformat(end_date) if end_date else None
    else:
        sd, ed = None, None
    
    data = await ticket_service.get_tat_by_client(sd, ed)
    
    return {
        "status": "success",
        "period": period or "all_time",
        "data": data
    }


@router.get("/tat-by-issue-type")
async def get_tat_by_issue_type(
    period: Optional[str] = Query(None, description="Time period: 1w, 1m, 3m, 6m, 1y"),
    start_date: Optional[str] = Query(None, description="Custom start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Custom end date (ISO format)")
):
    """
    Get average TAT per issue type.
    """
    if period:
        sd, ed = parse_date_filter(period)
    elif start_date or end_date:
        sd = datetime.fromisoformat(start_date) if start_date else None
        ed = datetime.fromisoformat(end_date) if end_date else None
    else:
        sd, ed = None, None
    
    data = await ticket_service.get_tat_by_issue_type(sd, ed)
    
    return {
        "status": "success",
        "period": period or "all_time",
        "data": data
    }
