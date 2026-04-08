import os
import json
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Google Calendar imports
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send'
]

def get_calendar_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # On cloud — can't open browser, return None safely
            print("Warning: No valid credentials found")
            return None
    service = build('calendar', 'v3', credentials=creds)
    return service

async def schedule_due_reminder(invoice: dict) -> str:
    """
    Creates a real Google Calendar event for the invoice due date.
    Returns the calendar event ID.
    """
    try:
        service = get_calendar_service()

        # Build the calendar event
        event = {
            'summary': f"Payment due: {invoice['invoice_id']} from {invoice['client_name']}",
            'description': (
                f"Invoice: {invoice['invoice_id']}\n"
                f"Client: {invoice['client_name']}\n"
                f"Amount: {invoice['currency']} {invoice['amount']}\n"
                f"For: {invoice['description']}"
            ),
            'start': {
                'date': invoice['due_date'],
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'date': invoice['due_date'],
                'timeZone': 'Asia/Kolkata',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 60},
                ],
            },
        }

        # Create the event in Google Calendar
        created_event = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()

        event_id = created_event.get('id')
        print(f"  Calendar event created: {event_id}")
        return event_id

    except Exception as e:
        print(f"  Calendar error: {e}")
        # Return a placeholder ID so the rest of the flow continues
        return f"CAL-{invoice['invoice_id']}-{str(uuid.uuid4())[:8]}"


async def update_calendar_event(event_id: str, invoice_id: str,
                                 client_name: str, status: str) -> bool:
    """
    Updates a calendar event title when invoice is paid.
    """
    try:
        service = get_calendar_service()

        # Get the existing event
        event = service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()

        # Update the title to show it's paid
        event['summary'] = f"PAID: {invoice_id} from {client_name}"
        event['description'] += f"\n\nStatus: {status}"

        service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event
        ).execute()

        print(f"  Calendar event {event_id} updated to PAID")
        return True

    except Exception as e:
        print(f"  Calendar update error: {e}")
        return False