import os
from dotenv import load_dotenv
from tools.database import get_client_history
import vertexai
from vertexai.generative_models import GenerativeModel

load_dotenv()

def get_gemini_model():
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    region = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
    vertexai.init(project=project, location=region)
    return GenerativeModel("gemini-2.5-flash")

async def risk_scorer_agent(client_name: str) -> str:

    history = get_client_history(client_name)

    if not history:
        return "Green"

    total_invoices = len(history)
    late_payments = 0
    total_days_late = 0

    for invoice in history:
        timing = invoice.get("payment_timing", "")
        if "late" in timing:
            late_payments += 1
            try:
                days = int(timing.split("_")[2])
                total_days_late += days
            except:
                total_days_late += 1

    late_percentage = (late_payments / total_invoices) * 100
    avg_days_late = total_days_late / total_invoices if total_invoices > 0 else 0

    prompt = f"""
    You are a payment risk analyst.

    Client: {client_name}
    Total past invoices: {total_invoices}
    Late payments: {late_payments}
    Late payment percentage: {late_percentage:.1f}%
    Average days late: {avg_days_late:.1f}

    Based on this payment history, assign a risk score.
    Return ONLY one word — either Green, Amber, or Red.

    Rules:
    - Green: less than 20% late payments OR new client
    - Amber: 20% to 50% late payments
    - Red: more than 50% late payments

    Return only one word: Green, Amber, or Red
    """

    model = get_gemini_model()
    response = model.generate_content(prompt)
    score = response.text.strip()

    if score not in ["Green", "Amber", "Red"]:
        score = "Green"

    return score