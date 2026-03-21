"""GraphQL queries and mutations for array disk administration."""

LIST_ASSIGNABLE_DISKS_QUERY = """
    query ListAssignableDisks {
      assignableDisks {
        id
        name
        device
        size
        serial
        vendor
        model
        status
      }
    }
"""

ADD_DISK_TO_ARRAY_MUTATION = """
    mutation AddDiskToArray($input: ArrayDiskInput!) {
      addDiskToArray(input: $input) {
        success
      }
    }
"""

REMOVE_DISK_FROM_ARRAY_MUTATION = """
    mutation RemoveDiskFromArray($input: ArrayDiskInput!) {
      removeDiskFromArray(input: $input) {
        success
      }
    }
"""

MOUNT_ARRAY_DISK_MUTATION = """
    mutation MountArrayDisk($input: ArrayDiskInput!) {
      mountArrayDisk(input: $input) {
        success
      }
    }
"""

UNMOUNT_ARRAY_DISK_MUTATION = """
    mutation UnmountArrayDisk($input: ArrayDiskInput!) {
      unmountArrayDisk(input: $input) {
        success
      }
    }
"""

CLEAR_ARRAY_DISK_STATISTICS_MUTATION = """
    mutation ClearArrayDiskStatistics($input: ArrayDiskInput!) {
      clearArrayDiskStatistics(input: $input) {
        success
      }
    }
"""
