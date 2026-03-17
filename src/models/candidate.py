"""
Pydantic models for Candidate domain.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
import re


class CandidateCreateRequest(BaseModel):
    """Request payload for creating a new candidate."""

    name: str
    email: EmailStr
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    job_id: str

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Candidate name must not be empty.")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Basic E.164 check — digits, optional leading +, 7-15 digits
        cleaned = re.sub(r"[\s\-\(\)]", "", v)
        if not re.match(r"^\+?\d{7,15}$", cleaned):
            raise ValueError("Phone number format is invalid.")
        return cleaned

    @field_validator("job_id")
    @classmethod
    def job_id_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("job_id must not be empty.")
        return v


class Candidate(BaseModel):
    """Standardized candidate representation."""

    id: str
    name: str
    email: str
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    job_id: str


class CandidateCreateResponse(BaseModel):
    """Response after successfully creating a candidate."""

    id: str
    name: str
    email: str
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    job_id: str
    message: str = "Candidate created and attached to the job successfully."


def map_breezy_candidate(raw: dict, job_id: str) -> CandidateCreateResponse:
    """
    Map a raw Breezy HR candidate object to a standardized response.

    Breezy fields:
      _id           -> id
      name          -> name
      email_address -> email
      phone_number  -> phone
    """
    return CandidateCreateResponse(
        id=str(raw.get("_id", raw.get("id", ""))),
        name=raw.get("name", ""),
        email=raw.get("email_address", raw.get("email", "")),
        phone=raw.get("phone_number") or raw.get("phone"),
        resume_url=raw.get("resume_url"),
        job_id=job_id,
    )
