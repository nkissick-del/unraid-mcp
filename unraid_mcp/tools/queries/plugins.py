"""GraphQL queries and mutations for plugin management."""

LIST_PLUGINS_QUERY = """
    query ListPlugins {
      plugins {
        name
        version
        hasApiModule
        hasCliModule
      }
    }
"""

LIST_INSTALLED_UNRAID_PLUGINS_QUERY = """
    query ListInstalledUnraidPlugins {
      installedUnraidPlugins
    }
"""

GET_PLUGIN_INSTALL_OPERATION_QUERY = """
    query GetPluginInstallOperation($operationId: String!) {
      pluginInstallOperation(operationId: $operationId) {
        id
        status
        progress
        error
      }
    }
"""

LIST_PLUGIN_INSTALL_OPERATIONS_QUERY = """
    query ListPluginInstallOperations {
      pluginInstallOperations {
        id
        url
        name
        status
        createdAt
        updatedAt
        finishedAt
        output
      }
    }
"""

ADD_PLUGIN_MUTATION = """
    mutation AddPlugin($input: PluginManagementInput!) {
      addPlugin(input: $input) {
        id
        status
      }
    }
"""

REMOVE_PLUGIN_MUTATION = """
    mutation RemovePlugin($input: PluginManagementInput!) {
      removePlugin(input: $input) {
        success
      }
    }
"""

# installPlugin is an alias for addPlugin — the API only has addPlugin
INSTALL_PLUGIN_MUTATION = """
    mutation InstallPlugin($input: PluginManagementInput!) {
      addPlugin(input: $input) {
        id
        status
      }
    }
"""
