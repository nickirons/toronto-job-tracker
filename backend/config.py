"""Configuration settings for the Toronto Job Tracker."""
import os
import json
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

# Settings file path
SETTINGS_FILE = Path(__file__).parent.parent / "settings.json"


class Settings(BaseSettings):
    """Application settings."""

    # JSearch API Configuration (RapidAPI - optional, paid)
    rapidapi_key: str = ""
    jsearch_base_url: str = "https://jsearch.p.rapidapi.com"
    jsearch_host: str = "jsearch.p.rapidapi.com"

    # Adzuna API Configuration (free tier - optional but recommended)
    # Register at: https://developer.adzuna.com/
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""

    # Refresh Configuration
    refresh_interval_minutes: int = 15

    # Database
    database_url: str = "sqlite:///./jobs.db"

    # Search queries for JSearch API
    search_queries: list[str] = [
        "software engineer intern Toronto",
        "software developer intern Toronto",
        "software co-op Toronto",
        "developer co-op Toronto",
        "data science intern Toronto",
        "machine learning intern Toronto",
        "devops intern Toronto",
        "frontend intern Toronto",
        "backend intern Toronto",
        "full stack intern Toronto",
        "software internship Toronto",
        "tech intern Toronto",
        "computer science co-op Toronto",
        "IT intern Toronto",
    ]

    # GitHub curated list URLs
    github_list_urls: list[str] = [
        "https://raw.githubusercontent.com/jenndryden/Canadian-Tech-Internships-Summer-2025/main/README.md",
        "https://raw.githubusercontent.com/hanzili/canada_sde_intern_position/main/README.md",
        "https://raw.githubusercontent.com/pittcsc/Summer2025-Internships/dev/README.md",
        "https://raw.githubusercontent.com/SimplifyJobs/Summer2025-Internships/dev/README.md",
    ]

    # Indeed RSS queries
    indeed_queries: list[str] = [
        "software+intern",
        "developer+intern",
        "data+science+intern",
        "co-op+software",
    ]

    class Config:
        env_file = ".env"


def load_settings() -> dict:
    """Load settings from JSON file."""
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_settings(settings: dict) -> None:
    """Save settings to JSON file."""
    existing = load_settings()
    existing.update(settings)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(existing, f, indent=2)


def get_rapidapi_key() -> str:
    """Get the RapidAPI key from settings file or environment."""
    settings = load_settings()
    return settings.get("rapidapi_key", os.getenv("RAPIDAPI_KEY", ""))


def set_rapidapi_key(key: str) -> None:
    """Set the RapidAPI key in settings file."""
    save_settings({"rapidapi_key": key})


def get_refresh_interval() -> int:
    """Get refresh interval in minutes."""
    settings = load_settings()
    return settings.get("refresh_interval_minutes", 15)


def set_refresh_interval(minutes: int) -> None:
    """Set refresh interval in minutes."""
    save_settings({"refresh_interval_minutes": minutes})


def get_adzuna_credentials() -> tuple[str, str]:
    """Get Adzuna API credentials from settings file or environment."""
    file_settings = load_settings()
    app_id = file_settings.get("adzuna_app_id", os.getenv("ADZUNA_APP_ID", ""))
    app_key = file_settings.get("adzuna_app_key", os.getenv("ADZUNA_APP_KEY", ""))
    return app_id, app_key


def set_adzuna_credentials(app_id: str, app_key: str) -> None:
    """Set Adzuna API credentials in settings file."""
    save_settings({"adzuna_app_id": app_id, "adzuna_app_key": app_key})


# Global settings instance
settings = Settings()
