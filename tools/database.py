import os
from google.cloud import firestore
from datetime import datetime

db = firestore.Client(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    database="default"
)

def save_invoice(invoice_dict: dict):
    doc_ref = db.collection("invoices").document(invoice_dict["invoice_id"])
    doc_ref.set(invoice_dict)
    return True

def get_invoice(invoice_id: str):
    doc = db.collection("invoices").document(invoice_id).get()
    if doc.exists:
        return doc.to_dict()
    return None

def update_invoice(invoice_id: str, fields: dict):
    db.collection("invoices").document(invoice_id).update(fields)
    return True

def get_all_pending():
    docs = db.collection("invoices").where("status", "==", "pending").stream()
    return [doc.to_dict() for doc in docs]

def get_overdue_invoices():
    docs = db.collection("invoices").where("status", "==", "overdue").stream()
    return [doc.to_dict() for doc in docs]

def get_client_history(client_name: str):
    docs = db.collection("invoices").where(
        "client_name", "==", client_name
    ).where("status", "==", "paid").stream()
    return [doc.to_dict() for doc in docs]

def save_email_draft(invoice_id: str, subject: str, body: str, sent: bool = False):
    db.collection("email_drafts").document(invoice_id).set({
        "invoice_id": invoice_id,
        "subject": subject,
        "body": body,
        "created_at": datetime.now().isoformat(),
        "sent": sent,
    })
    return True

def get_monthly_invoices():
    now = datetime.now()
    month_start = datetime(now.year, now.month, 1).isoformat()[:10]
    docs = db.collection("invoices").where(
        "issue_date", ">=", month_start
    ).stream()
    return [doc.to_dict() for doc in docs]