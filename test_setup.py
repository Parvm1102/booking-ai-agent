#!/usr/bin/env python3
"""
Test script to verify the AI Calendar Booking Assistant setup
"""

import os
import sys
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import streamlit
        print("✅ Streamlit")
    except ImportError as e:
        print(f"❌ Streamlit: {e}")
        return False
    
    try:
        import fastapi
        print("✅ FastAPI")
    except ImportError as e:
        print(f"❌ FastAPI: {e}")
        return False
    
    try:
        import langchain_google_genai
        print("✅ LangChain Google GenAI")
    except ImportError as e:
        print(f"❌ LangChain Google GenAI: {e}")
        return False
    
    try:
        import langgraph
        print("✅ LangGraph")
    except ImportError as e:
        print(f"❌ LangGraph: {e}")
        return False
    
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        print("✅ Google API Client")
    except ImportError as e:
        print(f"❌ Google API Client: {e}")
        return False
    
    return True

def test_env_file():
    """Test if .env file exists and has required variables"""
    print("\n🔍 Testing environment configuration...")
    
    if not Path(".env").exists():
        print("❌ .env file not found")
        return False
    
    load_dotenv()
    
    required_vars = ["GOOGLE_API_KEY", "GOOGLE_CALENDAR_ID"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment variables configured")
    return True

def test_service_account():
    """Test if service account file exists and is valid"""
    print("\n🔍 Testing service account...")
    
    if not Path("service_account.json").exists():
        print("❌ service_account.json not found")
        return False
    
    try:
        with open("service_account.json", "r") as f:
            data = json.load(f)
        
        required_fields = ["type", "project_id", "private_key_id", "private_key", "client_email"]
        missing_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Invalid service account file. Missing fields: {', '.join(missing_fields)}")
            return False
        
        print("✅ Service account file is valid")
        return True
        
    except json.JSONDecodeError:
        print("❌ service_account.json is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ Error reading service account file: {e}")
        return False

def test_backend_modules():
    """Test if backend modules can be imported"""
    print("\n🔍 Testing backend modules...")
    
    try:
        sys.path.append("backend")
        from calendar_utils import list_events, create_event, check_availability
        print("✅ Calendar utilities")
    except ImportError as e:
        print(f"❌ Calendar utilities: {e}")
        return False
    
    try:
        from langgraph_agent import invoke_agent
        print("✅ LangGraph agent")
    except ImportError as e:
        print(f"❌ LangGraph agent: {e}")
        return False
    
    try:
        from main import app
        print("✅ FastAPI app")
    except ImportError as e:
        print(f"❌ FastAPI app: {e}")
        return False
    
    return True

def test_frontend_modules():
    """Test if frontend modules can be imported"""
    print("\n🔍 Testing frontend modules...")
    
    try:
        sys.path.append("frontend")
        import app
        print("✅ Streamlit app")
    except ImportError as e:
        print(f"❌ Streamlit app: {e}")
        return False
    
    return True

def test_api_connection():
    """Test if the API can be reached"""
    print("\n🔍 Testing API connection...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API is running")
            print(f"   Status: {data.get('status')}")
            print(f"   Calendar connected: {data.get('calendar_connected')}")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API (is it running?)")
        return False
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 AI Calendar Booking Assistant - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("Environment Configuration", test_env_file),
        ("Service Account", test_service_account),
        ("Backend Modules", test_backend_modules),
        ("Frontend Modules", test_frontend_modules),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 To start the application:")
        print("   python start_app.py")
        print("\n   Or manually:")
        print("   cd backend && python main.py")
        print("   cd frontend && streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\n📖 See README.md for setup instructions.")
    
    # Optional API test
    print("\n🔍 Testing API connection (optional)...")
    test_api_connection()

if __name__ == "__main__":
    main() 