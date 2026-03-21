"""WebSocket subscription manager for real-time Unraid data.

This module manages GraphQL subscriptions over WebSocket connections,
providing real-time data streaming for MCP resources with comprehensive
error handling, reconnection logic, and authentication.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any
from urllib.parse import urlparse, urlunparse

import websockets
from graphql import OperationType
from graphql import parse as gql_parse
from graphql.error import GraphQLSyntaxError
from graphql.language.ast import OperationDefinitionNode
from websockets.legacy.protocol import Subprotocol

from ..config.logging import logger
from ..config.settings import UNRAID_API_KEY, UNRAID_API_URL
from ..core.constants import (
    WS_ACK_TIMEOUT_S,
    WS_CLOSE_TIMEOUT_S,
    WS_INITIAL_RETRY_DELAY_S,
    WS_MAX_RETRY_DELAY_S,
    WS_PING_INTERVAL_S,
    WS_PING_TIMEOUT_S,
    WS_RETRY_BACKOFF_FACTOR,
)
from ..core.exceptions import ValidationError
from ..core.types import SubscriptionData
from .configs import SUBSCRIPTION_CONFIGS


def _build_ws_auth_payload() -> dict[str, Any]:
    """Build WebSocket authentication payload for GraphQL-WS connection_init."""
    return {
        "Authorization": f"Bearer {UNRAID_API_KEY}",
        "x-api-key": UNRAID_API_KEY,
    }


def _build_ws_url(api_url: str) -> str:
    """Convert an HTTP(S) API URL to a WebSocket URL ending in /graphql."""
    parsed = urlparse(api_url)
    if not parsed.hostname:
        raise ValueError(f"URL has no host: {api_url}")
    if parsed.username or parsed.password:
        raise ValueError("URL must not contain userinfo (credentials)")
    if parsed.fragment:
        raise ValueError("URL must not contain a fragment")
    scheme_map = {"https": "wss", "http": "ws"}
    ws_scheme = scheme_map.get(parsed.scheme, "")
    if not ws_scheme:
        raise ValueError(f"Unsupported URL scheme '{parsed.scheme}': expected http or https")
    path = parsed.path.rstrip("/")
    if not path.endswith("/graphql"):
        path = path + "/graphql"
    return urlunparse((ws_scheme, parsed.netloc, path, "", parsed.query, ""))


def _validate_subscription_query(query: str) -> None:
    """Validate that a GraphQL query contains only subscription operations."""
    try:
        document = gql_parse(query)
    except GraphQLSyntaxError as e:
        raise ValidationError(f"Invalid GraphQL syntax: {e}") from e

    operations = [
        defn for defn in document.definitions if isinstance(defn, OperationDefinitionNode)
    ]
    if not operations:
        raise ValidationError("Query contains no operation definitions")

    for op in operations:
        if op.operation != OperationType.SUBSCRIPTION:
            raise ValidationError(
                f"Only subscription operations are allowed, got {op.operation.value}"
            )


class SubscriptionManager:
    """Manages GraphQL subscriptions and converts them to MCP resources."""

    def __init__(self) -> None:
        self.active_subscriptions: dict[str, asyncio.Task[None]] = {}
        self.resource_data: dict[str, SubscriptionData] = {}
        self.resource_data_lock = asyncio.Lock()
        self.websocket: Any = None
        self.subscription_lock = asyncio.Lock()

        # Configuration
        self.auto_start_enabled = (
            os.getenv("UNRAID_AUTO_START_SUBSCRIPTIONS", "true").lower() == "true"
        )
        self.reconnect_attempts: dict[str, int] = {}
        self.max_reconnect_attempts = int(os.getenv("UNRAID_MAX_RECONNECT_ATTEMPTS", "10"))
        self.connection_states: dict[str, str] = {}  # Track connection state per subscription
        self.last_error: dict[str, str] = {}  # Track last error per subscription

        # Shallow copy so runtime mutations don't affect the module constant
        self.subscription_configs = dict(SUBSCRIPTION_CONFIGS)

        logger.info(
            f"[SUBSCRIPTION_MANAGER] Initialized with auto_start={self.auto_start_enabled}, max_reconnects={self.max_reconnect_attempts}"
        )
        logger.debug(
            f"[SUBSCRIPTION_MANAGER] Available subscriptions: {list(self.subscription_configs.keys())}"
        )

    async def auto_start_all_subscriptions(self) -> None:
        """Auto-start all subscriptions marked for auto-start."""
        if not self.auto_start_enabled:
            logger.info("[SUBSCRIPTION_MANAGER] Auto-start disabled")
            return

        logger.info("[SUBSCRIPTION_MANAGER] Starting auto-start process...")
        auto_start_count = 0

        for subscription_name, config in self.subscription_configs.items():
            if config.get("auto_start", False):
                try:
                    logger.info(
                        f"[SUBSCRIPTION_MANAGER] Auto-starting subscription: {subscription_name}"
                    )
                    await self.start_subscription(subscription_name, str(config["query"]))
                    auto_start_count += 1
                except Exception as e:
                    logger.error(
                        f"[SUBSCRIPTION_MANAGER] Failed to auto-start {subscription_name}: {e}"
                    )
                    self.last_error[subscription_name] = str(e)

        logger.info(
            f"[SUBSCRIPTION_MANAGER] Auto-start completed. Started {auto_start_count} subscriptions"
        )

    async def start_subscription(
        self, subscription_name: str, query: str, variables: dict[str, Any] | None = None
    ) -> None:
        """Start a GraphQL subscription and maintain it as a resource."""
        logger.info(f"[SUBSCRIPTION:{subscription_name}] Starting subscription...")

        if subscription_name in self.active_subscriptions:
            logger.warning(
                f"[SUBSCRIPTION:{subscription_name}] Subscription already active, skipping"
            )
            return

        _validate_subscription_query(query)

        # Reset connection tracking
        self.reconnect_attempts[subscription_name] = 0
        self.connection_states[subscription_name] = "starting"

        async with self.subscription_lock:
            try:
                task = asyncio.create_task(
                    self._subscription_loop(subscription_name, query, variables or {})
                )
                self.active_subscriptions[subscription_name] = task
                logger.info(
                    f"[SUBSCRIPTION:{subscription_name}] Subscription task created and started"
                )
                self.connection_states[subscription_name] = "active"
            except Exception as e:
                logger.error(
                    f"[SUBSCRIPTION:{subscription_name}] Failed to start subscription task: {e}"
                )
                self.connection_states[subscription_name] = "failed"
                self.last_error[subscription_name] = str(e)
                raise

    async def stop_subscription(self, subscription_name: str) -> None:
        """Stop a specific subscription."""
        logger.info(f"[SUBSCRIPTION:{subscription_name}] Stopping subscription...")

        async with self.subscription_lock:
            if subscription_name in self.active_subscriptions:
                task = self.active_subscriptions[subscription_name]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.debug(f"[SUBSCRIPTION:{subscription_name}] Task cancelled successfully")
                del self.active_subscriptions[subscription_name]
                self.connection_states[subscription_name] = "stopped"
                logger.info(f"[SUBSCRIPTION:{subscription_name}] Subscription stopped")
            else:
                logger.warning(f"[SUBSCRIPTION:{subscription_name}] No active subscription to stop")

    async def stop_all_subscriptions(self) -> None:
        """Cancel all active subscription tasks for graceful shutdown."""
        async with self.subscription_lock:
            for name, task in list(self.active_subscriptions.items()):
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                    logger.info(f"[SHUTDOWN] Cancelled subscription: {name}")
            self.active_subscriptions.clear()

    async def _send_subscription_start(
        self,
        websocket: Any,
        subscription_name: str,
        query: str,
        variables: dict[str, Any] | None,
        selected_proto: str,
    ) -> None:
        """Build and send the GraphQL subscription start message.

        Args:
            websocket: Active WebSocket connection
            subscription_name: Name of the subscription
            query: GraphQL subscription query
            variables: Query variables
            selected_proto: Selected WebSocket subprotocol
        """
        logger.debug(f"[SUBSCRIPTION:{subscription_name}] Starting GraphQL subscription...")
        start_type = "subscribe" if selected_proto == "graphql-transport-ws" else "start"
        subscription_message = {
            "id": subscription_name,
            "type": start_type,
            "payload": {"query": query, "variables": variables},
        }

        logger.debug(f"[SUBSCRIPTION:{subscription_name}] Subscription message type: {start_type}")
        logger.debug(f"[SUBSCRIPTION:{subscription_name}] Query: {query[:100]}...")
        logger.debug(f"[SUBSCRIPTION:{subscription_name}] Variables: {variables}")

        await websocket.send(json.dumps(subscription_message))
        logger.info(f"[SUBSCRIPTION:{subscription_name}] Subscription started successfully")
        self.connection_states[subscription_name] = "subscribed"

    async def _process_ws_message(
        self, subscription_name: str, message: Any, selected_proto: str
    ) -> bool:
        """Handle a single WebSocket message from the subscription stream.

        Args:
            subscription_name: Name of the subscription
            message: Raw WebSocket message
            selected_proto: Selected WebSocket subprotocol

        Returns:
            False if the subscription should stop (server sent 'complete'), True otherwise
        """
        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")

            logger.debug(f"[DATA:{subscription_name}] Message: {message_type}")

            # Handle different message types
            expected_data_type = "next" if selected_proto == "graphql-transport-ws" else "data"

            if data.get("type") == expected_data_type and data.get("id") == subscription_name:
                payload = data.get("payload", {})

                if payload.get("data"):
                    logger.info(f"[DATA:{subscription_name}] Received subscription data update")
                    async with self.resource_data_lock:
                        self.resource_data[subscription_name] = SubscriptionData(
                            data=payload["data"],
                            last_updated=datetime.now(),
                            subscription_type=subscription_name,
                        )
                    logger.debug(
                        f"[RESOURCE:{subscription_name}] Resource data updated successfully"
                    )
                elif payload.get("errors"):
                    logger.error(
                        f"[DATA:{subscription_name}] GraphQL errors in response: {payload['errors']}"
                    )
                    self.last_error[subscription_name] = f"GraphQL errors: {payload['errors']}"
                else:
                    logger.warning(
                        f"[DATA:{subscription_name}] Empty or invalid data payload: {payload}"
                    )

            elif data.get("type") == "error":
                error_payload = data.get("payload", {})
                logger.error(
                    f"[SUBSCRIPTION:{subscription_name}] Subscription error: {error_payload}"
                )
                self.last_error[subscription_name] = f"Subscription error: {error_payload}"
                self.connection_states[subscription_name] = "error"

            elif data.get("type") == "complete":
                logger.info(f"[SUBSCRIPTION:{subscription_name}] Subscription completed by server")
                self.connection_states[subscription_name] = "completed"
                return False

            elif data.get("type") in ["ka", "pong"]:
                logger.debug(f"[PROTOCOL:{subscription_name}] Keepalive message: {message_type}")

            else:
                logger.debug(
                    f"[PROTOCOL:{subscription_name}] Unhandled message type: {message_type}"
                )

        except json.JSONDecodeError as e:
            msg_preview = (
                message[:200]
                if isinstance(message, str)
                else message[:200].decode("utf-8", errors="replace")
            )
            logger.error(
                f"[PROTOCOL:{subscription_name}] Failed to decode message: {msg_preview}..."
            )
            logger.error(f"[PROTOCOL:{subscription_name}] JSON decode error: {e}")
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"[DATA:{subscription_name}] Error processing message: {e}")
            msg_preview = (
                message[:200]
                if isinstance(message, str)
                else message[:200].decode("utf-8", errors="replace")
            )
            logger.debug(f"[DATA:{subscription_name}] Raw message: {msg_preview}...")

        return True

    def _handle_ws_error(self, subscription_name: str, error: Exception) -> bool:
        """Classify and log a WebSocket error, updating connection state.

        Args:
            subscription_name: Name of the subscription
            error: The exception that occurred

        Returns:
            True if the subscription should retry, False if it should stop
        """
        if isinstance(error, asyncio.TimeoutError):
            error_msg = "Connection or authentication timeout"
            logger.error(f"[WEBSOCKET:{subscription_name}] {error_msg}")
            self.last_error[subscription_name] = error_msg
            self.connection_states[subscription_name] = "timeout"
            return True

        if isinstance(error, websockets.exceptions.ConnectionClosed):
            error_msg = f"WebSocket connection closed: {error}"
            logger.warning(f"[WEBSOCKET:{subscription_name}] {error_msg}")
            self.last_error[subscription_name] = error_msg
            self.connection_states[subscription_name] = "disconnected"
            return True

        if isinstance(error, websockets.exceptions.InvalidURI):
            error_msg = f"Invalid WebSocket URI: {error}"
            logger.error(f"[WEBSOCKET:{subscription_name}] {error_msg}")
            self.last_error[subscription_name] = error_msg
            self.connection_states[subscription_name] = "invalid_uri"
            return False  # Don't retry on invalid URI

        # Generic/unexpected error
        error_msg = f"Unexpected error: {error}"
        logger.error(f"[WEBSOCKET:{subscription_name}] {error_msg}")
        self.last_error[subscription_name] = error_msg
        self.connection_states[subscription_name] = "error"
        return True

    async def _subscription_loop(
        self, subscription_name: str, query: str, variables: dict[str, Any] | None
    ) -> None:
        """Main loop for maintaining a GraphQL subscription with comprehensive logging."""
        retry_delay: int | float = WS_INITIAL_RETRY_DELAY_S
        max_retry_delay = WS_MAX_RETRY_DELAY_S

        while True:
            attempt = self.reconnect_attempts.get(subscription_name, 0) + 1
            self.reconnect_attempts[subscription_name] = attempt

            logger.info(
                f"[WEBSOCKET:{subscription_name}] Connection attempt #{attempt} (max: {self.max_reconnect_attempts})"
            )

            if attempt > self.max_reconnect_attempts:
                logger.error(
                    f"[WEBSOCKET:{subscription_name}] Max reconnection attempts ({self.max_reconnect_attempts}) exceeded, stopping"
                )
                self.connection_states[subscription_name] = "max_retries_exceeded"
                break

            try:
                # Build WebSocket URL with detailed logging
                if not UNRAID_API_URL:
                    raise ValueError("UNRAID_API_URL is not configured")

                ws_url = _build_ws_url(UNRAID_API_URL)

                logger.debug(f"[WEBSOCKET:{subscription_name}] Connecting to: {ws_url}")
                logger.debug(
                    f"[WEBSOCKET:{subscription_name}] API Key present: {'Yes' if UNRAID_API_KEY else 'No'}"
                )

                # Connection with timeout
                connect_timeout = WS_ACK_TIMEOUT_S
                logger.debug(
                    f"[WEBSOCKET:{subscription_name}] Connection timeout: {connect_timeout}s"
                )

                async with websockets.connect(
                    ws_url,
                    subprotocols=[Subprotocol("graphql-transport-ws"), Subprotocol("graphql-ws")],
                    ping_interval=WS_PING_INTERVAL_S,
                    ping_timeout=WS_PING_TIMEOUT_S,
                    close_timeout=WS_CLOSE_TIMEOUT_S,
                ) as websocket:

                    selected_proto = websocket.subprotocol or "none"
                    logger.info(
                        f"[WEBSOCKET:{subscription_name}] Connected! Protocol: {selected_proto}"
                    )
                    self.connection_states[subscription_name] = "connected"

                    # Reset retry count on successful connection
                    self.reconnect_attempts[subscription_name] = 0
                    retry_delay = WS_INITIAL_RETRY_DELAY_S

                    # Initialize GraphQL-WS protocol
                    logger.debug(
                        f"[PROTOCOL:{subscription_name}] Initializing GraphQL-WS protocol..."
                    )
                    init_type = "connection_init"
                    init_payload: dict[str, Any] = {"type": init_type}

                    if UNRAID_API_KEY:
                        logger.debug(f"[AUTH:{subscription_name}] Adding authentication payload")
                        init_payload["payload"] = _build_ws_auth_payload()
                    else:
                        logger.warning(
                            f"[AUTH:{subscription_name}] No API key available for authentication"
                        )

                    logger.debug(f"[PROTOCOL:{subscription_name}] Sending connection_init message")
                    await websocket.send(json.dumps(init_payload))

                    # Wait for connection acknowledgment
                    logger.debug(f"[PROTOCOL:{subscription_name}] Waiting for connection_ack...")
                    init_raw = await asyncio.wait_for(websocket.recv(), timeout=WS_ACK_TIMEOUT_S)

                    try:
                        init_data = json.loads(init_raw)
                        logger.debug(
                            f"[PROTOCOL:{subscription_name}] Received init response: {init_data.get('type')}"
                        )
                    except json.JSONDecodeError as e:
                        init_preview = (
                            init_raw[:200]
                            if isinstance(init_raw, str)
                            else init_raw[:200].decode("utf-8", errors="replace")
                        )
                        logger.error(
                            f"[PROTOCOL:{subscription_name}] Failed to decode init response: {init_preview}..."
                        )
                        self.last_error[subscription_name] = f"Invalid JSON in init response: {e}"
                        break

                    # Handle connection acknowledgment
                    if init_data.get("type") == "connection_ack":
                        logger.info(
                            f"[PROTOCOL:{subscription_name}] Connection acknowledged successfully"
                        )
                        self.connection_states[subscription_name] = "authenticated"
                    elif init_data.get("type") == "connection_error":
                        error_payload = init_data.get("payload", {})
                        logger.error(
                            f"[AUTH:{subscription_name}] Authentication failed: {error_payload}"
                        )
                        self.last_error[subscription_name] = (
                            f"Authentication error: {error_payload}"
                        )
                        self.connection_states[subscription_name] = "auth_failed"
                        break
                    else:
                        logger.warning(
                            f"[PROTOCOL:{subscription_name}] Unexpected init response: {init_data}"
                        )
                        # Continue anyway - some servers send other messages first

                    # Start the subscription
                    await self._send_subscription_start(
                        websocket, subscription_name, query, variables, selected_proto
                    )

                    # Listen for subscription data
                    async for message in websocket:
                        should_continue = await self._process_ws_message(
                            subscription_name, message, selected_proto
                        )
                        # Handle ping/pong — _process_ws_message can't send on websocket
                        try:
                            data = json.loads(message)
                            if data.get("type") == "ping":
                                await websocket.send(json.dumps({"type": "pong"}))
                        except (json.JSONDecodeError, TypeError):
                            pass  # Parse errors already logged in _process_ws_message
                        if not should_continue:
                            break

            except Exception as e:
                should_retry = self._handle_ws_error(subscription_name, e)
                if not should_retry:
                    break

            # Calculate backoff delay
            retry_delay = min(retry_delay * WS_RETRY_BACKOFF_FACTOR, max_retry_delay)
            logger.info(
                f"[WEBSOCKET:{subscription_name}] Reconnecting in {retry_delay:.1f} seconds..."
            )
            self.connection_states[subscription_name] = "reconnecting"
            await asyncio.sleep(retry_delay)

    async def get_resource_data(self, resource_name: str) -> dict[str, Any] | None:
        """Get current resource data with enhanced logging."""
        logger.debug(f"[RESOURCE:{resource_name}] Resource data requested")

        async with self.resource_data_lock:
            if resource_name in self.resource_data:
                data = self.resource_data[resource_name]
                age_seconds = (datetime.now() - data.last_updated).total_seconds()
                logger.debug(f"[RESOURCE:{resource_name}] Data found, age: {age_seconds:.1f}s")
                return data.data
            else:
                logger.debug(f"[RESOURCE:{resource_name}] No data available")
                return None

    def list_active_subscriptions(self) -> list[str]:
        """List all active subscriptions."""
        active = list(self.active_subscriptions.keys())
        logger.debug(f"[SUBSCRIPTION_MANAGER] Active subscriptions: {active}")
        return active

    async def get_subscription_status(self) -> dict[str, dict[str, Any]]:
        """Get detailed status of all subscriptions for diagnostics."""
        status = {}

        async with self.resource_data_lock:
            for sub_name, config in self.subscription_configs.items():
                sub_status = {
                    "config": {
                        "resource": config["resource"],
                        "description": config["description"],
                        "auto_start": config.get("auto_start", False),
                    },
                    "runtime": {
                        "active": sub_name in self.active_subscriptions,
                        "connection_state": self.connection_states.get(sub_name, "not_started"),
                        "reconnect_attempts": self.reconnect_attempts.get(sub_name, 0),
                        "last_error": self.last_error.get(sub_name, None),
                    },
                }

                # Add data info if available
                if sub_name in self.resource_data:
                    data_info = self.resource_data[sub_name]
                    age_seconds = (datetime.now() - data_info.last_updated).total_seconds()
                    sub_status["data"] = {
                        "available": True,
                        "last_updated": data_info.last_updated.isoformat(),
                        "age_seconds": age_seconds,
                    }
                else:
                    sub_status["data"] = {"available": False}

                status[sub_name] = sub_status

        logger.debug(f"[SUBSCRIPTION_MANAGER] Generated status for {len(status)} subscriptions")
        return status


# Global subscription manager instance
subscription_manager = SubscriptionManager()
