"""
Seed script for OpsFlow analytics testing.
Creates sample tickets with realistic issue types based on real ops data.
"""
import asyncio
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import random
import uuid
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "opsflow_db")

# Real brands from the ops report
BRANDS = [
    "Purplle", "Oziva", "Kapiva", "PUMA", "Atomberg", 
    "Snitch", "Giva", "Decathlon", "Nykaa", "Truemeds",
    "Bebodywise", "Souled Store", "Pantaloons", "Mokobara",
    "Bombay Shaving", "NEWME", "Hopscotch", "FYND", "ShopRocket"
]

# Issue types from the taxonomy
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

# Realistic issue weights (based on ops report analysis)
ISSUE_WEIGHTS = {
    "Pincode Serviceability": 25,
    "Webhook Issue": 12,
    "Order Creation Failure": 15,
    "Delay / TAT Issue": 10,
    "Alias Mapping": 10,
    "API / Integration Issue": 8,
    "Cost Policy Issue": 3,
    "Warehouse Issue": 5,
    "Shipment / AWB Issue": 7,
    "Panel / UI Issue": 2,
    "Other": 3
}

# Sample summaries for each issue type
SUMMARIES = {
    "Pincode Serviceability": [
        "Drop Pincode Not Serviceable - 400001",
        "Area not covered for delivery - Bangalore South",
        "Pincode 560034 showing non-serviceable",
        "NDD Pincode serviceability issue",
        "SDD pincode not available in system"
    ],
    "Webhook Issue": [
        "Webhook not triggering for status updates",
        "Callback URL returning 500 error",
        "Webhook payload missing tracking info",
        "Status webhook delayed by 24 hours",
        "Webhook activation required for new channel"
    ],
    "Order Creation Failure": [
        "Orders not getting created in system",
        "Order sync failing from Unicommerce",
        "Duplicate order creation error",
        "Order allocation not working",
        "Bulk order upload failing"
    ],
    "Delay / TAT Issue": [
        "Shipment stuck in transit for 5 days",
        "TAT exceeded - delivery delayed",
        "Multiple NDRs for same order",
        "Delivery delayed due to wrong routing",
        "TAT change request for metro cities"
    ],
    "Alias Mapping": [
        "Incorrect warehouse alias mapping",
        "New alias mapping request for WH_BLR",
        "Alias not syncing with partner system",
        "Wrong alias causing misrouting",
        "Alias update needed for new location"
    ],
    "API / Integration Issue": [
        "API timeout on order creation endpoint",
        "Invalid token error on authentication",
        "Integration with new logistics partner failing",
        "500 error on tracking API",
        "Rate limit exceeded for bulk operations"
    ],
    "Cost Policy Issue": [
        "Cost policy not applied for new zone",
        "Commercial rate update needed",
        "Billing discrepancy on COD orders",
        "Invoice amount mismatch",
        "Rate card update required"
    ],
    "Warehouse Issue": [
        "New warehouse setup required",
        "Warehouse address update needed",
        "Scanning issue at Blitz warehouse",
        "WH capacity limit reached",
        "Warehouse mapping incorrect"
    ],
    "Shipment / AWB Issue": [
        "AWB not generated for order",
        "Duplicate AWB assigned",
        "Shipment not getting created",
        "Wrong AWB on label",
        "AWB sync issue with partner"
    ],
    "Panel / UI Issue": [
        "Unable to login to Blitz panel",
        "Dashboard not loading orders",
        "UI error on bulk action page",
        "Report download failing",
        "Filter not working on orders page"
    ],
    "Other": [
        "General inquiry about service",
        "Request for documentation",
        "Account setup assistance needed",
        "Training request for new features",
        "Feedback on recent delivery"
    ]
}


def get_weighted_issue_type():
    """Select issue type based on weighted probability."""
    issues = list(ISSUE_WEIGHTS.keys())
    weights = list(ISSUE_WEIGHTS.values())
    return random.choices(issues, weights=weights, k=1)[0]


async def seed_tickets(count: int = 100):
    """Seed the database with sample tickets."""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    tickets_collection = db["tickets"]
    
    # Clear existing tickets
    await tickets_collection.delete_many({})
    print(f"Cleared existing tickets")
    
    tickets = []
    now = datetime.now(timezone.utc)
    
    for i in range(count):
        # Random date within last 60 days
        days_ago = random.randint(0, 60)
        created_at = now - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        brand = random.choice(BRANDS)
        issue_type = get_weighted_issue_type()
        summary = random.choice(SUMMARIES[issue_type])
        
        # Generate realistic email
        brand_slug = brand.lower().replace(" ", "")
        sender_email = f"support@{brand_slug}.com"
        
        # Status distribution: 60% open, 25% in-progress, 15% resolved
        status_roll = random.random()
        if status_roll < 0.60:
            status = "open"
        elif status_roll < 0.85:
            status = "in-progress"
        else:
            status = "resolved"
        
        ticket = {
            "id": str(uuid.uuid4()),
            "brand": brand,
            "sender_email": sender_email,
            "summary": summary,
            "full_message": f"Issue reported by {brand}:\n\n{summary}\n\nPlease investigate and resolve urgently.",
            "source": "email",
            "awb": f"AWB{random.randint(10000000, 99999999)}" if random.random() > 0.3 else None,
            "issue_type": issue_type,
            "status": status,
            "assigned_to": "Unassigned" if status == "open" else "Support Team",
            "latest_comment": "No comments yet." if status == "open" else "Being investigated",
            "resolution_notes": "Issue resolved" if status == "resolved" else None,
            "jira_issue_key": f"TEC-{random.randint(1000, 9999)}" if random.random() > 0.2 else None,
            "jira_issue_id": str(random.randint(100000, 999999)) if random.random() > 0.2 else None,
            "jira_url": None,
            "created_at": created_at,
            "updated_at": created_at + timedelta(hours=random.randint(1, 48)) if status != "open" else created_at
        }
        
        tickets.append(ticket)
    
    # Insert all tickets
    if tickets:
        await tickets_collection.insert_many(tickets)
        print(f"Inserted {len(tickets)} sample tickets")
    
    # Print summary
    print("\n=== Seed Data Summary ===")
    
    # Count by issue type
    type_counts = {}
    for t in tickets:
        it = t["issue_type"]
        type_counts[it] = type_counts.get(it, 0) + 1
    
    print("\nIssues by Type:")
    for it, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {it}: {count}")
    
    # Count by brand
    brand_counts = {}
    for t in tickets:
        b = t["brand"]
        brand_counts[b] = brand_counts.get(b, 0) + 1
    
    print("\nTop 5 Brands:")
    for b, count in sorted(brand_counts.items(), key=lambda x: -x[1])[:5]:
        print(f"  {b}: {count}")
    
    # Count by status
    status_counts = {}
    for t in tickets:
        s = t["status"]
        status_counts[s] = status_counts.get(s, 0) + 1
    
    print("\nBy Status:")
    for s, count in status_counts.items():
        print(f"  {s}: {count}")
    
    client.close()
    print("\n✅ Seed data created successfully!")


if __name__ == "__main__":
    asyncio.run(seed_tickets(100))
