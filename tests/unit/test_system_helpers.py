"""Tests for system helper functions (analyze_disk_health)."""

from unraid_mcp.tools.system import analyze_disk_health


class TestAnalyzeDiskHealth:
    def test_all_healthy(self):
        disks = [
            {"status": "DISK_OK"},
            {"status": "DISK_OK"},
        ]
        result = analyze_disk_health(disks, "data")
        assert result["healthy"] == 2
        assert result["failed"] == 0

    def test_disabled_counted_as_failed(self):
        disks = [{"status": "DISK_DSBL"}]
        result = analyze_disk_health(disks, "parity")
        assert result["failed"] == 1

    def test_invalid_counted_as_failed(self):
        disks = [{"status": "DISK_INVALID"}]
        result = analyze_disk_health(disks, "data")
        assert result["failed"] == 1

    def test_not_present_counted_as_missing(self):
        disks = [{"status": "DISK_NP"}]
        result = analyze_disk_health(disks, "data")
        assert result["missing"] == 1

    def test_new_counted_as_new(self):
        disks = [{"status": "DISK_NEW"}]
        result = analyze_disk_health(disks, "data")
        assert result["new"] == 1

    def test_ok_with_warning_flag(self):
        disks = [{"status": "DISK_OK", "warning": True}]
        result = analyze_disk_health(disks, "data")
        assert result["warning"] == 1
        assert result["healthy"] == 0

    def test_ok_with_critical_flag(self):
        disks = [{"status": "DISK_OK", "critical": True}]
        result = analyze_disk_health(disks, "data")
        assert result["warning"] == 1

    def test_empty_list(self):
        assert analyze_disk_health([], "data") == {}

    def test_mixed_statuses(self):
        disks = [
            {"status": "DISK_OK"},
            {"status": "DISK_DSBL"},
            {"status": "DISK_NP"},
            {"status": "DISK_NEW"},
            {"status": "DISK_OK", "warning": True},
        ]
        result = analyze_disk_health(disks, "data")
        assert result["healthy"] == 1
        assert result["failed"] == 1
        assert result["missing"] == 1
        assert result["new"] == 1
        assert result["warning"] == 1

    def test_unknown_status(self):
        disks = [{"status": "DISK_WEIRD"}]
        result = analyze_disk_health(disks, "data")
        assert result["unknown"] == 1
