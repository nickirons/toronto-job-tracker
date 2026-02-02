"""Database configuration and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Database file location
DB_PATH = Path(__file__).parent.parent / "jobs.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=False,  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize the database, creating all tables."""
    from backend.models.job import Job  # Import to register model

    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at {DB_PATH}")

    # Run migrations for existing databases
    _run_migrations()


def _run_migrations():
    """Run database migrations for schema updates."""
    import sqlite3

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Check existing columns
    cursor.execute("PRAGMA table_info(jobs)")
    columns = [col[1] for col in cursor.fetchall()]

    # Migration 1: Add apply_url column
    if "apply_url" not in columns:
        print("Running migration: Adding apply_url column...")
        cursor.execute("ALTER TABLE jobs ADD COLUMN apply_url TEXT")
        conn.commit()
        print("Migration complete: apply_url column added")

    # Migration 2: Add status column and migrate from is_viewed
    if "status" not in columns:
        print("Running migration: Adding status column...")
        cursor.execute("ALTER TABLE jobs ADD COLUMN status TEXT DEFAULT 'new'")
        conn.commit()

        # Migrate existing data: is_viewed=True -> status='reviewed', else 'new'
        if "is_viewed" in columns:
            print("Migrating is_viewed to status...")
            cursor.execute("UPDATE jobs SET status = 'reviewed' WHERE is_viewed = 1")
            cursor.execute("UPDATE jobs SET status = 'new' WHERE is_viewed = 0 OR is_viewed IS NULL")
            conn.commit()
            print("Migration complete: status column added and data migrated")
        else:
            print("Migration complete: status column added")

    conn.close()
