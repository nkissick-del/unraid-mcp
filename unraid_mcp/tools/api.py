"""Hybrid API tools for schema introspection and raw queries.

This module provides tools for exploring the Unraid GraphQL schema
and executing read-only queries directly against the API.
"""

import re
from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError


def register_api_tools(mcp: FastMCP) -> None:
    """Register all API tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    async def introspect_schema(type_name: str | None = None) -> dict[str, Any]:
        """Introspect the Unraid GraphQL schema. Without arguments, returns root query/mutation/subscription fields. With a type_name, returns fields and types for that specific type."""
        try:
            if type_name:
                logger.info(f"Introspecting schema type: {type_name}")
                query = """
                query IntrospectType($name: String!) {
                  __type(name: $name) {
                    name
                    kind
                    description
                    fields {
                      name
                      description
                      type {
                        name
                        kind
                        ofType { name kind ofType { name kind ofType { name kind } } }
                      }
                      args {
                        name
                        type {
                          name
                          kind
                          ofType { name kind ofType { name kind } }
                        }
                        defaultValue
                      }
                    }
                    inputFields {
                      name
                      type {
                        name
                        kind
                        ofType { name kind ofType { name kind } }
                      }
                      defaultValue
                    }
                    enumValues { name description }
                  }
                }
                """
                response_data = await make_graphql_request(query, {"name": type_name})
                type_info = response_data.get("__type")
                if not type_info:
                    raise ToolError(f"Type '{type_name}' not found in schema")
                return type_info
            else:
                logger.info("Introspecting root schema fields")
                query = """
                query IntrospectRootFields {
                  __schema {
                    queryType { fields { name description } }
                    mutationType { fields { name description } }
                    subscriptionType { fields { name description } }
                  }
                }
                """
                response_data = await make_graphql_request(query)
                schema = response_data.get("__schema", {})
                result: dict[str, Any] = {}
                if q := schema.get("queryType", {}).get("fields"):
                    result["queries"] = q
                if m := schema.get("mutationType", {}).get("fields"):
                    result["mutations"] = m
                if s := schema.get("subscriptionType", {}).get("fields"):
                    result["subscriptions"] = s
                return result

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in introspect_schema: {e}", exc_info=True)
            raise ToolError(f"Failed to introspect schema: {str(e)}") from e

    @mcp.tool()
    async def query_unraid_api(
        graphql_query: str,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a read-only GraphQL query against the Unraid API. Mutations are blocked for safety."""

        # Block mutations
        # Block mutations
        def _strip_comments(q: str) -> str:
            """Strip comments while preserving strings."""
            out = []
            i = 0
            n = len(q)
            while i < n:
                c = q[i]
                if c == '"':
                    is_block = i + 2 < n and q[i + 1 : i + 3] == '""'
                    if is_block:
                        out.append('"""')
                        i += 3
                        while i < n:
                            # End of block string if """ and not escaped (approximation)
                            if i + 2 < n and q[i : i + 3] == '""' and (i == 0 or q[i - 1] != "\\"):
                                out.append('"""')
                                i += 3
                                break
                            out.append(q[i])
                            i += 1
                    else:
                        out.append('"')
                        i += 1
                        while i < n:
                            if q[i] == '"' and (i == 0 or q[i - 1] != "\\"):
                                out.append('"')
                                i += 1
                                break
                            out.append(q[i])
                            i += 1
                elif c == "#":
                    while i < n and q[i] != "\n":
                        i += 1
                    out.append("\n")
                else:
                    out.append(c)
                    i += 1
            return "".join(out)

        stripped = _strip_comments(graphql_query)
        if re.search(r"\bmutation\b", stripped, re.IGNORECASE):
            raise ToolError(
                "Mutations are not allowed through this tool. "
                "Use the dedicated management tools for write operations."
            )

        try:
            logger.info("Executing raw GraphQL query via query_unraid_api")
            logger.debug(f"Query: {graphql_query[:200]}")
            response_data = await make_graphql_request(graphql_query, variables)
            return response_data
        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in query_unraid_api: {e}", exc_info=True)
            raise ToolError(f"Failed to execute query: {str(e)}") from e

    logger.info("API tools registered successfully")
