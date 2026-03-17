"""
Centralized exception types and error handling for Breezy API errors.
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)


class BreezyAPIError(Exception):
    """Exception raised when the Breezy HR API returns a non-2xx status code."""

    def __init__(self, status_code: int, message: str, raw_response: dict | None = None):
        self.status_code = status_code
        self.message = message
        self.raw_response = raw_response or {}
        super().__init__(f"BreezyAPIError [{status_code}]: {message}")


class ValidationError(Exception):
    """Raised for request payload validation failures."""

    def __init__(self, message: str, details: list | None = None):
        self.message = message
        self.details = details or []
        super().__init__(message)


class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str = "Resource not found."):
        self.message = message
        super().__init__(message)


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""

    pass


def handle_breezy_error(exc: BreezyAPIError) -> dict:
    """
    Convert a BreezyAPIError into a normalized error payload dict
    (to be wrapped by a response helper in the handler).
    """
    logger.error(
        "Breezy API error",
        extra={
            "status_code": exc.status_code,
            "message": exc.message,
            "raw": exc.raw_response,
        },
    )
    return {
        "error": {
            "code": "UPSTREAM_ERROR",
            "message": f"Breezy HR API error: {exc.message}",
        }
    }
