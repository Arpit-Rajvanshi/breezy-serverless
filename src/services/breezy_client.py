"""
BreezyClient — the single integration point with Breezy HR REST API v3.

This client encapsulates:
  - Base URL and authentication (via API Key and Company ID)
  - HTTP request execution with timeout
  - Retry logic (via @with_retry decorator)
  - Error normalization to BreezyAPIError
  - Pagination across multi-page endpoints
"""

import httpx
from typing import Any

from src.config.settings import get_settings
from src.utils.logger import get_logger
from src.utils.error_handler import BreezyAPIError
from src.utils.retry import with_retry

logger = get_logger(__name__)

# Production-grade timeout settings
_TIMEOUT = httpx.Timeout(connect=5.0, read=20.0, write=10.0, pool=5.0)


class BreezyClient:
    """Low-level HTTP client for Breezy HR API."""

    def __init__(self):
        settings = get_settings()
        self._base_url = settings.breezy_base_url
        self._company_id = settings.breezy_company_id
        self._api_key = settings.breezy_api_key

    def _get_headers(self) -> dict:
        return {
            "Authorization": self._api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _build_url(self, path: str) -> str:
        """Construct a full URL scoped to the company."""
        # Ensure path doesn't have leading slash to prevent double slashes
        clean_path = path.lstrip("/")
        return f"{self._base_url}/company/{self._company_id}/{clean_path}"

    @with_retry
    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json_data: dict | None = None,
    ) -> Any:
        """
        Execute an HTTP request and return the parsed JSON body.
        
        Raises BreezyAPIError for non-2xx responses.
        """
        url = self._build_url(path)
        logger.debug("Breezy API request", extra={"method": method, "url": url, "params": params})

        with httpx.Client(timeout=_TIMEOUT) as client:
            response = client.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                params=params,
                json=json_data,
            )

        logger.debug(
            "Breezy API response",
            extra={"status_code": response.status_code, "url": url},
        )

        try:
            body = response.json()
        except ValueError:
            body = {"message": response.text}

        if not response.is_success:
            # Try to extract a meaningful error message from Breezy's response
            error_msg = body.get("message") or body.get("error") or "Unknown Breezy API Error"
            raise BreezyAPIError(
                status_code=response.status_code,
                message=str(error_msg),
                raw_response=body,
            )

        return body

    def _paginate(self, path: str, params: dict | None = None) -> list[dict]:
        """
        Fetch all pages for a paginated Breezy endpoint.
        Uses the `url` from the `link` header or simple page incrementing if reliable.
        Breezy HR returns data as a plain list when paginating.
        """
        params = dict(params) if params else {}
        all_items: list[dict] = []
        
        # Breezy HR uses 1-indexed pages
        page = 1
        page_size = 100  # Max supported by most modern ATS

        while True:
            params["page"] = page
            params["pageSize"] = page_size

            items = self._request("GET", path, params=params)

            if not isinstance(items, list):
                logger.warning(f"Expected list response for {path}, got {type(items)}")
                break

            if not items:
                break  # Reached the end

            all_items.extend(items)

            if len(items) < page_size:
                break  # Last page

            page += 1

        return all_items

    # -------------------------------------------------------------------------
    # Domain-specific methods
    # -------------------------------------------------------------------------

    def list_positions(self, state: str | None = None) -> list[dict]:
        """
        Fetch all positions (jobs) from Breezy.
        
        Args:
            state: Optional filter (e.g., "published", "draft", "closed")
        """
        logger.info("Fetching positions from Breezy HR", extra={"state": state})
        params = {"state": state} if state else {}
        return self._paginate("positions", params=params)

    def create_candidate(self, position_id: str, payload: dict) -> dict:
        """
        Create a new candidate in a specific position pipeline.
        POST /company/{company_id}/position/{position_id}/candidates
        """
        logger.info(
            "Creating candidate in Breezy HR", 
            extra={"position_id": position_id, "email": payload.get("email_address")}
        )
        path = f"position/{position_id}/candidates"
        return self._request("POST", path, json_data=payload)

    def list_applications(self, position_id: str) -> list[dict]:
        """
        Fetch all candidates (applications) in a given position pipeline.
        GET /company/{company_id}/position/{position_id}/candidates
        """
        logger.info(
            "Fetching applications from Breezy HR", 
            extra={"position_id": position_id}
        )
        path = f"position/{position_id}/candidates"
        return self._paginate(path)
