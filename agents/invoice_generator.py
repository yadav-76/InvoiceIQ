import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel

load_dotenv()

def get_gemini_model():
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    region = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
    vertexai.init(project=project, location=region)
    return GenerativeModel("gemini-2.5-flash")

async def invoice_generator_agent(user_message: str) -> dict:

    prompt = f"""
    You are an invoice data extractor.
    Extract invoice details from the user message and return ONLY a JSON object.
    No extra text, no explanation, just the JSON.

    User message: "{user_message}"

    Return this exact JSON structure:
    {{
        "client_name": "extracted client name",
        "client_email": "extracted email or empty string if not mentioned",
        "amount": extracted amount as a number,
        "currency": "INR",
        "description": "what the invoice is for",
        "due_days": number of days until payment is due
    }}

    Rules:
    - If no currency mentioned, use INR
    - If no due date mentioned, use 30 as due_days
    - Amount should be a number only, no currency symbols
    - If email not mentioned, use empty string ""
    """

    model = get_gemini_model()
    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    # Clean markdown if present
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    raw_text = raw_text.strip()

    extracted = json.loads(raw_text)

    today = datetime.now()
    due_date = today + timedelta(days=int(extracted.get("due_days", 30)))
    invoice_id = f"INV-{today.strftime('%Y%m%d')}-{today.strftime('%H%M%S')}"

    invoice = {
        "invoice_id": invoice_id,
        "client_name": extracted.get("client_name", ""),
        "client_email": extracted.get("client_email", ""),
        "amount": float(extracted.get("amount", 0)),
        "currency": extracted.get("currency", "INR"),
        "description": extracted.get("description", ""),
        "issue_date": today.strftime("%Y-%m-%d"),
        "due_date": due_date.strftime("%Y-%m-%d"),
        "status": "pending",
        "paid_date": "",
        "payment_timing": "",
        "reminder_count": 0,
        "calendar_event_id": "",
        "client_risk_score": "Green",
    }

    return invoice