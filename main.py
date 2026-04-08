import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio

load_dotenv()

from agents.manager import (
    create_invoice,
    mark_invoice_paid,
    run_daily_check,
    get_ageing_report,
    get_monthly_summary,
)
from tools.database import get_invoice

app = FastAPI(
    title="InvoiceIQ v2",
    description="AI-powered invoice and payment management system",
    version="2.0.0"
)

# Request body model
class InvoiceRequest(BaseModel):
    message: str


# ── ENDPOINTS ──────────────────────────────────────────────────────────────

@app.get("/")
async def home():
    return {
        "system": "InvoiceIQ v2",
        "status": "running",
        "message": "AI-powered invoice management system",
        "endpoints": [
            "POST /invoice/create",
            "POST /invoice/mark-paid/{invoice_id}",
            "GET  /invoice/{invoice_id}",
            "POST /invoice/check-overdue",
            "GET  /invoice/ageing-report",
            "GET  /invoice/summary/monthly",
        ]
    }


@app.post("/invoice/create")
async def create_invoice_endpoint(request: InvoiceRequest):
    """
    Create a new invoice from a plain English message.
    Example: {"message": "Invoice Acme Corp Rs.45000 for web design, due in 30 days"}
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    result = await create_invoice(request.message)
    return result


@app.post("/invoice/mark-paid/{invoice_id}")
async def mark_paid_endpoint(invoice_id: str):
    """
    Mark an invoice as paid.
    Automatically calculates if paid on time or late.
    Updates risk score and calendar event.
    """
    result = await mark_invoice_paid(invoice_id)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])

    return result


@app.get("/invoice/ageing-report")
async def ageing_report_endpoint():
    """
    Returns AR ageing report — invoices grouped by how overdue they are.
    Buckets: 0-30 days, 31-60 days, 61-90 days, 90+ days.
    """
    report = await get_ageing_report()
    return report


@app.get("/invoice/summary/monthly")
async def monthly_summary_endpoint():
    """
    Returns monthly revenue summary.
    Shows total invoiced, paid, overdue, and collection rate.
    """
    summary = await get_monthly_summary()
    return summary


@app.post("/invoice/check-overdue")
async def check_overdue_endpoint():
    """
    Triggered daily by Cloud Scheduler.
    Scans overdue invoices, sends Gmail reminders, updates ageing report.
    """
    result = await run_daily_check()
    return result


@app.get("/invoice/{invoice_id}")
async def get_invoice_endpoint(invoice_id: str):
    """
    Fetch a specific invoice by ID.
    """
    invoice = get_invoice(invoice_id)

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"Invoice {invoice_id} not found"
        )

    return invoice