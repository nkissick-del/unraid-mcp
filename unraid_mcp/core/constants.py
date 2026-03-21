"""Module-level constants for Unraid MCP Server.

Centralizes magic numbers, strings, and configuration values
that are reused across multiple modules.
"""

# HTTP Timeouts (seconds)
HTTP_DEFAULT_TIMEOUT_S = 10.0
HTTP_DEFAULT_READ_TIMEOUT_S = 30.0
HTTP_DEFAULT_CONNECT_TIMEOUT_S = 5.0
HTTP_DISK_READ_TIMEOUT_S = 90.0

# HTTP connection pool limits
HTTP_MAX_CONNECTIONS = 20
HTTP_MAX_KEEPALIVE_CONNECTIONS = 5

# WebSocket connection parameters
WS_CONNECT_TIMEOUT_S = 10
WS_ACK_TIMEOUT_S = 30
WS_PING_INTERVAL_S = 20
WS_PING_TIMEOUT_S = 10
WS_CLOSE_TIMEOUT_S = 10
WS_INITIAL_RETRY_DELAY_S = 5
WS_MAX_RETRY_DELAY_S = 300
WS_RETRY_BACKOFF_FACTOR = 1.5

# Display / truncation limits
QUERY_TRUNCATION_LENGTH = 500
ERROR_TRUNCATION_LENGTH = 500
NOTIFICATION_MAX_LIMIT = 1000
LOG_TAIL_MAX_LINES = 10000
CONTAINER_DISPLAY_LIMIT = 10

# Docker retry configuration
DOCKER_STATE_MAX_RETRIES = 3
DOCKER_STATE_INITIAL_DELAY_S = 1.0
DOCKER_STATE_BACKOFF_FACTOR = 1.5
DOCKER_OPERATION_SETTLE_DELAY_S = 1.0

# Docker update container timeout (server-side script)
HTTP_DOCKER_UPDATE_READ_TIMEOUT_S = 120.0

# Docker container log limits
DOCKER_LOG_TAIL_DEFAULT = 100
DOCKER_LOG_TAIL_MAX = 10000

# Array operation retry config
ARRAY_OPERATION_SETTLE_DELAY_S = 2.0
ARRAY_STATE_MAX_RETRIES = 5
ARRAY_STATE_INITIAL_DELAY_S = 2.0
ARRAY_STATE_BACKOFF_FACTOR = 1.5

# Parity check actions
PARITY_CHECK_ACTIONS = ["START", "PAUSE", "RESUME", "CANCEL"]

# Parity operation retry config
PARITY_OPERATION_SETTLE_DELAY_S = 3.0
PARITY_STATE_MAX_RETRIES = 3
PARITY_STATE_INITIAL_DELAY_S = 2.0
PARITY_STATE_BACKOFF_FACTOR = 1.5

# Docker batch update timeout (batch can update many containers sequentially)
HTTP_DOCKER_BATCH_UPDATE_READ_TIMEOUT_S = 300.0

# Notification enum values (for validation)
NOTIFICATION_IMPORTANCE_VALUES = ["INFO", "WARNING", "ALERT"]
NOTIFICATION_TYPE_VALUES = ["UNREAD", "ARCHIVE"]

# Container ID pattern
CONTAINER_ID_PATTERN = r"[0-9a-fA-F]{12,64}"

# Prefixed container ID pattern (e.g., sha256:abcdef123456...)
CONTAINER_PREFIXED_ID_PATTERN = r"^[a-z0-9]+:[0-9a-fA-F]{12,64}$"

# RClone remote name validation
RCLONE_REMOTE_NAME_PATTERN = r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$"

# Disk status strings
DISK_STATUS_OK = "DISK_OK"
DISK_STATUS_DISABLED = "DISK_DSBL"
DISK_STATUS_INVALID = "DISK_INVALID"
DISK_STATUS_NOT_PRESENT = "DISK_NP"
DISK_STATUS_NEW = "DISK_NEW"
DISK_STATUS_FAILED = frozenset({DISK_STATUS_DISABLED, DISK_STATUS_INVALID})

# Array states considered healthy
HEALTHY_ARRAY_STATES = frozenset({"STARTED", "STOPPED"})

# Logging
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB

# Sensitive keys for variable redaction
SENSITIVE_VARIABLE_KEYS = frozenset({"password", "pass", "token", "secret", "key"})

# Allowed log directory prefixes (for server's own log output)
ALLOWED_LOG_DIR_PREFIXES = (
    "/app/logs",
    "/app/",
    "/var/log/",
    "/tmp",
)

# Allowed log file path prefixes (Unraid standard locations)
ALLOWED_LOG_PREFIXES = (
    "/var/log/",
    "/boot/logs/",
    "/boot/config/",
    "/mnt/user/",
    "/tmp/",
)
