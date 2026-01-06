import os
from dotenv import load_dotenv
from services.workflow import run_workflow
from loguru import logger
import traceback

load_dotenv()
from loguru import logger
import traceback

def test_workflow():
    job_id = "debug_job_001"
    topic = "Uber Backend System HLD"
    # We won't pass URLs, let it search/crawl (might take time) 
    # OR we can mock the expensive parts if needed.
    # But to reproduce "Job failed", we should try to run it.
    
    # Actually, crawling takes time. 
    # If the user's job failed quickly, it might be an import error.
    # If it failed after some time, it might be the logic.
    
    print("Testing workflow execution...")
    try:
        # Just run it. If it crawls, it crawls.
        # But to be faster, let's mock the text extraction if possible?
        # No, let's run it.
        result = run_workflow(job_id=job_id, topic=topic)
        print("Workflow finished successfully!")
        print("Result keys:", result.keys())
        if result.get("gif_url"):
            print("GIF URL present:", result["gif_url"])
        else:
            print("GIF URL MISSING/EMPTY")
            
    except Exception:
        print("WORKFLOW FAILED")
        traceback.print_exc()

if __name__ == "__main__":
    test_workflow()
