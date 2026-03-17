"""
Lambda handler for GET /applications

Fetches pipeline applications for a specific job from Breezy HR.
"""

from src.services.application_service import ApplicationService
from src.utils.response import ok, bad_request, not_found, internal_error, gateway_error
from src.utils.error_handler import BreezyAPIError, NotFoundError, ConfigurationError
from src.utils.pagination import parse_pagination
from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_applications(event: dict, context) -> dict:
    """
    Lambda handler: GET /applications?job_id=...

    Query Parameters:
        job_id    (str, required): Breezy HR position ID to filter by
        page      (int, optional): Page number. Default: 1
        page_size (int, optional): Items per page. Default: 25, Max: 100

    Returns:
        200: Paginated list of applications
        400: Missing job_id parameter
        404: Job not found in Breezy HR
        502: Upstream Breezy HR error
        500: Unexpected internal error
    """
    logger.info("Received GET /applications request")

    query_params = event.get("queryStringParameters") or {}
    job_id = (query_params.get("job_id") or "").strip()

    if not job_id:
        logger.warning("GET /applications called without job_id")
        return bad_request("Query parameter 'job_id' is required.")

    pagination = parse_pagination(query_params)

    try:
        service = ApplicationService()
        applications, total = service.get_applications(job_id=job_id, pagination=pagination)

        response_body = {
            "data": [app.model_dump() for app in applications],
            "total": total,
            "page": pagination.page,
            "page_size": pagination.page_size,
        }
        logger.info(
            "GET /applications succeeded",
            extra={"job_id": job_id, "total": total, "page": pagination.page},
        )
        return ok(response_body)

    except NotFoundError as exc:
        logger.warning("Job not found in GET /applications", extra={"job_id": job_id})
        return not_found(exc.message)

    except BreezyAPIError as exc:
        logger.error(
            "Breezy API error in GET /applications",
            extra={"status_code": exc.status_code},
        )
        return gateway_error(f"Breezy HR API error: {exc.message}")

    except (EnvironmentError, ConfigurationError) as exc:
        logger.critical("Configuration error", extra={"error": str(exc)})
        return internal_error("Service configuration error. Contact support.")

    except Exception:
        logger.exception("Unexpected error in GET /applications")
        return internal_error("An unexpected error occurred.")
