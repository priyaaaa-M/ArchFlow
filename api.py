from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional
from dotenv import load_dotenv

from fastapi import BackgroundTasks, FastAPI, HTTPException

load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from services.workflow import run_workflow
from database import db


app = FastAPI(title="LS Hackathon Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from output directory
app.mount("/files", StaticFiles(directory="output"), name="files")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return {}

# Keep in-memory cache for active jobs (optional performance optimization)
ACTIVE_JOBS: dict[str, dict[str, Any]] = {}


class GenerateRequest(BaseModel):
    title: str  # Changed from 'topic' to 'title' as requested
    type: str   # New field for HLD/LLD
    urls: Optional[list[str]] = None


class GenerateResponse(BaseModel):
    job_id: str
    status: str


def _run_job(job_id: str, topic: str, urls: Optional[list[str]]) -> None:
    # Update status to running in database
    db.update_job_status(job_id, "running")
    
    # Update in-memory cache
    if job_id in ACTIVE_JOBS:
        ACTIVE_JOBS[job_id]["status"] = "running"
        ACTIVE_JOBS[job_id]["updated_at"] = datetime.utcnow().isoformat() + "Z"

    try:
        result = run_workflow(job_id=job_id, topic=topic, urls=urls)
        
        # Save result to database
        db.save_job_result(job_id, result)
        
        # Update in-memory cache
        if job_id in ACTIVE_JOBS:
            ACTIVE_JOBS[job_id]["status"] = "completed"
            ACTIVE_JOBS[job_id]["result"] = result
            ACTIVE_JOBS[job_id]["updated_at"] = datetime.utcnow().isoformat() + "Z"
            
    except Exception as e:
        error_msg = str(e)
        
        # Save error to database
        db.update_job_status(job_id, "failed", error_msg)
        
        # Update in-memory cache
        if job_id in ACTIVE_JOBS:
            ACTIVE_JOBS[job_id]["status"] = "failed"
            ACTIVE_JOBS[job_id]["error"] = error_msg
            ACTIVE_JOBS[job_id]["updated_at"] = datetime.utcnow().isoformat() + "Z"


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest, background_tasks: BackgroundTasks) -> GenerateResponse:
    # Validate type parameter
    if req.type.upper() not in ["HLD", "LLD"]:
        raise HTTPException(status_code=400, detail="type must be either 'HLD' or 'LLD'")
    
    job_id = uuid.uuid4().hex
    topic = f"{req.title} {req.type.upper()}"
    
    # Create job in database
    success = db.create_job(job_id, req.title, req.type.upper(), topic)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create job in database")
    
    # Add to in-memory cache for active jobs
    ACTIVE_JOBS[job_id] = {
        "status": "queued",
        "title": req.title,
        "type": req.type.upper(),
        "topic": topic,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }

    background_tasks.add_task(_run_job, job_id, topic, req.urls)
    return GenerateResponse(job_id=job_id, status="queued")


@app.get("/status/{job_id}")
def status(job_id: str) -> dict:
    # Try in-memory cache first (for active jobs)
    if job_id in ACTIVE_JOBS:
        job = ACTIVE_JOBS[job_id]
        return {
            "job_id": job_id,
            "status": job.get("status"),
            "title": job.get("title"),
            "type": job.get("type"),
            "topic": job.get("topic"),
            "created_at": job.get("created_at"),
            "updated_at": job.get("updated_at"),
            "error": job.get("error"),
        }
    
    # Fallback to database
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_id not found")
    
    return {
        "job_id": job_id,
        "status": job.get("status"),
        "title": job.get("title"),
        "type": job.get("type"),
        "topic": job.get("topic"),
        "created_at": job.get("created_at"),
        "updated_at": job.get("updated_at"),
        "error": job.get("error"),
    }


@app.get("/result/{job_id}")
def result(job_id: str) -> dict:
    # Try in-memory cache first
    if job_id in ACTIVE_JOBS:
        job = ACTIVE_JOBS[job_id]
        if job.get("status") != "completed":
            raise HTTPException(status_code=409, detail="job not completed")
        return job.get("result") or {}
    
    # Fallback to database
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_id not found")
    if job.get("status") != "completed":
        raise HTTPException(status_code=409, detail="job not completed")
    return job.get("result") or {}


@app.get("/jobs")
def list_jobs(limit: int = 50, status: str = None) -> dict:
    """Get list of all jobs with optional filtering"""
    jobs = db.get_all_jobs(limit=limit, status=status)
    stats = db.get_job_stats()
    
    return {
        "jobs": jobs,
        "stats": stats,
        "total_returned": len(jobs)
    }


@app.get("/jobs/stats")
def job_statistics() -> dict:
    """Get job statistics"""
    return db.get_job_stats()


@app.delete("/jobs/cleanup")
def cleanup_old_jobs(days: int = 30) -> dict:
    """Clean up jobs older than specified days"""
    deleted_count = db.cleanup_old_jobs(days)
    return {
        "message": f"Cleaned up {deleted_count} jobs older than {days} days",
        "deleted_count": deleted_count
    }


@app.get("/jobs/{job_id}/components")
def get_job_components(job_id: str) -> dict:
    """Get all components for a specific job"""
    components = db.get_job_components(job_id)
    return {
        "job_id": job_id,
        "components": components,
        "count": len(components)
    }


@app.get("/jobs/{job_id}/relationships")
def get_job_relationships(job_id: str) -> dict:
    """Get all relationships for a specific job"""
    relationships = db.get_job_relationships(job_id)
    return {
        "job_id": job_id,
        "relationships": relationships,
        "count": len(relationships)
    }


@app.get("/components")
def list_components(component_type: str = None, limit: int = 100) -> dict:
    """Get components across all jobs, optionally filtered by type"""
    if component_type:
        components = db.get_components_by_type(component_type, limit)
        return {
            "components": components,
            "type_filter": component_type,
            "count": len(components)
        }
    else:
        # Get all component types and their stats
        stats = db.get_component_stats()
        return {
            "component_stats": stats,
            "available_types": list(stats.get('component_types', {}).keys())
        }


@app.get("/analytics/components")
def component_analytics() -> dict:
    """Get analytics about components across all jobs"""
    stats = db.get_component_stats()
    job_stats = db.get_job_stats()
    
    return {
        "component_analytics": stats,
        "job_summary": job_stats,
        "insights": {
            "avg_components_per_job": round(stats['total_components'] / max(job_stats['completed'], 1), 2),
            "avg_relationships_per_job": round(stats['total_relationships'] / max(job_stats['completed'], 1), 2),
            "most_common_component_type": max(stats['component_types'].items(), key=lambda x: x[1])[0] if stats['component_types'] else None
        }
    }
