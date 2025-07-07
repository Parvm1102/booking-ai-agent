from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from langgraph_agent import invoke_agent
from calendar_utils import get_current_time_iso
import json

app = FastAPI(title="Calendar Booking Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    response: str
    tool_calls: Optional[List[Dict[str, Any]]] = []
    status: str = "success"

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    calendar_connected: bool

@app.get("/")
async def root():
    return {"message": "Calendar Booking Assistant API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        from calendar_utils import service
        calendar_connected = service is not None
    except:
        calendar_connected = False
    
    return HealthResponse(
        status="healthy",
        timestamp=get_current_time_iso(),
        calendar_connected=calendar_connected
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint that processes user messages through the LangGraph agent"""
    try:
        # Build conversation history as list of dicts
        conversation = request.conversation_history or []
        # Add the latest user message
        conversation.append({"role": "user", "content": request.message})
        # Call the agent with the full conversation
        final_response = invoke_agent(conversation)
        return ChatResponse(response=final_response)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.get("/calendar/events")
async def get_events(start_time: Optional[str] = None):
    """Get calendar events from a specific start time"""
    try:
        from calendar_utils import list_events
        if not start_time:
            start_time = get_current_time_iso()
        
        events = list_events(start_time)
        return {"events": events}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching events: {str(e)}"
        )

@app.post("/calendar/events")
async def create_calendar_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: str = ""
):
    """Create a new calendar event"""
    try:
        from calendar_utils import create_event
        event = create_event(summary, start_time, end_time, description)
        return {"event": event}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating event: {str(e)}"
        )

@app.get("/calendar/availability")
async def check_availability(start_time: str, end_time: str):
    """Check availability for a time slot"""
    try:
        from calendar_utils import check_availability
        availability = check_availability(start_time, end_time)
        return availability
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking availability: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
