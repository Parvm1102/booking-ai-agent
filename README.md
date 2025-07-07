# 📅 AI Calendar Booking Assistant

A modern calendar booking application powered by **Gemini AI**, **LangGraph**, and **Google Calendar API**. This application allows users to interact with their calendar using natural language through an AI assistant. 

## The project is live on https://booking-ai-agent-aff7.onrender.com/ and you can view the changes in this [calendar](https://calendar.google.com/calendar/u/0?cid=YWQ5ZDhmYWI5MmM4MGFhYjdjN2JhYjc4YzEwOGExZGY0MTQwNTBhYTdjMTg3OTk1ZTE2YzYyNjZkZjg2ZmZmY0Bncm91cC5jYWxlbmRhci5nb29nbGUuY29t)

## 🚀 Features

- **Natural Language Processing**: Book meetings, list events, and check availability using conversational language (e.g., "Book a meeting tomorrow at 2 PM for 1 hour")
- **AI-Powered Assistant**: Built with Gemini AI and LangGraph for intelligent, context-aware responses
- **Google Calendar Integration**: Seamless integration with Google Calendar API
- **Modern UI**: Beautiful Streamlit frontend with real-time chat interface
- **FastAPI Backend**: Robust REST API with proper error handling
- **Time Zone Support**: All meetings are booked and displayed in IST (Asia/Kolkata, GMT+5:30)
- **Edit Meetings**: Update meeting details (title, time, description) or reschedule existing events
- **List Upcoming Events**: View all your upcoming meetings/events in a friendly format
- **Real-time Status**: Live monitoring of API and calendar connection status

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **AI/ML**: Google Gemini AI, LangGraph
- **Calendar**: Google Calendar API
- **Authentication**: Google Service Account

## 📋 Prerequisites

1. **Python 3.8+**
2. **Google Cloud Project** with Calendar API enabled
3. **Google Service Account** with Calendar permissions
4. **Gemini API Key**

## 🔧 Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd intern
pip install -r requirements.txt
```

### 2. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google Calendar API**
4. Create a **Service Account**:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Download the JSON key file
   - Place it in the root directory as `service_account.json`

### 3. Gemini API Setup

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key

### 4. Environment Configuration

Create a `.env` file in the root directory:

```env
# Google API Configuration
GOOGLE_API_KEY=your_gemini_api_key_here
GOOGLE_CALENDAR_ID=your_calendar_id_here

# Service Account Configuration
SERVICE_ACCOUNT_FILE=service_account.json

# API Configuration
API_URL=http://localhost:8000
```

**Note**: For `GOOGLE_CALENDAR_ID`, use:
- `primary` for your main calendar
- Or the specific calendar ID from Google Calendar settings

### 5. Calendar Permissions

Make sure your service account has access to the calendar:
1. In Google Calendar, go to Settings
2. Find your calendar and click "Share with specific people"
3. Add your service account email (found in the JSON file)
4. Grant "Make changes to events" permission

## 🚀 Running the Application

### Start the App (Backend + Frontend)

From the project root, run:

```bash
python start_app.py
```

- The backend (FastAPI) will be available at `http://localhost:8000`
- The frontend (Streamlit) will be available at `http://localhost:8501`

## 💬 Usage Examples

The AI assistant can understand natural language requests like:

- **"Book a meeting tomorrow at 2 PM for 1 hour"**
- **"Show me my calendar for next week"**
- **"Check if I'm free on Friday at 3 PM"**
- **"Schedule a team meeting next Monday at 10 AM"**
- **"What meetings do I have today?"**
- **"Edit my meeting on Friday to 4 PM and change the title to 'Project Review'"**
- **"List all my upcoming events"**

## 🔍 API Endpoints

### Health Check
```
GET /health
```

### Chat with AI
```
POST /chat
{
  "message": "Book a meeting tomorrow at 2 PM"
}
```

### Calendar Operations
```
GET /calendar/events?start_time=2024-01-15T10:00:00+05:30
POST /calendar/events
GET /calendar/availability?start_time=...&end_time=...
```

## 🏗️ Project Structure

```
intern/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── langgraph_agent.py   # LangGraph agent implementation
│   └── calendar_utils.py    # Google Calendar utilities
├── frontend/
│   └── app.py              # Streamlit frontend
├── requirements.txt         # Python dependencies
├── service_account.json    # Google service account (not in repo)
├── start_app.py            # Startup script for backend & frontend
└── README.md              # This file
```

## 🔧 Configuration Options

### Timezone Support
All meetings are booked and displayed in IST (Asia/Kolkata, GMT+5:30) by default for maximum clarity and consistency.

### API Customization
You can customize the AI behavior by modifying the prompts and tools in `backend/langgraph_agent.py`.

## 🐛 Troubleshooting

### Common Issues

1. **"Calendar service not initialized"**
   - Check if `service_account.json` exists and is valid
   - Verify the service account has calendar permissions

2. **"API Error: 401"**
   - Check if your Gemini API key is correct
   - Verify the API key has proper permissions

3. **"Connection Error"**
   - Ensure the backend is running on the correct port
   - Check if the API_URL in the frontend matches the backend

### Debug Mode

To enable debug logging, set the environment variable:
```bash
export DEBUG=true
```

- Google Gemini AI for the language model
- LangGraph for the agent framework
- Streamlit for the beautiful UI framework
- FastAPI for the robust backend framework 
