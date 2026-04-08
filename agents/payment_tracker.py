from datetime import datetime
from tools.database import get_all_pending, update_invoice

async def payment_tracker_agent() -> list:
    """
    Scans all pending invoices.
    Marks overdue ones in Firestore.
    Returns list of overdue invoices for follow-up agent.
    """
    print("  Payment Tracker: scanning all pending invoices...")

    today = datetime.now().date()
    pending_invoices = get_all_pending()
    overdue_list = []

    for invoice in pending_invoices:
        due_date_str = invoice.get("due_date", "")

        if not due_date_str:
            continue

        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()

        if today > due_date:
            days_overdue = (today - due_date).days

            # Update status to overdue in Firestore
            update_invoice(invoice["invoice_id"], {
                "status": "overdue",
                "days_overdue": days_overdue
            })

            invoice["status"] = "overdue"
            invoice["days_overdue"] = days_overdue
            overdue_list.append(invoice)

            print(f"  Marked overdue: {invoice['invoice_id']} "
                  f"— {invoice['client_name']} "
                  f"— {days_overdue} days late")

    print(f"  Payment Tracker: found {len(overdue_list)} overdue invoices")
    return overdue_list