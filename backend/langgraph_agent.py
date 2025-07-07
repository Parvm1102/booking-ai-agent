import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from calendar_utils import list_events, create_event, check_availability, list_upcoming_events, edit_event, parse_datetime_string, get_current_time_iso
import json
from google.generativeai.generative_models import GenerativeModel
from google.generativeai.models import list_models
from typing import Optional, List

load_dotenv()  # Loads .env vars including GOOGLE_API_KEY

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    temperature=0.1,
    convert_system_message_to_human=True
)

# Define tools

def list_calendar_events(start_time_iso: str) -> str:
    """List calendar events from a specific start time.
    
    Args:
        start_time_iso: ISO format datetime string (e.g., "2024-01-15T10:00:00Z")
    
    Returns:
        JSON string containing list of events
    """
    try:
        events = list_events(start_time_iso)
        return json.dumps(events, default=str, indent=2)
    except Exception as e:
        return f"Error listing events: {str(e)}"

def list_upcoming_events_tool(max_results: int = 20) -> str:
    """List all upcoming calendar events from now (default: next 20)."""
    try:
        events = list_upcoming_events(max_results)
        return json.dumps(events, default=str, indent=2)
    except Exception as e:
        return f"Error listing upcoming events: {str(e)}"

def create_calendar_event(summary: str, start_time_iso: str, end_time_iso: str, description: str = "", guests: Optional[List[str]] = None) -> str:
    """Create a new calendar event with optional guests and description.
    Args:
        summary: Title of the event
        start_time_iso: Start time in ISO format (e.g., "2024-01-15T10:00:00Z")
        end_time_iso: End time in ISO format (e.g., "2024-01-15T11:00:00Z")
        description: Optional description of the event
        guests: Optional list of guest emails
    Returns:
        JSON string containing the created event details
    """
    try:
        # Always parse to IST
        start_time_ist = parse_datetime_string(start_time_iso)
        end_time_ist = parse_datetime_string(end_time_iso)
        event = create_event(summary, start_time_ist, end_time_ist, description, guests)
        return json.dumps(event, default=str, indent=2)
    except Exception as e:
        return f"Error creating event: {str(e)}"

def edit_calendar_event(event_id: str, summary: Optional[str] = None, start_time_iso: Optional[str] = None, end_time_iso: Optional[str] = None, description: Optional[str] = None, guests: Optional[List[str]] = None) -> str:
    """Edit an existing calendar event by event_id. Only provided fields are updated.
    Args:
        event_id: The ID of the event to edit
        summary: New title (optional)
        start_time_iso: New start time (optional)
        end_time_iso: New end time (optional)
        description: New description (optional)
        guests: New list of guest emails (optional)
    Returns:
        JSON string containing the updated event details
    """
    try:
        # Always parse to IST if provided
        start_time_ist = parse_datetime_string(start_time_iso) if start_time_iso else None
        end_time_ist = parse_datetime_string(end_time_iso) if end_time_iso else None
        event = edit_event(event_id, summary, start_time_ist, end_time_ist, description, guests)
        return json.dumps(event, default=str, indent=2)
    except Exception as e:
        return f"Error editing event: {str(e)}"

def check_calendar_availability(start_time_iso: str, end_time_iso: str) -> str:
    """Check if a time slot is available for booking.
    
    Args:
        start_time_iso: Start time in ISO format (e.g., "2024-01-15T10:00:00Z")
        end_time_iso: End time in ISO format (e.g., "2024-01-15T11:00:00Z")
    
    Returns:
        JSON string indicating availability status
    """
    try:
        availability = check_availability(start_time_iso, end_time_iso)
        return json.dumps(availability, default=str, indent=2)
    except Exception as e:
        return f"Error checking availability: {str(e)}"

# Create tools list
tools = [
    list_calendar_events,
    list_upcoming_events_tool,
    create_calendar_event,
    edit_calendar_event,
    check_calendar_availability
]

# Create the ReAct agent with LangGraph prebuilt
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=(
        "You are an intelligent calendar booking assistant. "
        "Always use the available tools to check availability, list events, or book meetings. "
        "If a user request is ambiguous, ask clarifying questions. "
        "Summarize your actions and confirm bookings with the user."
    )
)

def convert_history_to_messages(conversation: list) -> list:
    """Convert a list of dicts with 'role' and 'content' to LangChain message objects."""
    messages = []
    for msg in conversation:
        role = msg.get("role")
        content = msg.get("content")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
        elif role == "system":
            messages.append(SystemMessage(content=content))
    return messages

def invoke_agent(conversation: list) -> str:
    """Invoke the agent with a conversation history and return the AI's reply as a string."""
    messages = convert_history_to_messages(conversation)
    # Inject current date/time as a system message if not already present
    system_time_message = SystemMessage(content=f"Current date and time (IST): {get_current_time_iso()}")
    # Only add if not already present in the conversation
    if not any(isinstance(m, SystemMessage) and "Current date and time" in m.content for m in messages):
        messages = [system_time_message] + messages
    result = agent.invoke({"messages": messages})
    # result is a dict with 'messages' key
    messages_out = result.get("messages", [])
    for msg in reversed(messages_out):
        if isinstance(msg, AIMessage):
            content = msg.content
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                return "\n".join(str(x) for x in content)
            elif isinstance(content, dict):
                return json.dumps(content)
    return "No reply from agent."

def print_available_gemini_models():
    """Print available Gemini models for the current API key."""
    try:
        models = list_models()
        print("Available Gemini models:")
        for m in models:
            print(f"- {m['name']}")
    except Exception as e:
        print(f"Error listing models: {e}")

# Uncomment to run this check at startup
# print_available_gemini_models()
