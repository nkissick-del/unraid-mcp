"""Logging handlers and formatters for Unraid MCP Server.

This module contains custom logging handlers (OverwriteFileHandler),
formatters (JsonFormatter), and filters (RedactingFilter).
"""

import json
import logging
import os
import re
from pathlib import Path

from ..core.constants import LOG_FILE_MAX_BYTES


class OverwriteFileHandler(logging.FileHandler):
    """Custom file handler that overwrites the log file when it reaches max size."""

    _CHECK_INTERVAL = 100

    def __init__(
        self,
        filename: str | Path,
        max_bytes: int = LOG_FILE_MAX_BYTES,
        mode: str = "a",
        encoding: str | None = None,
        delay: bool = False,
    ) -> None:
        """Initialize the handler.

        Args:
            filename: Path to the log file
            max_bytes: Maximum file size in bytes before overwriting (default: 10MB)
            mode: File open mode
            encoding: File encoding
            delay: Whether to delay file opening
        """
        self.max_bytes = max_bytes
        self._emit_count = 0
        super().__init__(filename, mode, encoding, delay)

    def _maybe_reset_file(self) -> None:
        """Check file size and reset if it exceeds the limit."""
        try:
            file_size = os.path.getsize(self.baseFilename)
            if file_size >= self.max_bytes:
                self.close()
                os.remove(self.baseFilename)
                self.stream = self._open()

                reset_record = logging.LogRecord(
                    name="UnraidMCPServer.Logging",
                    level=logging.INFO,
                    pathname="",
                    lineno=0,
                    msg=f"=== LOG FILE RESET ({self.max_bytes // (1024 * 1024)}MB limit reached) ===",
                    args=(),
                    exc_info=None,
                )
                super().emit(reset_record)
        except OSError:
            pass

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record, checking file size every _CHECK_INTERVAL messages."""
        self._emit_count += 1
        if self._emit_count >= self._CHECK_INTERVAL:
            self._emit_count = 0
            self._maybe_reset_file()
        super().emit(record)


class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging in production."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, object] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


class RedactingFilter(logging.Filter):
    """Logging filter that redacts sensitive patterns from log messages."""

    _STATIC_PATTERNS = [
        re.compile(r"Bearer\s+\S+"),
        re.compile(r"[Aa]pi[_-]?[Kk]ey\s*[:=]\s*\S+"),
        re.compile(r"[Xx]-[Aa]pi-[Kk]ey\s*[:=]\s*\S+"),
    ]

    def __init__(self, name: str = "") -> None:
        super().__init__(name)
        self._dynamic_patterns: list[re.Pattern[str]] = []
        self._build_dynamic_patterns()

    def _build_dynamic_patterns(self) -> None:
        """Build patterns from actual configured secrets."""
        from .settings import UNRAID_API_KEY

        if UNRAID_API_KEY and len(UNRAID_API_KEY) >= 8:
            self._dynamic_patterns.append(re.compile(re.escape(UNRAID_API_KEY)))

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = self._redact(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: self._redact(v) if isinstance(v, str) else v for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    self._redact(a) if isinstance(a, str) else a for a in record.args
                )
        return True

    def _redact(self, msg: object) -> object:
        if not isinstance(msg, str):
            return msg
        for pattern in self._STATIC_PATTERNS + self._dynamic_patterns:
            msg = pattern.sub("[REDACTED]", msg)
        return msg
