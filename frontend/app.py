import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import pytz
from typing import Dict, Any
import time
import os

# Page configuration
st.set_page_config(
    page_title="📅 AI Calendar Assistant",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #1976d2;
        color: #fff;
        border-left: 4px solid #1565c0;
    }
    .assistant-message {
        background-color: #8e24aa;
        color: #fff;
        border-left: 4px solid #6a1b9a;
    }
    .tool-call {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        font-family: monospace;
        font-size: 0.9rem;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-connected {
        background-color: #4caf50;
    }
    .status-disconnected {
        background-color: #f44336;
    }
    .input-hint {
        color: #888;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    .example-bubble {
        background: #f5f5f5;
        color: #333;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        display: inline-block;
        cursor: pointer;
        transition: background 0.2s;
    }
    .example-bubble:hover {
        background: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
CHAT_ENDPOINT = f"{API_URL}/chat"
HEALTH_ENDPOINT = f"{API_URL}/health"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_status" not in st.session_state:
    st.session_state.api_status = "unknown"

def check_api_health():
    """Check if the API is running and healthy"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            data = response.json()
            st.session_state.api_status = "connected" if data.get("calendar_connected") else "disconnected"
            return data
        else:
            st.session_state.api_status = "error"
            return None
    except requests.exceptions.RequestException:
        st.session_state.api_status = "error"
        return None

def send_message(message: str) -> Dict[str, Any]:
    """Send a message to the API and get response"""
    try:
        # Send the full conversation history
        response = requests.post(
            CHAT_ENDPOINT,
            json={
                "message": message,
                "conversation_history": st.session_state.messages
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection Error: {str(e)}"}

def format_datetime(dt_str: str) -> str:
    """Format datetime string for display"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return dt_str

def display_tool_calls(tool_calls):
    """Display tool calls in a formatted way"""
    if not tool_calls:
        return
    
    st.markdown("**🔧 Actions Taken:**")
    for tool_call in tool_calls:
        tool_name = tool_call.get("name", "Unknown")
        args = tool_call.get("args", {})
        
        if tool_name == "create_calendar_event":
            st.markdown(f"""
            <div class="tool-call">
            📅 <strong>Created Event:</strong><br>
            • Title: {args.get('summary', 'N/A')}<br>
            • Start: {format_datetime(args.get('start_time_iso', 'N/A'))}<br>
            • End: {format_datetime(args.get('end_time_iso', 'N/A'))}<br>
            • Description: {args.get('description', 'N/A')}
            </div>
            """, unsafe_allow_html=True)
        elif tool_name == "check_calendar_availability":
            st.markdown(f"""
            <div class="tool-call">
            🔍 <strong>Checked Availability:</strong><br>
            • Start: {format_datetime(args.get('start_time_iso', 'N/A'))}<br>
            • End: {format_datetime(args.get('end_time_iso', 'N/A'))}
            </div>
            """, unsafe_allow_html=True)
        elif tool_name == "list_calendar_events":
            st.markdown(f"""
            <div class="tool-call">
            📋 <strong>Listed Events:</strong><br>
            • From: {format_datetime(args.get('start_time_iso', 'N/A'))}
            </div>
            """, unsafe_allow_html=True)

# Main UI
st.markdown('<h1 class="main-header">📅 AI Calendar Assistant</h1>', unsafe_allow_html=True)

# Sidebar for configuration and status
with st.sidebar:
    st.header("🔧 Configuration")
    
    # API Status
    st.subheader("API Status")
    status_class = "status-connected" if st.session_state.api_status == "connected" else "status-disconnected"
    status_text = "Connected" if st.session_state.api_status == "connected" else "Disconnected"
    
    st.markdown(f"""
    <div class="status-indicator {status_class}"></div>
    {status_text}
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Status"):
        check_api_health()
        st.rerun()
    
    st.divider()
    
    # Clear Chat
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Main chat area
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("\U0001F4AC Chat with AI Assistant")
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
            <strong>\U0001F464 You:</strong><br>
            {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
            <strong>\U0001F916 Assistant:</strong><br>
            {message["content"]}
            </div>
            """, unsafe_allow_html=True)
    
    # Input area
    with st.container():
        st.markdown('<div class="input-hint">Press <b>Enter</b> to send, <b>Shift+Enter</b> for a new line.</div>', unsafe_allow_html=True)
        user_input = st.text_area(
            "Type your message here...",
            key="user_input",
            height=100,
            placeholder="Try: 'Book a meeting tomorrow at 2 PM for 1 hour' or 'Show me my calendar for next week'",
        )
        col1_, col2_, col3_ = st.columns([1, 1, 1])
        with col2_:
            if st.button("\U0001F680 Send", type="primary", use_container_width=True):
                if user_input.strip():
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    with st.spinner("\U0001F916 AI is thinking..."):
                        response = send_message(user_input)
                    if "error" not in response:
                        st.session_state.messages.append({"role": "assistant", "content": response.get("response", "")})
                        tool_calls = response.get("tool_calls")
                        if tool_calls:
                            display_tool_calls(tool_calls)
                    else:
                        st.error(f"Error: {response['error']}")
                    st.rerun()

with col2:
    st.subheader("\U0001F4DD Quick Prompts")
    st.markdown("<div style='color:#888; font-size:0.95rem; margin-bottom:0.5rem;'>Click a prompt to send it instantly:</div>", unsafe_allow_html=True)
    examples = [
        "Book a meeting tomorrow at 2 PM for 1 hour",
        "Show me my calendar for next week",
        "Check if I'm free on Friday at 3 PM",
        "Schedule a team meeting next Monday at 10 AM",
        "What meetings do I have today?",
        "Book a 30-minute call with John on Wednesday"
    ]
    for example in examples:
        if st.button(example, key=f"example_{example[:20]}"):
            st.session_state.messages.append({"role": "user", "content": example})
            with st.spinner("\U0001F916 AI is thinking..."):
                response = send_message(example)
            if "error" not in response:
                st.session_state.messages.append({"role": "assistant", "content": response.get("response", "")})
            st.rerun()
        else:
            st.markdown(f'<span class="example-bubble">{example}</span>', unsafe_allow_html=True)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    Powered by Gemini AI + LangGraph + Google Calendar API
</div>
""", unsafe_allow_html=True)

# Check API health on startup
if st.session_state.api_status == "unknown":
    check_api_health()
