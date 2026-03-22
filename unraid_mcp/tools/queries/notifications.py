"""GraphQL mutations for notification management.

All notification mutations are top-level (not nested under a namespace).
"""

NOTIFICATION_OVERVIEW_FIELDS = """
    unread {
      info
      warning
      alert
      total
    }
    archive {
      info
      warning
      alert
      total
    }
"""

ARCHIVE_NOTIFICATION_MUTATION = """
    mutation ArchiveNotification($id: PrefixedID!) {
      archiveNotification(id: $id) {
        id
        importance
        subject
        description
        timestamp
      }
    }
"""

ARCHIVE_ALL_NOTIFICATIONS_MUTATION = f"""
    mutation ArchiveAllNotifications($importance: NotificationImportance) {{
      archiveAll(importance: $importance) {{
        {NOTIFICATION_OVERVIEW_FIELDS}
      }}
    }}
"""

DELETE_NOTIFICATION_MUTATION = f"""
    mutation DeleteNotification($id: PrefixedID!, $type: NotificationType!) {{
      deleteNotification(id: $id, type: $type) {{
        {NOTIFICATION_OVERVIEW_FIELDS}
      }}
    }}
"""

DELETE_ARCHIVED_NOTIFICATIONS_MUTATION = f"""
    mutation DeleteArchivedNotifications {{
      deleteArchivedNotifications {{
        {NOTIFICATION_OVERVIEW_FIELDS}
      }}
    }}
"""
