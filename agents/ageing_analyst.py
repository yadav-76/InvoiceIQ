from datetime import datetime
from tools.database import get_overdue_invoices

async def ageing_analyst_agent() -> dict:
    """
    Groups all overdue invoices into time buckets.
    Returns a structured ageing report.
    """
    print("  Ageing Analyst: generating AR ageing report...")

    overdue_invoices = get_overdue_invoices()
    today = datetime.now().date()

    # Define the buckets
    buckets = {
        "0_to_30_days": {"invoices": [], "total": 0},
        "31_to_60_days": {"invoices": [], "total": 0},
        "61_to_90_days": {"invoices": [], "total": 0},
        "over_90_days":  {"invoices": [], "total": 0},
    }

    grand_total = 0

    for invoice in overdue_invoices:
        due_date = datetime.strptime(
            invoice["due_date"], "%Y-%m-%d"
        ).date()

        days_overdue = (today - due_date).days
        amount = float(invoice.get("amount", 0))
        grand_total += amount

        # Summarised invoice info for the report
        summary = {
            "invoice_id": invoice["invoice_id"],
            "client_name": invoice["client_name"],
            "amount": amount,
            "currency": invoice.get("currency", "INR"),
            "days_overdue": days_overdue,
            "due_date": invoice["due_date"],
        }

        # Place into correct bucket
        if days_overdue <= 30:
            buckets["0_to_30_days"]["invoices"].append(summary)
            buckets["0_to_30_days"]["total"] += amount
        elif days_overdue <= 60:
            buckets["31_to_60_days"]["invoices"].append(summary)
            buckets["31_to_60_days"]["total"] += amount
        elif days_overdue <= 90:
            buckets["61_to_90_days"]["invoices"].append(summary)
            buckets["61_to_90_days"]["total"] += amount
        else:
            buckets["over_90_days"]["invoices"].append(summary)
            buckets["over_90_days"]["total"] += amount

    report = {
        "generated_on": str(today),
        "total_overdue_amount": grand_total,
        "total_overdue_invoices": len(overdue_invoices),
        "buckets": buckets,
    }

    print(f"  Ageing Analyst: {len(overdue_invoices)} overdue invoices "
          f"totalling {grand_total}")
    return report