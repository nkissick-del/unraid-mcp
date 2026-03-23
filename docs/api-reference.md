# Unraid GraphQL API Reference

Auto-generated from live API introspection.

## Queries

| Field | Return Type | Description |
|-------|------------|-------------|
| `apiKey`(`id`: PrefixedID!) | `ApiKey` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **API_KEY** |
| `apiKeyPossiblePermissions` | `[Permission!]!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **PERMISSION**  #### Description:  All possible permissions for API keys |
| `apiKeyPossibleRoles` | `[Role!]!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **PERMISSION**  #### Description:  All possible roles for API keys |
| `apiKeys` | `[ApiKey!]!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **API_KEY** |
| `array` | `UnraidArray!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **ARRAY** |
| `assignableDisks` | `[Disk!]!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **DISK** |
| `cloud` | `Cloud!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **CLOUD** |
| `config` | `Config!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **CONFIG** |
| `connect` | `Connect!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **CONNECT** |
| `customization` | `Customization` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **CUSTOMIZATIONS** |
| `disk`(`id`: PrefixedID!) | `Disk!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **DISK** |
| `disks` | `[Disk!]!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **DISK** |
| `display` | `InfoDisplay!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **DISPLAY** |
| `docker` | `Docker!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **DOCKER** |
| `flash` | `Flash!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **FLASH** |
| `getApiKeyCreationFormSchema` | `ApiKeyFormSettings!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **API_KEY**  #### Description:  Get JSON Schema for API key creation form |
| `getAvailableAuthActions` | `[AuthAction!]!` | Get all available authentication actions with possession |
| `getPermissionsForRoles`(`roles`: [Role!]!) | `[Permission!]!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **PERMISSION**  #### Description:  Get the actual permissions that would be granted by a set of roles |
| `info` | `Info!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **INFO** |
| `installedUnraidPlugins` | `[String!]!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **CONFIG**  #### Description:  List installed Unraid OS plugins by .plg filename |
| `internalBootContext` | `OnboardingInternalBootContext!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **WELCOME**  #### Description:  Get the latest onboarding context for configuring internal boot |
| `isFreshInstall` | `Boolean!` | Whether the system is a fresh install (no license key) |
| `isSSOEnabled` | `Boolean!` |  |
| `logFile`(`path`: String!, `lines`: Int, `startLine`: Int) | `LogFileContent!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **LOGS** |
| `logFiles` | `[LogFile!]!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **LOGS** |
| `me` | `UserAccount!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **ME** |
| `metrics` | `Metrics!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **INFO** |
| `network` | `Network!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **NETWORK** |
| `notifications` | `Notifications!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **NOTIFICATIONS**  #### Description:  Get all notifications |
| `oidcConfiguration` | `OidcConfiguration!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **CONFIG**  #### Description:  Get the full OIDC configuration (admin only) |
| `oidcProvider`(`id`: PrefixedID!) | `OidcProvider` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **CONFIG**  #### Description:  Get a specific OIDC provider by ID |
| `oidcProviders` | `[OidcProvider!]!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **CONFIG**  #### Description:  Get all configured OIDC providers (admin only) |
| `online` | `Boolean!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **ONLINE** |
| `owner` | `Owner!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **OWNER** |
| `parityHistory` | `[ParityCheck!]!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **ARRAY** |
| `pluginInstallOperation`(`operationId`: ID!) | `PluginInstallOperation` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **CONFIG**  #### Description:  Retrieve a plugin installation operation by identifier |
| `pluginInstallOperations` | `[PluginInstallOperation!]!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **CONFIG**  #### Description:  List all tracked plugin installation operations |
| `plugins` | `[Plugin!]!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **CONFIG**  #### Description:  List all installed plugins with their metadata |
| `previewEffectivePermissions`(`roles`: [Role!], `permissions`: [AddPermissionInput!]) | `[Permission!]!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **PERMISSION**  #### Description:  Preview the effective permissions for a combination of roles and explicit permissions |
| `publicOidcProviders` | `[PublicOidcProvider!]!` | Get public OIDC provider information for login buttons |
| `publicTheme` | `Theme!` |  |
| `rclone` | `RCloneBackupSettings!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **FLASH** |
| `registration` | `Registration` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **REGISTRATION** |
| `remoteAccess` | `RemoteAccess!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **CONNECT** |
| `server` | `Server` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **SERVERS** |
| `servers` | `[Server!]!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **SERVERS** |
| `services` | `[Service!]!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **SERVICES** |
| `settings` | `Settings!` |  |
| `shares` | `[Share!]!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **SHARE** |
| `systemTime` | `SystemTime!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **VARS**  #### Description:  Retrieve current system time configuration |
| `timeZoneOptions` | `[TimeZoneOption!]!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **CONFIG**  #### Description:  Retrieve available time zone options |
| `upsConfiguration` | `UPSConfiguration!` |  |
| `upsDeviceById`(`id`: String!) | `UPSDevice` |  |
| `upsDevices` | `[UPSDevice!]!` |  |
| `validateOidcSession`(`token`: String!) | `OidcSessionValidation!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **CONFIG**  #### Description:  Validate an OIDC session token (internal use for CLI validation) |
| `vars` | `Vars!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **VARS** |
| `vms` | `Vms!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **VMS**  #### Description:  Get information about all VMs on the system |

## Mutations

| Field | Return Type | Description |
|-------|------------|-------------|
| `addPlugin`(`input`: PluginManagementInput!) | `Boolean!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **CONFIG**  #### Description:  Add one or more plugins to the API. Returns false if restart was triggered automatically, true if manual restart is required. |
| `apiKey` | `ApiKeyMutations!` |  |
| `archiveAll`(`importance`: NotificationImportance) | `NotificationOverview!` |  |
| `archiveNotification`(`id`: PrefixedID!) | `Notification!` | Marks a notification as archived. |
| `archiveNotifications`(`ids`: [PrefixedID!]!) | `NotificationOverview!` |  |
| `array` | `ArrayMutations!` |  |
| `configureUps`(`config`: UPSConfigInput!) | `Boolean!` |  |
| `connectSignIn`(`input`: ConnectSignInInput!) | `Boolean!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **CONNECT** |
| `connectSignOut` | `Boolean!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **CONNECT** |
| `createDockerFolder`(`name`: String!, `parentId`: String, `childrenIds`: [String!]) | `ResolvedOrganizerV1!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **DOCKER** |
| `createDockerFolderWithItems`(`name`: String!, `parentId`: String, `sourceEntryIds`: [String!], `position`: Float) | `ResolvedOrganizerV1!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **DOCKER** |
| `createNotification`(`input`: NotificationData!) | `Notification!` | Creates a new notification record |
| `customization` | `CustomizationMutations!` |  |
| `deleteArchivedNotifications` | `NotificationOverview!` | Deletes all archived notifications on server. |
| `deleteDockerEntries`(`entryIds`: [String!]!) | `ResolvedOrganizerV1!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **DOCKER** |
| `deleteNotification`(`id`: PrefixedID!, `type`: NotificationType!) | `NotificationOverview!` |  |
| `docker` | `DockerMutations!` |  |
| `enableDynamicRemoteAccess`(`input`: EnableDynamicRemoteAccessInput!) | `Boolean!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **CONNECT__REMOTE_ACCESS** |
| `initiateFlashBackup`(`input`: InitiateFlashBackupInput!) | `FlashBackupStatus!` | Initiates a flash drive backup using a configured remote. |
| `moveDockerEntriesToFolder`(`sourceEntryIds`: [String!]!, `destinationFolderId`: String!) | `ResolvedOrganizerV1!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **DOCKER** |
| `moveDockerItemsToPosition`(`sourceEntryIds`: [String!]!, `destinationFolderId`: String!, `position`: Float!) | `ResolvedOrganizerV1!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **DOCKER** |
| `notifyIfUnique`(`input`: NotificationData!) | `Notification` | Creates a notification if an equivalent unread notification does not already exist. |
| `onboarding` | `OnboardingMutations!` |  |
| `parityCheck` | `ParityCheckMutations!` |  |
| `rclone` | `RCloneMutations!` |  |
| `recalculateOverview` | `NotificationOverview!` | Reads each notification to recompute & update the overview. |
| `refreshDockerDigests` | `Boolean!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **DOCKER** |
| `removePlugin`(`input`: PluginManagementInput!) | `Boolean!` | #### Required Permissions:  - Action: **DELETE_ANY** - Resource: **CONFIG**  #### Description:  Remove one or more plugins from the API. Returns false if restart was triggered automatically, true if manual restart is required. |
| `renameDockerFolder`(`folderId`: String!, `newName`: String!) | `ResolvedOrganizerV1!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **DOCKER** |
| `resetDockerTemplateMappings` | `Boolean!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **DOCKER**  #### Description:  Reset Docker template mappings to defaults. Use this to recover from corrupted state. |
| `setDockerFolderChildren`(`folderId`: String, `childrenIds`: [String!]!) | `ResolvedOrganizerV1!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **DOCKER** |
| `setupRemoteAccess`(`input`: SetupRemoteAccessInput!) | `Boolean!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **CONNECT** |
| `syncDockerTemplatePaths` | `DockerTemplateSyncResult!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **DOCKER** |
| `unarchiveAll`(`importance`: NotificationImportance) | `NotificationOverview!` |  |
| `unarchiveNotifications`(`ids`: [PrefixedID!]!) | `NotificationOverview!` |  |
| `unraidPlugins` | `UnraidPluginsMutations!` |  |
| `unreadNotification`(`id`: PrefixedID!) | `Notification!` | Marks a notification as unread. |
| `updateApiSettings`(`input`: ConnectSettingsInput!) | `ConnectSettingsValues!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **CONFIG** |
| `updateDockerViewPreferences`(`viewId`: String, `prefs`: JSON!) | `ResolvedOrganizerV1!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **DOCKER** |
| `updateServerIdentity`(`name`: String!, `comment`: String, `sysModel`: String) | `Server!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **SERVERS**  #### Description:  Update server name, comment, and model |
| `updateSettings`(`input`: JSON!) | `UpdateSettingsResponse!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **CONFIG** |
| `updateSshSettings`(`input`: UpdateSshInput!) | `Vars!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **VARS** |
| `updateSystemTime`(`input`: UpdateSystemTimeInput!) | `SystemTime!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **CONFIG**  #### Description:  Update system time configuration |
| `updateTemperatureConfig`(`input`: TemperatureConfigInput!) | `Boolean!` | #### Required Permissions:  - Action: **UPDATE_ANY** - Resource: **INFO** |
| `vm` | `VmMutations!` |  |

## Subscriptions

| Field | Return Type | Description |
|-------|------------|-------------|
| `arraySubscription` | `UnraidArray!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **ARRAY** |
| `displaySubscription` | `InfoDisplay!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **DISPLAY** |
| `dockerContainerStats` | `DockerContainerStats!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **DOCKER** |
| `logFile`(`path`: String!) | `LogFileContent!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **LOGS** |
| `notificationAdded` | `Notification!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **NOTIFICATIONS** |
| `notificationsOverview` | `NotificationOverview!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **NOTIFICATIONS** |
| `notificationsWarningsAndAlerts` | `[Notification!]!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **NOTIFICATIONS** |
| `ownerSubscription` | `Owner!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **OWNER** |
| `parityHistorySubscription` | `ParityCheck!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **ARRAY** |
| `pluginInstallUpdates`(`operationId`: ID!) | `PluginInstallEvent!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **CONFIG** |
| `serversSubscription` | `Server!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **SERVERS** |
| `systemMetricsCpu` | `CpuUtilization!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **INFO** |
| `systemMetricsCpuTelemetry` | `CpuPackages!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **INFO** |
| `systemMetricsMemory` | `MemoryUtilization!` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **INFO** |
| `systemMetricsTemperature` | `TemperatureMetrics` | #### Required Permissions:  - Action: **READ_ANY** - Resource: **INFO** |
| `upsUpdates` | `UPSDevice!` |  |

## Types

### `AccessUrl` (OBJECT)

| Field | Type |
|-------|------|
| `type` | `URL_TYPE!` |
| `name` | `String` |
| `ipv4` | `URL` |
| `ipv6` | `URL` |

### `AccessUrlInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `type` | `URL_TYPE!` |
| `name` | `String` |
| `ipv4` | `URL` |
| `ipv6` | `URL` |

### `AccessUrlObject` (OBJECT)

| Field | Type |
|-------|------|
| `ipv4` | `String` |
| `ipv6` | `String` |
| `type` | `URL_TYPE!` |
| `name` | `String` |

### `AccessUrlObjectInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `ipv4` | `String` |
| `ipv6` | `String` |
| `type` | `URL_TYPE!` |
| `name` | `String` |

### `ActivationCode` (OBJECT)

| Field | Type |
|-------|------|
| `code` | `String` |
| `partner` | `PartnerConfig` |
| `branding` | `BrandingConfig` |
| `system` | `SystemConfig` |

### `ActivationCodeOverrideInput` (INPUT_OBJECT)

Activation code override input


| Field | Type |
|-------|------|
| `code` | `String` |
| `partner` | `PartnerConfigInput` |
| `branding` | `BrandingConfigInput` |
| `system` | `SystemConfigInput` |

### `AddPermissionInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `resource` | `Resource!` |
| `actions` | `[AuthAction!]!` |

### `AddRoleForApiKeyInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `apiKeyId` | `PrefixedID!` |
| `role` | `Role!` |

### `ApiConfig` (OBJECT)

| Field | Type |
|-------|------|
| `version` | `String!` |
| `extraOrigins` | `[String!]!` |
| `sandbox` | `Boolean` |
| `ssoSubIds` | `[String!]!` |
| `plugins` | `[String!]!` |

### `ApiKey` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `key` | `String!` |
| `name` | `String!` |
| `description` | `String` |
| `roles` | `[Role!]!` |
| `createdAt` | `String!` |
| `permissions` | `[Permission!]!` |

### `ApiKeyFormSettings` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `dataSchema` | `JSON!` |
| `uiSchema` | `JSON!` |
| `values` | `JSON!` |

### `ApiKeyMutations` (OBJECT)

API Key related mutations


| Field | Type |
|-------|------|
| `create` | `ApiKey!` |
| `addRole` | `Boolean!` |
| `removeRole` | `Boolean!` |
| `delete` | `Boolean!` |
| `update` | `ApiKey!` |

### `ApiKeyResponse` (OBJECT)

| Field | Type |
|-------|------|
| `valid` | `Boolean!` |
| `error` | `String` |

### `ArrayCapacity` (OBJECT)

| Field | Type |
|-------|------|
| `kilobytes` | `Capacity!` |
| `disks` | `Capacity!` |

### `ArrayDisk` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `idx` | `Int!` |
| `name` | `String` |
| `device` | `String` |
| `size` | `BigInt` |
| `status` | `ArrayDiskStatus` |
| `rotational` | `Boolean` |
| `temp` | `Int` |
| `numReads` | `BigInt` |
| `numWrites` | `BigInt` |
| `numErrors` | `BigInt` |
| `fsSize` | `BigInt` |
| `fsFree` | `BigInt` |
| `fsUsed` | `BigInt` |
| `exportable` | `Boolean` |
| `type` | `ArrayDiskType!` |
| `warning` | `Int` |
| `critical` | `Int` |
| `fsType` | `String` |
| `comment` | `String` |
| `format` | `String` |
| `transport` | `String` |
| `color` | `ArrayDiskFsColor` |
| `isSpinning` | `Boolean` |

### `ArrayDiskFsColor` (ENUM)

Values: `GREEN_ON`, `GREEN_BLINK`, `BLUE_ON`, `BLUE_BLINK`, `YELLOW_ON`, `YELLOW_BLINK`, `RED_ON`, `RED_OFF`, `GREY_OFF`

### `ArrayDiskInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `slot` | `Int` |

### `ArrayDiskStatus` (ENUM)

Values: `DISK_NP`, `DISK_OK`, `DISK_NP_MISSING`, `DISK_INVALID`, `DISK_WRONG`, `DISK_DSBL`, `DISK_NP_DSBL`, `DISK_DSBL_NEW`, `DISK_NEW`

### `ArrayDiskType` (ENUM)

Values: `DATA`, `PARITY`, `BOOT`, `FLASH`, `CACHE`

### `ArrayMutations` (OBJECT)

| Field | Type |
|-------|------|
| `setState` | `UnraidArray!` |
| `addDiskToArray` | `UnraidArray!` |
| `removeDiskFromArray` | `UnraidArray!` |
| `mountArrayDisk` | `ArrayDisk!` |
| `unmountArrayDisk` | `ArrayDisk!` |
| `clearArrayDiskStatistics` | `Boolean!` |

### `ArrayState` (ENUM)

Values: `STARTED`, `STOPPED`, `NEW_ARRAY`, `RECON_DISK`, `DISABLE_DISK`, `SWAP_DSBL`, `INVALID_EXPANSION`, `PARITY_NOT_BIGGEST`, `TOO_MANY_MISSING_DISKS`, `NEW_DISK_TOO_SMALL`, `NO_DATA_DISKS`

### `ArrayStateInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `desiredState` | `ArrayStateInputState!` |

### `ArrayStateInputState` (ENUM)

Values: `START`, `STOP`

### `AuthAction` (ENUM)

Authentication actions with possession (e.g., create:any, read:own)


Values: `CREATE_ANY`, `CREATE_OWN`, `READ_ANY`, `READ_OWN`, `UPDATE_ANY`, `UPDATE_OWN`, `DELETE_ANY`, `DELETE_OWN`

### `AuthorizationOperator` (ENUM)

Operators for authorization rule matching


Values: `EQUALS`, `CONTAINS`, `ENDS_WITH`, `STARTS_WITH`

### `AuthorizationRuleMode` (ENUM)

Mode for evaluating authorization rules - OR (any rule passes) or AND (all rules must pass)


Values: `OR`, `AND`

### `BrandingConfig` (OBJECT)

| Field | Type |
|-------|------|
| `header` | `String` |
| `headermetacolor` | `String` |
| `background` | `String` |
| `showBannerGradient` | `Boolean` |
| `theme` | `String` |
| `bannerImage` | `String` |
| `caseModel` | `String` |
| `caseModelImage` | `String` |
| `partnerLogoLightUrl` | `String` |
| `partnerLogoDarkUrl` | `String` |
| `hasPartnerLogo` | `Boolean` |
| `onboardingTitle` | `String` |
| `onboardingSubtitle` | `String` |
| `onboardingTitleFreshInstall` | `String` |
| `onboardingSubtitleFreshInstall` | `String` |
| `onboardingTitleUpgrade` | `String` |
| `onboardingSubtitleUpgrade` | `String` |
| `onboardingTitleDowngrade` | `String` |
| `onboardingSubtitleDowngrade` | `String` |
| `onboardingTitleIncomplete` | `String` |
| `onboardingSubtitleIncomplete` | `String` |

### `BrandingConfigInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `header` | `String` |
| `headermetacolor` | `String` |
| `background` | `String` |
| `showBannerGradient` | `Boolean` |
| `theme` | `String` |
| `bannerImage` | `String` |
| `caseModel` | `String` |
| `caseModelImage` | `String` |
| `partnerLogoLightUrl` | `String` |
| `partnerLogoDarkUrl` | `String` |
| `hasPartnerLogo` | `Boolean` |
| `onboardingTitle` | `String` |
| `onboardingSubtitle` | `String` |
| `onboardingTitleFreshInstall` | `String` |
| `onboardingSubtitleFreshInstall` | `String` |
| `onboardingTitleUpgrade` | `String` |
| `onboardingSubtitleUpgrade` | `String` |
| `onboardingTitleDowngrade` | `String` |
| `onboardingSubtitleDowngrade` | `String` |
| `onboardingTitleIncomplete` | `String` |
| `onboardingSubtitleIncomplete` | `String` |

### `Capacity` (OBJECT)

| Field | Type |
|-------|------|
| `free` | `String!` |
| `used` | `String!` |
| `total` | `String!` |

### `Cloud` (OBJECT)

| Field | Type |
|-------|------|
| `error` | `String` |
| `apiKey` | `ApiKeyResponse!` |
| `relay` | `RelayResponse` |
| `minigraphql` | `MinigraphqlResponse!` |
| `cloud` | `CloudResponse!` |
| `allowedOrigins` | `[String!]!` |

### `CloudResponse` (OBJECT)

| Field | Type |
|-------|------|
| `status` | `String!` |
| `ip` | `String` |
| `error` | `String` |

### `Config` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `valid` | `Boolean` |
| `error` | `String` |

### `ConfigErrorState` (ENUM)

Possible error states for configuration


Values: `UNKNOWN_ERROR`, `INELIGIBLE`, `INVALID`, `NO_KEY_SERVER`, `WITHDRAWN`

### `Connect` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `dynamicRemoteAccess` | `DynamicRemoteAccessStatus!` |
| `settings` | `ConnectSettings!` |

### `ConnectSettings` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `dataSchema` | `JSON!` |
| `uiSchema` | `JSON!` |
| `values` | `ConnectSettingsValues!` |

### `ConnectSettingsInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `accessType` | `WAN_ACCESS_TYPE` |
| `forwardType` | `WAN_FORWARD_TYPE` |
| `port` | `Int` |

### `ConnectSettingsValues` (OBJECT)

| Field | Type |
|-------|------|
| `accessType` | `WAN_ACCESS_TYPE!` |
| `forwardType` | `WAN_FORWARD_TYPE` |
| `port` | `Int` |

### `ConnectSignInInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `apiKey` | `String!` |
| `userInfo` | `ConnectUserInfoInput` |

### `ConnectUserInfoInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `preferred_username` | `String!` |
| `email` | `String!` |
| `avatar` | `String` |

### `ContainerHostConfig` (OBJECT)

| Field | Type |
|-------|------|
| `networkMode` | `String!` |

### `ContainerPort` (OBJECT)

| Field | Type |
|-------|------|
| `ip` | `String` |
| `privatePort` | `Port` |
| `publicPort` | `Port` |
| `type` | `ContainerPortType!` |

### `ContainerPortType` (ENUM)

Values: `TCP`, `UDP`

### `ContainerState` (ENUM)

Values: `RUNNING`, `PAUSED`, `EXITED`

### `CoreVersions` (OBJECT)

| Field | Type |
|-------|------|
| `unraid` | `String` |
| `api` | `String` |
| `kernel` | `String` |

### `CpuLoad` (OBJECT)

CPU load for a single core


| Field | Type |
|-------|------|
| `percentTotal` | `Float!` |
| `percentUser` | `Float!` |
| `percentSystem` | `Float!` |
| `percentNice` | `Float!` |
| `percentIdle` | `Float!` |
| `percentIrq` | `Float!` |
| `percentGuest` | `Float!` |
| `percentSteal` | `Float!` |

### `CpuPackages` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `totalPower` | `Float!` |
| `power` | `[Float!]!` |
| `temp` | `[Float!]!` |

### `CpuUtilization` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `percentTotal` | `Float!` |
| `cpus` | `[CpuLoad!]!` |

### `CreateApiKeyInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `name` | `String!` |
| `description` | `String` |
| `roles` | `[Role!]` |
| `permissions` | `[AddPermissionInput!]` |
| `overwrite` | `Boolean` |

### `CreateInternalBootPoolInput` (INPUT_OBJECT)

Input for creating an internal boot pool during onboarding


| Field | Type |
|-------|------|
| `poolName` | `String!` |
| `devices` | `[String!]!` |
| `bootSizeMiB` | `Int!` |
| `updateBios` | `Boolean!` |
| `reboot` | `Boolean` |

### `CreateRCloneRemoteInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `name` | `String!` |
| `type` | `String!` |
| `parameters` | `JSON!` |

### `Customization` (OBJECT)

| Field | Type |
|-------|------|
| `activationCode` | `ActivationCode` |
| `onboarding` | `Onboarding!` |
| `availableLanguages` | `[Language!]` |

### `CustomizationMutations` (OBJECT)

Customization related mutations


| Field | Type |
|-------|------|
| `setTheme` | `Theme!` |
| `setLocale` | `String!` |

### `DeleteApiKeyInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `ids` | `[PrefixedID!]!` |

### `DeleteRCloneRemoteInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `name` | `String!` |

### `Disk` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `device` | `String!` |
| `type` | `String!` |
| `name` | `String!` |
| `vendor` | `String!` |
| `size` | `Float!` |
| `bytesPerSector` | `Float!` |
| `totalCylinders` | `Float!` |
| `totalHeads` | `Float!` |
| `totalSectors` | `Float!` |
| `totalTracks` | `Float!` |
| `tracksPerCylinder` | `Float!` |
| `sectorsPerTrack` | `Float!` |
| `firmwareRevision` | `String!` |
| `serialNum` | `String!` |
| `interfaceType` | `DiskInterfaceType!` |
| `smartStatus` | `DiskSmartStatus!` |
| `temperature` | `Float` |
| `partitions` | `[DiskPartition!]!` |
| `isSpinning` | `Boolean!` |

### `DiskFsType` (ENUM)

The type of filesystem on the disk partition


Values: `XFS`, `BTRFS`, `VFAT`, `ZFS`, `EXT4`, `NTFS`

### `DiskInterfaceType` (ENUM)

The type of interface the disk uses to connect to the system


Values: `SAS`, `SATA`, `USB`, `PCIE`, `UNKNOWN`

### `DiskPartition` (OBJECT)

| Field | Type |
|-------|------|
| `name` | `String!` |
| `fsType` | `DiskFsType!` |
| `size` | `Float!` |

### `DiskSmartStatus` (ENUM)

The SMART (Self-Monitoring, Analysis and Reporting Technology) status of the disk


Values: `OK`, `UNKNOWN`

### `Docker` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `containers` | `[DockerContainer!]!` |
| `networks` | `[DockerNetwork!]!` |
| `portConflicts` | `DockerPortConflicts!` |
| `logs` | `DockerContainerLogs!` |
| `container` | `DockerContainer` |
| `organizer` | `ResolvedOrganizerV1!` |
| `containerUpdateStatuses` | `[ExplicitStatusItem!]!` |

### `DockerAutostartEntryInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `autoStart` | `Boolean!` |
| `wait` | `Int` |

### `DockerContainer` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `names` | `[String!]!` |
| `image` | `String!` |
| `imageId` | `String!` |
| `command` | `String!` |
| `created` | `Int!` |
| `ports` | `[ContainerPort!]!` |
| `lanIpPorts` | `[String!]` |
| `sizeRootFs` | `BigInt` |
| `sizeRw` | `BigInt` |
| `sizeLog` | `BigInt` |
| `labels` | `JSON` |
| `state` | `ContainerState!` |
| `status` | `String!` |
| `hostConfig` | `ContainerHostConfig` |
| `networkSettings` | `JSON` |
| `mounts` | `[JSON!]` |
| `autoStart` | `Boolean!` |
| `autoStartOrder` | `Int` |
| `autoStartWait` | `Int` |
| `templatePath` | `String` |
| `projectUrl` | `String` |
| `registryUrl` | `String` |
| `supportUrl` | `String` |
| `iconUrl` | `String` |
| `webUiUrl` | `String` |
| `shell` | `String` |
| `templatePorts` | `[ContainerPort!]` |
| `isOrphaned` | `Boolean!` |
| `isUpdateAvailable` | `Boolean` |
| `isRebuildReady` | `Boolean` |
| `tailscaleEnabled` | `Boolean!` |
| `tailscaleStatus` | `TailscaleStatus` |

### `DockerContainerLogLine` (OBJECT)

| Field | Type |
|-------|------|
| `timestamp` | `DateTime!` |
| `message` | `String!` |

### `DockerContainerLogs` (OBJECT)

| Field | Type |
|-------|------|
| `containerId` | `PrefixedID!` |
| `lines` | `[DockerContainerLogLine!]!` |
| `cursor` | `DateTime` |

### `DockerContainerPortConflict` (OBJECT)

| Field | Type |
|-------|------|
| `privatePort` | `Port!` |
| `type` | `ContainerPortType!` |
| `containers` | `[DockerPortConflictContainer!]!` |

### `DockerContainerStats` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `cpuPercent` | `Float!` |
| `memUsage` | `String!` |
| `memPercent` | `Float!` |
| `netIO` | `String!` |
| `blockIO` | `String!` |

### `DockerLanPortConflict` (OBJECT)

| Field | Type |
|-------|------|
| `lanIpPort` | `String!` |
| `publicPort` | `Port` |
| `type` | `ContainerPortType!` |
| `containers` | `[DockerPortConflictContainer!]!` |

### `DockerMutations` (OBJECT)

| Field | Type |
|-------|------|
| `start` | `DockerContainer!` |
| `stop` | `DockerContainer!` |
| `pause` | `DockerContainer!` |
| `unpause` | `DockerContainer!` |
| `removeContainer` | `Boolean!` |
| `updateAutostartConfiguration` | `Boolean!` |
| `updateContainer` | `DockerContainer!` |
| `updateContainers` | `[DockerContainer!]!` |
| `updateAllContainers` | `[DockerContainer!]!` |

### `DockerNetwork` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `name` | `String!` |
| `created` | `String!` |
| `scope` | `String!` |
| `driver` | `String!` |
| `enableIPv6` | `Boolean!` |
| `ipam` | `JSON!` |
| `internal` | `Boolean!` |
| `attachable` | `Boolean!` |
| `ingress` | `Boolean!` |
| `configFrom` | `JSON!` |
| `configOnly` | `Boolean!` |
| `containers` | `JSON!` |
| `options` | `JSON!` |
| `labels` | `JSON!` |

### `DockerPortConflictContainer` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `name` | `String!` |

### `DockerPortConflicts` (OBJECT)

| Field | Type |
|-------|------|
| `containerPorts` | `[DockerContainerPortConflict!]!` |
| `lanPorts` | `[DockerLanPortConflict!]!` |

### `DockerTemplateSyncResult` (OBJECT)

| Field | Type |
|-------|------|
| `scanned` | `Int!` |
| `matched` | `Int!` |
| `skipped` | `Int!` |
| `errors` | `[String!]!` |

### `DynamicRemoteAccessStatus` (OBJECT)

| Field | Type |
|-------|------|
| `enabledType` | `DynamicRemoteAccessType!` |
| `runningType` | `DynamicRemoteAccessType!` |
| `error` | `String` |

### `DynamicRemoteAccessType` (ENUM)

Values: `STATIC`, `UPNP`, `DISABLED`

### `EnableDynamicRemoteAccessInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `url` | `AccessUrlInput!` |
| `enabled` | `Boolean!` |

### `ExplicitStatusItem` (OBJECT)

| Field | Type |
|-------|------|
| `name` | `String!` |
| `updateStatus` | `UpdateStatus!` |

### `Flash` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `guid` | `String!` |
| `vendor` | `String!` |
| `product` | `String!` |

### `FlashBackupStatus` (OBJECT)

| Field | Type |
|-------|------|
| `status` | `String!` |
| `jobId` | `String` |

### `FlatOrganizerEntry` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `String!` |
| `type` | `String!` |
| `name` | `String!` |
| `parentId` | `String` |
| `depth` | `Float!` |
| `position` | `Float!` |
| `path` | `[String!]!` |
| `hasChildren` | `Boolean!` |
| `childrenIds` | `[String!]!` |
| `meta` | `DockerContainer` |

### `Info` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `time` | `DateTime!` |
| `baseboard` | `InfoBaseboard!` |
| `cpu` | `InfoCpu!` |
| `devices` | `InfoDevices!` |
| `display` | `InfoDisplay!` |
| `machineId` | `ID` |
| `memory` | `InfoMemory!` |
| `os` | `InfoOs!` |
| `system` | `InfoSystem!` |
| `versions` | `InfoVersions!` |
| `networkInterfaces` | `[InfoNetworkInterface!]!` |
| `primaryNetwork` | `InfoNetworkInterface` |

### `InfoBaseboard` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `manufacturer` | `String` |
| `model` | `String` |
| `version` | `String` |
| `serial` | `String` |
| `assetTag` | `String` |
| `memMax` | `Float` |
| `memSlots` | `Float` |

### `InfoCpu` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `manufacturer` | `String` |
| `brand` | `String` |
| `vendor` | `String` |
| `family` | `String` |
| `model` | `String` |
| `stepping` | `Int` |
| `revision` | `String` |
| `voltage` | `String` |
| `speed` | `Float` |
| `speedmin` | `Float` |
| `speedmax` | `Float` |
| `threads` | `Int` |
| `cores` | `Int` |
| `processors` | `Int` |
| `socket` | `String` |
| `cache` | `JSON` |
| `flags` | `[String!]` |
| `topology` | `[[Unknown]!]!` |
| `packages` | `CpuPackages!` |

### `InfoDevices` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `gpu` | `[InfoGpu!]` |
| `network` | `[InfoNetwork!]` |
| `pci` | `[InfoPci!]` |
| `usb` | `[InfoUsb!]` |

### `InfoDisplay` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `case` | `InfoDisplayCase!` |
| `theme` | `ThemeName!` |
| `unit` | `Temperature!` |
| `scale` | `Boolean!` |
| `tabs` | `Boolean!` |
| `resize` | `Boolean!` |
| `wwn` | `Boolean!` |
| `total` | `Boolean!` |
| `usage` | `Boolean!` |
| `text` | `Boolean!` |
| `warning` | `Int!` |
| `critical` | `Int!` |
| `hot` | `Int!` |
| `max` | `Int` |
| `locale` | `String` |

### `InfoDisplayCase` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `url` | `String!` |
| `icon` | `String!` |
| `error` | `String!` |
| `base64` | `String!` |

### `InfoGpu` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `type` | `String!` |
| `typeid` | `String!` |
| `blacklisted` | `Boolean!` |
| `class` | `String!` |
| `productid` | `String!` |
| `vendorname` | `String` |

### `InfoMemory` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `layout` | `[MemoryLayout!]!` |

### `InfoNetwork` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `iface` | `String!` |
| `model` | `String` |
| `vendor` | `String` |
| `mac` | `String` |
| `virtual` | `Boolean` |
| `speed` | `String` |
| `dhcp` | `Boolean` |

### `InfoNetworkInterface` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `name` | `String!` |
| `description` | `String` |
| `macAddress` | `String` |
| `status` | `String` |
| `protocol` | `String` |
| `ipAddress` | `String` |
| `netmask` | `String` |
| `gateway` | `String` |
| `useDhcp` | `Boolean` |
| `ipv6Address` | `String` |
| `ipv6Netmask` | `String` |
| `ipv6Gateway` | `String` |
| `useDhcp6` | `Boolean` |

### `InfoOs` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `platform` | `String` |
| `distro` | `String` |
| `release` | `String` |
| `codename` | `String` |
| `kernel` | `String` |
| `arch` | `String` |
| `hostname` | `String` |
| `fqdn` | `String` |
| `build` | `String` |
| `servicepack` | `String` |
| `uptime` | `String` |
| `logofile` | `String` |
| `serial` | `String` |
| `uefi` | `Boolean` |

### `InfoPci` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `type` | `String!` |
| `typeid` | `String!` |
| `vendorname` | `String` |
| `vendorid` | `String!` |
| `productname` | `String` |
| `productid` | `String!` |
| `blacklisted` | `String!` |
| `class` | `String!` |

### `InfoSystem` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `manufacturer` | `String` |
| `model` | `String` |
| `version` | `String` |
| `serial` | `String` |
| `uuid` | `String` |
| `sku` | `String` |
| `virtual` | `Boolean` |

### `InfoUsb` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `name` | `String!` |
| `bus` | `String` |
| `device` | `String` |

### `InfoVersions` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `core` | `CoreVersions!` |
| `packages` | `PackageVersions` |

### `InitiateFlashBackupInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `remoteName` | `String!` |
| `sourcePath` | `String!` |
| `destinationPath` | `String!` |
| `options` | `JSON` |

### `InstallPluginInput` (INPUT_OBJECT)

Input payload for installing a plugin


| Field | Type |
|-------|------|
| `url` | `String!` |
| `name` | `String` |
| `forced` | `Boolean` |

### `IpmiConfig` (OBJECT)

| Field | Type |
|-------|------|
| `enabled` | `Boolean` |
| `args` | `[String!]` |

### `IpmiConfigInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `enabled` | `Boolean` |
| `args` | `[String!]` |

### `KeyFile` (OBJECT)

| Field | Type |
|-------|------|
| `location` | `String` |
| `contents` | `String` |

### `Language` (OBJECT)

| Field | Type |
|-------|------|
| `code` | `String!` |
| `name` | `String!` |
| `url` | `String` |

### `LmSensorsConfig` (OBJECT)

| Field | Type |
|-------|------|
| `enabled` | `Boolean` |
| `config_path` | `String` |

### `LmSensorsConfigInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `enabled` | `Boolean` |
| `config_path` | `String` |

### `LogFile` (OBJECT)

| Field | Type |
|-------|------|
| `name` | `String!` |
| `path` | `String!` |
| `size` | `Int!` |
| `modifiedAt` | `DateTime!` |

### `LogFileContent` (OBJECT)

| Field | Type |
|-------|------|
| `path` | `String!` |
| `content` | `String!` |
| `totalLines` | `Int!` |
| `startLine` | `Int` |

### `MemoryLayout` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `size` | `BigInt!` |
| `bank` | `String` |
| `type` | `String` |
| `clockSpeed` | `Int` |
| `partNum` | `String` |
| `serialNum` | `String` |
| `manufacturer` | `String` |
| `formFactor` | `String` |
| `voltageConfigured` | `Int` |
| `voltageMin` | `Int` |
| `voltageMax` | `Int` |

### `MemoryUtilization` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `total` | `BigInt!` |
| `used` | `BigInt!` |
| `free` | `BigInt!` |
| `available` | `BigInt!` |
| `active` | `BigInt!` |
| `buffcache` | `BigInt!` |
| `percentTotal` | `Float!` |
| `swapTotal` | `BigInt!` |
| `swapUsed` | `BigInt!` |
| `swapFree` | `BigInt!` |
| `percentSwapTotal` | `Float!` |

### `Metrics` (OBJECT)

System metrics including CPU and memory utilization


| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `cpu` | `CpuUtilization` |
| `memory` | `MemoryUtilization` |
| `temperature` | `TemperatureMetrics` |

### `MinigraphStatus` (ENUM)

The status of the minigraph


Values: `PRE_INIT`, `CONNECTING`, `CONNECTED`, `PING_FAILURE`, `ERROR_RETRYING`

### `MinigraphqlResponse` (OBJECT)

| Field | Type |
|-------|------|
| `status` | `MinigraphStatus!` |
| `timeout` | `Int` |
| `error` | `String` |

### `Mutation` (OBJECT)

| Field | Type |
|-------|------|
| `createNotification` | `Notification!` |
| `deleteNotification` | `NotificationOverview!` |
| `deleteArchivedNotifications` | `NotificationOverview!` |
| `archiveNotification` | `Notification!` |
| `archiveNotifications` | `NotificationOverview!` |
| `notifyIfUnique` | `Notification` |
| `archiveAll` | `NotificationOverview!` |
| `unreadNotification` | `Notification!` |
| `unarchiveNotifications` | `NotificationOverview!` |
| `unarchiveAll` | `NotificationOverview!` |
| `recalculateOverview` | `NotificationOverview!` |
| `array` | `ArrayMutations!` |
| `docker` | `DockerMutations!` |
| `vm` | `VmMutations!` |
| `parityCheck` | `ParityCheckMutations!` |
| `apiKey` | `ApiKeyMutations!` |
| `customization` | `CustomizationMutations!` |
| `rclone` | `RCloneMutations!` |
| `onboarding` | `OnboardingMutations!` |
| `unraidPlugins` | `UnraidPluginsMutations!` |
| `updateServerIdentity` | `Server!` |
| `updateSshSettings` | `Vars!` |
| `createDockerFolder` | `ResolvedOrganizerV1!` |
| `setDockerFolderChildren` | `ResolvedOrganizerV1!` |
| `deleteDockerEntries` | `ResolvedOrganizerV1!` |
| `moveDockerEntriesToFolder` | `ResolvedOrganizerV1!` |
| `moveDockerItemsToPosition` | `ResolvedOrganizerV1!` |
| `renameDockerFolder` | `ResolvedOrganizerV1!` |
| `createDockerFolderWithItems` | `ResolvedOrganizerV1!` |
| `updateDockerViewPreferences` | `ResolvedOrganizerV1!` |
| `syncDockerTemplatePaths` | `DockerTemplateSyncResult!` |
| `resetDockerTemplateMappings` | `Boolean!` |
| `refreshDockerDigests` | `Boolean!` |
| `initiateFlashBackup` | `FlashBackupStatus!` |
| `updateSettings` | `UpdateSettingsResponse!` |
| `updateTemperatureConfig` | `Boolean!` |
| `updateSystemTime` | `SystemTime!` |
| `configureUps` | `Boolean!` |
| `addPlugin` | `Boolean!` |
| `removePlugin` | `Boolean!` |
| `updateApiSettings` | `ConnectSettingsValues!` |
| `connectSignIn` | `Boolean!` |
| `connectSignOut` | `Boolean!` |
| `setupRemoteAccess` | `Boolean!` |
| `enableDynamicRemoteAccess` | `Boolean!` |

### `Network` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `accessUrls` | `[AccessUrl!]` |

### `Notification` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `title` | `String!` |
| `subject` | `String!` |
| `description` | `String!` |
| `importance` | `NotificationImportance!` |
| `link` | `String` |
| `type` | `NotificationType!` |
| `timestamp` | `String` |
| `formattedTimestamp` | `String` |

### `NotificationCounts` (OBJECT)

| Field | Type |
|-------|------|
| `info` | `Int!` |
| `warning` | `Int!` |
| `alert` | `Int!` |
| `total` | `Int!` |

### `NotificationData` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `title` | `String!` |
| `subject` | `String!` |
| `description` | `String!` |
| `importance` | `NotificationImportance!` |
| `link` | `String` |

### `NotificationFilter` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `importance` | `NotificationImportance` |
| `type` | `NotificationType!` |
| `offset` | `Int!` |
| `limit` | `Int!` |

### `NotificationImportance` (ENUM)

Values: `ALERT`, `INFO`, `WARNING`

### `NotificationOverview` (OBJECT)

| Field | Type |
|-------|------|
| `unread` | `NotificationCounts!` |
| `archive` | `NotificationCounts!` |

### `NotificationType` (ENUM)

Values: `UNREAD`, `ARCHIVE`

### `Notifications` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `overview` | `NotificationOverview!` |
| `list` | `[Notification!]!` |
| `warningsAndAlerts` | `[Notification!]!` |

### `OidcAuthorizationRule` (OBJECT)

| Field | Type |
|-------|------|
| `claim` | `String!` |
| `operator` | `AuthorizationOperator!` |
| `value` | `[String!]!` |

### `OidcConfiguration` (OBJECT)

| Field | Type |
|-------|------|
| `providers` | `[OidcProvider!]!` |
| `defaultAllowedOrigins` | `[String!]` |

### `OidcProvider` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `name` | `String!` |
| `clientId` | `String!` |
| `clientSecret` | `String` |
| `issuer` | `String` |
| `authorizationEndpoint` | `String` |
| `tokenEndpoint` | `String` |
| `jwksUri` | `String` |
| `scopes` | `[String!]!` |
| `authorizationRules` | `[OidcAuthorizationRule!]` |
| `authorizationRuleMode` | `AuthorizationRuleMode` |
| `buttonText` | `String` |
| `buttonIcon` | `String` |
| `buttonVariant` | `String` |
| `buttonStyle` | `String` |

### `OidcSessionValidation` (OBJECT)

| Field | Type |
|-------|------|
| `valid` | `Boolean!` |
| `username` | `String` |

### `Onboarding` (OBJECT)

Onboarding completion state and context


| Field | Type |
|-------|------|
| `status` | `OnboardingStatus!` |
| `isPartnerBuild` | `Boolean!` |
| `completed` | `Boolean!` |
| `completedAtVersion` | `String` |
| `activationCode` | `String` |
| `onboardingState` | `OnboardingState!` |

### `OnboardingInternalBootContext` (OBJECT)

Current onboarding context for configuring internal boot


| Field | Type |
|-------|------|
| `arrayStopped` | `Boolean!` |
| `bootEligible` | `Boolean` |
| `bootedFromFlashWithInternalBootSetup` | `Boolean!` |
| `enableBootTransfer` | `String` |
| `reservedNames` | `[String!]!` |
| `shareNames` | `[String!]!` |
| `poolNames` | `[String!]!` |
| `assignableDisks` | `[Disk!]!` |

### `OnboardingInternalBootResult` (OBJECT)

Result of attempting internal boot pool setup


| Field | Type |
|-------|------|
| `ok` | `Boolean!` |
| `code` | `Int` |
| `output` | `String!` |

### `OnboardingMutations` (OBJECT)

Onboarding related mutations


| Field | Type |
|-------|------|
| `completeOnboarding` | `Onboarding!` |
| `resetOnboarding` | `Onboarding!` |
| `setOnboardingOverride` | `Onboarding!` |
| `clearOnboardingOverride` | `Onboarding!` |
| `createInternalBootPool` | `OnboardingInternalBootResult!` |
| `refreshInternalBootContext` | `OnboardingInternalBootContext!` |

### `OnboardingOverrideCompletionInput` (INPUT_OBJECT)

Onboarding completion override input


| Field | Type |
|-------|------|
| `completed` | `Boolean` |
| `completedAtVersion` | `String` |

### `OnboardingOverrideInput` (INPUT_OBJECT)

Onboarding override input for testing


| Field | Type |
|-------|------|
| `onboarding` | `OnboardingOverrideCompletionInput` |
| `activationCode` | `ActivationCodeOverrideInput` |
| `partnerInfo` | `PartnerInfoOverrideInput` |
| `registrationState` | `RegistrationState` |

### `OnboardingState` (OBJECT)

| Field | Type |
|-------|------|
| `registrationState` | `RegistrationState` |
| `isRegistered` | `Boolean!` |
| `isFreshInstall` | `Boolean!` |
| `hasActivationCode` | `Boolean!` |
| `activationRequired` | `Boolean!` |

### `OnboardingStatus` (ENUM)

The current onboarding status based on completion state and version relationship


Values: `INCOMPLETE`, `UPGRADE`, `DOWNGRADE`, `COMPLETED`

### `Owner` (OBJECT)

| Field | Type |
|-------|------|
| `username` | `String!` |
| `url` | `String!` |
| `avatar` | `String!` |

### `PackageVersions` (OBJECT)

| Field | Type |
|-------|------|
| `openssl` | `String` |
| `node` | `String` |
| `npm` | `String` |
| `pm2` | `String` |
| `git` | `String` |
| `nginx` | `String` |
| `php` | `String` |
| `docker` | `String` |

### `ParityCheck` (OBJECT)

| Field | Type |
|-------|------|
| `date` | `DateTime` |
| `duration` | `Int` |
| `speed` | `String` |
| `status` | `ParityCheckStatus!` |
| `errors` | `Int` |
| `progress` | `Int` |
| `correcting` | `Boolean` |
| `paused` | `Boolean` |
| `running` | `Boolean` |

### `ParityCheckMutations` (OBJECT)

Parity check related mutations, WIP, response types and functionaliy will change


| Field | Type |
|-------|------|
| `start` | `JSON!` |
| `pause` | `JSON!` |
| `resume` | `JSON!` |
| `cancel` | `JSON!` |

### `ParityCheckStatus` (ENUM)

Values: `NEVER_RUN`, `RUNNING`, `PAUSED`, `COMPLETED`, `CANCELLED`, `FAILED`

### `PartnerConfig` (OBJECT)

| Field | Type |
|-------|------|
| `name` | `String` |
| `url` | `String` |
| `hardwareSpecsUrl` | `String` |
| `manualUrl` | `String` |
| `supportUrl` | `String` |
| `extraLinks` | `[PartnerLink!]` |

### `PartnerConfigInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `name` | `String` |
| `url` | `String` |
| `hardwareSpecsUrl` | `String` |
| `manualUrl` | `String` |
| `supportUrl` | `String` |
| `extraLinks` | `[PartnerLinkInput!]` |

### `PartnerInfoOverrideInput` (INPUT_OBJECT)

Partner info override input


| Field | Type |
|-------|------|
| `partner` | `PartnerConfigInput` |
| `branding` | `BrandingConfigInput` |

### `PartnerLink` (OBJECT)

| Field | Type |
|-------|------|
| `title` | `String!` |
| `url` | `String!` |

### `PartnerLinkInput` (INPUT_OBJECT)

Partner link input for custom links


| Field | Type |
|-------|------|
| `title` | `String!` |
| `url` | `String!` |

### `Permission` (OBJECT)

| Field | Type |
|-------|------|
| `resource` | `Resource!` |
| `actions` | `[AuthAction!]!` |

### `Plugin` (OBJECT)

| Field | Type |
|-------|------|
| `name` | `String!` |
| `version` | `String!` |
| `hasApiModule` | `Boolean` |
| `hasCliModule` | `Boolean` |

### `PluginInstallEvent` (OBJECT)

Emitted event representing progress for a plugin installation


| Field | Type |
|-------|------|
| `operationId` | `ID!` |
| `status` | `PluginInstallStatus!` |
| `output` | `[String!]` |
| `timestamp` | `DateTime!` |

### `PluginInstallOperation` (OBJECT)

Represents a tracked plugin installation operation


| Field | Type |
|-------|------|
| `id` | `ID!` |
| `url` | `String!` |
| `name` | `String` |
| `status` | `PluginInstallStatus!` |
| `createdAt` | `DateTime!` |
| `updatedAt` | `DateTime` |
| `finishedAt` | `DateTime` |
| `output` | `[String!]!` |

### `PluginInstallStatus` (ENUM)

Status of a plugin installation operation


Values: `FAILED`, `QUEUED`, `RUNNING`, `SUCCEEDED`

### `PluginManagementInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `names` | `[String!]!` |
| `bundled` | `Boolean!` |
| `restart` | `Boolean!` |

### `ProfileModel` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `username` | `String!` |
| `url` | `String!` |
| `avatar` | `String!` |

### `PublicOidcProvider` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `ID!` |
| `name` | `String!` |
| `buttonText` | `String` |
| `buttonIcon` | `String` |
| `buttonVariant` | `String` |
| `buttonStyle` | `String` |

### `Query` (OBJECT)

| Field | Type |
|-------|------|
| `apiKeys` | `[ApiKey!]!` |
| `apiKey` | `ApiKey` |
| `apiKeyPossibleRoles` | `[Role!]!` |
| `apiKeyPossiblePermissions` | `[Permission!]!` |
| `getPermissionsForRoles` | `[Permission!]!` |
| `previewEffectivePermissions` | `[Permission!]!` |
| `getAvailableAuthActions` | `[AuthAction!]!` |
| `getApiKeyCreationFormSchema` | `ApiKeyFormSettings!` |
| `config` | `Config!` |
| `display` | `InfoDisplay!` |
| `flash` | `Flash!` |
| `me` | `UserAccount!` |
| `notifications` | `Notifications!` |
| `online` | `Boolean!` |
| `owner` | `Owner!` |
| `internalBootContext` | `OnboardingInternalBootContext!` |
| `registration` | `Registration` |
| `server` | `Server` |
| `servers` | `[Server!]!` |
| `services` | `[Service!]!` |
| `shares` | `[Share!]!` |
| `vars` | `Vars!` |
| `vms` | `Vms!` |
| `parityHistory` | `[ParityCheck!]!` |
| `array` | `UnraidArray!` |
| `customization` | `Customization` |
| `isFreshInstall` | `Boolean!` |
| `publicTheme` | `Theme!` |
| `info` | `Info!` |
| `docker` | `Docker!` |
| `disks` | `[Disk!]!` |
| `assignableDisks` | `[Disk!]!` |
| `disk` | `Disk!` |
| `rclone` | `RCloneBackupSettings!` |
| `logFiles` | `[LogFile!]!` |
| `logFile` | `LogFileContent!` |
| `settings` | `Settings!` |
| `isSSOEnabled` | `Boolean!` |
| `publicOidcProviders` | `[PublicOidcProvider!]!` |
| `oidcProviders` | `[OidcProvider!]!` |
| `oidcProvider` | `OidcProvider` |
| `oidcConfiguration` | `OidcConfiguration!` |
| `validateOidcSession` | `OidcSessionValidation!` |
| `metrics` | `Metrics!` |
| `systemTime` | `SystemTime!` |
| `timeZoneOptions` | `[TimeZoneOption!]!` |
| `upsDevices` | `[UPSDevice!]!` |
| `upsDeviceById` | `UPSDevice` |
| `upsConfiguration` | `UPSConfiguration!` |
| `pluginInstallOperation` | `PluginInstallOperation` |
| `pluginInstallOperations` | `[PluginInstallOperation!]!` |
| `installedUnraidPlugins` | `[String!]!` |
| `plugins` | `[Plugin!]!` |
| `remoteAccess` | `RemoteAccess!` |
| `connect` | `Connect!` |
| `network` | `Network!` |
| `cloud` | `Cloud!` |

### `RCloneBackupConfigForm` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `ID!` |
| `dataSchema` | `JSON!` |
| `uiSchema` | `JSON!` |

### `RCloneBackupSettings` (OBJECT)

| Field | Type |
|-------|------|
| `configForm` | `RCloneBackupConfigForm!` |
| `drives` | `[RCloneDrive!]!` |
| `remotes` | `[RCloneRemote!]!` |

### `RCloneConfigFormInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `providerType` | `String` |
| `showAdvanced` | `Boolean` |
| `parameters` | `JSON` |

### `RCloneDrive` (OBJECT)

| Field | Type |
|-------|------|
| `name` | `String!` |
| `options` | `JSON!` |

### `RCloneMutations` (OBJECT)

RClone related mutations


| Field | Type |
|-------|------|
| `createRCloneRemote` | `RCloneRemote!` |
| `deleteRCloneRemote` | `Boolean!` |

### `RCloneRemote` (OBJECT)

| Field | Type |
|-------|------|
| `name` | `String!` |
| `type` | `String!` |
| `parameters` | `JSON!` |
| `config` | `JSON!` |

### `Registration` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `type` | `registrationType` |
| `keyFile` | `KeyFile` |
| `state` | `RegistrationState` |
| `expiration` | `String` |
| `updateExpiration` | `String` |

### `RegistrationState` (ENUM)

Values: `TRIAL`, `BASIC`, `PLUS`, `PRO`, `STARTER`, `UNLEASHED`, `LIFETIME`, `EEXPIRED`, `EGUID`, `EGUID1`, `ETRIAL`, `ENOKEYFILE`, `ENOKEYFILE1`, `ENOKEYFILE2`, `ENOFLASH`, `ENOFLASH1`, `ENOFLASH2`, `ENOFLASH3`, `ENOFLASH4`, `ENOFLASH5`, `ENOFLASH6`, `ENOFLASH7`, `EBLACKLISTED`, `EBLACKLISTED1`, `EBLACKLISTED2`, `ENOCONN`

### `RelayResponse` (OBJECT)

| Field | Type |
|-------|------|
| `status` | `String!` |
| `timeout` | `String` |
| `error` | `String` |

### `RemoteAccess` (OBJECT)

| Field | Type |
|-------|------|
| `accessType` | `WAN_ACCESS_TYPE!` |
| `forwardType` | `WAN_FORWARD_TYPE` |
| `port` | `Int` |

### `RemoveRoleFromApiKeyInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `apiKeyId` | `PrefixedID!` |
| `role` | `Role!` |

### `ResolvedOrganizerV1` (OBJECT)

| Field | Type |
|-------|------|
| `version` | `Float!` |
| `views` | `[ResolvedOrganizerView!]!` |

### `ResolvedOrganizerView` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `String!` |
| `name` | `String!` |
| `rootId` | `String!` |
| `flatEntries` | `[FlatOrganizerEntry!]!` |
| `prefs` | `JSON` |

### `Resource` (ENUM)

Available resources for permissions


Values: `ACTIVATION_CODE`, `API_KEY`, `ARRAY`, `CLOUD`, `CONFIG`, `CONNECT`, `CONNECT__REMOTE_ACCESS`, `CUSTOMIZATIONS`, `DASHBOARD`, `DISK`, `DISPLAY`, `DOCKER`, `FLASH`, `INFO`, `LOGS`, `ME`, `NETWORK`, `NOTIFICATIONS`, `ONLINE`, `OS`, `OWNER`, `PERMISSION`, `REGISTRATION`, `SERVERS`, `SERVICES`, `SHARE`, `VARS`, `VMS`, `WELCOME`

### `Role` (ENUM)

Available roles for API keys and users


Values: `ADMIN`, `CONNECT`, `GUEST`, `VIEWER`

### `SensorConfig` (OBJECT)

| Field | Type |
|-------|------|
| `enabled` | `Boolean` |

### `SensorConfigInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `enabled` | `Boolean` |

### `SensorType` (ENUM)

Type of temperature sensor


Values: `CPU_PACKAGE`, `CPU_CORE`, `MOTHERBOARD`, `CHIPSET`, `GPU`, `DISK`, `NVME`, `AMBIENT`, `VRM`, `CUSTOM`

### `Server` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `owner` | `ProfileModel!` |
| `guid` | `String!` |
| `apikey` | `String!` |
| `name` | `String!` |
| `comment` | `String` |
| `status` | `ServerStatus!` |
| `wanip` | `String!` |
| `lanip` | `String!` |
| `localurl` | `String!` |
| `remoteurl` | `String!` |

### `ServerStatus` (ENUM)

Values: `ONLINE`, `OFFLINE`, `NEVER_CONNECTED`

### `Service` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `name` | `String` |
| `online` | `Boolean` |
| `uptime` | `Uptime` |
| `version` | `String` |

### `Settings` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `unified` | `UnifiedSettings!` |
| `sso` | `SsoSettings!` |
| `api` | `ApiConfig!` |

### `SetupRemoteAccessInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `accessType` | `WAN_ACCESS_TYPE!` |
| `forwardType` | `WAN_FORWARD_TYPE` |
| `port` | `Int` |

### `Share` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `name` | `String` |
| `free` | `BigInt` |
| `used` | `BigInt` |
| `size` | `BigInt` |
| `include` | `[String!]` |
| `exclude` | `[String!]` |
| `cache` | `Boolean` |
| `nameOrig` | `String` |
| `comment` | `String` |
| `allocator` | `String` |
| `splitLevel` | `String` |
| `floor` | `String` |
| `cow` | `String` |
| `color` | `String` |
| `luksStatus` | `String` |

### `SsoSettings` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `oidcProviders` | `[OidcProvider!]!` |

### `Subscription` (OBJECT)

| Field | Type |
|-------|------|
| `displaySubscription` | `InfoDisplay!` |
| `notificationAdded` | `Notification!` |
| `notificationsOverview` | `NotificationOverview!` |
| `notificationsWarningsAndAlerts` | `[Notification!]!` |
| `ownerSubscription` | `Owner!` |
| `serversSubscription` | `Server!` |
| `parityHistorySubscription` | `ParityCheck!` |
| `arraySubscription` | `UnraidArray!` |
| `dockerContainerStats` | `DockerContainerStats!` |
| `logFile` | `LogFileContent!` |
| `systemMetricsCpu` | `CpuUtilization!` |
| `systemMetricsCpuTelemetry` | `CpuPackages!` |
| `systemMetricsMemory` | `MemoryUtilization!` |
| `systemMetricsTemperature` | `TemperatureMetrics` |
| `upsUpdates` | `UPSDevice!` |
| `pluginInstallUpdates` | `PluginInstallEvent!` |

### `SystemConfig` (OBJECT)

| Field | Type |
|-------|------|
| `serverName` | `String` |
| `model` | `String` |
| `comment` | `String` |

### `SystemConfigInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `serverName` | `String` |
| `model` | `String` |
| `comment` | `String` |

### `SystemTime` (OBJECT)

System time configuration and current status


| Field | Type |
|-------|------|
| `currentTime` | `String!` |
| `timeZone` | `String!` |
| `useNtp` | `Boolean!` |
| `ntpServers` | `[String!]!` |

### `TailscaleExitNodeStatus` (OBJECT)

Tailscale exit node connection status


| Field | Type |
|-------|------|
| `online` | `Boolean!` |
| `tailscaleIps` | `[String!]` |

### `TailscaleStatus` (OBJECT)

Tailscale status for a Docker container


| Field | Type |
|-------|------|
| `online` | `Boolean!` |
| `version` | `String` |
| `latestVersion` | `String` |
| `updateAvailable` | `Boolean!` |
| `hostname` | `String` |
| `dnsName` | `String` |
| `relay` | `String` |
| `relayName` | `String` |
| `tailscaleIps` | `[String!]` |
| `primaryRoutes` | `[String!]` |
| `isExitNode` | `Boolean!` |
| `exitNodeStatus` | `TailscaleExitNodeStatus` |
| `webUiUrl` | `String` |
| `keyExpiry` | `DateTime` |
| `keyExpiryDays` | `Int` |
| `keyExpired` | `Boolean!` |
| `backendState` | `String` |
| `authUrl` | `String` |

### `Temperature` (ENUM)

Temperature unit


Values: `CELSIUS`, `FAHRENHEIT`

### `TemperatureConfigInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `enabled` | `Boolean` |
| `polling_interval` | `Int` |
| `default_unit` | `TemperatureUnit` |
| `sensors` | `TemperatureSensorsConfigInput` |
| `thresholds` | `TemperatureThresholdsConfigInput` |
| `history` | `TemperatureHistoryConfigInput` |

### `TemperatureHistoryConfig` (OBJECT)

| Field | Type |
|-------|------|
| `max_readings` | `Int` |
| `retention_ms` | `Int` |

### `TemperatureHistoryConfigInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `max_readings` | `Int` |
| `retention_ms` | `Int` |

### `TemperatureMetrics` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `sensors` | `[TemperatureSensor!]!` |
| `summary` | `TemperatureSummary!` |

### `TemperatureReading` (OBJECT)

| Field | Type |
|-------|------|
| `value` | `Float!` |
| `unit` | `TemperatureUnit!` |
| `timestamp` | `DateTime!` |
| `status` | `TemperatureStatus!` |

### `TemperatureSensor` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `name` | `String!` |
| `type` | `SensorType!` |
| `location` | `String` |
| `current` | `TemperatureReading!` |
| `min` | `TemperatureReading` |
| `max` | `TemperatureReading` |
| `warning` | `Float` |
| `critical` | `Float` |
| `history` | `[TemperatureReading!]` |

### `TemperatureSensorsConfig` (OBJECT)

| Field | Type |
|-------|------|
| `lm_sensors` | `LmSensorsConfig` |
| `smartctl` | `SensorConfig` |
| `ipmi` | `IpmiConfig` |

### `TemperatureSensorsConfigInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `lm_sensors` | `LmSensorsConfigInput` |
| `smartctl` | `SensorConfigInput` |
| `ipmi` | `IpmiConfigInput` |

### `TemperatureStatus` (ENUM)

Values: `NORMAL`, `WARNING`, `CRITICAL`, `UNKNOWN`

### `TemperatureSummary` (OBJECT)

| Field | Type |
|-------|------|
| `average` | `Float!` |
| `hottest` | `TemperatureSensor!` |
| `coolest` | `TemperatureSensor!` |
| `warningCount` | `Int!` |
| `criticalCount` | `Int!` |

### `TemperatureThresholdsConfig` (OBJECT)

| Field | Type |
|-------|------|
| `cpu_warning` | `Int` |
| `cpu_critical` | `Int` |
| `disk_warning` | `Int` |
| `disk_critical` | `Int` |
| `warning` | `Int` |
| `critical` | `Int` |

### `TemperatureThresholdsConfigInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `cpu_warning` | `Int` |
| `cpu_critical` | `Int` |
| `disk_warning` | `Int` |
| `disk_critical` | `Int` |
| `warning` | `Int` |
| `critical` | `Int` |

### `TemperatureUnit` (ENUM)

Values: `CELSIUS`, `FAHRENHEIT`, `KELVIN`, `RANKINE`

### `Theme` (OBJECT)

| Field | Type |
|-------|------|
| `name` | `ThemeName!` |
| `showBannerImage` | `Boolean!` |
| `showBannerGradient` | `Boolean!` |
| `showHeaderDescription` | `Boolean!` |
| `headerBackgroundColor` | `String` |
| `headerPrimaryTextColor` | `String` |
| `headerSecondaryTextColor` | `String` |

### `ThemeName` (ENUM)

The theme name


Values: `azure`, `black`, `gray`, `white`

### `TimeZoneOption` (OBJECT)

Selectable timezone option from the system list


| Field | Type |
|-------|------|
| `value` | `String!` |
| `label` | `String!` |

### `UPSBattery` (OBJECT)

| Field | Type |
|-------|------|
| `chargeLevel` | `Int!` |
| `estimatedRuntime` | `Int!` |
| `health` | `String!` |

### `UPSCableType` (ENUM)

UPS cable connection types


Values: `USB`, `SIMPLE`, `SMART`, `ETHER`, `CUSTOM`

### `UPSConfigInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `service` | `UPSServiceState` |
| `upsCable` | `UPSCableType` |
| `customUpsCable` | `String` |
| `upsType` | `UPSType` |
| `device` | `String` |
| `overrideUpsCapacity` | `Int` |
| `batteryLevel` | `Int` |
| `minutes` | `Int` |
| `timeout` | `Int` |
| `killUps` | `UPSKillPower` |

### `UPSConfiguration` (OBJECT)

| Field | Type |
|-------|------|
| `service` | `String` |
| `upsCable` | `String` |
| `customUpsCable` | `String` |
| `upsType` | `String` |
| `device` | `String` |
| `overrideUpsCapacity` | `Int` |
| `batteryLevel` | `Int` |
| `minutes` | `Int` |
| `timeout` | `Int` |
| `killUps` | `String` |
| `nisIp` | `String` |
| `netServer` | `String` |
| `upsName` | `String` |
| `modelName` | `String` |

### `UPSDevice` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `ID!` |
| `name` | `String!` |
| `model` | `String!` |
| `status` | `String!` |
| `battery` | `UPSBattery!` |
| `power` | `UPSPower!` |

### `UPSKillPower` (ENUM)

Kill UPS power after shutdown option


Values: `YES`, `NO`

### `UPSPower` (OBJECT)

| Field | Type |
|-------|------|
| `inputVoltage` | `Float!` |
| `outputVoltage` | `Float!` |
| `loadPercentage` | `Int!` |
| `nominalPower` | `Int` |
| `currentPower` | `Float` |

### `UPSServiceState` (ENUM)

Service state for UPS daemon


Values: `ENABLE`, `DISABLE`

### `UPSType` (ENUM)

UPS communication protocols


Values: `USB`, `APCSMART`, `NET`, `SNMP`, `DUMB`, `PCNET`, `MODBUS`

### `URL_TYPE` (ENUM)

Values: `LAN`, `WIREGUARD`, `WAN`, `MDNS`, `OTHER`, `DEFAULT`

### `UnifiedSettings` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `dataSchema` | `JSON!` |
| `uiSchema` | `JSON!` |
| `values` | `JSON!` |

### `UnraidArray` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `state` | `ArrayState!` |
| `capacity` | `ArrayCapacity!` |
| `boot` | `ArrayDisk` |
| `bootDevices` | `[ArrayDisk!]!` |
| `parities` | `[ArrayDisk!]!` |
| `parityCheckStatus` | `ParityCheck!` |
| `disks` | `[ArrayDisk!]!` |
| `caches` | `[ArrayDisk!]!` |

### `UnraidPluginsMutations` (OBJECT)

Unraid plugin management mutations


| Field | Type |
|-------|------|
| `installPlugin` | `PluginInstallOperation!` |
| `installLanguage` | `PluginInstallOperation!` |

### `UpdateApiKeyInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `name` | `String` |
| `description` | `String` |
| `roles` | `[Role!]` |
| `permissions` | `[AddPermissionInput!]` |

### `UpdateSettingsResponse` (OBJECT)

| Field | Type |
|-------|------|
| `restartRequired` | `Boolean!` |
| `values` | `JSON!` |
| `warnings` | `[String!]` |

### `UpdateSshInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `enabled` | `Boolean!` |
| `port` | `Int!` |

### `UpdateStatus` (ENUM)

Update status of a container.


Values: `UP_TO_DATE`, `UPDATE_AVAILABLE`, `REBUILD_READY`, `UNKNOWN`

### `UpdateSystemTimeInput` (INPUT_OBJECT)

| Field | Type |
|-------|------|
| `timeZone` | `String` |
| `useNtp` | `Boolean` |
| `ntpServers` | `[String!]` |
| `manualDateTime` | `String` |

### `Uptime` (OBJECT)

| Field | Type |
|-------|------|
| `timestamp` | `String` |

### `UserAccount` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `name` | `String!` |
| `description` | `String!` |
| `roles` | `[Role!]!` |
| `permissions` | `[Permission!]` |

### `Vars` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `version` | `String` |
| `maxArraysz` | `Int` |
| `maxCachesz` | `Int` |
| `name` | `String` |
| `timeZone` | `String` |
| `comment` | `String` |
| `security` | `String` |
| `workgroup` | `String` |
| `domain` | `String` |
| `domainShort` | `String` |
| `hideDotFiles` | `Boolean` |
| `localMaster` | `Boolean` |
| `enableFruit` | `String` |
| `useNtp` | `Boolean` |
| `ntpServer1` | `String` |
| `ntpServer2` | `String` |
| `ntpServer3` | `String` |
| `ntpServer4` | `String` |
| `domainLogin` | `String` |
| `sysModel` | `String` |
| `sysArraySlots` | `Int` |
| `sysCacheSlots` | `Int` |
| `sysFlashSlots` | `Int` |
| `useSsl` | `Boolean` |
| `port` | `Int` |
| `portssl` | `Int` |
| `localTld` | `String` |
| `bindMgt` | `Boolean` |
| `useTelnet` | `Boolean` |
| `porttelnet` | `Int` |
| `useSsh` | `Boolean` |
| `portssh` | `Int` |
| `startPage` | `String` |
| `startArray` | `Boolean` |
| `spindownDelay` | `String` |
| `queueDepth` | `String` |
| `spinupGroups` | `Boolean` |
| `defaultFormat` | `String` |
| `defaultFsType` | `String` |
| `shutdownTimeout` | `Int` |
| `luksKeyfile` | `String` |
| `pollAttributes` | `String` |
| `pollAttributesDefault` | `String` |
| `pollAttributesStatus` | `String` |
| `nrRequests` | `Int` |
| `nrRequestsDefault` | `Int` |
| `nrRequestsStatus` | `String` |
| `mdNumStripes` | `Int` |
| `mdNumStripesDefault` | `Int` |
| `mdNumStripesStatus` | `String` |
| `mdSyncWindow` | `Int` |
| `mdSyncWindowDefault` | `Int` |
| `mdSyncWindowStatus` | `String` |
| `mdSyncThresh` | `Int` |
| `mdSyncThreshDefault` | `Int` |
| `mdSyncThreshStatus` | `String` |
| `mdWriteMethod` | `Int` |
| `mdWriteMethodDefault` | `String` |
| `mdWriteMethodStatus` | `String` |
| `shareDisk` | `String` |
| `shareUser` | `String` |
| `shareUserInclude` | `String` |
| `shareUserExclude` | `String` |
| `shareSmbEnabled` | `Boolean` |
| `shareNfsEnabled` | `Boolean` |
| `shareAfpEnabled` | `Boolean` |
| `shareInitialOwner` | `String` |
| `shareInitialGroup` | `String` |
| `shareCacheEnabled` | `Boolean` |
| `shareCacheFloor` | `String` |
| `shareMoverSchedule` | `String` |
| `shareMoverLogging` | `Boolean` |
| `fuseRemember` | `String` |
| `fuseRememberDefault` | `String` |
| `fuseRememberStatus` | `String` |
| `fuseDirectio` | `String` |
| `fuseDirectioDefault` | `String` |
| `fuseDirectioStatus` | `String` |
| `shareAvahiEnabled` | `Boolean` |
| `shareAvahiSmbName` | `String` |
| `shareAvahiSmbModel` | `String` |
| `shareAvahiAfpName` | `String` |
| `shareAvahiAfpModel` | `String` |
| `safeMode` | `Boolean` |
| `startMode` | `String` |
| `configValid` | `Boolean` |
| `configError` | `ConfigErrorState` |
| `joinStatus` | `String` |
| `deviceCount` | `Int` |
| `flashGuid` | `String` |
| `flashProduct` | `String` |
| `flashVendor` | `String` |
| `tpmGuid` | `String` |
| `regCheck` | `String` |
| `regFile` | `String` |
| `regGuid` | `String` |
| `regTy` | `registrationType` |
| `regState` | `RegistrationState` |
| `regTo` | `String` |
| `regTm` | `String` |
| `regTm2` | `String` |
| `regGen` | `String` |
| `sbName` | `String` |
| `sbVersion` | `String` |
| `sbUpdated` | `String` |
| `sbEvents` | `Int` |
| `sbState` | `String` |
| `sbClean` | `Boolean` |
| `sbSynced` | `Int` |
| `sbSyncErrs` | `Int` |
| `sbSynced2` | `Int` |
| `sbSyncExit` | `String` |
| `sbNumDisks` | `Int` |
| `mdColor` | `String` |
| `mdNumDisks` | `Int` |
| `mdNumDisabled` | `Int` |
| `mdNumInvalid` | `Int` |
| `mdNumMissing` | `Int` |
| `mdNumNew` | `Int` |
| `mdNumErased` | `Int` |
| `mdResync` | `Int` |
| `mdResyncCorr` | `String` |
| `mdResyncPos` | `String` |
| `mdResyncDb` | `String` |
| `mdResyncDt` | `String` |
| `mdResyncAction` | `String` |
| `mdResyncSize` | `Int` |
| `mdState` | `String` |
| `mdVersion` | `String` |
| `cacheNumDevices` | `Int` |
| `cacheSbNumDisks` | `Int` |
| `fsState` | `String` |
| `bootEligible` | `Boolean` |
| `enableBootTransfer` | `String` |
| `bootedFromFlashWithInternalBootSetup` | `Boolean` |
| `reservedNames` | `String` |
| `fsProgress` | `String` |
| `fsCopyPrcnt` | `Int` |
| `fsNumMounted` | `Int` |
| `fsNumUnmountable` | `Int` |
| `fsUnmountableMask` | `String` |
| `shareCount` | `Int` |
| `shareSmbCount` | `Int` |
| `shareNfsCount` | `Int` |
| `shareAfpCount` | `Int` |
| `shareMoverActive` | `Boolean` |
| `csrfToken` | `String` |

### `VmDomain` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `name` | `String` |
| `state` | `VmState!` |

### `VmMutations` (OBJECT)

| Field | Type |
|-------|------|
| `start` | `Boolean!` |
| `stop` | `Boolean!` |
| `pause` | `Boolean!` |
| `resume` | `Boolean!` |
| `forceStop` | `Boolean!` |
| `reboot` | `Boolean!` |
| `reset` | `Boolean!` |

### `VmState` (ENUM)

The state of a virtual machine


Values: `NOSTATE`, `RUNNING`, `IDLE`, `PAUSED`, `SHUTDOWN`, `SHUTOFF`, `CRASHED`, `PMSUSPENDED`

### `Vms` (OBJECT)

| Field | Type |
|-------|------|
| `id` | `PrefixedID!` |
| `domains` | `[VmDomain!]` |
| `domain` | `[VmDomain!]` |

### `WAN_ACCESS_TYPE` (ENUM)

Values: `DYNAMIC`, `ALWAYS`, `DISABLED`

### `WAN_FORWARD_TYPE` (ENUM)

Values: `UPNP`, `STATIC`

### `registrationType` (ENUM)

Values: `BASIC`, `PLUS`, `PRO`, `STARTER`, `UNLEASHED`, `LIFETIME`, `INVALID`, `TRIAL`
