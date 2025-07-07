#!/usr/bin/env python3
"""
Startup script for the AI Calendar Booking Assistant
This script can start both the backend and frontend services
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import fastapi
        import langchain_google_genai
        import langgraph
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    if not Path(".env").exists():
        print("⚠️  .env file not found")
        print("Please create a .env file with the following variables:")
        print("GOOGLE_API_KEY=your_gemini_api_key_here")
        print("GOOGLE_CALENDAR_ID=your_calendar_id_here")
        print("SERVICE_ACCOUNT_FILE=service_account.json")
        return False
    return True

def check_service_account():
    """Check if service account file exists"""
    if not Path("service_account.json").exists():
        print("⚠️  service_account.json not found")
        print("Please download your Google service account key and save it as service_account.json")
        return False
    return True

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return None
    
    try:
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment to see if it starts successfully
        time.sleep(2)
        if process.poll() is None:
            print("✅ Backend started successfully")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Backend failed to start: {stderr}")
            return None
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend():
    """Start the Streamlit frontend"""
    print("🚀 Starting Streamlit frontend...")
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None
    
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment to see if it starts successfully
        time.sleep(3)
        if process.poll() is None:
            print("✅ Frontend started successfully")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Frontend failed to start: {stderr}")
            return None
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down services...")
    sys.exit(0)

def main():
    """Main function"""
    print("📅 AI Calendar Booking Assistant")
    print("=" * 40)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check prerequisites
    if not check_dependencies():
        sys.exit(1)
    
    if not check_env_file():
        print("Continue anyway? (y/n): ", end="")
        if input().lower() != 'y':
            sys.exit(1)
    
    if not check_service_account():
        print("Continue anyway? (y/n): ", end="")
        if input().lower() != 'y':
            sys.exit(1)
    
    print("\n🔧 Starting services...")
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend. Exiting.")
        sys.exit(1)
    
    # Wait a bit for backend to fully start
    time.sleep(2)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend. Stopping backend...")
        backend_process.terminate()
        sys.exit(1)
    
    print("\n🎉 Application started successfully!")
    print("📱 Frontend: http://localhost:8501")
    print("🔧 Backend:  http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly")
                break
            
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        # Cleanup
        if backend_process and backend_process.poll() is None:
            backend_process.terminate()
            print("✅ Backend stopped")
        
        if frontend_process and frontend_process.poll() is None:
            frontend_process.terminate()
            print("✅ Frontend stopped")

if __name__ == "__main__":
    main() 