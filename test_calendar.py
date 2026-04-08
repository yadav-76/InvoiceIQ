import asyncio
from dotenv import load_dotenv
load_dotenv()

from tools.calendar_mcp import schedule_due_reminder

async def test():
    print("Testing Google Calendar connection...\n")

    # Test invoice
    test_invoice = {
        "invoice_id": "INV-TEST-CAL-001",
        "client_name": "Acme Corp",
        "amount": 45000.0,
        "currency": "INR",
        "description": "Web design project",
        "due_date": "2026-05-07",
    }

    print("Creating calendar event...")
    event_id = await schedule_due_reminder(test_invoice)
    print(f"Event ID: {event_id}")
    print()
    print("Open your Google Calendar and check for the event on 7 May 2026!")

asyncio.run(test())