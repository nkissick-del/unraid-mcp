"""GraphQL queries and mutations for Unraid Connect administration."""

GET_CONNECT_INFO_QUERY = """
    query GetConnectInfo {
      connect {
        id
        status
        signedIn
        username
        email
        serverName
      }
    }
"""

GET_REMOTE_ACCESS_QUERY = """
    query GetRemoteAccess {
      remoteAccess {
        id
        enabled
        url
        type
        port
        status
      }
    }
"""

GET_CLOUD_INFO_QUERY = """
    query GetCloudInfo {
      cloud {
        id
        status
        error
        apiKey
        allowedOrigins
      }
    }
"""

UPDATE_API_SETTINGS_MUTATION = """
    mutation UpdateApiSettings($input: ApiSettingsInput!) {
      updateApiSettings(input: $input) {
        success
      }
    }
"""

CONNECT_SIGN_IN_MUTATION = """
    mutation ConnectSignIn($input: ConnectSignInInput!) {
      connectSignIn(input: $input) {
        success
      }
    }
"""

CONNECT_SIGN_OUT_MUTATION = """
    mutation ConnectSignOut {
      connectSignOut {
        success
      }
    }
"""

SETUP_REMOTE_ACCESS_MUTATION = """
    mutation SetupRemoteAccess($input: RemoteAccessInput!) {
      setupRemoteAccess(input: $input) {
        enabled
        url
        type
        port
        status
      }
    }
"""

ENABLE_DYNAMIC_REMOTE_ACCESS_MUTATION = """
    mutation EnableDynamicRemoteAccess($input: DynamicRemoteAccessInput!) {
      enableDynamicRemoteAccess(input: $input) {
        enabled
        url
        type
        port
        status
      }
    }
"""
