"""GraphQL mutations for extended notification management.

All notification mutations are top-level (not nested under a namespace).
"""

from .notifications import NOTIFICATION_OVERVIEW_FIELDS

NOTIFICATION_DETAIL_FIELDS = """
    id
    importance
    subject
    description
    timestamp
    type
"""

CREATE_NOTIFICATION_MUTATION = f"""
    mutation CreateNotification($input: NotificationData!) {{
      createNotification(input: $input) {{
        {NOTIFICATION_DETAIL_FIELDS}
      }}
    }}
"""

ARCHIVE_NOTIFICATIONS_BATCH_MUTATION = f"""
    mutation ArchiveNotifications($ids: [String!]!) {{
      archiveNotifications(ids: $ids) {{
        {NOTIFICATION_OVERVIEW_FIELDS}
      }}
    }}
"""

NOTIFY_IF_UNIQUE_MUTATION = f"""
    mutation NotifyIfUnique($input: NotificationData!) {{
      notifyIfUnique(input: $input) {{
        {NOTIFICATION_DETAIL_FIELDS}
      }}
    }}
"""

UNREAD_NOTIFICATION_MUTATION = f"""
    mutation UnreadNotification($id: PrefixedID!) {{
      unreadNotification(id: $id) {{
        {NOTIFICATION_DETAIL_FIELDS}
      }}
    }}
"""

UNARCHIVE_NOTIFICATIONS_MUTATION = f"""
    mutation UnarchiveNotifications($ids: [String!]!) {{
      unarchiveNotifications(ids: $ids) {{
        {NOTIFICATION_OVERVIEW_FIELDS}
      }}
    }}
"""

UNARCHIVE_ALL_NOTIFICATIONS_MUTATION = f"""
    mutation UnarchiveAllNotifications {{
      unarchiveAll {{
        {NOTIFICATION_OVERVIEW_FIELDS}
      }}
    }}
"""

RECALCULATE_NOTIFICATION_OVERVIEW_MUTATION = f"""
    mutation RecalculateNotificationOverview {{
      recalculateOverview {{
        {NOTIFICATION_OVERVIEW_FIELDS}
      }}
    }}
"""
