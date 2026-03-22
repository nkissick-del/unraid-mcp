"""Shared data types for Unraid MCP Server."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class SubscriptionData:
    """Container for subscription data with metadata."""

    data: dict[str, Any]
    last_updated: datetime
    subscription_type: str
