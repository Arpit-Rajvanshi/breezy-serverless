"""
Lambda handler for GET /jobs

Fetches open jobs from Breezy HR and returns a paginated, standardized response.
"""

import json
from src.services.job_service import JobService
from src.utils.response import ok, internal_error, gateway_error
from src.utils.error_handler import BreezyAPIError, ConfigurationError
from src.utils.pagination import parse_pagination
from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_jobs(event: dict, context) -> dict:
    """
    Lambda handler: GET /jobs

    Query Parameters:
        page (int, optional): Page number. Default: 1
        page_size (int, optional): Items per page. Default: 25, Max: 100

    Returns:
        200: Paginated list of jobs in standardized format
        502: Upstream Breezy HR error
        500: Unexpected internal error
    """
    logger.info("Received GET /jobs request", extra={"event": _safe_event(event)})

    query_params = event.get("queryStringParameters") or {}
    pagination = parse_pagination(query_params)

    try:
        service = JobService()
        jobs, total = service.get_open_jobs(pagination)

        response_body = {
            "data": [job.model_dump() for job in jobs],
            "total": total,
            "page": pagination.page,
            "page_size": pagination.page_size,
        }
        logger.info("GET /jobs succeeded", extra={"total": total, "page": pagination.page})
        return ok(response_body)

    except BreezyAPIError as exc:
        logger.error("Breezy API error in GET /jobs", extra={"status_code": exc.status_code})
        return gateway_error(f"Breezy HR API error: {exc.message}")

    except (EnvironmentError, ConfigurationError) as exc:
        logger.critical("Configuration error", extra={"error": str(exc)})
        return internal_error("Service configuration error. Contact support.")

    except Exception as exc:
        logger.exception("Unexpected error in GET /jobs")
        return internal_error("An unexpected error occurred.")


def _safe_event(event: dict) -> dict:
    """Strip sensitive fields before logging the event."""
    safe = {k: v for k, v in event.items() if k not in ("headers", "body")}
    return safe
