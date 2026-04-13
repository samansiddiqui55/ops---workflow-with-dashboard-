"""
Seed historical ticket data from the TechSupport Report PDF.
This populates MongoDB with real historical issue data for analytics and dashboard.
"""
import asyncio
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from config import get_settings
import uuid
import random

settings = get_settings()
client = AsyncIOMotorClient(settings.mongo_url)
db = client[settings.db_name]

# Historical issues extracted from the PDF report
HISTORICAL_ISSUES = [
    {"date": "2024-11-12", "brand": "Purplle", "issue_type": "Shipment / AWB Issue", "summary": "Numeric Waybill Issue", "status": "resolved", "orders_impacted": 1},
    {"date": "2024-11-25", "brand": "OZiva", "issue_type": "Shipment / AWB Issue", "summary": "Offloaded Shipments at Airport", "status": "resolved", "orders_impacted": 31},
    {"date": "2024-12-03", "brand": "Heallo", "issue_type": "Shipment / AWB Issue", "summary": "Duplicate AWB & Serviceability Issue", "status": "resolved", "orders_impacted": 3},
    {"date": "2024-12-05", "brand": "Onestolabs", "issue_type": "Webhook Issue", "summary": "Delay in Order Sync & Webhook Integration", "status": "resolved", "orders_impacted": 10},
    {"date": "2024-12-20", "brand": "Powerlook", "issue_type": "Pincode Serviceability", "summary": "Serviceability Issue - Multiple Pincodes", "status": "resolved", "orders_impacted": 50},
    {"date": "2024-12-21", "brand": "TrueMeds", "issue_type": "API / Integration Issue", "summary": "Authorization failures and webhook issues", "status": "resolved", "orders_impacted": 14},
    {"date": "2025-01-02", "brand": "Powerlook", "issue_type": "API / Integration Issue", "summary": "Invalid Token - Authorization Error", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-01-06", "brand": "Shipdelight", "issue_type": "Cost Policy Issue", "summary": "Cost Policy Missing for Route", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-01-10", "brand": "PUMA", "issue_type": "Shipment / AWB Issue", "summary": "Duplicate AWB assigned Error", "status": "resolved", "orders_impacted": 1},
    {"date": "2025-01-13", "brand": "Atomberg", "issue_type": "Webhook Issue", "summary": "Webhook status flow not triggered", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-01-16", "brand": "Kapiva", "issue_type": "Order Creation Failure", "summary": "Order Creation Failure - Automation Issue", "status": "resolved", "orders_impacted": 9},
    {"date": "2025-01-20", "brand": "PROZO", "issue_type": "Pincode Serviceability", "summary": "Pincode Serviceability - Internal Server Error", "status": "resolved", "orders_impacted": 2},
    {"date": "2025-01-23", "brand": "Snitch", "issue_type": "Delay / TAT Issue", "summary": "EDD mismatch for SDD and NDD shipments", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-01-27", "brand": "Shoppers Stop", "issue_type": "Pincode Serviceability", "summary": "Pin Code Error - Service Area Issue", "status": "resolved", "orders_impacted": 1},
    {"date": "2025-02-01", "brand": "EshopBox", "issue_type": "Delay / TAT Issue", "summary": "Delay in Delivery for Multiple Shipments", "status": "resolved", "orders_impacted": 4},
    {"date": "2025-02-03", "brand": "Bebodywise", "issue_type": "Pincode Serviceability", "summary": "Pickup from particular Pincode failing", "status": "resolved", "orders_impacted": 1},
    {"date": "2025-02-04", "brand": "Purplle", "issue_type": "Shipment / AWB Issue", "summary": "Incorrect Return Address on Label", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-02-05", "brand": "Giva", "issue_type": "Order Creation Failure", "summary": "Hyperlocal Account Created - Order Failure", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-02-06", "brand": "Truemeds", "issue_type": "Order Creation Failure", "summary": "Courier Booking Error - System Issue", "status": "resolved", "orders_impacted": 11},
    {"date": "2025-02-07", "brand": "Decathlon", "issue_type": "Order Creation Failure", "summary": "Shipment Not Getting Created", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-02-10", "brand": "Shiprocket", "issue_type": "Warehouse Issue", "summary": "Warehouse Mapping Request", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-02-12", "brand": "Souled Store", "issue_type": "API / Integration Issue", "summary": "Pushing same token causing duplicate", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-02-17", "brand": "Pantaloons", "issue_type": "Pincode Serviceability", "summary": "Dead Weight Pincode Serviceability Issue", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-02-20", "brand": "Mossaic Wellness", "issue_type": "Delay / TAT Issue", "summary": "NDD Operations - Service Availability Confirmation", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-02-21", "brand": "Bebodywise", "issue_type": "Webhook Issue", "summary": "Order Sync Issue: Tracking Status Update Delay", "status": "resolved", "orders_impacted": 10},
    {"date": "2025-02-24", "brand": "Shiprocket", "issue_type": "API / Integration Issue", "summary": "Integration with New Logistics Partner", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-02-25", "brand": "OZiva", "issue_type": "Order Creation Failure", "summary": "Orders Not Getting Created - System Error", "status": "resolved", "orders_impacted": 83},
    {"date": "2025-02-26", "brand": "ShipDelight", "issue_type": "Warehouse Issue", "summary": "WH Mapping Request for New Warehouse", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-03-04", "brand": "ShoppersStop", "issue_type": "Order Creation Failure", "summary": "Allocation Issue - Orders Not Processed", "status": "resolved", "orders_impacted": 3},
    {"date": "2025-03-13", "brand": "Mossaic Wellness", "issue_type": "Alias Mapping", "summary": "Alias Mapping for Lucknow Warehouse", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-03-17", "brand": "OZiva", "issue_type": "Pincode Serviceability", "summary": "Errors due to NDD/SDD Pincode Serviceability", "status": "resolved", "orders_impacted": 13},
    {"date": "2025-03-22", "brand": "The House of Rare", "issue_type": "Pincode Serviceability", "summary": "Metro-to-Metro Orders Failing", "status": "resolved", "orders_impacted": 2},
    {"date": "2025-03-25", "brand": "Mokobara", "issue_type": "Panel / UI Issue", "summary": "Unable to log on Blitz account", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-03-29", "brand": "Bombay Shaving", "issue_type": "Cost Policy Issue", "summary": "Bombay Shaving & Wellness Commercial update", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-04-01", "brand": "House of Vaaree", "issue_type": "Webhook Issue", "summary": "Tracking Update on Client Panel Sync Issue", "status": "resolved", "orders_impacted": 20},
    {"date": "2025-04-02", "brand": "iThink Logistics", "issue_type": "Alias Mapping", "summary": "RTO address to be updated in system", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-04-03", "brand": "Easycom", "issue_type": "Order Creation Failure", "summary": "Allocated to Shiprocket but supposed to be Grow Simplee", "status": "resolved", "orders_impacted": 10},
    {"date": "2025-04-07", "brand": "Clickpost", "issue_type": "API / Integration Issue", "summary": "Wrong token causing auth failures", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-04-08", "brand": "Snitch", "issue_type": "Pincode Serviceability", "summary": "Issue with Non Serviceable Pincodes", "status": "resolved", "orders_impacted": 15},
    {"date": "2025-04-09", "brand": "ShipDelight", "issue_type": "Shipment / AWB Issue", "summary": "Cancelled Shipments to Be marked As Lost", "status": "resolved", "orders_impacted": 5},
    {"date": "2025-04-10", "brand": "House of Vaaree", "issue_type": "Alias Mapping", "summary": "Allocation Logix - Alias Mapping Error", "status": "resolved", "orders_impacted": 5},
    {"date": "2025-04-10", "brand": "NEWME", "issue_type": "Warehouse Issue", "summary": "Warehouse Address Update Required", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-04-24", "brand": "OZiva", "issue_type": "Shipment / AWB Issue", "summary": "Scanning Issue at Blitz Facility", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-04-28", "brand": "EshopBox", "issue_type": "Order Creation Failure", "summary": "Please Try After Sometime Error For Booking", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-04-29", "brand": "Decathlon", "issue_type": "Webhook Issue", "summary": "Status not sync in easyecom", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-04-29", "brand": "Bombay Shaving", "issue_type": "Webhook Issue", "summary": "Blitz Webhook Activation Required", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-05-06", "brand": "ShipDelight", "issue_type": "Order Creation Failure", "summary": "In Process Error For Blitz Booking", "status": "resolved", "orders_impacted": 102},
    {"date": "2025-05-13", "brand": "Alamode Label", "issue_type": "Alias Mapping", "summary": "Alias Mapping for New Location", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-05-14", "brand": "Atomberg", "issue_type": "Order Creation Failure", "summary": "Multiple NDRs for Buyer-Cancelled Orders", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-05-15", "brand": "Protonics", "issue_type": "Alias Mapping", "summary": "Alias Mapping Update Required", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-05-21", "brand": "BNSL-Shipsy", "issue_type": "Order Creation Failure", "summary": "Unable to Cancel Order in System", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-05-27", "brand": "Bright Lifecare", "issue_type": "Delay / TAT Issue", "summary": "Bombay shaving company TAT change request", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-05-29", "brand": "Medikabazaar", "issue_type": "Shipment / AWB Issue", "summary": "Forcefully shipment received to customer", "status": "resolved", "orders_impacted": 1},
    {"date": "2025-05-30", "brand": "Decathlon", "issue_type": "Shipment / AWB Issue", "summary": "Manual Data Error in Shipment", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-05-30", "brand": "Hopscotch", "issue_type": "Shipment / AWB Issue", "summary": "AWB Not Sent to Unicommerce", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-03", "brand": "EshopBox", "issue_type": "Order Creation Failure", "summary": "Transporter Allocation Error", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-06", "brand": "ShipDelight", "issue_type": "API / Integration Issue", "summary": "Auth Token - Correct API Details Provided", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-09", "brand": "Jhaji", "issue_type": "Alias Mapping", "summary": "Alias Mapping so pincode not serviceable", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-10", "brand": "Hyugalife", "issue_type": "Pincode Serviceability", "summary": "Orders don't belong to Blitz - Lane Issue", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-10", "brand": "iThink Logistics", "issue_type": "Alias Mapping", "summary": "Lane between pincodes were not activated", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-11", "brand": "All Things Baby", "issue_type": "Order Creation Failure", "summary": "New Account SignUp - Order Creation Issue", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-11", "brand": "FYND", "issue_type": "Shipment / AWB Issue", "summary": "Multiple Hits from client causing duplicates", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-14", "brand": "MossaicWellness", "issue_type": "Webhook Issue", "summary": "Webhook remarks accuracy issue", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-18", "brand": "ShipRocket", "issue_type": "Order Creation Failure", "summary": "Issue in Automation Rule", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-18", "brand": "Souled Store", "issue_type": "Cost Policy Issue", "summary": "Change Prepaid to Postpaid", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-23", "brand": "Heallo", "issue_type": "API / Integration Issue", "summary": "Invite attempt was for last year - token expired", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-23", "brand": "Hamster London", "issue_type": "Shipment / AWB Issue", "summary": "Shipments are of 2024 can't find logs", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-24", "brand": "Kartmax", "issue_type": "Alias Mapping", "summary": "Client was pushing wrong Alias Name", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-25", "brand": "Giva", "issue_type": "API / Integration Issue", "summary": "Shopify integration - Required reinstall", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-26", "brand": "Bombay Shaving", "issue_type": "Webhook Issue", "summary": "Webhook mapping done for tracking", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-27", "brand": "Eshopbox", "issue_type": "Shipment / AWB Issue", "summary": "Return address label mismatch - System limitation", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-28", "brand": "ShipDelight", "issue_type": "Pincode Serviceability", "summary": "All Pincodes Unserviceable", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-30", "brand": "Rosier Foods", "issue_type": "Alias Mapping", "summary": "Mapping for BLR & MUM Warehouses", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-06-30", "brand": "Wellness Forever", "issue_type": "Shipment / AWB Issue", "summary": "Label Generation Errors", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-07-01", "brand": "BLITZSHIP", "issue_type": "Shipment / AWB Issue", "summary": "Label errors & AWB cancellation", "status": "resolved", "orders_impacted": 2},
    {"date": "2025-07-02", "brand": "Kapiva", "issue_type": "Alias Mapping", "summary": "Alias Mapping/Setup for New Routes", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-07-03", "brand": "Decathlon", "issue_type": "Shipment / AWB Issue", "summary": "Label Mismatch in Generated Labels", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-07-04", "brand": "ShipDelight", "issue_type": "Webhook Issue", "summary": "Webhook status flow shared & configured", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-07-05", "brand": "Nykaa", "issue_type": "Order Creation Failure", "summary": "Order creation failed due to missing source address", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-07-06", "brand": "Rosier Foods", "issue_type": "Order Creation Failure", "summary": "Order creation failure for BLR location", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-07-07", "brand": "Shipdelight", "issue_type": "Alias Mapping", "summary": "AWB generation failed due to missing alias mapping", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-07-08", "brand": "Truemeds", "issue_type": "Order Creation Failure", "summary": "Orders showing In Process error - 104 orders failed", "status": "resolved", "orders_impacted": 104},
    {"date": "2025-07-09", "brand": "Nimbuspost", "issue_type": "API / Integration Issue", "summary": "Timeout error during order manifestation", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-07-10", "brand": "AYUVYA", "issue_type": "Alias Mapping", "summary": "Alias mismatch and unserviceable pincode", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-07-10", "brand": "UBON", "issue_type": "Pincode Serviceability", "summary": "Response delay - non-serviceable pincode 400066", "status": "resolved", "orders_impacted": 0},
    {"date": "2025-07-11", "brand": "ShipDelight", "issue_type": "Shipment / AWB Issue", "summary": "Order Creation Failure due to Duplicate AWB", "status": "resolved", "orders_impacted": 0},
    # Some open/recent tickets for dashboard testing
    {"date": "2025-07-12", "brand": "OZiva", "issue_type": "Pincode Serviceability", "summary": "NDD pincode not serviceable in Bangalore zone", "status": "open", "orders_impacted": 5},
    {"date": "2025-07-12", "brand": "Decathlon", "issue_type": "Webhook Issue", "summary": "Webhook Setup for new tracking integration", "status": "open", "orders_impacted": 0},
    {"date": "2025-07-13", "brand": "Truemeds", "issue_type": "Order Creation Failure", "summary": "Order Booking Failure due to timeout and lane restriction", "status": "open", "orders_impacted": 8},
    {"date": "2025-07-13", "brand": "Nykaa", "issue_type": "API / Integration Issue", "summary": "API Timeout / Weight Configuration exceeding limits", "status": "open", "orders_impacted": 3},
    {"date": "2025-07-13", "brand": "Kapiva", "issue_type": "Alias Mapping", "summary": "Alias & Pincode Issue for new warehouse location", "status": "open", "orders_impacted": 0},
    {"date": "2025-07-14", "brand": "Shipdelight", "issue_type": "Shipment / AWB Issue", "summary": "Waybill API & Onboarding issues", "status": "open", "orders_impacted": 0},
    {"date": "2025-07-14", "brand": "Bombay Shaving", "issue_type": "Delay / TAT Issue", "summary": "Delivery Slip Generation Failing for multiple orders", "status": "open", "orders_impacted": 12},
    {"date": "2025-07-14", "brand": "Giva", "issue_type": "Order Creation Failure", "summary": "Shopify & Warehouse Setup causing order failures", "status": "open", "orders_impacted": 2},
]

# Brand to email domain mapping  
BRAND_EMAILS = {
    "Purplle": "support@purplle.com",
    "OZiva": "ops@oziva.in",
    "Heallo": "support@heallo.ai",
    "Onestolabs": "ops@onestolabs.com",
    "Powerlook": "logistics@powerlook.in",
    "TrueMeds": "ops@truemeds.in",
    "Shipdelight": "support@shipdelight.com",
    "PUMA": "logistics@puma.com",
    "Atomberg": "ops@atomberg.com",
    "Kapiva": "support@kapiva.in",
    "PROZO": "ops@prozo.com",
    "Snitch": "logistics@snitch.co.in",
    "Shoppers Stop": "ops@shoppersstop.com",
    "EshopBox": "support@eshopbox.com",
    "Bebodywise": "ops@bebodywise.com",
    "Giva": "support@giva.co",
    "Truemeds": "ops@truemeds.in",
    "Decathlon": "logistics@decathlon.in",
    "Shiprocket": "ops@shiprocket.in",
    "Souled Store": "support@thesouledstore.com",
    "Pantaloons": "ops@pantaloons.com",
    "Mossaic Wellness": "support@mossaicwellness.com",
    "ShoppersStop": "ops@shoppersstop.com",
    "The House of Rare": "support@houseofrare.com",
    "Mokobara": "ops@mokobara.com",
    "Bombay Shaving": "support@bombayshaving.com",
    "House of Vaaree": "ops@houseofvaaree.com",
    "iThink Logistics": "support@ithinklogistics.com",
    "Easycom": "ops@easycom.io",
    "Clickpost": "support@clickpost.in",
    "ShipDelight": "support@shipdelight.com",
    "NEWME": "ops@newme.in",
    "Alamode Label": "support@alamodelabel.com",
    "Protonics": "ops@protonics.in",
    "BNSL-Shipsy": "support@shipsy.in",
    "Bright Lifecare": "ops@brightlifecare.com",
    "Medikabazaar": "support@medikabazaar.com",
    "Hopscotch": "ops@hopscotch.in",
    "Jhaji": "support@jhaji.com",
    "Hyugalife": "ops@hyugalife.com",
    "All Things Baby": "support@allthingsbaby.in",
    "FYND": "ops@fynd.com",
    "MossaicWellness": "support@mossaicwellness.com",
    "ShipRocket": "ops@shiprocket.in",
    "Hamster London": "support@hamsterlondon.com",
    "Kartmax": "ops@kartmax.in",
    "Eshopbox": "support@eshopbox.com",
    "Rosier Foods": "ops@rosierfoods.com",
    "Wellness Forever": "support@wellnessforever.in",
    "BLITZSHIP": "ops@blitzship.com",
    "Nykaa": "support@nykaa.com",
    "Nimbuspost": "ops@nimbuspost.com",
    "AYUVYA": "support@ayuvya.com",
    "UBON": "ops@ubon.in",
}


async def seed_data():
    """Seed historical ticket data into MongoDB."""
    tickets_collection = db["tickets"]
    
    # Check if data already seeded
    count = await tickets_collection.count_documents({})
    if count > 0:
        print(f"Database already has {count} tickets. Skipping seed.")
        return
    
    tickets = []
    jira_counter = 100
    
    for issue in HISTORICAL_ISSUES:
        jira_counter += 1
        date = datetime.strptime(issue["date"], "%Y-%m-%d").replace(
            hour=random.randint(8, 18),
            minute=random.randint(0, 59),
            tzinfo=timezone.utc
        )
        
        sender_email = BRAND_EMAILS.get(issue["brand"], f"support@{issue['brand'].lower().replace(' ', '')}.com")
        is_resolved = issue["status"] == "resolved"
        
        # Calculate TAT for resolved tickets (random 2-72 hours)
        tat_hours = round(random.uniform(2, 72), 2) if is_resolved else None
        resolved_at = date + timedelta(hours=tat_hours) if tat_hours else None
        
        jira_key = f"TEC-{jira_counter}"
        
        ticket = {
            "id": str(uuid.uuid4()),
            "brand": issue["brand"],
            "sender_email": sender_email,
            "summary": issue["summary"],
            "full_message": f"Issue reported by {issue['brand']}: {issue['summary']}. Orders impacted: {issue['orders_impacted']}. This requires immediate attention from the operations team.",
            "source": "email",
            "awb": f"AWB{random.randint(100000, 999999)}" if random.random() > 0.3 else None,
            "issue_type": issue["issue_type"],
            "status": issue["status"],
            "assigned_to": None,
            "latest_comment": "Issue resolved and customer updated." if is_resolved else "Awaiting investigation.",
            "resolution_notes": "Resolved by ops team." if is_resolved else None,
            "jira_issue_key": jira_key,
            "jira_issue_id": str(random.randint(10000, 99999)),
            "jira_url": f"https://grow-simplee.atlassian.net/browse/{jira_key}",
            "resolved_at": resolved_at,
            "tat_hours": tat_hours,
            "created_at": date,
            "updated_at": resolved_at if resolved_at else date,
        }
        
        tickets.append(ticket)
    
    if tickets:
        await tickets_collection.insert_many(tickets)
        print(f"Seeded {len(tickets)} historical tickets successfully!")
        
        # Print summary
        open_count = sum(1 for t in tickets if t["status"] == "open")
        resolved_count = sum(1 for t in tickets if t["status"] == "resolved")
        brands = set(t["brand"] for t in tickets)
        print(f"  Open: {open_count}, Resolved: {resolved_count}")
        print(f"  Unique brands: {len(brands)}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_data())
