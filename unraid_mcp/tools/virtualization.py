"""Virtual machine management tools.

This module provides tools for VM lifecycle management and monitoring
including listing VMs, VM operations (start/stop/pause/reboot/etc),
and detailed VM information retrieval.
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.decorators import tool_error_handler
from ..core.exceptions import ToolError
from ..core.utils import ensure_dict, ensure_list, validate_enum, validate_string_not_empty
from .queries.virtualization import VM_ACTION_MUTATIONS


def register_vm_tools(mcp: FastMCP) -> None:
    """Register all VM tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    @tool_error_handler("list virtual machines")
    async def list_vms() -> list[dict[str, Any]]:
        """Lists all Virtual Machines (VMs) on the Unraid system and their current state.

        Returns:
            List of VM information dictionaries with UUID, name, and state
        """
        query = """
        query ListVMs {
          vms {
            id
            domains {
              id
              name
              state
              uuid
            }
          }
        }
        """
        response_data = await make_graphql_request(query)
        logger.debug(f"VM query response: {response_data}")
        if response_data.get("vms") and response_data["vms"].get("domains"):
            vms = response_data["vms"]["domains"]
            logger.info(f"Found {len(vms)} VMs")
            return ensure_list(vms)
        else:
            logger.info("No VMs found in domains field")
            return []

    @mcp.tool()
    @tool_error_handler("manage virtual machine")
    async def manage_vm(vm_uuid: str, action: str) -> dict[str, Any]:
        """Manages a VM: start, stop, pause, resume, force_stop, reboot, reset. Uses VM UUID.

        Args:
            vm_uuid: UUID of the VM to manage
            action: Action to perform - one of: start, stop, pause, resume, forceStop, reboot, reset

        Returns:
            Dict containing operation success status and details
        """
        validate_string_not_empty(vm_uuid, "vm_uuid")
        mutation_name = validate_enum(action, list(VM_ACTION_MUTATIONS), "action")
        query = VM_ACTION_MUTATIONS[mutation_name]
        variables = {"id": vm_uuid}
        response_data = await make_graphql_request(query, variables)
        if response_data.get("vm") and mutation_name in response_data["vm"]:
            # Mutations for VM return Boolean for success
            success = response_data["vm"][mutation_name]
            return {"success": success, "action": action, "vm_uuid": vm_uuid}
        raise ToolError(f"Failed to {action} VM or unexpected response structure.")

    @mcp.tool()
    @tool_error_handler("retrieve VM details")
    async def get_vm_details(vm_identifier: str) -> dict[str, Any]:
        """Retrieves detailed information for a specific VM by its UUID or name.

        Args:
            vm_identifier: VM UUID or name to retrieve details for

        Returns:
            Dict containing detailed VM information
        """
        validate_string_not_empty(vm_identifier, "vm_identifier")
        # Make direct GraphQL call instead of calling list_vms() tool
        query = """
        query GetVmDetails {
          vms {
            domains {
              id
              name
              state
              uuid
            }
            domain {
              id
              name
              state
              uuid
            }
          }
        }
        """
        response_data = await make_graphql_request(query)

        if response_data.get("vms"):
            vms_data = response_data["vms"]
            # Try to get VMs from either domains or domain field
            vms = vms_data.get("domains") or []
            if not vms:
                domain = vms_data.get("domain")
                if isinstance(domain, list):
                    vms = domain
                elif isinstance(domain, dict):
                    vms = [domain]

            if vms:
                for vm_data in vms:
                    if (
                        vm_data.get("uuid") == vm_identifier
                        or vm_data.get("id") == vm_identifier
                        or vm_data.get("name") == vm_identifier
                    ):
                        logger.info(f"Found VM {vm_identifier}")
                        return ensure_dict(vm_data)

                logger.warning(f"VM with identifier '{vm_identifier}' not found.")
                available_vms = [
                    f"{vm.get('name')} (UUID: {vm.get('uuid')}, ID: {vm.get('id')})" for vm in vms
                ]
                raise ToolError(
                    f"VM '{vm_identifier}' not found. Available VMs: {', '.join(available_vms)}"
                )
            else:
                raise ToolError("No VMs available or VMs not accessible")
        else:
            raise ToolError("No VMs data returned from server")

    logger.info("VM tools registered successfully")
