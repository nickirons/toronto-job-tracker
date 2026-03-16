"""Jobs API routes."""
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models.job import Job, JobUpdate, JobResponse
from backend.services.job_fetcher import job_fetcher, _dedup_key

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("", response_model=List[JobResponse])
async def get_jobs(
    search: Optional[str] = Query(None, description="Search by title, company, or location"),
    source: Optional[str] = Query(None, description="Filter by source"),
    status: Optional[str] = Query(None, description="Filter by status (new, reviewed, applied, rejected)"),
    saved: Optional[bool] = Query(None, description="Filter for saved jobs only"),
    startup: Optional[bool] = Query(None, description="Filter for startup jobs"),
    db: Session = Depends(get_db),
):
    """Get all jobs with optional filters."""
    query = db.query(Job)

    # Apply filters
    if search:
        search_term = f"%{search.lower()}%"
        query = query.filter(
            (func.lower(Job.title).like(search_term)) |
            (func.lower(Job.company).like(search_term)) |
            (func.lower(Job.location).like(search_term))
        )

    if source:
        query = query.filter(Job.source == source)

    if status:
        query = query.filter(Job.status == status)

    if saved is True:
        query = query.filter(Job.is_saved == True)

    if startup is not None:
        query = query.filter(Job.is_startup == startup)

    # Order by added_at descending (newest first)
    jobs = query.order_by(Job.added_at.desc()).all()

    return [JobResponse(**job.to_dict()) for job in jobs]


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get job statistics."""
    total = db.query(Job).count()

    # Count by status
    status_counts = db.query(
        Job.status,
        func.count(Job.id)
    ).group_by(Job.status).all()
    by_status = {status: count for status, count in status_counts}

    # Saved jobs
    saved_count = db.query(Job).filter(Job.is_saved == True).count()

    # Count by source
    source_counts = db.query(
        Job.source,
        func.count(Job.id)
    ).group_by(Job.source).all()

    return {
        "total": total,
        "new": by_status.get("new", 0),
        "reviewed": by_status.get("reviewed", 0),
        "applied": by_status.get("applied", 0),
        "rejected": by_status.get("rejected", 0),
        "saved": saved_count,
        "by_status": by_status,
        "by_source": {source: count for source, count in source_counts},
        "last_refresh": job_fetcher.last_refresh.isoformat() if job_fetcher.last_refresh else None,
    }


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: Session = Depends(get_db)):
    """Get a single job by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(**job.to_dict())


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    update: JobUpdate,
    db: Session = Depends(get_db),
):
    """Update a job (change status, toggle saved)."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if update.status is not None:
        # Validate status value
        valid_statuses = ["new", "reviewed", "applied", "rejected"]
        if update.status in valid_statuses:
            job.status = update.status

    if update.is_saved is not None:
        job.is_saved = update.is_saved

    db.commit()
    db.refresh(job)

    return JobResponse(**job.to_dict())


@router.delete("/{job_id}")
async def delete_job(job_id: str, db: Session = Depends(get_db)):
    """Delete a job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job)
    db.commit()

    return {"message": "Job deleted"}


@router.post("/refresh")
async def refresh_jobs(db: Session = Depends(get_db)):
    """Trigger a manual job refresh."""
    new_count, total_count = await job_fetcher.fetch_all_jobs(db)

    return {
        "message": f"Refresh complete. {new_count} new jobs found.",
        "new_jobs": new_count,
        "total_jobs": total_count,
        "last_refresh": job_fetcher.last_refresh.isoformat() if job_fetcher.last_refresh else None,
    }


@router.delete("")
async def clear_all_jobs(db: Session = Depends(get_db)):
    """Delete all jobs."""
    count = db.query(Job).delete()
    db.commit()

    return {"message": f"Deleted {count} jobs"}


@router.post("/deduplicate")
async def deduplicate_jobs(db: Session = Depends(get_db)):
    """Remove duplicate jobs from the database by matching title+company.
    Keeps the oldest entry (first added) and removes newer duplicates.
    Saved jobs are always kept over unsaved ones."""
    all_jobs = db.query(Job).order_by(Job.added_at.asc()).all()

    seen = {}  # dedup_key -> job to keep
    to_delete = []

    for job in all_jobs:
        key = _dedup_key(job.title, job.company)
        if key not in seen:
            seen[key] = job
        else:
            existing = seen[key]
            # Prefer keeping saved jobs
            if job.is_saved and not existing.is_saved:
                to_delete.append(existing.id)
                seen[key] = job
            elif job.status in ("applied", "reviewed") and existing.status == "new":
                to_delete.append(existing.id)
                seen[key] = job
            else:
                to_delete.append(job.id)

    if to_delete:
        db.query(Job).filter(Job.id.in_(to_delete)).delete(synchronize_session=False)
        db.commit()

    return {
        "message": f"Removed {len(to_delete)} duplicate jobs",
        "duplicates_removed": len(to_delete),
        "jobs_remaining": len(all_jobs) - len(to_delete),
    }


@router.post("/resolve-urls")
async def resolve_apply_urls(db: Session = Depends(get_db)):
    """Resolve direct application URLs for jobs that don't have them."""
    from backend.utils.url_resolver import resolve_apply_url

    # Get jobs without apply_url
    jobs = db.query(Job).filter(
        (Job.apply_url == None) | (Job.apply_url == "")
    ).all()

    if not jobs:
        return {"message": "All jobs already have apply URLs", "resolved": 0, "total": 0}

    print(f"🔗 Resolving application URLs for {len(jobs)} jobs...")

    resolved_count = 0
    for job in jobs:
        resolved_url = await resolve_apply_url(job.url)
        if resolved_url and resolved_url != job.url:
            job.apply_url = resolved_url
            resolved_count += 1

    db.commit()

    return {
        "message": f"Resolved {resolved_count} application URLs",
        "resolved": resolved_count,
        "total": len(jobs)
    }
