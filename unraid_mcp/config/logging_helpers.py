"""Rich console logging helpers for Unraid MCP Server.

This module provides development logging helpers with Rich formatting,
including timestamped messages, headers, separators, and level-based styling.
"""

import unicodedata
from datetime import datetime

import pytz
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

# Global Rich console for consistent formatting
console = Console(stderr=True, force_terminal=True)


def get_est_timestamp() -> str:
    """Get current timestamp in EST timezone with YY/MM/DD format."""
    est = pytz.timezone("US/Eastern")
    now = datetime.now(est)
    return now.strftime("%y/%m/%d %H:%M:%S")


def log_header(title: str) -> None:
    """Print a beautiful header panel with Nordic blue styling."""
    panel = Panel(
        Align.center(Text(title, style="bold white")),
        style="#5E81AC",  # Nordic blue
        padding=(0, 2),
        border_style="#81A1C1",  # Light Nordic blue
    )
    console.print(panel)


def log_with_level_and_indent(message: str, level: str = "info", indent: int = 0) -> None:
    """Log a message with specific level and indentation."""
    timestamp = get_est_timestamp()
    indent_str = "  " * indent

    # Enhanced Nordic color scheme with more blues
    level_config = {
        "error": {"color": "#BF616A", "icon": "❌", "style": "bold"},  # Nordic red
        "warning": {"color": "#EBCB8B", "icon": "⚠️", "style": ""},  # Nordic yellow
        "success": {"color": "#A3BE8C", "icon": "✅", "style": "bold"},  # Nordic green
        "info": {"color": "#5E81AC", "icon": "ℹ️", "style": "bold"},  # Nordic blue (bold)
        "status": {"color": "#81A1C1", "icon": "🔍", "style": ""},  # Light Nordic blue
        "debug": {"color": "#4C566A", "icon": "🐛", "style": ""},  # Nordic dark gray
    }

    config = level_config.get(
        level, {"color": "#81A1C1", "icon": "•", "style": ""}
    )  # Default to light Nordic blue

    # Create beautifully formatted text
    text = Text()

    # Timestamp with Nordic blue styling
    text.append(f"[{timestamp}]", style="#81A1C1")  # Light Nordic blue for timestamps
    text.append(" ")

    # Indentation with Nordic blue styling
    if indent > 0:
        text.append(indent_str, style="#81A1C1")

    # Level icon (only for certain levels)
    if level in ["error", "warning", "success"]:
        # Skip icon if message already starts with an emoji/symbol character
        starts_with_emoji = (
            message
            and (unicodedata.category(message[0]) == "So" or ord(message[0]) >= 0x1F300)
        )
        if not starts_with_emoji:
            text.append(f"{config['icon']} ", style=config["color"])

    # Message content
    message_style = f"{config['color']} {config['style']}".strip()
    text.append(message, style=message_style)

    console.print(text)


def log_separator() -> None:
    """Print a beautiful separator line with Nordic blue styling."""
    console.print(Rule(style="#81A1C1"))


# Convenience functions for different log levels
def log_error(message: str, indent: int = 0) -> None:
    log_with_level_and_indent(message, "error", indent)


def log_warning(message: str, indent: int = 0) -> None:
    log_with_level_and_indent(message, "warning", indent)


def log_success(message: str, indent: int = 0) -> None:
    log_with_level_and_indent(message, "success", indent)


def log_info(message: str, indent: int = 0) -> None:
    log_with_level_and_indent(message, "info", indent)


def log_status(message: str, indent: int = 0) -> None:
    log_with_level_and_indent(message, "status", indent)
