"""GraphQL client for Unraid API communication.

This module provides the HTTP client interface for making GraphQL requests
to the Unraid API with proper timeout handling and error management.
"""

import asyncio
import json
import re
from typing import Any

import httpx

from ..config.logging import logger
from ..config.settings import TIMEOUT_CONFIG, UNRAID_API_KEY, UNRAID_API_URL, UNRAID_VERIFY_SSL
from ..core.constants import (
    HTTP_DOCKER_BATCH_UPDATE_READ_TIMEOUT_S,
    HTTP_DOCKER_UPDATE_READ_TIMEOUT_S,
    HTTP_MAX_CONNECTIONS,
    HTTP_MAX_KEEPALIVE_CONNECTIONS,
    QUERY_TRUNCATION_LENGTH,
    SENSITIVE_VARIABLE_KEYS,
)
from ..core.exceptions import ToolError
from ..core.utils import truncate_for_error

# HTTP timeout configuration
DEFAULT_TIMEOUT = httpx.Timeout(10.0, read=30.0, connect=5.0)
DISK_TIMEOUT = httpx.Timeout(10.0, read=TIMEOUT_CONFIG["disk_operations"], connect=5.0)
DOCKER_UPDATE_TIMEOUT = httpx.Timeout(10.0, read=HTTP_DOCKER_UPDATE_READ_TIMEOUT_S, connect=5.0)
DOCKER_BATCH_UPDATE_TIMEOUT = httpx.Timeout(
    10.0, read=HTTP_DOCKER_BATCH_UPDATE_READ_TIMEOUT_S, connect=5.0
)

# Module-level HTTP client singleton for connection pooling
_http_client: httpx.AsyncClient | None = None
_http_client_lock = asyncio.Lock()


async def _get_http_client() -> httpx.AsyncClient:
    """Get or create the singleton HTTP client with connection pooling."""
    global _http_client
    if _http_client is None or _http_client.is_closed:
        async with _http_client_lock:
            # Double-check after acquiring lock
            if _http_client is None or _http_client.is_closed:
                _http_client = httpx.AsyncClient(
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": UNRAID_API_KEY or "",
                        "User-Agent": "UnraidMCPServer/0.1.0",
                    },
                    verify=UNRAID_VERIFY_SSL,
                    limits=httpx.Limits(
                        max_connections=HTTP_MAX_CONNECTIONS,
                        max_keepalive_connections=HTTP_MAX_KEEPALIVE_CONNECTIONS,
                    ),
                )
    return _http_client


async def close_http_client() -> None:
    """Close the HTTP client and release connections."""
    global _http_client
    if _http_client is not None and not _http_client.is_closed:
        await _http_client.aclose()
        _http_client = None


def sanitize_query(query: str) -> str:
    """Remove potential secrets from query string before logging.

    Primary secret protection is performed by variables masking. This function
    serves as defense-in-depth for type naming and definitions.
    """
    # Remove variable definitions and replace with placeholders
    # This is a basic sanitization; for production, consider a proper GraphQL parser
    # Remove variable definitions like $var: Type
    query = re.sub(r"\$[a-zA-Z_][a-zA-Z0-9_]*\s*:\s*[^,)]+", "$VARIABLE", query)
    # Truncate to safe length
    return query[:QUERY_TRUNCATION_LENGTH]


def is_idempotent_error(error_message: str, operation: str) -> bool:
    """Check if a GraphQL error represents an idempotent operation that should be treated as success.

    Args:
        error_message: The error message from GraphQL API
        operation: The operation being performed (e.g., 'start', 'stop')

    Returns:
        True if this is an idempotent error that should be treated as success
    """
    error_lower = error_message.lower()

    # Docker container operation patterns
    if operation == "start":
        return (
            "already started" in error_lower
            or "container already running" in error_lower
            or "http code 304" in error_lower
        )
    elif operation == "stop":
        return (
            "already stopped" in error_lower
            or "container already stopped" in error_lower
            or "container not running" in error_lower
            or "http code 304" in error_lower
        )
    elif operation == "pause":
        return "already paused" in error_lower or "http code 304" in error_lower
    elif operation == "unpause":
        return "not paused" in error_lower or "http code 304" in error_lower

    return False


async def make_graphql_request(
    query: str,
    variables: dict[str, Any] | None = None,
    custom_timeout: httpx.Timeout | None = None,
    operation_context: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Make GraphQL requests to the Unraid API.

    Args:
        query: GraphQL query string
        variables: Optional query variables
        custom_timeout: Optional custom timeout configuration
        operation_context: Optional context for operation-specific error handling
                          Should contain 'operation' key (e.g., 'start', 'stop')

    Returns:
        Dict containing the GraphQL response data

    Raises:
        ToolError: For HTTP errors, network errors, or non-idempotent GraphQL errors
    """
    if not UNRAID_API_URL:
        raise ToolError("UNRAID_API_URL not configured")

    if not UNRAID_API_KEY:
        raise ToolError("UNRAID_API_KEY not configured")

    payload: dict[str, Any] = {"query": query}
    if variables:
        payload["variables"] = variables

    logger.debug(f"Making GraphQL request to {UNRAID_API_URL}:")
    sanitized = sanitize_query(query)
    logger.debug(f"Query: {sanitized}")
    if variables:
        # Mask variables to prevent logging secrets
        def _redact_recursive(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {
                    k: (
                        "[REDACTED]"
                        if any(s in k.lower() for s in SENSITIVE_VARIABLE_KEYS)
                        else _redact_recursive(v)
                    )
                    for k, v in obj.items()
                }
            elif isinstance(obj, list):
                return [_redact_recursive(i) for i in obj]
            elif isinstance(obj, tuple):
                return tuple(_redact_recursive(i) for i in obj)
            return obj

        masked = _redact_recursive(variables)
        logger.debug(f"Variables: {masked}")

    current_timeout = custom_timeout if custom_timeout is not None else DEFAULT_TIMEOUT
    client = await _get_http_client()

    try:
        response = await client.post(UNRAID_API_URL, json=payload, timeout=current_timeout)
        response.raise_for_status()  # Raise an exception for HTTP error codes 4xx/5xx

        response_data = response.json()
        if "errors" in response_data and response_data["errors"]:
            error_details = "; ".join(
                [err.get("message", str(err)) for err in response_data["errors"]]
            )

            # Check if this is an idempotent error that should be treated as success
            if operation_context and operation_context.get("operation"):
                operation = operation_context["operation"]
                if is_idempotent_error(error_details, operation):
                    logger.warning(
                        f"Idempotent operation '{operation}' - treating as success: {error_details}"
                    )
                    # Return a success response with the current state information
                    return {
                        "idempotent_success": True,
                        "operation": operation,
                        "message": error_details,
                        "original_errors": response_data["errors"],
                    }

            logger.error(f"GraphQL API returned errors: {response_data['errors']}")
            # Use ToolError for GraphQL errors to provide better feedback to LLM
            raise ToolError(f"GraphQL API error: {error_details}")

        logger.debug("GraphQL request successful.")
        data = response_data.get("data", {})
        return data if isinstance(data, dict) else {}  # Ensure we return dict

    except httpx.HTTPStatusError as e:
        truncated = truncate_for_error(e.response.text)
        logger.error(f"HTTP error occurred: {e.response.status_code} - {truncated}")
        raise ToolError(f"Unraid API returned HTTP {e.response.status_code}") from e
    except httpx.RequestError as e:
        logger.error(f"Request error occurred: {e}")
        raise ToolError(f"Network connection error: {str(e)}") from e
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON response: {e}")
        raise ToolError(f"Invalid JSON response from Unraid API: {str(e)}") from e


def get_timeout_for_operation(operation_type: str = "default") -> httpx.Timeout:
    """Get appropriate timeout configuration for different operation types.

    Args:
        operation_type: Type of operation ('default', 'disk_operations')

    Returns:
        httpx.Timeout configuration appropriate for the operation
    """
    if operation_type == "disk_operations":
        return DISK_TIMEOUT
    elif operation_type == "docker_update":
        return DOCKER_UPDATE_TIMEOUT
    elif operation_type == "docker_batch_update":
        return DOCKER_BATCH_UPDATE_TIMEOUT
    else:
        return DEFAULT_TIMEOUT
