from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
import pytz
from pathlib import Path
import dateparser

load_dotenv()  # Load .env variables

SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Always resolve the service account file relative to the project root
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "service_account.json")
if not os.path.isabs(SERVICE_ACCOUNT_FILE):
    # Resolve relative to the project root (one level up from this file)
    SERVICE_ACCOUNT_FILE = str(Path(__file__).parent.parent / SERVICE_ACCOUNT_FILE)

CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

# Default timezone
DEFAULT_TIMEZONE = "Asia/Kolkata"

try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("calendar", "v3", credentials=credentials)
except Exception as e:
    print(f"Error initializing Google Calendar service: {e}")
    service = None

def list_events(start_time_iso):
    """List events from a specific start time."""
    if not service:
        return {"error": "Calendar service not initialized"}
    
    try:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_time_iso,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        return events_result.get("items", [])
    except Exception as e:
        return {"error": f"Failed to list events: {str(e)}"}

def create_event(summary, start_time_iso, end_time_iso, description="", guests=None):
    """Create a new calendar event with optional guests."""
    if not service:
        return {"error": "Calendar service not initialized"}
    if guests is None:
        guests = []
    try:
        event = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_time_iso, "timeZone": DEFAULT_TIMEZONE},
            "end": {"dateTime": end_time_iso, "timeZone": DEFAULT_TIMEZONE},
        }
        if guests:
            event["attendees"] = [{"email": email} for email in guests]
        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return created_event
    except Exception as e:
        return {"error": f"Failed to create event: {str(e)}"}

def check_availability(start_time_iso, end_time_iso):
    """Check if a time slot is available for booking."""
    if not service:
        return {"error": "Calendar service not initialized"}
    
    try:
        # Get events that overlap with the requested time slot
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_time_iso,
            timeMax=end_time_iso,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        conflicting_events = events_result.get("items", [])
        
        if conflicting_events:
            return {
                "available": False,
                "conflicts": len(conflicting_events),
                "conflicting_events": [
                    {
                        "summary": event.get("summary", "No title"),
                        "start": event.get("start", {}).get("dateTime"),
                        "end": event.get("end", {}).get("dateTime")
                    }
                    for event in conflicting_events
                ]
            }
        else:
            return {
                "available": True,
                "conflicts": 0,
                "conflicting_events": []
            }
    except Exception as e:
        return {"error": f"Failed to check availability: {str(e)}"}

def get_current_time_iso():
    """Get current time in ISO format."""
    return datetime.now(timezone.utc).isoformat()

def parse_datetime_string(datetime_str):
    """Parse various datetime string formats or natural language to ISO format (IST)."""
    try:
        ist = pytz.timezone('Asia/Kolkata')
        dt = dateparser.parse(
            datetime_str,
            settings={
                'PREFER_DATES_FROM': 'future',
                'RELATIVE_BASE': datetime.now(ist),
                'RETURN_AS_TIMEZONE_AWARE': True,
                'TIMEZONE': 'Asia/Kolkata',
                'TO_TIMEZONE': 'Asia/Kolkata',
                'PREFER_DAY_OF_MONTH': 'first',
            }
        )
        if dt is None:
            return datetime_str  # fallback: return as is
        return dt.astimezone(ist).isoformat()
    except Exception as e:
        return datetime_str

def edit_event(event_id, summary=None, start_time_iso=None, end_time_iso=None, description=None, guests=None):
    """Edit an existing calendar event by event_id. Only provided fields are updated."""
    if not service:
        return {"error": "Calendar service not initialized"}
    try:
        event = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()
        if summary is not None:
            event["summary"] = summary
        if description is not None:
            event["description"] = description
        if start_time_iso is not None:
            event["start"]["dateTime"] = start_time_iso
            event["start"]["timeZone"] = DEFAULT_TIMEZONE
        if end_time_iso is not None:
            event["end"]["dateTime"] = end_time_iso
            event["end"]["timeZone"] = DEFAULT_TIMEZONE
        if guests is not None:
            event["attendees"] = [{"email": email} for email in guests]
        updated_event = service.events().update(calendarId=CALENDAR_ID, eventId=event_id, body=event).execute()
        return updated_event
    except Exception as e:
        return {"error": f"Failed to edit event: {str(e)}"}

def list_upcoming_events(max_results=20):
    """List all upcoming events from now (default: next 20 events)."""
    if not service:
        return {"error": "Calendar service not initialized"}
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=now_iso,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        return events_result.get("items", [])
    except Exception as e:
        return {"error": f"Failed to list upcoming events: {str(e)}"}
