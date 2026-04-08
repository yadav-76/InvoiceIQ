import os
import base64
import pickle
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send'
]

def get_gmail_service():
    """
    Gets authenticated Gmail service.
    Uses same token.pickle as Calendar — both use same credentials.
    """
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service


def create_email(to: str, subject: str, body: str) -> dict:
    """
    Creates an email message in the format Gmail API expects.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # Encode the message to base64
    raw = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode('utf-8')

    return {'raw': raw}


async def send_email(to: str, subject: str, body: str) -> bool:
    """
    Sends a real email via Gmail.
    Returns True if sent successfully.
    """
    try:
        service = get_gmail_service()
        message = create_email(to, subject, body)

        sent = service.users().messages().send(
            userId='me',
            body=message
        ).execute()

        print(f"  Email sent to {to} — Message ID: {sent['id']}")
        return True

    except Exception as e:
        print(f"  Gmail error: {e}")
        return False