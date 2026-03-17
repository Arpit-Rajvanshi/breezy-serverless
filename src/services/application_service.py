"""
Application service — business logic for fetching applications for a job.

Fetches pipeline candidates from Breezy HR for a given position and maps
them to the standardized Application model.
"""

from src.services.breezy_client import BreezyClient
from src.models.application import Application, map_breezy_application
from src.utils.logger import get_logger
from src.utils.error_handler import BreezyAPIError, NotFoundError
from src.utils.pagination import PaginationParams

logger = get_logger(__name__)


class ApplicationService:
    """Encapsulates application retrieval and normalization logic."""

    def __init__(self, client: BreezyClient | None = None):
        self._client = client or BreezyClient()

    def get_applications(
        self, job_id: str, pagination: PaginationParams
    ) -> tuple[list[Application], int]:
        """
        Fetch all applications for a job and return a paginated slice.

        Args:
            job_id: The Breezy HR position ID to query.
            pagination: Pagination parameters (page, page_size).

        Returns:
            (applications, total) tuple.

        Raises:
            NotFoundError: If the job_id is not found in Breezy HR.
            BreezyAPIError: For other upstream errors.
        """
        logger.info(
            "Fetching applications for job",
            extra={"job_id": job_id, "page": pagination.page},
        )

        try:
            raw_applications = self._client.list_applications(position_id=job_id)
        except BreezyAPIError as exc:
            if exc.status_code == 404:
                raise NotFoundError(f"Job '{job_id}' not found in Breezy HR.") from exc
            raise

        applications: list[Application] = [map_breezy_application(r) for r in raw_applications]
        total = len(applications)

        # Apply pagination slice
        start = (pagination.page - 1) * pagination.page_size
        end = start + pagination.page_size
        page_apps = applications[start:end]

        logger.info(
            "Applications fetched",
            extra={"job_id": job_id, "total": total, "returned": len(page_apps)},
        )
        return page_apps, total
