"""Contract tests validating tool response shapes against Pydantic models.

Each test mocks make_graphql_request with realistic data, calls the tool
function, and validates the result against a Pydantic model that encodes
the expected response contract.
"""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import BaseModel

from tests.helpers import get_tool_fn
from unraid_mcp.tools.docker import register_docker_tools
from unraid_mcp.tools.health import register_health_tools
from unraid_mcp.tools.storage import register_storage_tools
from unraid_mcp.tools.system import register_system_tools
from unraid_mcp.tools.ups_tools import register_ups_tools

# ---------------------------------------------------------------------------
# Pydantic models defining response contracts
# ---------------------------------------------------------------------------


class SystemInfoSummary(BaseModel):
    os: str | None = None
    hostname: str | None = None
    uptime: int | float | None = None
    cpu: str | None = None
    memory_summary: str | None = None
    memory_layout_details: list[str] | None = None
    versions: str | None = None


class SystemInfoResponse(BaseModel):
    summary: dict[str, Any]
    details: dict[str, Any]


class ArrayStatusSummary(BaseModel):
    state: str | None = None
    capacity_total: str | None = None
    capacity_used: str | None = None
    capacity_free: str | None = None
    num_parity_disks: int
    num_data_disks: int
    num_cache_pools: int
    overall_health: str
    health_summary: dict[str, Any]


class ArrayStatusResponse(BaseModel):
    summary: dict[str, Any]
    details: dict[str, Any]


class DockerContainerItem(BaseModel):
    id: str | None = None
    names: list[str] | None = None
    image: str | None = None
    state: str | None = None
    status: str | None = None


class DockerContainerDetails(BaseModel):
    id: str | None = None
    names: list[str] | None = None
    image: str | None = None
    state: str | None = None
    status: str | None = None
    command: str | None = None
    created: int | float | None = None
    autoStart: bool | None = None


class ShareItem(BaseModel):
    id: str | None = None
    name: str | None = None
    free: int | float | str | None = None
    used: int | float | str | None = None
    size: int | float | str | None = None


class PhysicalDiskItem(BaseModel):
    id: str | None = None
    device: str | None = None
    name: str | None = None


class HealthCheckServer(BaseModel):
    name: str
    version: str
    transport: str
    host: str
    port: int
    process_uptime_seconds: float


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    api_latency_ms: float
    server: dict[str, Any]
    performance: dict[str, Any] | None = None


class UpsDevicesResponse(BaseModel):
    count: int
    devices: list[dict[str, Any]]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MOCK_SYSTEM_INFO_RESPONSE: dict[str, Any] = {
    "info": {
        "os": {
            "platform": "linux",
            "distro": "Slackware",
            "release": "15.0",
            "codename": "",
            "kernel": "6.1.64-Unraid",
            "arch": "x86_64",
            "hostname": "Tower",
            "logofile": "",
            "serial": "",
            "build": "",
            "uptime": 123456,
        },
        "cpu": {
            "manufacturer": "AMD",
            "brand": "Ryzen 9 5950X",
            "vendor": "AuthenticAMD",
            "family": "25",
            "model": "33",
            "stepping": "2",
            "revision": "",
            "voltage": "",
            "speed": "3.4",
            "speedmin": "2.2",
            "speedmax": "4.9",
            "threads": 32,
            "cores": 16,
            "processors": 1,
            "socket": "AM4",
            "cache": {},
            "flags": "",
        },
        "memory": {
            "layout": [
                {
                    "bank": "BANK 0",
                    "type": "DDR4",
                    "clockSpeed": 3600,
                    "formFactor": "DIMM",
                    "manufacturer": "G.Skill",
                    "partNum": "F4-3600C16",
                    "serialNum": "00000001",
                },
            ],
        },
        "baseboard": {
            "manufacturer": "ASRock",
            "model": "X570 Taichi",
            "version": "",
            "serial": "ABC123",
            "assetTag": "",
        },
        "system": {
            "manufacturer": "ASRock",
            "model": "X570 Taichi",
            "version": "",
            "serial": "SYS123",
            "uuid": "uuid-1234",
            "sku": "",
        },
        "versions": {
            "core": {"unraid": "6.12.6", "api": "2.0.0", "kernel": "6.1.64"},
            "packages": {
                "openssl": "3.1.4",
                "node": "20.10.0",
                "npm": "10.2.3",
                "pm2": "5.3.0",
                "git": "2.43.0",
                "nginx": "1.25.3",
                "php": "8.3.1",
                "docker": "24.0.7",
            },
        },
        "machineId": "machine-id-abc",
        "time": 1700000000,
    }
}

MOCK_ARRAY_STATUS_RESPONSE: dict[str, Any] = {
    "array": {
        "id": "array:1",
        "state": "STARTED",
        "capacity": {
            "kilobytes": {"free": 5000000000, "used": 3000000000, "total": 8000000000},
            "disks": {"free": 5, "used": 3, "total": 8},
        },
        "boot": None,
        "parities": [
            {
                "id": "parity:1",
                "idx": 0,
                "name": "parity",
                "device": "sda",
                "size": "8000000000000",
                "status": "DISK_OK",
                "rotational": True,
                "temp": 35,
                "numReads": 100,
                "numWrites": 200,
                "numErrors": 0,
                "fsSize": 0,
                "fsFree": 0,
                "fsUsed": 0,
                "exportable": None,
                "type": None,
                "warning": None,
                "critical": None,
                "fsType": None,
                "comment": None,
                "format": None,
                "transport": "sata",
                "color": "green",
            }
        ],
        "disks": [
            {
                "id": "disk:1",
                "idx": 1,
                "name": "disk1",
                "device": "sdb",
                "size": "4000000000000",
                "status": "DISK_OK",
                "rotational": True,
                "temp": 37,
                "numReads": 500,
                "numWrites": 1000,
                "numErrors": 0,
                "fsSize": 4000000000,
                "fsFree": 1000000000,
                "fsUsed": 3000000000,
                "exportable": None,
                "type": None,
                "warning": None,
                "critical": None,
                "fsType": "xfs",
                "comment": None,
                "format": None,
                "transport": "sata",
                "color": "green",
            }
        ],
        "caches": [
            {
                "id": "cache:1",
                "idx": 0,
                "name": "cache",
                "device": "nvme0n1",
                "size": "500000000000",
                "status": "DISK_OK",
                "rotational": False,
                "temp": 42,
                "numReads": 2000,
                "numWrites": 5000,
                "numErrors": 0,
                "fsSize": 500000000,
                "fsFree": 200000000,
                "fsUsed": 300000000,
                "exportable": None,
                "type": None,
                "warning": None,
                "critical": None,
                "fsType": "btrfs",
                "comment": None,
                "format": None,
                "transport": "nvme",
                "color": "green",
            }
        ],
    }
}

MOCK_DOCKER_LIST_RESPONSE: dict[str, Any] = {
    "docker": {
        "containers": [
            {
                "id": "sha256:abc123def456",
                "names": ["plex"],
                "image": "linuxserver/plex:latest",
                "imageId": "sha256:img123",
                "state": "running",
                "status": "Up 2 days",
                "autoStart": True,
            },
            {
                "id": "sha256:789xyz000111",
                "names": ["homeassistant"],
                "image": "homeassistant/home-assistant:latest",
                "imageId": "sha256:img456",
                "state": "running",
                "status": "Up 5 hours",
                "autoStart": True,
            },
        ]
    }
}

MOCK_DOCKER_DETAILS_RESPONSE: dict[str, Any] = {
    "docker": {
        "containers": [
            {
                "id": "sha256:abc123def456",
                "names": ["plex"],
                "image": "linuxserver/plex:latest",
                "imageId": "sha256:img123",
                "command": "/init",
                "created": 1700000000,
                "ports": [
                    {"ip": "0.0.0.0", "privatePort": 32400, "publicPort": 32400, "type": "tcp"}
                ],
                "sizeRootFs": 500000000,
                "labels": {"maintainer": "linuxserver"},
                "state": "running",
                "status": "Up 2 days",
                "hostConfig": {"networkMode": "bridge"},
                "networkSettings": {},
                "mounts": [],
                "autoStart": True,
            }
        ]
    }
}

MOCK_SHARES_RESPONSE: dict[str, Any] = {
    "shares": [
        {
            "id": "share:1",
            "name": "appdata",
            "free": 100000000,
            "used": 50000000,
            "size": 150000000,
            "include": "",
            "exclude": "",
            "cache": "prefer",
            "nameOrig": "appdata",
            "comment": "Application data",
            "allocator": "highwater",
            "splitLevel": "",
            "floor": "0",
            "cow": "auto",
            "color": "green",
            "luksStatus": "0",
        },
        {
            "id": "share:2",
            "name": "media",
            "free": 2000000000,
            "used": 1500000000,
            "size": 3500000000,
            "include": "",
            "exclude": "",
            "cache": "no",
            "nameOrig": "media",
            "comment": "Media files",
            "allocator": "highwater",
            "splitLevel": "",
            "floor": "0",
            "cow": "auto",
            "color": "green",
            "luksStatus": "0",
        },
    ]
}

MOCK_PHYSICAL_DISKS_RESPONSE: dict[str, Any] = {
    "disks": [
        {"id": "disk:sda", "device": "/dev/sda", "name": "WDC WD80EFAX"},
        {"id": "disk:sdb", "device": "/dev/sdb", "name": "Seagate ST8000VN004"},
        {"id": "disk:nvme0n1", "device": "/dev/nvme0n1", "name": "Samsung 970 EVO"},
    ]
}

MOCK_HEALTH_CHECK_RESPONSE: dict[str, Any] = {
    "info": {
        "machineId": "machine-id-abc",
        "time": 1700000000,
        "versions": {"core": {"unraid": "6.12.6"}},
        "os": {"uptime": 123456},
    },
    "array": {"state": "STARTED"},
    "notifications": {"overview": {"unread": {"alert": 0, "warning": 2, "total": 5}}},
    "docker": {
        "containers": [
            {"id": "c1", "state": "running", "status": "Up 2 days"},
            {"id": "c2", "state": "running", "status": "Up 5 hours"},
            {"id": "c3", "state": "exited", "status": "Exited (0) 1 hour ago"},
        ]
    },
}

MOCK_UPS_DEVICES_RESPONSE: dict[str, Any] = {
    "upsDevices": [
        {
            "id": "ups:1",
            "name": "APC Back-UPS 1500",
            "model": "Back-UPS RS 1500G",
            "status": "OL",
            "batteryCharge": 100.0,
            "batteryRuntime": 3600,
            "loadPercent": 25.0,
            "inputVoltage": 120.5,
            "outputVoltage": 120.0,
        }
    ]
}


# ---------------------------------------------------------------------------
# Contract tests
# ---------------------------------------------------------------------------


class TestSystemInfoContract:
    @pytest.mark.asyncio
    async def test_get_system_info_shape(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "unraid_mcp.tools.system.make_graphql_request",
            lambda *a, **kw: _async_return(MOCK_SYSTEM_INFO_RESPONSE),
        )
        fn = get_tool_fn(register_system_tools, "get_system_info")
        result = await fn()
        validated = SystemInfoResponse.model_validate(result)
        assert validated.summary is not None
        assert validated.details is not None
        # Validate summary sub-fields
        summary = SystemInfoSummary.model_validate(validated.summary)
        assert summary.hostname == "Tower"
        assert summary.cpu is not None
        assert "Ryzen" in (summary.cpu or "")

    @pytest.mark.asyncio
    async def test_get_array_status_shape(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "unraid_mcp.tools.system.make_graphql_request",
            lambda *a, **kw: _async_return(MOCK_ARRAY_STATUS_RESPONSE),
        )
        fn = get_tool_fn(register_system_tools, "get_array_status")
        result = await fn()
        validated = ArrayStatusResponse.model_validate(result)
        assert validated.summary is not None
        summary = ArrayStatusSummary.model_validate(validated.summary)
        assert summary.state == "STARTED"
        assert summary.num_parity_disks == 1
        assert summary.num_data_disks == 1
        assert summary.num_cache_pools == 1
        assert summary.overall_health == "HEALTHY"


class TestDockerContainerContract:
    @pytest.mark.asyncio
    async def test_list_docker_containers_shape(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "unraid_mcp.tools.docker.make_graphql_request",
            lambda *a, **kw: _async_return(MOCK_DOCKER_LIST_RESPONSE),
        )
        fn = get_tool_fn(register_docker_tools, "list_docker_containers")
        result = await fn()
        assert isinstance(result, list)
        assert len(result) == 2
        for item in result:
            DockerContainerItem.model_validate(item)

    @pytest.mark.asyncio
    async def test_get_docker_container_details_shape(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "unraid_mcp.tools.docker.make_graphql_request",
            lambda *a, **kw: _async_return(MOCK_DOCKER_DETAILS_RESPONSE),
        )
        fn = get_tool_fn(register_docker_tools, "get_docker_container_details")
        result = await fn(container_identifier="plex")
        validated = DockerContainerDetails.model_validate(result)
        assert validated.id == "sha256:abc123def456"
        assert validated.names == ["plex"]
        assert validated.state == "running"
        assert validated.autoStart is True


class TestStorageContract:
    @pytest.mark.asyncio
    async def test_get_shares_info_shape(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "unraid_mcp.tools.storage.make_graphql_request",
            lambda *a, **kw: _async_return(MOCK_SHARES_RESPONSE),
        )
        fn = get_tool_fn(register_storage_tools, "get_shares_info")
        result = await fn()
        assert isinstance(result, list)
        assert len(result) == 2
        for item in result:
            ShareItem.model_validate(item)

    @pytest.mark.asyncio
    async def test_list_physical_disks_shape(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "unraid_mcp.tools.storage.make_graphql_request",
            lambda *a, **kw: _async_return(MOCK_PHYSICAL_DISKS_RESPONSE),
        )
        fn = get_tool_fn(register_storage_tools, "list_physical_disks")
        result = await fn()
        assert isinstance(result, list)
        assert len(result) == 3
        for item in result:
            PhysicalDiskItem.model_validate(item)


class TestHealthCheckContract:
    @pytest.mark.asyncio
    async def test_health_check_shape(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "unraid_mcp.tools.health.make_graphql_request",
            lambda *a, **kw: _async_return(MOCK_HEALTH_CHECK_RESPONSE),
        )
        fn = get_tool_fn(register_health_tools, "health_check")
        result = await fn()
        validated = HealthCheckResponse.model_validate(result)
        assert validated.status in ("healthy", "warning", "degraded", "unhealthy")
        assert validated.api_latency_ms >= 0
        assert validated.server["name"] == "Unraid MCP Server"
        assert "version" in validated.server


class TestUpsDevicesContract:
    @pytest.mark.asyncio
    async def test_list_ups_devices_shape(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "unraid_mcp.tools.ups_tools.make_graphql_request",
            lambda *a, **kw: _async_return(MOCK_UPS_DEVICES_RESPONSE),
        )
        fn = get_tool_fn(register_ups_tools, "list_ups_devices")
        result = await fn()
        validated = UpsDevicesResponse.model_validate(result)
        assert validated.count == 1
        assert len(validated.devices) == 1
        assert validated.devices[0]["name"] == "APC Back-UPS 1500"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _async_return(value: Any) -> Any:
    """Wrap a value in a coroutine so it can replace an async function."""
    return value
