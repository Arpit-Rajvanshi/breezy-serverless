"""
Pydantic models for Application domain.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class ApplicationStatus(str, Enum):
    APPLIED = "APPLIED"
    SCREENING = "SCREENING"
    REJECTED = "REJECTED"
    HIRED = "HIRED"


class Application(BaseModel):
    """Standardized application representation returned by the API."""

    id: str
    candidate_name: str
    email: str
    status: ApplicationStatus

    model_config = {"use_enum_values": True}


class ApplicationListResponse(BaseModel):
    """Paginated list of applications."""

    data: list[Application]
    total: int
    page: int
    page_size: int


# Breezy HR stage-name -> our normalized status
_STAGE_STATUS_MAP: dict[str, ApplicationStatus] = {
    # Applied / New
    "applied": ApplicationStatus.APPLIED,
    "new": ApplicationStatus.APPLIED,
    "reviewing": ApplicationStatus.SCREENING,
    "screening": ApplicationStatus.SCREENING,
    "phone screen": ApplicationStatus.SCREENING,
    "interview": ApplicationStatus.SCREENING,
    "shortlisted": ApplicationStatus.SCREENING,
    "offer": ApplicationStatus.SCREENING,
    "hired": ApplicationStatus.HIRED,
    "declined": ApplicationStatus.REJECTED,
    "rejected": ApplicationStatus.REJECTED,
    "not a fit": ApplicationStatus.REJECTED,
    "withdrawn": ApplicationStatus.REJECTED,
}


def map_breezy_application(raw: dict) -> Application:
    """
    Map a raw Breezy HR candidate-in-pipeline object to a standardized Application.

    Breezy fields:
      _id                       -> id
      name                      -> candidate_name
      email_address             -> email
      stage.name / origin.type  -> status
    """
    stage = raw.get("stage") or {}
    stage_name = (stage.get("name") or "applied").lower()
    status = _STAGE_STATUS_MAP.get(stage_name, ApplicationStatus.APPLIED)

    candidate = raw.get("candidate") or raw  # Breezy may nest or flatten
    return Application(
        id=str(raw.get("_id", raw.get("id", ""))),
        candidate_name=candidate.get("name", raw.get("name", "")),
        email=candidate.get("email_address", raw.get("email_address", raw.get("email", ""))),
        status=status,
    )
