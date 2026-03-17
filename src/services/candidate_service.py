"""
Candidate service — business logic for candidate creation workflow.

Workflow:
  1. Build Breezy-format payload
  2. POST to position-scoped /candidates endpoint (create + attach in one call)
  3. Map response to standardized CandidateCreateResponse
"""

from src.services.breezy_client import BreezyClient
from src.models.candidate import CandidateCreateRequest, CandidateCreateResponse, map_breezy_candidate
from src.utils.logger import get_logger
from src.utils.error_handler import BreezyAPIError, NotFoundError

logger = get_logger(__name__)


class CandidateService:
    """Encapsulates candidate creation and attachment logic."""

    def __init__(self, client: BreezyClient | None = None):
        self._client = client or BreezyClient()

    def create_and_attach(self, request: CandidateCreateRequest) -> CandidateCreateResponse:
        """
        Create a new candidate in Breezy HR and attach them to the specified job.

        The Breezy HR position-scoped candidate endpoint handles both
        creation and pipeline attachment in a single API call.

        Args:
            request: Validated CandidateCreateRequest from the handler.

        Returns:
            CandidateCreateResponse with standardized fields.

        Raises:
            BreezyAPIError: If Breezy returns an error response.
            NotFoundError: If the position_id does not exist (404 from Breezy).
        """
        logger.info(
            "Creating candidate",
            extra={"email": request.email, "job_id": request.job_id},
        )

        # Build Breezy HR candidate payload
        breezy_payload: dict = {
            "name": request.name,
            "email_address": request.email,
        }
        if request.phone:
            breezy_payload["phone_number"] = request.phone
        if request.resume_url:
            breezy_payload["resume_url"] = request.resume_url

        try:
            raw_candidate = self._client.create_candidate(
                position_id=request.job_id,
                payload=breezy_payload,
            )
        except BreezyAPIError as exc:
            if exc.status_code == 404:
                raise NotFoundError(f"Job '{request.job_id}' not found in Breezy HR.") from exc
            raise

        logger.info(
            "Candidate created successfully",
            extra={"candidate_id": raw_candidate.get("_id"), "job_id": request.job_id},
        )

        return map_breezy_candidate(raw_candidate, job_id=request.job_id)
