from dotenv import load_dotenv
load_dotenv()

from tools.database import save_invoice, get_invoice

test_invoice = {
    "invoice_id": "TEST-001",
    "client_name": "Test Client",
    "client_email": "test@example.com",
    "amount": 1000.0,
    "currency": "INR",
    "description": "Test invoice",
    "issue_date": "2024-04-01",
    "due_date": "2024-04-30",
    "status": "pending",
    "paid_date": "",
    "payment_timing": "",
    "reminder_count": 0,
    "calendar_event_id": "",
    "client_risk_score": "Green",
}

print("Saving test invoice...")
save_invoice(test_invoice)
print("Saved!")

print("Reading it back...")
result = get_invoice("TEST-001")
print(result)