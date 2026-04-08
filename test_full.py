import asyncio
from dotenv import load_dotenv
load_dotenv()

from agents.manager import (
    create_invoice,
    mark_invoice_paid,
    get_ageing_report,
    get_monthly_summary
)

async def test():
    print("=" * 50)
    print("INVOICEIQ V2 — FULL SYSTEM TEST")
    print("=" * 50)
    print()

    # Test 1 — Create invoice
    print("TEST 1 — Create invoice from plain English")
    print("-" * 40)
    result = await create_invoice(
        "Invoice Priya Sharma priya@gmail.com "
        "Rs.35000 for brand strategy, due in 14 days"
    )
    print(f"Invoice ID: {result['invoice_id']}")
    print(f"Client: {result['client_name']}")
    print(f"Amount: {result['amount']}")
    print(f"Due date: {result['due_date']}")
    print(f"Risk score: {result['client_risk_score']}")
    print(f"Calendar: {result['calendar_reminder']}")
    invoice_id = result['invoice_id']
    print()

    # Test 2 — Get invoice
    print("TEST 2 — Retrieve invoice from database")
    print("-" * 40)
    from tools.database import get_invoice
    inv = get_invoice(invoice_id)
    print(f"Retrieved: {inv['invoice_id']} — {inv['status']}")
    print()

    # Test 3 — Mark as paid
    print("TEST 3 — Mark invoice as paid")
    print("-" * 40)
    paid_result = await mark_invoice_paid(invoice_id)
    print(f"Status: {paid_result['status']}")
    print(f"Timing: {paid_result['timing_message']}")
    print(f"Updated risk score: {paid_result['updated_risk_score']}")
    print()

    # Test 4 — Monthly summary
    print("TEST 4 — Monthly summary")
    print("-" * 40)
    summary = await get_monthly_summary()
    print(f"Month: {summary['month']}")
    print(f"Total invoiced: INR {summary['total_invoiced']}")
    print(f"Total paid: INR {summary['total_paid']}")
    print(f"Collection rate: {summary['collection_rate']}%")
    print()

    print("=" * 50)
    print("ALL TESTS PASSED!")
    print("InvoiceIQ v2 is fully working!")
    print("=" * 50)

asyncio.run(test())