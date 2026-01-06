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
    print("Starting FastAPI Backend...")
    
    # Add Graphviz to PATH for Windows
    if os.name == 'nt':
        graphviz_path = r"C:\Program Files\Graphviz\bin"
        if Path(graphviz_path).exists():
            os.environ['PATH'] += f";{graphviz_path}"
    
    backend_cmd = [
        sys.executable, "-m", "uvicorn", "backend.api:app",
        "--reload", "--host", "127.0.0.1", "--port", "8000"
    ]
    
    return subprocess.Popen(
        backend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

def start_frontend():
    """Frontend removed from this repository.

    This project no longer includes a Python Streamlit frontend (app.py).
    This function remains as a placeholder so older scripts don't fail if
    accidentally called; it will raise to make the absence explicit.
    """
    raise RuntimeError("No Python frontend (app.py) is present in this repository.")

def main():
    print("System Design Generator - Startup Script")
    print("=" * 60)
    
    # Check if we're in the right directory
    # Ensure backend package exists
    if not Path("backend/api.py").exists():
        print("❌ Error: backend/api.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    # Start backend only (no Python frontend in this repo)
    backend_process = start_backend()
    
    # Wait for backend to start
    print("Waiting for backend to start...")
    for i in range(30):  # Wait up to 30 seconds
        if check_backend_health():
            print("Backend is running at http://127.0.0.1:8000")
            break
        time.sleep(1)
        print(f"   Checking backend... ({i+1}/30)")
    else:
        print("❌ Backend failed to start within 30 seconds")
        backend_process.terminate()
        sys.exit(1)

    print("\nSystem Design Generator is ready!")
    print("=" * 60)
    print("Backend API: http://127.0.0.1:8000")
    print("API Docs: http://127.0.0.1:8000/docs")
    print("=" * 60)
    print("\nTip: Press Ctrl+C to stop the backend service")
    
    try:
        # Keep backend process running
        while True:
            # Check if process is still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly")
                break
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nShutting down services...")
        
        # Terminate backend process only
        try:
            backend_process.terminate()
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
        
        print("Backend service stopped successfully")

if __name__ == "__main__":
    main()