# Unraid API Coverage Audit

**Date:** 2026-03-21
**Source:** [`unraid/api`](https://github.com/unraid/api) `generated-schema.graphql` (main branch)
**MCP Server State:** 128 tools, 16 resources, 16 subscriptions across 28 modules

---

## Coverage Summary

| Category | Covered | Total | % |
|----------|---------|-------|---|
| Queries | 51 | 57 | 89.5% |
| Mutations | 100 | ~106 | 94.3% |
| Subscriptions | 16 | 16 | 100% |
| **Overall** | **167** | **~179** | **93.3%** |

> Note: `query_unraid_api()` acts as a read-only escape hatch for any uncovered query, so effective query coverage is higher for advanced users who can write GraphQL.

---

## Covered Operations

### Queries Covered (51/57)

| API Query | MCP Tool | Module |
|-----------|----------|--------|
| `info` | `get_system_info()` | system |
| `array` | `get_array_status()` | system |
| `network` | `get_network_config()` | system |
| `registration` | `get_registration_info()` | system |
| `settings` | `get_connect_settings()` | system |
| `vars` | `get_unraid_variables()` | system |
| `shares` | `get_shares_info()` | storage |
| `notifications` (overview) | `get_notifications_overview()` | storage |
| `notifications` (list) | `list_notifications()` | storage |
| `logFiles` | `list_available_log_files()` | storage |
| `logFile` | `get_logs()` | storage |
| `disks` | `list_physical_disks()` | storage |
| `disk` | `get_disk_details()` | storage |
| `docker` (containers) | `list_docker_containers()` | docker |
| `docker` (details) | `get_docker_container_details()` | docker |
| `docker` (logs) | `get_docker_container_logs()` | docker |
| `vms` | `list_vms()` | vms |
| `vms` (details) | `get_vm_details()` | vms |
| `rclone` (remotes) | `list_rclone_remotes()` | rclone |
| `rclone` (configForm) | `get_rclone_config_form()` | rclone |
| `__schema` (introspection) | `introspect_schema()` | api |
| `config` | `get_config_status()` | system-extra |
| `flash` | `get_flash_info()` | system-extra |
| `services` | `list_services()` | system-extra |
| `online` | `get_online_status()` | system-extra |
| `server`/`servers` | `list_servers()` | system-extra |
| `metrics` | `get_system_metrics()` | metrics |
| `systemTime` | `get_system_time()` | metrics |
| `timeZoneOptions` | `list_timezone_options()` | metrics |
| `upsDevices` | `list_ups_devices()` | ups |
| `upsDeviceById` | `get_ups_device()` | ups |
| `upsConfiguration` | `get_ups_configuration()` | ups |
| `parityHistory` | `get_parity_history()` | parity |
| `display` | `get_display_settings()` | customization |
| `me` | `get_current_user()` | customization |
| `owner` | `get_owner_info()` | customization |
| `customization` | `get_customization()` | customization |
| `publicTheme` | `get_public_theme()` | customization |
| `freshInstall` | `is_fresh_install()` | onboarding |
| `plugins` | `list_plugins()` | plugins |
| `installedUnraidPlugins` | `list_installed_unraid_plugins()` | plugins |
| `pluginInstallOperation` | `get_plugin_install_operation()` | plugins |
| `pluginInstallOperations` | `list_plugin_install_operations()` | plugins |
| `connect` | `get_connect_info()` | connect |
| `remoteAccess` | `get_remote_access()` | connect |
| `cloud` | `get_cloud_info()` | connect |
| `apiKeys` | `list_api_keys()` | auth |
| `apiKey` | `get_api_key()` | auth |
| `apiKeyPossibleRoles` | `get_api_key_possible_roles()` | auth |
| `apiKeyPossiblePermissions` | `get_api_key_possible_permissions()` | auth |
| `assignableDisks` | `list_assignable_disks()` | array-admin |

### Mutations Covered (100/~106)

| API Mutation | MCP Tool | Module |
|-------------|----------|--------|
| `array.setState` | `manage_array()` | array |
| `docker.start` | `manage_docker_container("start")` | docker |
| `docker.stop` | `manage_docker_container("stop")` | docker |
| `docker.pause` | `manage_docker_container("pause")` | docker |
| `docker.unpause` | `manage_docker_container("unpause")` | docker |
| `docker.removeContainer` | `remove_docker_container()` | docker-admin |
| `docker.updateContainer` | `update_docker_container()` | docker-admin |
| `vm.start` | `manage_vm("start")` | vms |
| `vm.stop` | `manage_vm("stop")` | vms |
| `vm.pause` | `manage_vm("pause")` | vms |
| `vm.resume` | `manage_vm("resume")` | vms |
| `vm.forceStop` | `manage_vm("forceStop")` | vms |
| `vm.reboot` | `manage_vm("reboot")` | vms |
| `vm.reset` | `manage_vm("reset")` | vms |
| `archiveNotification` | `archive_notification()` | notifications |
| `archiveAll` | `archive_all_notifications()` | notifications |
| `deleteNotification` | `delete_notification()` | notifications |
| `deleteArchivedNotifications` | `delete_archived_notifications()` | notifications |
| `rclone.createRCloneRemote` | `create_rclone_remote()` | rclone |
| `rclone.deleteRCloneRemote` | `delete_rclone_remote()` | rclone |
| `parityCheck.start` | `manage_parity_check("START")` | parity |
| `parityCheck.pause` | `manage_parity_check("PAUSE")` | parity |
| `parityCheck.resume` | `manage_parity_check("RESUME")` | parity |
| `parityCheck.cancel` | `manage_parity_check("CANCEL")` | parity |
| `docker.updateContainers` | `update_docker_containers()` | docker-batch |
| `docker.updateAllContainers` | `update_all_docker_containers()` | docker-batch |
| `docker.updateAutostartConfiguration` | `update_docker_autostart()` | docker-batch |
| `createNotification` | `create_notification()` | notifications-extra |
| `archiveNotifications` | `archive_notifications()` | notifications-extra |
| `notifyIfUnique` | `notify_if_unique()` | notifications-extra |
| `unreadNotification` | `unread_notification()` | notifications-extra |
| `unarchiveNotifications` | `unarchive_notifications()` | notifications-extra |
| `unarchiveAll` | `unarchive_all_notifications()` | notifications-extra |
| `recalculateOverview` | `recalculate_notification_overview()` | notifications-extra |
| `configureUps` | `configure_ups()` | ups-admin |
| `setTheme` | `set_theme()` | customization |
| `setLocale` | `set_locale()` | customization |
| `onboarding.complete` | `complete_onboarding()` | onboarding |
| `onboarding.reset` | `reset_onboarding()` | onboarding |
| `onboarding.open` | `open_onboarding()` | onboarding |
| `onboarding.close` | `close_onboarding()` | onboarding |
| `onboarding.bypass` | `bypass_onboarding()` | onboarding |
| `onboarding.resume` | `resume_onboarding()` | onboarding |
| `onboarding.setOverride` | `set_onboarding_override()` | onboarding |
| `onboarding.clearOverride` | `clear_onboarding_override()` | onboarding |
| `onboarding.createInternalBootPool` | `create_internal_boot_pool()` | onboarding |
| `onboarding.refreshInternalBootContext` | `refresh_internal_boot_context()` | onboarding |
| `docker.createFolder` | `create_docker_folder()` | docker-organize |
| `docker.setFolderChildren` | `set_docker_folder_children()` | docker-organize |
| `docker.deleteEntries` | `delete_docker_entries()` | docker-organize |
| `docker.moveEntriesToFolder` | `move_docker_entries_to_folder()` | docker-organize |
| `docker.moveItemsToPosition` | `move_docker_items_to_position()` | docker-organize |
| `docker.renameFolder` | `rename_docker_folder()` | docker-organize |
| `docker.createFolderWithItems` | `create_docker_folder_with_items()` | docker-organize |
| `docker.updateViewPreferences` | `update_docker_view_preferences()` | docker-organize |
| `docker.syncTemplatePaths` | `sync_docker_template_paths()` | docker-organize |
| `docker.resetTemplateMappings` | `reset_docker_template_mappings()` | docker-organize |
| `docker.refreshDigests` | `refresh_docker_digests()` | docker-organize |
| `addPlugin` | `add_plugin()` | plugins |
| `removePlugin` | `remove_plugin()` | plugins |
| `installPlugin` | `install_plugin()` | plugins |
| `updateServerIdentity` | `update_server_identity()` | server-admin |
| `updateSshSettings` | `update_ssh_settings()` | server-admin |
| `updateSettings` | `update_settings()` | server-admin |
| `updateTemperatureConfig` | `update_temperature_config()` | server-admin |
| `updateSystemTime` | `update_system_time()` | server-admin |
| `initiateFlashBackup` | `initiate_flash_backup()` | server-admin |
| `updateApiSettings` | `update_api_settings()` | connect |
| `connectSignIn` | `connect_sign_in()` | connect |
| `connectSignOut` | `connect_sign_out()` | connect |
| `setupRemoteAccess` | `setup_remote_access()` | connect |
| `enableDynamicRemoteAccess` | `enable_dynamic_remote_access()` | connect |
| `createApiKey` | `create_api_key()` | auth |
| `addRoleToApiKey` | `add_role_to_api_key()` | auth |
| `removeRoleFromApiKey` | `remove_role_from_api_key()` | auth |
| `deleteApiKey` | `delete_api_key()` | auth |
| `updateApiKey` | `update_api_key()` | auth |
| `addDiskToArray` | `add_disk_to_array()` | array-admin |
| `removeDiskFromArray` | `remove_disk_from_array()` | array-admin |
| `mountArrayDisk` | `mount_array_disk()` | array-admin |
| `unmountArrayDisk` | `unmount_array_disk()` | array-admin |
| `clearArrayDiskStatistics` | `clear_array_disk_statistics()` | array-admin |

### Subscriptions Covered (16/16)

| API Subscription | MCP Resource URI | Auto-start | Module |
|-----------------|------------------|------------|--------|
| `arraySubscription` | `unraid://array/status` | yes | subscriptions |
| `dockerContainerStats` | `unraid://docker/stats` | yes | subscriptions |
| `logFile` | `unraid://logs/stream` | manual | base |
| `systemMetricsCpu` | `unraid://system/cpu` | yes | subscriptions |
| `systemMetricsMemory` | `unraid://system/memory` | yes | subscriptions |
| `notificationAdded` | `unraid://notifications/stream` | yes | subscriptions-extra |
| `notificationsWarningsAndAlerts` | `unraid://notifications/alerts` | yes | subscriptions-extra |
| `parityHistorySubscription` | `unraid://parity/status` | yes | subscriptions-extra |
| `systemMetricsTemperature` | `unraid://system/temperature` | yes | subscriptions-extra |
| `notificationsOverview` | `unraid://notifications/overview` | yes | subscriptions-extra |
| `systemMetricsCpuTelemetry` | `unraid://system/cpu-telemetry` | yes | subscriptions-extra |
| `upsUpdates` | `unraid://ups/status` | yes | subscriptions-extra |
| `pluginInstallUpdates` | `unraid://plugins/install-progress` | no (event-driven) | subscriptions-extra |
| `displaySubscription` | `unraid://display/updates` | yes | subscriptions-extra |
| `ownerSubscription` | `unraid://owner/updates` | yes | subscriptions-extra |
| `serversSubscription` | `unraid://servers/updates` | yes | subscriptions-extra |

---

## Uncovered Operations

### Uncovered Queries (6/57)

| Category | Queries |
|----------|---------|
| SSO/OIDC (6) | `isSSOEnabled`, `publicOidcProviders`, `oidcProviders`, `oidcProvider`, `oidcConfiguration`, `validateOidcSession` |

### Uncovered Mutations (~1)

| Category | Mutations | Reason |
|----------|-----------|--------|
| Plugins | `installLanguage` | Unclear schema, niche use case |

> Note: SSO/OIDC mutations (if any exist) are excluded along with their queries.

---

## Module Taxonomy

### All Modules (28)

| Module | Tools | Default | Risk |
|--------|-------|---------|------|
| `system` | 6 | yes | Read-only |
| `storage` | 7 | yes | Read-only |
| `docker` | 4 | yes | Moderate |
| `docker-admin` | 2 | no | Destructive |
| `docker-organize` | 11 | no | Low |
| `docker-batch` | 3 | no | High |
| `vms` | 3 | yes | Moderate |
| `health` | 1 | yes | Read-only |
| `rclone` | 4 | yes | Moderate |
| `api` | 2 | yes | Read-only |
| `diagnostics` | 2 | yes | Read-only |
| `system-extra` | 5 | yes | Read-only |
| `metrics` | 3 | yes | Read-only |
| `ups` | 3 | yes | Read-only |
| `ups-admin` | 1 | no | Med |
| `array` | 1 | no | Critical |
| `array-admin` | 6 | no | Critical |
| `notifications` | 4 | no | Destructive |
| `notifications-extra` | 7 | no | Low |
| `parity` | 1 (dispatches 4 mutations) | no | Critical |
| `subscriptions` | 4 resources | no | Resource-heavy |
| `subscriptions-extra` | 11 resources | no | Resource-heavy |
| *(base)* | 1 resource (logFile) | always | Read-only |
| `customization` | 7 | no | Low |
| `onboarding` | 11 | no | Low |
| `plugins` | 7 | no | High |
| `server-admin` | 6 | no | High |
| `connect` | 8 | no | High |
| `auth` | 13 | no | High |

---

## Deliberately Excluded

| Item | Reason |
|------|--------|
| SSO/OIDC queries (6) | Different auth paradigm (OAuth flows). Future `sso` module if needed. |
| `installLanguage` mutation | Unclear schema, niche use case. |

These 7 items prevent reaching exactly 100% but aren't practical MCP tools.

---

## Projected Coverage by Phase

| Phase | Tools | Query % | Mutation % | Subscription % | Overall % |
|-------|-------|---------|------------|----------------|-----------|
| Phase 1 (complete) | 46 | 57.9% | 37.1% | 31.3% | 43.4% |
| Phase 2 (complete) | 59 | 57.9% | 50.0% | 31.3% | 50.0% |
| Phase 3 (complete) | 59 | 57.9% | 50.0% | 100% | 58.7% |
| **Phase 4 (complete)** | **128** | **89.5%** | **94.3%** | **100%** | **93.3%** |

> Phases 1-3 delivered ~60% of the practical value. Phase 4 covers operations that are either niche (onboarding, SSO), UI-centric (docker folders, customization), or security-sensitive (auth, connect, remote access) where MCP tools need careful safety gates.
