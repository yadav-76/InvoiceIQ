import asyncio
from datetime import datetime
from dotenv import load_dotenv

from agents.invoice_generator import invoice_generator_agent
from agents.risk_scorer import risk_scorer_agent
from agents.payment_tracker import payment_tracker_agent
from agents.followup_agent import followup_agent
from agents.ageing_analyst import ageing_analyst_agent
from tools.database import (
    save_invoice, update_invoice,
    get_invoice, get_all_pending,
    get_monthly_invoices
)
from tools.calendar_mcp import schedule_due_reminder, update_calendar_event

load_dotenv()


async def create_invoice(user_message: str) -> dict:
    """
    Main invoice creation flow.
    Step 1 — Generate invoice from message
    Step 2 — Run Risk Scorer + Calendar + DB save in parallel
    Step 3 — Return confirmation
    """
    print(f"\nManager: creating invoice from message...")

    # Step 1 — Generate invoice
    invoice = await invoice_generator_agent(user_message)
    print(f"  Invoice generated: {invoice['invoice_id']}")

    # Step 2 — Run Risk Scorer and Calendar scheduling in parallel
    risk_score, event_id = await asyncio.gather(
        risk_scorer_agent(invoice["client_name"]),
        schedule_due_reminder(invoice)
    )

    # Update invoice with risk score and calendar event ID
    invoice["client_risk_score"] = risk_score
    invoice["calendar_event_id"] = event_id
    print(f"  Risk score: {risk_score}")
    print(f"  Calendar event: {event_id}")

    # Step 3 — Save complete invoice to Firestore
    save_invoice(invoice)
    print(f"  Saved to database")

    return {
        "success": True,
        "invoice_id": invoice["invoice_id"],
        "client_name": invoice["client_name"],
        "amount": f"{invoice['currency']} {invoice['amount']}",
        "due_date": invoice["due_date"],
        "client_risk_score": risk_score,
        "calendar_reminder": "scheduled",
        "message": (
            f"Invoice {invoice['invoice_id']} created successfully. "
            f"Payment due on {invoice['due_date']}. "
            f"Client risk score: {risk_score}."
        )
    }


async def mark_invoice_paid(invoice_id: str) -> dict:
    """
    Updates invoice when customer pays.
    Calculates if paid on time or late.
    Updates risk score and calendar event.
    """
    print(f"\nManager: marking {invoice_id} as paid...")

    # Get the invoice
    invoice = get_invoice(invoice_id)
    if not invoice:
        return {"success": False, "message": f"Invoice {invoice_id} not found"}

    today = datetime.now().date()
    due_date = datetime.strptime(invoice["due_date"], "%Y-%m-%d").date()

    # Calculate payment timing
    if today <= due_date:
        payment_timing = "paid_on_time"
        timing_message = "Paid on time"
    else:
        days_late = (today - due_date).days
        payment_timing = f"paid_late_{days_late}_days"
        timing_message = f"Paid {days_late} days late"

    # Update invoice in Firestore
    update_invoice(invoice_id, {
        "status": "paid",
        "paid_date": str(today),
        "payment_timing": payment_timing,
    })
    print(f"  Invoice updated: {payment_timing}")

    # Recalculate client risk score
    new_risk_score = await risk_scorer_agent(invoice["client_name"])
    update_invoice(invoice_id, {"client_risk_score": new_risk_score})
    print(f"  New risk score: {new_risk_score}")

    # Update calendar event if it exists
    if invoice.get("calendar_event_id"):
        await update_calendar_event(
            invoice["calendar_event_id"],
            invoice_id,
            invoice["client_name"],
            "PAID"
        )

    return {
        "success": True,
        "invoice_id": invoice_id,
        "status": "paid",
        "paid_date": str(today),
        "payment_timing": payment_timing,
        "timing_message": timing_message,
        "updated_risk_score": new_risk_score,
        "message": f"Invoice {invoice_id} marked as paid. {timing_message}."
    }


async def run_daily_check() -> dict:
    """
    Runs every morning via Cloud Scheduler.
    Checks overdue invoices, sends emails, updates ageing report.
    """
    print("\nManager: running daily check...")

    # Step 1 — Find overdue invoices
    overdue = await payment_tracker_agent()

    # Step 2 — Send follow-up emails
    emails_sent = await followup_agent(overdue)

    # Step 3 — Generate ageing report
    ageing_report = await ageing_analyst_agent()

    return {
        "success": True,
        "overdue_count": len(overdue),
        "emails_sent": emails_sent,
        "ageing_report": ageing_report,
        "message": (
            f"Daily check complete. "
            f"{len(overdue)} overdue invoices found. "
            f"{emails_sent} reminder emails sent."
        )
    }


async def get_ageing_report() -> dict:
    """Returns the current AR ageing report."""
    return await ageing_analyst_agent()


async def get_monthly_summary() -> dict:
    """Returns monthly revenue summary."""
    invoices = get_monthly_invoices()

    total_invoiced = sum(i.get("amount", 0) for i in invoices)
    total_paid = sum(
        i.get("amount", 0) for i in invoices
        if i.get("status") == "paid"
    )
    total_overdue = sum(
        i.get("amount", 0) for i in invoices
        if i.get("status") == "overdue"
    )
    on_time = sum(
        1 for i in invoices
        if i.get("payment_timing") == "paid_on_time"
    )
    late = sum(
        1 for i in invoices
        if "paid_late" in i.get("payment_timing", "")
    )

    return {
        "month": datetime.now().strftime("%B %Y"),
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "total_overdue": total_overdue,
        "total_pending": total_invoiced - total_paid - total_overdue,
        "invoice_count": len(invoices),
        "paid_on_time_count": on_time,
        "paid_late_count": late,
        "collection_rate": (
            round((total_paid / total_invoiced * 100), 1)
            if total_invoiced > 0 else 0
        ),
    }