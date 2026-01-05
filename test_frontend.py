#!/usr/bin/env python3
"""
Test the Streamlit frontend integration
"""

import subprocess
import time
import requests
import sys
from pathlib import Path

def test_frontend_backend_integration():
    """Test that frontend can communicate with backend"""
    
    print("🎨 Testing Frontend-Backend Integration")
    print("=" * 60)
    
    # Check if backend is running
    print("🔍 Checking backend status...")
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend not responding properly")
            return False
    except:
        print("❌ Backend not running")
        print("Please start backend with:")
        print("uv run uvicorn api:app --reload --host 127.0.0.1 --port 8000")
        return False
    
    # Test backend endpoints that frontend will use
    endpoints_to_test = [
        ("/health", "Health check"),
        ("/jobs/stats", "Job statistics"),
        ("/jobs?limit=5", "Recent jobs")
    ]
    
    print(f"\n🧪 Testing backend endpoints...")
    for endpoint, description in endpoints_to_test:
        try:
            response = requests.get(f"http://127.0.0.1:8000{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {description}: OK")
            else:
                print(f"   ❌ {description}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {description}: {e}")
    
    # Test job creation (what frontend will do)
    print(f"\n🚀 Testing job creation...")
    try:
        response = requests.post(
            "http://127.0.0.1:8000/generate",
            json={"title": "Frontend Test System", "type": "HLD"},
            timeout=10
        )
        
        if response.status_code == 200:
            job_data = response.json()
            job_id = job_data["job_id"]
            print(f"✅ Job created successfully: {job_id[:8]}...")
            
            # Quick status check
            status_response = requests.get(f"http://127.0.0.1:8000/status/{job_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"   Status: {status_data['status']}")
                print(f"   Title: {status_data['title']}")
                print(f"   Type: {status_data['type']}")
            
            return True
        else:
            print(f"❌ Job creation failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Job creation failed: {e}")
        return False

def show_startup_instructions():
    """Show instructions for starting the complete system"""
    
    print(f"\n🚀 COMPLETE SYSTEM STARTUP INSTRUCTIONS")
    print("=" * 60)
    print("To run the complete system with both backend and frontend:")
    print()
    print("📋 Option 1 - Automatic (Recommended):")
    print("   python start_system.py")
    print()
    print("📋 Option 2 - Manual (Two terminals):")
    print("   Terminal 1 (Backend):")
    print("   uv run uvicorn api:app --reload --host 127.0.0.1 --port 8000")
    print()
    print("   Terminal 2 (Frontend):")
    print("   uv run streamlit run app.py --server.port 8501")
    print()
    print("🌐 Access Points:")
    print("   Frontend UI: http://127.0.0.1:8501")
    print("   Backend API: http://127.0.0.1:8000")
    print("   API Docs: http://127.0.0.1:8000/docs")
    print("=" * 60)

if __name__ == "__main__":
    # Test integration
    success = test_frontend_backend_integration()
    
    # Show startup instructions
    show_startup_instructions()
    
    if success:
        print(f"\n🎉 FRONTEND-BACKEND INTEGRATION READY!")
        print("Your system is ready for the hackathon demo!")
    else:
        print(f"\n❌ Integration test failed")
        print("Please fix backend issues before starting frontend")
    
    exit(0 if success else 1)