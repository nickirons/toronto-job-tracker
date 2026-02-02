"""Settings API routes."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from backend.config import (
    get_rapidapi_key,
    set_rapidapi_key,
    get_refresh_interval,
    set_refresh_interval,
    load_settings,
)

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingsResponse(BaseModel):
    """Settings response schema."""
    rapidapi_key: str
    rapidapi_key_set: bool
    refresh_interval_minutes: int


class SettingsUpdate(BaseModel):
    """Settings update schema."""
    rapidapi_key: Optional[str] = None
    refresh_interval_minutes: Optional[int] = None


@router.get("", response_model=SettingsResponse)
async def get_settings():
    """Get current settings."""
    api_key = get_rapidapi_key()

    return SettingsResponse(
        rapidapi_key=api_key[:10] + "..." if len(api_key) > 10 else api_key,
        rapidapi_key_set=bool(api_key),
        refresh_interval_minutes=get_refresh_interval(),
    )


@router.put("", response_model=SettingsResponse)
async def update_settings(update: SettingsUpdate):
    """Update settings."""
    if update.rapidapi_key is not None:
        set_rapidapi_key(update.rapidapi_key)

    if update.refresh_interval_minutes is not None:
        set_refresh_interval(update.refresh_interval_minutes)

    # Return updated settings
    return await get_settings()
