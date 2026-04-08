from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Invoice:
    invoice_id: str = ""
    client_name: str = ""
    client_email: str = ""
    amount: float = 0.0
    currency: str = "INR"
    description: str = ""
    issue_date: str = ""
    due_date: str = ""
    status: str = "pending"
    paid_date: str = ""
    payment_timing: str = ""
    reminder_count: int = 0
    calendar_event_id: str = ""
    client_risk_score: str = "Green"

    def to_dict(self):
        return {
            "invoice_id": self.invoice_id,
            "client_name": self.client_name,
            "client_email": self.client_email,
            "amount": self.amount,
            "currency": self.currency,
            "description": self.description,
            "issue_date": self.issue_date,
            "due_date": self.due_date,
            "status": self.status,
            "paid_date": self.paid_date,
            "payment_timing": self.payment_timing,
            "reminder_count": self.reminder_count,
            "calendar_event_id": self.calendar_event_id,
            "client_risk_score": self.client_risk_score,
        }