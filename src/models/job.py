"""
Pydantic models for Job domain.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator


class JobStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    DRAFT = "DRAFT"


class Job(BaseModel):
    """Standardized job representation returned by the API."""

    id: str
    title: str
    location: str
    status: JobStatus
    external_url: Optional[str] = None

    model_config = {"use_enum_values": True}


class JobListResponse(BaseModel):
    """Paginated list of jobs."""

    data: list[Job]
    total: int
    page: int
    page_size: int


def map_breezy_job(raw: dict) -> Job:
    """
    Map a raw Breezy HR position object to a standardized Job model.

    Breezy field reference:
      _id           -> id
      name          -> title
      location.name -> location
      state         -> status  (published=OPEN, closed=CLOSED, draft=DRAFT)
      friendly_url  -> external_url
    """
    state_map = {
        "published": JobStatus.OPEN,
        "closed": JobStatus.CLOSED,
        "draft": JobStatus.DRAFT,
        "archived": JobStatus.CLOSED,
    }

    location = raw.get("location") or {}
    location_name = location.get("name", "") if isinstance(location, dict) else str(location)

    raw_state = str(raw.get("state", "draft")).lower()
    status = state_map.get(raw_state, JobStatus.DRAFT)

    return Job(
        id=str(raw.get("_id", raw.get("id", ""))),
        title=raw.get("name", ""),
        location=location_name,
        status=status,
        external_url=raw.get("friendly_url") or raw.get("external_url"),
    )
