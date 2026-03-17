"""
Centralized HTTP response helpers for API Gateway Lambda proxy integration.
All responses include CORS headers and Content-Type: application/json.
"""

import json
from typing import Any


_CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
}


def _build(status_code: int, body: Any) -> dict:
    """Internal helper to build a Lambda proxy response dict."""
    return {
        "statusCode": status_code,
        "headers": _CORS_HEADERS,
        "body": json.dumps(body, default=str),
    }


def ok(data: Any) -> dict:
    """200 OK"""
    return _build(200, data)


def created(data: Any) -> dict:
    """201 Created"""
    return _build(201, data)


def bad_request(message: str, details: Any = None) -> dict:
    """400 Bad Request"""
    body = {"error": {"code": "BAD_REQUEST", "message": message}}
    if details:
        body["error"]["details"] = details
    return _build(400, body)


def not_found(message: str = "Resource not found.") -> dict:
    """404 Not Found"""
    return _build(404, {"error": {"code": "NOT_FOUND", "message": message}})


def unprocessable(message: str, details: Any = None) -> dict:
    """422 Unprocessable Entity – validation errors"""
    body = {"error": {"code": "VALIDATION_ERROR", "message": message}}
    if details:
        body["error"]["details"] = details
    return _build(422, body)


def internal_error(message: str = "An unexpected error occurred.") -> dict:
    """500 Internal Server Error"""
    return _build(500, {"error": {"code": "INTERNAL_ERROR", "message": message}})


def gateway_error(message: str) -> dict:
    """502 Bad Gateway – upstream (Breezy) error"""
    return _build(502, {"error": {"code": "UPSTREAM_ERROR", "message": message}})
