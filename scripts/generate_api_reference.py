#!/usr/bin/env python3
"""Generate API reference documentation by introspecting the Unraid GraphQL API.

This script sends an introspection query directly to the Unraid GraphQL API
and generates:
  - docs/api-reference.md  — human-readable API reference
  - docs/schema.graphql    — SDL representation of the schema

Usage:
    uv run python scripts/generate_api_reference.py

Environment variables:
    UNRAID_API_URL  — GraphQL endpoint (default: from .env / settings)
    UNRAID_API_KEY  — API key for authentication
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import httpx

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"

# Try to load settings from the project if available
try:
    sys.path.insert(0, str(PROJECT_ROOT))
    from unraid_mcp.config.settings import UNRAID_API_KEY, UNRAID_API_URL
except Exception:
    UNRAID_API_URL = os.environ.get("UNRAID_API_URL", "")
    UNRAID_API_KEY = os.environ.get("UNRAID_API_KEY", "")

INTROSPECTION_QUERY = """
{
  __schema {
    queryType { fields { name description args { name type { ...TypeRef } } type { ...TypeRef } } }
    mutationType { fields { name description args { name type { ...TypeRef } } type { ...TypeRef } } }
    subscriptionType { fields { name description args { name type { ...TypeRef } } type { ...TypeRef } } }
    types { name kind description fields { name description type { ...TypeRef } } enumValues { name } inputFields { name type { ...TypeRef } } }
  }
}
fragment TypeRef on __Type { name kind ofType { name kind ofType { name kind ofType { name kind } } } }
"""

# ---------------------------------------------------------------------------
# Type formatting helpers
# ---------------------------------------------------------------------------


def format_type_ref(type_ref: dict[str, Any] | None) -> str:
    """Recursively format a __Type reference into a human-readable string."""
    if type_ref is None:
        return "Unknown"
    kind = type_ref.get("kind", "")
    name = type_ref.get("name")
    of_type = type_ref.get("ofType")

    if kind == "NON_NULL":
        return f"{format_type_ref(of_type)}!"
    if kind == "LIST":
        return f"[{format_type_ref(of_type)}]"
    return name or "Unknown"


def format_type_ref_sdl(type_ref: dict[str, Any] | None) -> str:
    """Format a __Type reference into SDL notation."""
    return format_type_ref(type_ref)


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------


def generate_api_reference_md(schema: dict[str, Any]) -> str:
    """Generate a Markdown API reference from introspection data."""
    lines: list[str] = []
    lines.append("# Unraid GraphQL API Reference")
    lines.append("")
    lines.append("Auto-generated from live API introspection.")
    lines.append("")

    for section_key, section_title in [
        ("queryType", "Queries"),
        ("mutationType", "Mutations"),
        ("subscriptionType", "Subscriptions"),
    ]:
        type_data = schema.get(section_key)
        if not type_data or not type_data.get("fields"):
            continue

        lines.append(f"## {section_title}")
        lines.append("")
        lines.append("| Field | Return Type | Description |")
        lines.append("|-------|------------|-------------|")

        for field in sorted(type_data["fields"], key=lambda f: f["name"]):
            name = field["name"]
            return_type = format_type_ref(field.get("type"))
            desc = (field.get("description") or "").replace("\n", " ").strip()
            args_list = field.get("args", [])
            if args_list:
                args_str = ", ".join(
                    f"`{a['name']}`: {format_type_ref(a.get('type'))}" for a in args_list
                )
                name = f"`{name}`({args_str})"
            else:
                name = f"`{name}`"
            lines.append(f"| {name} | `{return_type}` | {desc} |")

        lines.append("")

    # Named types summary
    types = schema.get("types", [])
    user_types = [
        t
        for t in types
        if t.get("name")
        and not t["name"].startswith("__")
        and t.get("kind") in ("OBJECT", "INPUT_OBJECT", "ENUM")
    ]

    if user_types:
        lines.append("## Types")
        lines.append("")

        for t in sorted(user_types, key=lambda x: x["name"]):
            kind = t["kind"]
            name = t["name"]
            desc = (t.get("description") or "").replace("\n", " ").strip()

            lines.append(f"### `{name}` ({kind})")
            if desc:
                lines.append(f"\n{desc}\n")
            lines.append("")

            if kind == "ENUM" and t.get("enumValues"):
                lines.append("Values: " + ", ".join(f"`{e['name']}`" for e in t["enumValues"]))
                lines.append("")
            elif kind in ("OBJECT", "INPUT_OBJECT"):
                fields = t.get("fields") or t.get("inputFields") or []
                if fields:
                    lines.append("| Field | Type |")
                    lines.append("|-------|------|")
                    for f in fields:
                        fname = f["name"]
                        ftype = format_type_ref(f.get("type"))
                        lines.append(f"| `{fname}` | `{ftype}` |")
                    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# SDL generation
# ---------------------------------------------------------------------------


def generate_schema_sdl(schema: dict[str, Any]) -> str:
    """Generate an SDL representation from introspection data."""
    lines: list[str] = []
    lines.append("# Auto-generated Unraid GraphQL Schema (SDL)")
    lines.append("")

    types = schema.get("types", [])
    user_types = [t for t in types if t.get("name") and not t["name"].startswith("__")]

    kind_order = {
        "SCALAR": 0,
        "ENUM": 1,
        "INPUT_OBJECT": 2,
        "OBJECT": 3,
        "UNION": 4,
        "INTERFACE": 5,
    }

    for t in sorted(user_types, key=lambda x: (kind_order.get(x.get("kind", ""), 9), x["name"])):
        kind = t["kind"]
        name = t["name"]
        desc = t.get("description")

        if kind == "SCALAR":
            if name not in ("String", "Int", "Float", "Boolean", "ID"):
                lines.append(f"scalar {name}")
                lines.append("")

        elif kind == "ENUM":
            if desc:
                lines.append(f'"""{desc}"""')
            lines.append(f"enum {name} {{")
            for ev in t.get("enumValues", []):
                lines.append(f"  {ev['name']}")
            lines.append("}")
            lines.append("")

        elif kind == "INPUT_OBJECT":
            if desc:
                lines.append(f'"""{desc}"""')
            lines.append(f"input {name} {{")
            for f in t.get("inputFields", []):
                ftype = format_type_ref_sdl(f.get("type"))
                lines.append(f"  {f['name']}: {ftype}")
            lines.append("}")
            lines.append("")

        elif kind == "OBJECT":
            if desc:
                lines.append(f'"""{desc}"""')
            keyword = "type"
            lines.append(f"{keyword} {name} {{")
            for f in t.get("fields", []):
                ftype = format_type_ref_sdl(f.get("type"))
                lines.append(f"  {f['name']}: {ftype}")
            lines.append("}")
            lines.append("")

        elif kind == "INTERFACE":
            if desc:
                lines.append(f'"""{desc}"""')
            lines.append(f"interface {name} {{")
            for f in t.get("fields", []):
                ftype = format_type_ref_sdl(f.get("type"))
                lines.append(f"  {f['name']}: {ftype}")
            lines.append("}")
            lines.append("")

        elif kind == "UNION":
            lines.append(f"union {name}")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if not UNRAID_API_URL:
        print(
            "ERROR: UNRAID_API_URL not set. Configure it in .env or environment.", file=sys.stderr
        )
        sys.exit(1)

    if not UNRAID_API_KEY:
        print(
            "ERROR: UNRAID_API_KEY not set. Configure it in .env or environment.", file=sys.stderr
        )
        sys.exit(1)

    # Send introspection query directly to the GraphQL endpoint
    graphql_url = UNRAID_API_URL.rstrip("/")
    if not graphql_url.endswith("/graphql"):
        graphql_url = f"{graphql_url}/graphql"

    print(f"Querying {graphql_url} for schema introspection...")

    headers = {
        "Content-Type": "application/json",
        "x-api-key": UNRAID_API_KEY,
    }

    try:
        response = httpx.post(
            graphql_url,
            json={"query": INTROSPECTION_QUERY},
            headers=headers,
            timeout=30.0,
            verify=False,  # Unraid often uses self-signed certs
        )
        response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"ERROR: Failed to query API: {e}", file=sys.stderr)
        sys.exit(1)

    result = response.json()
    if "errors" in result:
        print(f"GraphQL errors: {json.dumps(result['errors'], indent=2)}", file=sys.stderr)
        sys.exit(1)

    schema = result.get("data", {}).get("__schema")
    if not schema:
        print("ERROR: No __schema found in response.", file=sys.stderr)
        sys.exit(1)

    # Ensure docs directory exists
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate API reference
    api_ref = generate_api_reference_md(schema)
    api_ref_path = DOCS_DIR / "api-reference.md"
    api_ref_path.write_text(api_ref)
    print(f"Generated {api_ref_path}")

    # Generate SDL schema
    sdl = generate_schema_sdl(schema)
    sdl_path = DOCS_DIR / "schema.graphql"
    sdl_path.write_text(sdl)
    print(f"Generated {sdl_path}")

    # Summary
    query_count = len((schema.get("queryType") or {}).get("fields", []))
    mutation_count = len((schema.get("mutationType") or {}).get("fields", []))
    subscription_count = len((schema.get("subscriptionType") or {}).get("fields", []))
    type_count = len([t for t in schema.get("types", []) if not t["name"].startswith("__")])
    print(
        f"\nSchema summary: {query_count} queries, {mutation_count} mutations, "
        f"{subscription_count} subscriptions, {type_count} types"
    )


if __name__ == "__main__":
    main()
