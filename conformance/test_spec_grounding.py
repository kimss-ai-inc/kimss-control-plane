"""Ground the public OpenAPI spec against kimssApi control-plane routes (origin/main)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "openapi" / "control-plane.yaml"
EXAMPLES = ROOT / "examples"

REQUIRED_PATHS = frozenset(
    {
        "/health",
        "/api/v1/status",
        "/api/v1/whoami",
        "/api/v1/governed-requests/meter",
        "/api/v1/mcp-servers",
        "/api/v1/mcp-servers/{server_name}",
        "/api/v1/mcp-servers/{server_name}/rotate",
        "/api/v1/mcp-servers/{server_name}/discover",
        "/api/v1/mcp-servers/{server_name}/grants",
        "/audit_log/",
        "/agent_set_status/",
        "/v1/agents/register",
        "/v1/usage/events",
        "/api/v1/me/usage",
        "/api/v1/telemetry/execution-summary",
    }
)

REQUIRED_SCHEMAS = frozenset(
    {
        "GovernedRequestsMeter",
        "McpServerRegisterRequest",
        "McpToolGrantUpsertRequest",
        "AuditLogRequest",
        "AgentSetStatusRequest",
        "GovernedRequestsExhaustedDetail",
    }
)


@pytest.fixture(scope="module")
def spec() -> dict:
    with SPEC_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def test_spec_loads() -> None:
    assert SPEC_PATH.is_file()


def test_required_paths_present(spec: dict) -> None:
    paths = set(spec.get("paths", {}))
    missing = REQUIRED_PATHS - paths
    assert not missing, f"missing paths: {sorted(missing)}"


def test_required_schemas_present(spec: dict) -> None:
    schemas = set(spec.get("components", {}).get("schemas", {}))
    missing = REQUIRED_SCHEMAS - schemas
    assert not missing, f"missing schemas: {sorted(missing)}"


def test_governed_requests_meter_fields(spec: dict) -> None:
    meter = spec["components"]["schemas"]["GovernedRequestsMeter"]
    props = set(meter.get("properties", {}))
    assert {"tenant_id", "year_month", "used", "included", "allows_overage", "unlimited"} <= props


def test_governed_requests_exhausted_error_code(spec: dict) -> None:
    detail = spec["components"]["schemas"]["GovernedRequestsExhaustedDetail"]
    error_prop = detail["allOf"][1]["properties"]["error"]
    assert error_prop.get("const") == "governed_requests_exhausted"


def test_mcp_grant_principal_kinds(spec: dict) -> None:
    grant = spec["components"]["schemas"]["McpToolGrantUpsertRequest"]
    kinds = set(grant["properties"]["principal_kind"]["enum"])
    assert kinds == {"role", "oid", "group"}


def test_agent_kill_switch_status_enum(spec: dict) -> None:
    body = spec["components"]["schemas"]["AgentSetStatusRequest"]
    statuses = set(body["properties"]["status"]["enum"])
    assert statuses == {"active", "disabled"}


def test_example_files_parse() -> None:
    for path in EXAMPLES.glob("*.json"):
        with path.open(encoding="utf-8") as fh:
            json.load(fh)


def test_governed_meter_example_matches_schema(spec: dict) -> None:
    example_path = EXAMPLES / "governed-requests-meter-response.json"
    payload = json.loads(example_path.read_text(encoding="utf-8"))
    meter = payload["res"]
    required = spec["components"]["schemas"]["GovernedRequestsMeter"]["required"]
    for field in required:
        assert field in meter
