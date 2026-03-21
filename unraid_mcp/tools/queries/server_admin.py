"""GraphQL mutations for server administration."""

UPDATE_SERVER_IDENTITY_MUTATION = """
    mutation UpdateServerIdentity($input: ServerIdentityInput!) {
      updateServerIdentity(input: $input) {
        name
        comment
        model
        description
      }
    }
"""

UPDATE_SSH_SETTINGS_MUTATION = """
    mutation UpdateSshSettings($input: SshSettingsInput!) {
      updateSshSettings(input: $input) {
        enabled
        port
        allowRootLogin
      }
    }
"""

UPDATE_SETTINGS_MUTATION = """
    mutation UpdateSettings($input: SettingsInput!) {
      updateSettings(input: $input) {
        success
      }
    }
"""

UPDATE_TEMPERATURE_CONFIG_MUTATION = """
    mutation UpdateTemperatureConfig($input: TemperatureConfigInput!) {
      updateTemperatureConfig(input: $input) {
        unit
        warning
        critical
      }
    }
"""

UPDATE_SYSTEM_TIME_MUTATION = """
    mutation UpdateSystemTime($input: SystemTimeInput!) {
      updateSystemTime(input: $input) {
        timezone
        ntpEnabled
        ntpServer
      }
    }
"""

INITIATE_FLASH_BACKUP_MUTATION = """
    mutation InitiateFlashBackup {
      initiateFlashBackup {
        success
      }
    }
"""
