"""GraphQL mutations for UPS administration."""

CONFIGURE_UPS_MUTATION = """
    mutation ConfigureUps($config: UPSConfigInput!) {
      configureUps(config: $config) {
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
