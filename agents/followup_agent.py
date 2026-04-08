import os
import json
import httpx
from dotenv import load_dotenv
from tools.database import update_invoice, save_email_draft
from tools.gmail_mcp import send_email


load_dotenv()

async def followup_agent(overdue_invoices: list) -> int:
    """
    For each overdue invoice:
    1. Writes a personalised email using Gemini
    2. Sends it via Gmail MCP
    3. Updates reminder_count in Firestore
    Returns number of emails sent.
    """
    if not overdue_invoices:
        print("  Follow-up Agent: no overdue invoices to follow up on")
        return 0

    emails_sent = 0

    for invoice in overdue_invoices:
        reminder_count = invoice.get("reminder_count", 0)
        client_email = invoice.get("client_email", "")

        # Skip if no email address
        if not client_email:
            print(f"  Skipping {invoice['invoice_id']} — no email address")
            continue

        # Determine tone based on how many reminders already sent
        if reminder_count == 0:
            tone = "friendly and polite"
            urgency = "gentle reminder"
        elif reminder_count == 1:
            tone = "firm and professional"
            urgency = "follow-up request"
        else:
            tone = "serious and final"
            urgency = "final notice before further action"

        # Ask Gemini to write the email
        prompt = f"""
        Write a payment reminder email with a {tone} tone.
        
        Invoice details:
        - Invoice ID: {invoice['invoice_id']}
        - Client name: {invoice['client_name']}
        - Amount: {invoice['currency']} {invoice['amount']}
        - Due date: {invoice['due_date']}
        - Days overdue: {invoice.get('days_overdue', 0)}
        - Description: {invoice['description']}
        - This is reminder number: {reminder_count + 1}
        - Urgency level: {urgency}
        
        Return ONLY a JSON object with:
        {{
            "subject": "email subject line",
            "body": "full email body text"
        }}
        
        Keep the email under 150 words. 
        Be professional. 
        Do not use HTML.
        Return ONLY the JSON.
        """

        

        # Clean markdown if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        raw_text = raw_text.strip()

        email_data = json.loads(raw_text)
        subject = email_data["subject"]
        body = email_data["body"]

        # Save draft to Firestore first
        save_email_draft(invoice["invoice_id"], subject, body, sent=False)

        # Send the actual email via Gmail MCP
        sent = await send_email(client_email, subject, body)

        if sent:
            emails_sent += 1
            # Update reminder count in Firestore
            update_invoice(invoice["invoice_id"], {
                "reminder_count": reminder_count + 1
            })
            # Update draft to mark as sent
            save_email_draft(invoice["invoice_id"], subject, body, sent=True)
            print(f"  Email sent to {invoice['client_name']} "
                  f"({client_email}) — Reminder #{reminder_count + 1}")

    print(f"  Follow-up Agent: sent {emails_sent} reminder emails")
    return emails_sent