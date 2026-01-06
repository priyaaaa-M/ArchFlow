import sys
import os
from pathlib import Path
from services.converter import generate_animated_gif
from loguru import logger

# Mock structure
structure = {
    "components": [
        {"id": "user", "name": "User", "type": "client"},
        {"id": "api", "name": "API Gateway", "type": "gateway"},
        {"id": "service", "name": "Auth Service", "type": "service"},
        {"id": "db", "name": "User DB", "type": "database"}
    ],
    "relationships": [
        {"source": "user", "target": "api", "label": "Register"},
        {"source": "api", "target": "service", "label": "Create User"},
        {"source": "service", "target": "db", "label": "Save"}
    ]
}

def test_gif_generation():
    job_id = "test_verification_job"
    logger.info(f"Starting GIF generation test for job: {job_id}")
    
    try:
        gif_path = generate_animated_gif(structure, job_id)
        
        if gif_path and os.path.exists(gif_path):
            print(f"SUCCESS: GIF generated at {gif_path}")
            print(f"File size: {os.path.getsize(gif_path)} bytes")
        else:
            print("FAILURE: GIF path returned empty or file does not exist")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_gif_generation()
