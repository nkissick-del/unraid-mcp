# Unraid API Coverage Audit

**Date:** 2026-03-21
**Source:** [`unraid/api`](https://github.com/unraid/api) `generated-schema.graphql` (main branch)
**MCP Server State:** 34 tools, 5 resources, 5 subscriptions across 12 modules

---

## Coverage Summary

| Category | Covered | Total | % |
|----------|---------|-------|---|
| Queries | 21 | 57 | 36.8% |
| Mutations | 26 | ~70 | 37.1% |
| Subscriptions | 5 | 16 | 31.3% |
| **Overall** | **52** | **~143** | **36.4%** |

> Note: `query_unraid_api()` acts as a read-only escape hatch for any uncovered query, so effective query coverage is higher for advanced users who can write GraphQL.

---

## Covered Operations

### Queries Covered (21/57)

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

### Mutations Covered (26/~70)

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

### Uncovered Queries (36/57)

| Category | Queries |
|----------|---------|
| API Key Mgmt (8) | `apiKeys`, `apiKey`, `apiKeyPossibleRoles`, `apiKeyPossiblePermissions`, `getPermissionsForRoles`, `previewEffectivePermissions`, `getAvailableAuthActions`, `getApiKeyCreationFormSchema` |
| SSO/OIDC (6) | `isSSOEnabled`, `publicOidcProviders`, `oidcProviders`, `oidcProvider`, `oidcConfiguration`, `validateOidcSession` |
| Plugins (4) | `plugins`, `installedUnraidPlugins`, `pluginInstallOperation`, `pluginInstallOperations` |
| UPS (3) | `upsDevices`, `upsDeviceById`, `upsConfiguration` |
| System (7) | `config`, `display`, `flash`, `me`, `online`, `owner`, `services` |
| Server/Connect (5) | `server`, `servers`, `connect`, `remoteAccess`, `cloud` |
| Metrics (3) | `metrics`, `systemTime`, `timeZoneOptions` |
| Other (5) | `parityHistory`, `customization`, `isFreshInstall`, `publicTheme`, `assignableDisks` |

### Uncovered Mutations (44/~70)

| Category | Mutations | Risk |
|----------|-----------|------|
| Parity Check (4) | `start`, `pause`, `resume`, `cancel` | Critical |
| Array Disk Ops (5) | `addDiskToArray`, `removeDiskFromArray`, `mountArrayDisk`, `unmountArrayDisk`, `clearArrayDiskStatistics` | Critical/Med |
| Docker Batch (3) | `updateContainers`, `updateAllContainers`, `updateAutostartConfiguration` | High/Med |
| Docker Organizer (8) | `createDockerFolder`, `setDockerFolderChildren`, `deleteDockerEntries`, `moveDockerEntriesToFolder`, `moveDockerItemsToPosition`, `renameDockerFolder`, `createDockerFolderWithItems`, `updateDockerViewPreferences` | Low |
| Docker Templates (3) | `syncDockerTemplatePaths`, `resetDockerTemplateMappings`, `refreshDockerDigests` | Low |
| Notifications (7) | `createNotification`, `archiveNotifications` (batch), `notifyIfUnique`, `unreadNotification`, `unarchiveNotifications`, `unarchiveAll`, `recalculateOverview` | Low |
| API Keys (5) | `create`, `addRole`, `removeRole`, `delete`, `update` | Med |
| Plugins (3) | `addPlugin`, `removePlugin`, `installPlugin`, `installLanguage` | High |
| Server Config (5) | `updateServerIdentity`, `updateSshSettings`, `updateSettings`, `updateTemperatureConfig`, `updateSystemTime` | Med/High |
| UPS (1) | `configureUps` | Med |
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

### Existing Modules (12)

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

### New Modules (15)

| Module | New Tools | Default | Risk | Description |
|--------|-----------|---------|------|-------------|
| `system-extra` | 5 queries | yes | Read-only | `config`, `flash`, `services`, `online`, `server`/`servers` |
| `metrics` | 3 queries | yes | Read-only | `metrics`, `systemTime`, `timeZoneOptions` |
| `ups` | 3-4 queries + 1 mutation | yes* | Low/Med | Complete UPS monitoring stack (*mutation gated separately) |
| `plugins` | 4 queries + 2 mutations | no | High | Plugin inventory + install/remove |
| `parity` | 1 query + 4 mutations | no | Critical | `parityHistory` + check lifecycle |
| `array-admin` | 5 mutations | no | Critical | Disk-level array operations |
| `docker-batch` | 3 mutations | no | Destructive | Bulk update operations |
| `docker-organize` | 8 mutations | no | Low | Folder/entry organization |
| `notifications-extra` | 5 mutations | no | Low | Create, unarchive, recalculate |
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
| Current | 34 | 36.8% | 37.1% | 31.3% | 36.4% |
| After Phase 1 | 46 | ~55% | 37.1% | 31.3% | ~45% |
| After Phase 2 | 59 | ~55% | ~56% | 31.3% | ~55% |
| After Phase 3 | 59 | ~55% | ~56% | ~100% | ~60% |
| After Phase 4 | ~120 | ~95% | ~95% | ~100% | ~95% |

> Phases 1-3 deliver ~75% of the practical value. Phase 4 covers operations that are either niche (onboarding, SSO), UI-centric (docker folders, customization), or security-sensitive (auth, connect, remote access) where MCP tools are arguably not the ideal interface.
