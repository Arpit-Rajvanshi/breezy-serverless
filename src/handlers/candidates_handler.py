"""
Lambda handler for POST /candidates

Accepts candidate data, validates with Pydantic, creates candidate in Breezy HR,
and attaches them to the specified job.
"""

import json
from pydantic import ValidationError as PydanticValidationError

from src.services.candidate_service import CandidateService
from src.models.candidate import CandidateCreateRequest
from src.utils.response import created, bad_request, unprocessable, not_found, internal_error, gateway_error
from src.utils.error_handler import BreezyAPIError, NotFoundError, ConfigurationError
from src.utils.logger import get_logger

logger = get_logger(__name__)


def create_candidate(event: dict, context) -> dict:
    """
    Lambda handler: POST /candidates

    Request Body (JSON):
        name       (str, required)
        email      (str, required, validated)
        phone      (str, optional, E.164 format)
        resume_url (str, optional)
        job_id     (str, required)

    Returns:
        201: Candidate created and attached to job
        400: Malformed JSON body
        404: Job not found in Breezy HR
        422: Request payload validation error
        502: Upstream Breezy HR error
        500: Unexpected internal error
    """
    logger.info("Received POST /candidates request")

    # --- Parse body ---
    body_raw = event.get("body") or "{}"
    try:
        body = json.loads(body_raw)
    except json.JSONDecodeError as exc:
        logger.warning("Invalid JSON body", extra={"error": str(exc)})
        return bad_request("Request body must be valid JSON.")

    if not isinstance(body, dict):
        return bad_request("Request body must be a JSON object.")

    # --- Validate with Pydantic ---
    try:
        request = CandidateCreateRequest(**body)
    except PydanticValidationError as exc:
        errors = [
            {"field": ".".join(str(loc) for loc in e["loc"]), "message": e["msg"]}
            for e in exc.errors()
        ]
        logger.warning("Validation error for POST /candidates", extra={"errors": errors})
        return unprocessable("Request payload validation failed.", details=errors)

    # --- Execute business logic ---
    try:
        service = CandidateService()
        result = service.create_and_attach(request)
        logger.info("POST /candidates succeeded", extra={"candidate_id": result.id})
        return created(result.model_dump())

    except NotFoundError as exc:
        logger.warning("Job not found", extra={"job_id": request.job_id})
        return not_found(exc.message)

    except BreezyAPIError as exc:
        logger.error("Breezy API error in POST /candidates", extra={"status_code": exc.status_code})
        return gateway_error(f"Breezy HR API error: {exc.message}")

    except (EnvironmentError, ConfigurationError) as exc:
        logger.critical("Configuration error", extra={"error": str(exc)})
        return internal_error("Service configuration error. Contact support.")

    except Exception:
        logger.exception("Unexpected error in POST /candidates")
        return internal_error("An unexpected error occurred.")
