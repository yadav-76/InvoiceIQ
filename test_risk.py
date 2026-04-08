import asyncio
from dotenv import load_dotenv
load_dotenv()

from agents.risk_scorer import risk_scorer_agent
from tools.database import save_invoice

async def test():
    print("Testing Risk Scorer Agent...\n")

    # Test 1 — New client with no history
    print("Test 1 — New client (no payment history):")
    score = await risk_scorer_agent("Brand New Client")
    print(f"  Risk Score: {score}")
    print(f"  Expected: Green (new client defaults to Green)")
    print()

    # Test 2 — Create some fake payment history first
    print("Test 2 — Client who always pays on time:")

    # Save 3 on-time payment records for this client
    for i in range(3):
        save_invoice({
            "invoice_id": f"HIST-GOOD-00{i}",
            "client_name": "Good Payer Corp",
            "client_email": "good@test.com",
            "amount": 10000.0,
            "currency": "INR",
            "description": "Test",
            "issue_date": "2024-01-01",
            "due_date": "2024-01-30",
            "status": "paid",
            "paid_date": "2024-01-28",
            "payment_timing": "paid_on_time",
            "reminder_count": 0,
            "calendar_event_id": "",
            "client_risk_score": "Green",
        })

    score2 = await risk_scorer_agent("Good Payer Corp")
    print(f"  Risk Score: {score2}")
    print(f"  Expected: Green")
    print()

    # Test 3 — Client who always pays late
    print("Test 3 — Client who always pays late:")

    for i in range(4):
        save_invoice({
            "invoice_id": f"HIST-BAD-00{i}",
            "client_name": "Late Payer Inc",
            "client_email": "late@test.com",
            "amount": 10000.0,
            "currency": "INR",
            "description": "Test",
            "issue_date": "2024-01-01",
            "due_date": "2024-01-30",
            "status": "paid",
            "paid_date": "2024-03-15",
            "payment_timing": "paid_late_45_days",
            "reminder_count": 3,
            "calendar_event_id": "",
            "client_risk_score": "Red",
        })

    score3 = await risk_scorer_agent("Late Payer Inc")
    print(f"  Risk Score: {score3}")
    print(f"  Expected: Red")
    print()

    print("Risk Scorer test complete!")

asyncio.run(test())