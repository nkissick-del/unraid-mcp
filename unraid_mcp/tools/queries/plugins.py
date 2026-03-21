"""GraphQL queries and mutations for plugin management."""

LIST_PLUGINS_QUERY = """
    query ListPlugins {
      plugins {
        id
        name
        version
        author
        url
        icon
        status
        description
      }
    }
"""

LIST_INSTALLED_UNRAID_PLUGINS_QUERY = """
    query ListInstalledUnraidPlugins {
      installedUnraidPlugins {
        id
        name
        version
        author
        url
        icon
        status
      }
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
        status
        progress
        error
      }
    }
"""

ADD_PLUGIN_MUTATION = """
    mutation AddPlugin($url: String!) {
      addPlugin(url: $url) {
        id
        status
      }
    }
"""

REMOVE_PLUGIN_MUTATION = """
    mutation RemovePlugin($name: String!) {
      removePlugin(name: $name) {
        success
      }
    }
"""

INSTALL_PLUGIN_MUTATION = """
    mutation InstallPlugin($url: String!) {
      installPlugin(url: $url) {
        id
        status
      }
    }
"""
