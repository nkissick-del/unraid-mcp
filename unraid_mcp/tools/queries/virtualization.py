"""GraphQL queries and mutations for virtual machine management."""

# Pre-built mutation queries keyed by action — eliminates f-string interpolation of user input
VM_ACTION_MUTATIONS: dict[str, str] = {
    "start": """
        mutation ManageVM($id: PrefixedID!) {
          vm { start(id: $id) }
        }
    """,
    "stop": """
        mutation ManageVM($id: PrefixedID!) {
          vm { stop(id: $id) }
        }
    """,
    "pause": """
        mutation ManageVM($id: PrefixedID!) {
          vm { pause(id: $id) }
        }
    """,
    "resume": """
        mutation ManageVM($id: PrefixedID!) {
          vm { resume(id: $id) }
        }
    """,
    "forceStop": """
        mutation ManageVM($id: PrefixedID!) {
          vm { forceStop(id: $id) }
        }
    """,
    "reboot": """
        mutation ManageVM($id: PrefixedID!) {
          vm { reboot(id: $id) }
        }
    """,
    "reset": """
        mutation ManageVM($id: PrefixedID!) {
          vm { reset(id: $id) }
        }
    """,
}
