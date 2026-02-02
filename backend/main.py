"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import asyncio

from backend.database import init_db, SessionLocal
from backend.routers import jobs_router, settings_router
from backend.services.job_fetcher import job_fetcher
from backend.config import get_refresh_interval


# Background refresh task
async def background_refresh():
    """Background task to refresh jobs periodically."""
    while True:
        try:
            interval = get_refresh_interval() * 60  # Convert to seconds
            await asyncio.sleep(interval)

            print(f"\n🔄 Auto-refresh triggered (every {interval // 60} minutes)")
            db = SessionLocal()
            try:
                await job_fetcher.fetch_all_jobs(db)
            finally:
                db.close()

        except Exception as e:
            print(f"Background refresh error: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("🚀 Starting Toronto Job Tracker API...")
    init_db()

    # Start background refresh task
    refresh_task = asyncio.create_task(background_refresh())

    yield

    # Shutdown
    refresh_task.cancel()
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Toronto Job Tracker API",
    description="API for tracking Toronto internship job listings",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs_router)
app.include_router(settings_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Toronto Job Tracker API",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# Serve frontend static files (if built)
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
