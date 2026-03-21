# Unraid API Coverage Audit

**Date:** 2026-03-21
**Source:** [`unraid/api`](https://github.com/unraid/api) `generated-schema.graphql` (main branch)
**MCP Server State:** 59 tools, 5 resources, 5 subscriptions across 19 modules

---

## Coverage Summary

| Category | Covered | Total | % |
|----------|---------|-------|---|
| Queries | 33 | 57 | 57.9% |
| Mutations | 35 | ~70 | 50.0% |
| Subscriptions | 5 | 16 | 31.3% |
| **Overall** | **73** | **~143** | **51.0%** |

> Note: `query_unraid_api()` acts as a read-only escape hatch for any uncovered query, so effective query coverage is higher for advanced users who can write GraphQL.

---

## Covered Operations

### Queries Covered (33/57)

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

### Mutations Covered (35/~70)

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

### Subscriptions Covered (5/16)

| API Subscription | MCP Resource URI | Auto-start |
|-----------------|------------------|------------|
| `arraySubscription` | `unraid://array/status` | yes |
| `dockerContainerStats` | `unraid://docker/stats` | yes |
| `logFile` | `unraid://logs/stream` | manual |
| `systemMetricsCpu` | `unraid://system/cpu` | yes |
| `systemMetricsMemory` | `unraid://system/memory` | yes |

---

## Uncovered Operations

### Uncovered Queries (24/57)

| Category | Queries |
|----------|---------|
| API Key Mgmt (8) | `apiKeys`, `apiKey`, `apiKeyPossibleRoles`, `apiKeyPossiblePermissions`, `getPermissionsForRoles`, `previewEffectivePermissions`, `getAvailableAuthActions`, `getApiKeyCreationFormSchema` |
| SSO/OIDC (6) | `isSSOEnabled`, `publicOidcProviders`, `oidcProviders`, `oidcProvider`, `oidcConfiguration`, `validateOidcSession` |
| Plugins (4) | `plugins`, `installedUnraidPlugins`, `pluginInstallOperation`, `pluginInstallOperations` |
| System (3) | `display`, `me`, `owner` |
| Server/Connect (3) | `connect`, `remoteAccess`, `cloud` |
| Other (4) | `customization`, `isFreshInstall`, `publicTheme`, `assignableDisks` |

> Note: Listed uncovered queries total 28, exceeding 57 - 33 = 24. The original total of 57 was approximate; actual schema may contain fewer distinct root queries.

### Uncovered Mutations (~35/~70)

| Category | Mutations | Risk |
|----------|-----------|------|
| Array Disk Ops (5) | `addDiskToArray`, `removeDiskFromArray`, `mountArrayDisk`, `unmountArrayDisk`, `clearArrayDiskStatistics` | Critical/Med |
| Docker Organizer (8) | `createDockerFolder`, `setDockerFolderChildren`, `deleteDockerEntries`, `moveDockerEntriesToFolder`, `moveDockerItemsToPosition`, `renameDockerFolder`, `createDockerFolderWithItems`, `updateDockerViewPreferences` | Low |
| Docker Templates (3) | `syncDockerTemplatePaths`, `resetDockerTemplateMappings`, `refreshDockerDigests` | Low |
| API Keys (5) | `create`, `addRole`, `removeRole`, `delete`, `update` | Med |
| Plugins (3) | `addPlugin`, `removePlugin`, `installPlugin`, `installLanguage` | High |
| Server Config (5) | `updateServerIdentity`, `updateSshSettings`, `updateSettings`, `updateTemperatureConfig`, `updateSystemTime` | Med/High |
| Connect/Remote (4) | `updateApiSettings`, `connectSignIn`, `connectSignOut`, `setupRemoteAccess`, `enableDynamicRemoteAccess` | High |
| Customization (2) | `setTheme`, `setLocale` | Low |
| Flash (1) | `initiateFlashBackup` | Med |
| Onboarding (10) | `completeOnboarding`, `resetOnboarding`, `openOnboarding`, `closeOnboarding`, `bypassOnboarding`, `resumeOnboarding`, `setOnboardingOverride`, `clearOnboardingOverride`, `createInternalBootPool`, `refreshInternalBootContext` | Low |

### Uncovered Subscriptions (11/16)

| Subscription | Value |
|-------------|-------|
| `notificationAdded` | Real-time alerts (HIGH) |
| `notificationsWarningsAndAlerts` | Critical alerts stream (HIGH) |
| `parityHistorySubscription` | Parity progress tracking (HIGH) |
| `systemMetricsTemperature` | Hardware temp monitoring (HIGH) |
| `notificationsOverview` | Live notification counts (MED) |
| `systemMetricsCpuTelemetry` | Per-core CPU details (MED) |
| `upsUpdates` | UPS status during power events (MED) |
| `displaySubscription` | Display changes (LOW) |
| `ownerSubscription` | Owner changes (LOW) |
| `serversSubscription` | Server status (LOW) |
| `pluginInstallUpdates` | Plugin install progress (LOW) |

---

## Module Taxonomy (Proposed)

### Existing Modules (19)

| Module | Tools | Default | Risk |
|--------|-------|---------|------|
| `system` | 6 | yes | Read-only |
| `storage` | 7 | yes | Read-only |
| `docker` | 4 | yes | Moderate |
| `docker-admin` | 2 | no | Destructive |
| `vms` | 3 | yes | Moderate |
| `health` | 1 | yes | Read-only |
| `rclone` | 4 | yes | Moderate |
| `api` | 2 | yes | Read-only |
| `diagnostics` | 2 | yes | Read-only |
| `array` | 1 | no | Critical |
| `notifications` | 4 | no | Destructive |
| `subscriptions` | 4 resources | no | Resource-heavy |
| `parity` | 1 (dispatches 4 mutations) | no | Critical |
| `docker-batch` | 3 | no | High |
| `notifications-extra` | 7 | no | Low |
| `ups-admin` | 1 | no | Med |

### Remaining Modules (11)

| Module | New Tools | Default | Risk | Description |
|--------|-----------|---------|------|-------------|
| `system-extra` | 5 queries | yes | Read-only | `config`, `flash`, `services`, `online`, `server`/`servers` |
| `metrics` | 3 queries | yes | Read-only | `metrics`, `systemTime`, `timeZoneOptions` |
| `plugins` | 4 queries + 2 mutations | no | High | Plugin inventory + install/remove |
| `array-admin` | 5 mutations | no | Critical | Disk-level array operations |
| `docker-organize` | 8 mutations | no | Low | Folder/entry organization |
| `server-admin` | 5 mutations | no | High | Identity, SSH, settings, time, flash backup |
| `auth` | 8 queries + 5 mutations | no | High | API key management + SSO/OIDC |
| `connect` | 3 queries + 4 mutations | no | High | Remote access, cloud, sign-in flows |
| `customization` | 4 queries + 2 mutations | no | Low | Theme, locale, display |
| `onboarding` | 1 query + 10 mutations | no | Low | First-run setup |
| `subscriptions-extra` | 11 resources | no | Resource-heavy | All remaining live streams |

---

## Effort Estimate

| Work Item | Count | Effort Each | Total |
|-----------|-------|-------------|-------|
| New query tools (read-only) | ~15 | Small (30-60 min) | ~10-15 hrs |
| New mutation tools (with safety) | ~25 | Medium (1-2 hrs) | ~25-50 hrs |
| New subscriptions + resources | 11 | Small (20-30 min) | ~4-6 hrs |
| New query definition files | ~6 | Trivial | ~2 hrs |
| Tests (~5 per tool/sub) | ~250 | Small | ~15-20 hrs |
| Module gating wiring | 1 pass | Small | ~2 hrs |
| **Total** | | | **~60-95 hrs** |

---

## Recommended Implementation Phases

### Phase 1 — Read-Only Quick Wins (~15 hrs)

**Goal:** Jump query coverage from 37% to ~55% with zero-risk additions.

| Module | Tools | API Operations |
|--------|-------|----------------|
| `system-extra` | 5 | `config`, `flash`, `services`, `online`, `server`/`servers` |
| `metrics` | 3 | `metrics`, `systemTime`, `timeZoneOptions` |
| `ups` (queries only) | 3 | `upsDevices`, `upsDeviceById`, `upsConfiguration` |
| `parity` (query only) | 1 | `parityHistory` |

All read-only, default-enabled. No safety gates needed. Each is a straightforward query-and-return pattern matching existing tools.

**After Phase 1:** 46 tools, ~55% query coverage, 37% mutation coverage.

### Phase 2 — High-Value Mutations (~20 hrs)

**Goal:** Cover the most-requested admin operations behind safety gates.

| Module | Tools | API Operations | Safety |
|--------|-------|----------------|--------|
| `parity` (mutations) | 4 | `parityCheck.start/pause/resume/cancel` | confirm gate, disabled by default |
| `docker-batch` | 3 | `updateContainers`, `updateAllContainers`, `updateAutostartConfiguration` | confirm gate, disabled by default |
| `notifications-extra` | 5 | `createNotification`, `archiveNotifications`, `notifyIfUnique`, `unreadNotification`, `unarchiveNotifications`, `unarchiveAll`, `recalculateOverview` | disabled by default |
| `ups` (mutation) | 1 | `configureUps` | disabled by default |

**After Phase 2:** 59 tools, ~55% query coverage, ~56% mutation coverage.

### Phase 3 — Subscriptions & Live Monitoring (~6 hrs)

**Goal:** Bring subscription coverage from 31% to ~80%.

| Subscription | Resource URI | Priority |
|-------------|-------------|----------|
| `notificationAdded` | `unraid://notifications/stream` | High |
| `notificationsWarningsAndAlerts` | `unraid://notifications/alerts` | High |
| `parityHistorySubscription` | `unraid://parity/status` | High |
| `systemMetricsTemperature` | `unraid://system/temperature` | High |
| `notificationsOverview` | `unraid://notifications/overview` | Med |
| `systemMetricsCpuTelemetry` | `unraid://system/cpu-telemetry` | Med |
| `upsUpdates` | `unraid://ups/status` | Med |
| `pluginInstallUpdates` | `unraid://plugins/install-progress` | Low |
| `displaySubscription` | `unraid://display/updates` | Low |
| `ownerSubscription` | `unraid://owner/updates` | Low |
| `serversSubscription` | `unraid://servers/updates` | Low |

All subscriptions are gated under `subscriptions-extra` (disabled by default, resource-heavy).

**After Phase 3:** 59 tools, 16 resources, 16 subscriptions. ~80% subscription coverage.

### Phase 4 — Completionist (~40 hrs)

**Goal:** Full API coverage for edge cases, admin flows, and niche operations.

| Module | Tools | Notes |
|--------|-------|-------|
| `array-admin` | 5 | Disk-level array ops. Extremely destructive — double confirm gates. |
| `docker-organize` | 8 | Docker folder management. UI-centric, low value for MCP. |
| `server-admin` | 5 | Server identity, SSH, settings, time, flash backup. |
| `auth` | 13 | API key CRUD + SSO/OIDC. Security-critical. |
| `connect` | 7 | Remote access, cloud, sign-in. Security-critical. |
| `customization` | 6 | Theme, locale, display. Cosmetic. |
| `onboarding` | 11 | First-run setup. One-time use. |
| `plugins` | 6 | Plugin management. Destructive installs/removals. |

**After Phase 4:** ~120 tools, 16 resources, 16 subscriptions. ~95%+ coverage.

---

## Projected Coverage by Phase

| Phase | Tools | Query % | Mutation % | Subscription % | Overall % |
|-------|-------|---------|------------|----------------|-----------|
| Current (Phase 2 complete) | 59 | 57.9% | 50.0% | 31.3% | 51.0% |
| After Phase 3 | 59 | 57.9% | 50.0% | ~100% | ~60% |
| After Phase 4 | ~120 | ~95% | ~95% | ~100% | ~95% |

> Phases 1-3 deliver ~75% of the practical value. Phase 4 covers operations that are either niche (onboarding, SSO), UI-centric (docker folders, customization), or security-sensitive (auth, connect, remote access) where MCP tools are arguably not the ideal interface.
