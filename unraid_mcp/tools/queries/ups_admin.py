"""GraphQL mutations for UPS administration."""

CONFIGURE_UPS_MUTATION = """
    mutation ConfigureUps($input: UpsConfigurationInput!) {
      configureUps(input: $input) {
        service
        upsCable
        customUpsCable
        upsType
        device
        overrideUpsCapacity
        batteryLevel
        minutes
        timeout
        killUps
        nisIp
        netServer
        upsName
        modelName
      }
    }
"""
