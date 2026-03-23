"""GraphQL queries and mutations for array disk administration."""

LIST_ASSIGNABLE_DISKS_QUERY = """
    query ListAssignableDisks {
      assignableDisks {
        id
        device
        type
        name
        vendor
        size
        serialNum
        interfaceType
        smartStatus
        temperature
      }
    }
"""

ADD_DISK_TO_ARRAY_MUTATION = """
    mutation AddDiskToArray($input: ArrayDiskInput!) {
      array {
        addDiskToArray(input: $input) {
          success
        }
      }
    }
"""

REMOVE_DISK_FROM_ARRAY_MUTATION = """
    mutation RemoveDiskFromArray($input: ArrayDiskInput!) {
      array {
        removeDiskFromArray(input: $input) {
          success
        }
      }
    }
"""

MOUNT_ARRAY_DISK_MUTATION = """
    mutation MountArrayDisk($id: PrefixedID!) {
      array {
        mountArrayDisk(id: $id) {
          success
        }
      }
    }
"""

UNMOUNT_ARRAY_DISK_MUTATION = """
    mutation UnmountArrayDisk($id: PrefixedID!) {
      array {
        unmountArrayDisk(id: $id) {
          success
        }
      }
    }
"""

CLEAR_ARRAY_DISK_STATISTICS_MUTATION = """
    mutation ClearArrayDiskStatistics($id: PrefixedID!) {
      array {
        clearArrayDiskStatistics(id: $id) {
          success
        }
      }
    }
"""
