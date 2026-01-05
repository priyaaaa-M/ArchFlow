#!/usr/bin/env python3
"""
Startup script to run both FastAPI backend and Streamlit frontend
"""

import subprocess
import time
import sys
import os
import requests
from pathlib import Path

def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """Start FastAPI backend"""
    print("🚀 Starting FastAPI Backend...")
    
    # Add Graphviz to PATH for Windows
    if os.name == 'nt':
        graphviz_path = r"C:\Program Files\Graphviz\bin"
        if Path(graphviz_path).exists():
            os.environ['PATH'] += f";{graphviz_path}"
    
    backend_cmd = [
        "uv", "run", "uvicorn", "api:app",
        "--reload", "--host", "127.0.0.1", "--port", "8000"
    ]
    
    return subprocess.Popen(
        backend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

def start_frontend():
    """Start Streamlit frontend"""
    print("🎨 Starting Streamlit Frontend...")
    
    frontend_cmd = [
        "uv", "run", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.address", "127.0.0.1"
    ]
    
    return subprocess.Popen(
        frontend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

def main():
    print("🛠️ System Design Generator - Startup Script")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("api.py").exists():
        print("❌ Error: api.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    if not Path("app.py").exists():
        print("❌ Error: app.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    
    # Wait for backend to start
    print("⏳ Waiting for backend to start...")
    for i in range(30):  # Wait up to 30 seconds
        if check_backend_health():
            print("✅ Backend is running at http://127.0.0.1:8000")
            break
        time.sleep(1)
        print(f"   Checking backend... ({i+1}/30)")
    else:
        print("❌ Backend failed to start within 30 seconds")
        backend_process.terminate()
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    
    print("✅ Frontend starting at http://127.0.0.1:8501")
    print("\n🎉 System Design Generator is ready!")
    print("=" * 60)
    print("📊 Backend API: http://127.0.0.1:8000")
    print("🎨 Frontend UI: http://127.0.0.1:8501")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("=" * 60)
    print("\n💡 Press Ctrl+C to stop both services")
    
    try:
        # Keep both processes running
        while True:
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly")
                break
            
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped unexpectedly")
                break
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        
        # Terminate processes
        try:
            backend_process.terminate()
            frontend_process.terminate()
            
            # Wait for graceful shutdown
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
            
        except subprocess.TimeoutExpired:
            # Force kill if needed
            backend_process.kill()
            frontend_process.kill()
        
        print("✅ Services stopped successfully")

if __name__ == "__main__":
    main()