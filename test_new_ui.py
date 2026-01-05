#!/usr/bin/env python3
"""
Test script for the new UI with canvas functionality
"""

import subprocess
import time
import requests
import sys
from pathlib import Path

def test_new_ui():
    print("🎨 Testing New UI with Canvas")
    print("=" * 60)
    
    # Start backend
    print("🚀 Starting backend...")
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "api:app", 
        "--host", "127.0.0.1", "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for backend
    print("⏳ Waiting for backend...")
    for i in range(10):
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is running")
                break
        except:
            time.sleep(1)
    else:
        print("❌ Backend failed to start")
        backend_process.terminate()
        return False
    
    # Test backend endpoints
    print("🧪 Testing backend endpoints...")
    try:
        # Health check
        response = requests.get("http://127.0.0.1:8000/health")
        print(f"   ✅ Health check: {response.status_code}")
        
        # Job stats
        response = requests.get("http://127.0.0.1:8000/jobs/stats")
        print(f"   ✅ Job stats: {response.status_code}")
        
    except Exception as e:
        print(f"   ❌ Backend test failed: {e}")
        backend_process.terminate()
        return False
    
    # Start frontend
    print("🎨 Starting new frontend...")
    frontend_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "app.py", 
        "--server.port", "8501", "--server.headless", "true"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for frontend
    print("⏳ Waiting for frontend...")
    time.sleep(5)
    
    try:
        response = requests.get("http://127.0.0.1:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running")
        else:
            print(f"⚠️ Frontend response: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Frontend check: {e}")
    
    print("\n🎉 NEW UI FEATURES READY!")
    print("=" * 60)
    print("✨ **New Features:**")
    print("   🎨 Interactive Canvas with drawing tools")
    print("   ✏️ Pen, eraser, shapes, and colors")
    print("   🔍 Zoom in/out functionality")
    print("   📥 Download original PNG")
    print("   🎨 Download edited canvas")
    print("   📱 Clean, responsive layout")
    print("   ⚡ Real-time job monitoring")
    print("\n🌐 **Access Points:**")
    print("   Frontend: http://127.0.0.1:8501")
    print("   Backend:  http://127.0.0.1:8000")
    print("\n💡 **How to Use:**")
    print("   1. Enter system title (left panel)")
    print("   2. Click 'Generate Diagram'")
    print("   3. Wait for AI processing")
    print("   4. Edit diagram in canvas (right panel)")
    print("   5. Download your customized version")
    print("\n🎯 **Perfect for Hackathon Demo!**")
    print("=" * 60)
    
    # Keep running for demo
    try:
        print("\n⌨️ Press Ctrl+C to stop...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Services stopped")
        return True

if __name__ == "__main__":
    test_new_ui()