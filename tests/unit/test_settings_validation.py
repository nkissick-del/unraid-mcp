"""Tests for log directory and log file name validation in settings.py."""

import importlib
import warnings
from unittest.mock import patch


class TestLogDirValidation:
    def test_valid_log_dir_accepted(self):
        """A log dir under /tmp should be accepted without warnings."""
        with (
            patch.dict(
                "os.environ",
                {"UNRAID_MCP_LOG_DIR": "/tmp/test-logs", "UNRAID_MCP_LOG_FILE": "test.log"},
            ),
            warnings.catch_warnings(record=True) as w,
        ):
            warnings.simplefilter("always")
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            log_dir_warnings = [x for x in w if "UNRAID_MCP_LOG_DIR" in str(x.message)]
            assert len(log_dir_warnings) == 0
            assert str(settings_mod.LOGS_DIR).startswith("/tmp")

    def test_disallowed_log_dir_falls_back(self):
        """A log dir outside allowed prefixes should fall back to /tmp."""
        with (
            patch.dict(
                "os.environ",
                {"UNRAID_MCP_LOG_DIR": "/etc/evil", "UNRAID_MCP_LOG_FILE": "test.log"},
            ),
            warnings.catch_warnings(record=True) as w,
        ):
            warnings.simplefilter("always")
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            log_dir_warnings = [x for x in w if "UNRAID_MCP_LOG_DIR" in str(x.message)]
            assert len(log_dir_warnings) == 1
            assert settings_mod.LOGS_DIR == __import__("pathlib").Path("/tmp")

    def test_log_file_name_traversal_rejected(self):
        """A log file name with path traversal should fall back to default."""
        with (
            patch.dict(
                "os.environ",
                {
                    "UNRAID_MCP_LOG_DIR": "/tmp",
                    "UNRAID_MCP_LOG_FILE": "../../etc/passwd",
                },
            ),
            warnings.catch_warnings(record=True) as w,
        ):
            warnings.simplefilter("always")
            import unraid_mcp.config.settings as settings_mod

            importlib.reload(settings_mod)
            file_warnings = [x for x in w if "UNRAID_MCP_LOG_FILE" in str(x.message)]
            assert len(file_warnings) == 1
            assert settings_mod.LOG_FILE_NAME == "unraid-mcp.log"


def test_auth_token_loaded_from_env(monkeypatch):
    """MCP_AUTH_TOKEN should be read from UNRAID_MCP_AUTH_TOKEN env var."""
    monkeypatch.setenv("UNRAID_MCP_AUTH_TOKEN", "test-secret-token")
    monkeypatch.setenv("UNRAID_API_URL", "https://fake:8443/graphql")
    monkeypatch.setenv("UNRAID_API_KEY", "fake-key")
    import unraid_mcp.config.settings as settings_mod

    importlib.reload(settings_mod)
    assert settings_mod.MCP_AUTH_TOKEN == "test-secret-token"


def test_auth_token_empty_when_unset(monkeypatch):
    """MCP_AUTH_TOKEN should be empty string when env var is not set."""
    monkeypatch.delenv("UNRAID_MCP_AUTH_TOKEN", raising=False)
    monkeypatch.setenv("UNRAID_API_URL", "https://fake:8443/graphql")
    monkeypatch.setenv("UNRAID_API_KEY", "fake-key")
    import unraid_mcp.config.settings as settings_mod

    importlib.reload(settings_mod)
    assert settings_mod.MCP_AUTH_TOKEN == ""
