"""
Centralized configuration management using pydantic-settings with dotenv support.
All environment variables are validated at startup.
"""

import os
from functools import lru_cache
from dotenv import load_dotenv

# Load .env file for local development (no-op in Lambda)
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # Breezy HR API
    breezy_api_key: str
    breezy_company_id: str
    breezy_base_url: str

    # Logging
    log_level: str

    # Application
    stage: str

    def __init__(self):
        self.breezy_api_key = self._require("BREEZY_API_KEY")
        self.breezy_company_id = self._require("BREEZY_COMPANY_ID")
        self.breezy_base_url = os.getenv("BREEZY_BASE_URL", "https://api.breezy.hr/v3").rstrip("/")
        
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.stage = os.getenv("STAGE", "dev")

    @staticmethod
    def _require(key: str) -> str:
        """Read a required env variable or raise a clear error."""
        value = os.getenv(key)
        if not value:
            raise EnvironmentError(
                f"Required environment variable '{key}' is not set. "
                "Please check your .env file or Lambda environment configuration."
            )
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings singleton (safe for Lambda cold-start reuse)."""
    return Settings()
