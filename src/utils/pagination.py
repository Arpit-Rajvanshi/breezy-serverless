"""
Pagination utilities for Breezy HR API responses.

Breezy HR uses page+per_page query params and returns results as a list.
This module provides helpers to:
  - Extract pagination params from API Gateway query params
  - Build paginated response envelopes
"""

from dataclasses import dataclass


@dataclass
class PaginationParams:
    page: int = 1
    page_size: int = 25

    def as_breezy_params(self) -> dict:
        """Convert to Breezy HR query param names."""
        return {
            "page": self.page,
            "per_page": min(self.page_size, 100),  # Breezy max is 100
        }


def parse_pagination(query_params: dict | None) -> PaginationParams:
    """
    Extract pagination params from API Gateway query string parameters.

    Supports:
      ?page=2&page_size=10
    """
    params = query_params or {}
    try:
        page = max(1, int(params.get("page", 1)))
    except (ValueError, TypeError):
        page = 1

    try:
        page_size = max(1, min(100, int(params.get("page_size", 25))))
    except (ValueError, TypeError):
        page_size = 25

    return PaginationParams(page=page, page_size=page_size)


def paginate_response(data: list, total: int, pagination: PaginationParams) -> dict:
    """
    Build a standardized paginated response envelope.
    Local slicing is used when the upstream already returns all items.
    """
    start = (pagination.page - 1) * pagination.page_size
    end = start + pagination.page_size
    sliced = data[start:end]

    return {
        "data": sliced,
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
    }
