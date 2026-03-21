"""GraphQL queries for UPS device management."""

UPS_DEVICES_QUERY = """
    query ListUpsDevices {
      upsDevices {
        id
        name
        model
        status
        battery { chargeLevel estimatedRuntime health }
        power { inputVoltage outputVoltage loadPercentage nominalPower currentPower }
      }
    }
"""

UPS_DEVICE_BY_ID_QUERY = """
    query GetUpsDeviceById($id: String!) {
      upsDeviceById(id: $id) {
        id
        name
        model
        status
        battery { chargeLevel estimatedRuntime health }
        power { inputVoltage outputVoltage loadPercentage nominalPower currentPower }
      }
    }
"""

UPS_CONFIGURATION_QUERY = """
    query GetUpsConfiguration {
      upsConfiguration {
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
