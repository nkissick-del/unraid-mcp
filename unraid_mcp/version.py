"""Single source of truth for package version."""

from importlib.metadata import PackageNotFoundError, version

try:
    VERSION = version("unraid-mcp")
except PackageNotFoundError:
    VERSION = "0.0.0"
