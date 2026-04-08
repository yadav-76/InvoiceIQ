import asyncio
from dotenv import load_dotenv
load_dotenv()

from tools.database import save_invoice
from agents.payment_tracker import payment_tracker_agent
from agents.followup_agent import followup_agent
from agents.ageing_analyst import ageing_analyst_agent
from datetime import datetime, timedelta

async def test():
    print("Testing daily automation agents...\n")

    # First create a fake overdue invoice to test with
    print("Setting up test data...")
    yesterday = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

    save_invoice({
        "invoice_id": "INV-OVERDUE-TEST",
        "client_name": "Test Overdue Client",
        "client_email": "likithyadav123ab@gmail.com",
        "amount": 25000.0,
        "currency": "INR",
        "description": "Website development",
        "issue_date": "2026-03-01",
        "due_date": yesterday,
        "status": "pending",
        "paid_date": "",
        "payment_timing": "",
        "reminder_count": 0,
        "calendar_event_id": "",
        "client_risk_score": "Green",
    })
    print("  Test overdue invoice created\n")

    # Step 1 — Run Payment Tracker
    print("Step 1 — Running Payment Tracker...")
    overdue = await payment_tracker_agent()
    print(f"  Found {len(overdue)} overdue invoices\n")

    # Step 2 — Run Follow-up Agent
    print("Step 2 — Running Follow-up Agent...")
    emails_sent = await followup_agent(overdue)
    print(f"  Sent {emails_sent} emails\n")

    # Step 3 — Run Ageing Analyst
    print("Step 3 — Running Ageing Analyst...")
    report = await ageing_analyst_agent()
    print(f"  Total overdue: INR {report['total_overdue_amount']}")
    print(f"  0-30 days bucket: {len(report['buckets']['0_to_30_days']['invoices'])} invoices")
    print(f"  31-60 days bucket: {len(report['buckets']['31_to_60_days']['invoices'])} invoices")
    print()

    print("Daily automation test complete!")
    print("Check your Gmail inbox for the reminder email!")

asyncio.run(test())