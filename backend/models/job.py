"""Job model for the database."""
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, Boolean
from pydantic import BaseModel
from typing import Optional
from backend.database import Base


class Job(Base):
    """SQLAlchemy Job model."""

    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, default="Toronto, ON")
    url = Column(String, nullable=False, unique=True)  # Job listing URL (Indeed, LinkedIn, etc.)
    apply_url = Column(String, nullable=True)  # Direct application portal URL (Workday, Greenhouse, Lever, etc.)
    source = Column(String, nullable=False)  # JSearch, GitHub, Indeed, RemoteOK, Arbeitnow
    salary = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    posted_date = Column(DateTime, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    duration = Column(String, nullable=True)  # 4/8/12/16 months
    # Status: new, reviewed, applied, rejected
    status = Column(String, default="new")
    is_saved = Column(Boolean, default=False)
    is_startup = Column(Boolean, default=False)

    @property
    def is_new(self) -> bool:
        """Job is new if status is 'new'."""
        return self.status == "new"

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "url": self.url,
            "apply_url": self.apply_url,
            "source": self.source,
            "salary": self.salary,
            "description": self.description,
            "posted_date": self.posted_date.isoformat() if self.posted_date else None,
            "added_at": self.added_at.isoformat() if self.added_at else None,
            "duration": self.duration,
            "status": self.status,
            "is_saved": self.is_saved,
            "is_startup": self.is_startup,
            "is_new": self.is_new,
        }


# Pydantic models for API
class JobCreate(BaseModel):
    """Schema for creating a job."""

    title: str
    company: str
    location: str = "Toronto, ON"
    url: str
    source: str
    salary: Optional[str] = None
    description: Optional[str] = None
    posted_date: Optional[datetime] = None
    duration: Optional[str] = None
    is_startup: bool = False


class JobUpdate(BaseModel):
    """Schema for updating a job."""

    status: Optional[str] = None  # new, reviewed, applied, rejected
    is_saved: Optional[bool] = None


class JobResponse(BaseModel):
    """Schema for job API response."""

    id: str
    title: str
    company: str
    location: str
    url: str
    apply_url: Optional[str]
    source: str
    salary: Optional[str]
    description: Optional[str]
    posted_date: Optional[str]
    added_at: Optional[str]
    duration: Optional[str]
    status: str  # new, reviewed, applied, rejected
    is_saved: bool
    is_startup: bool
    is_new: bool

    class Config:
        from_attributes = True


class JobData(BaseModel):
    """Internal schema for job data from fetchers."""

    title: str
    company: str
    location: str = "Toronto, ON"
    url: str
    apply_url: Optional[str] = None  # Direct application portal URL (resolved from redirects)
    source: str
    salary: Optional[str] = None
    description: Optional[str] = None
    posted_date: Optional[datetime] = None
    duration: Optional[str] = None
    is_startup: bool = False
