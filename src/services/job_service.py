"""
Job service — business logic layer for job-related operations.

Orchestrates calls to BreezyClient and maps results to domain models.
"""

from src.services.breezy_client import BreezyClient
from src.models.job import Job, map_breezy_job
from src.utils.logger import get_logger
from src.utils.pagination import PaginationParams

logger = get_logger(__name__)


class JobService:
    """Encapsulates job retrieval logic."""

    def __init__(self, client: BreezyClient | None = None):
        self._client = client or BreezyClient()

    def get_open_jobs(self, pagination: PaginationParams) -> tuple[list[Job], int]:
        """
        Fetch open jobs from Breezy HR and normalize them.

        Returns:
            (jobs, total) tuple where jobs is the current page slice
            and total is the full count of available jobs.
        """
        logger.info("Fetching open jobs", extra={"page": pagination.page, "page_size": pagination.page_size})

        raw_jobs = self._client.list_positions(state="published")
        jobs: list[Job] = [map_breezy_job(r) for r in raw_jobs]

        total = len(jobs)

        # Apply pagination slice
        start = (pagination.page - 1) * pagination.page_size
        end = start + pagination.page_size
        page_jobs = jobs[start:end]

        logger.info("Jobs fetched", extra={"total": total, "returned": len(page_jobs)})
        return page_jobs, total
