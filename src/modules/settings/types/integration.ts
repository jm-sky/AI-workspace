export type IntegrationVisibilityScope = 'user' | 'team' | 'tenant'

export interface IntegrationScopeOption {
  id: string
  labelKey: string
  descriptionKey: string
  required: boolean
}

export interface IntegrationProviderSetup {
  id: string
  enabled: boolean
  kind?: 'oauth_app' | 'github_app'
  scopes: IntegrationScopeOption[]
}

export interface IntegrationSetup {
  tenantId: string
  tenantRole: string
  canManageShared: boolean
  teams: Array<{ id: string, name: string }>
  providers: IntegrationProviderSetup[]
}

export interface IntegrationConnection {
  id: string
  provider: string
  visibilityScope: IntegrationVisibilityScope
  tenantId?: string | null
  teamId?: string | null
  teamName?: string | null
  ownerUserId: string
  isOwner: boolean
  expiresAt?: string | null
  scopes?: string | null
  hasRefreshToken: boolean
  providerMetadata?: Record<string, unknown> | null
  canManage: boolean
}

export interface IntegrationAuthUrlResponse {
  authUrl: string
  state: string
}

export interface IntegrationConnectRequest {
  provider: string
  scopes: string[]
  visibilityScope: IntegrationVisibilityScope
  teamId?: string | null
}

export interface IntegrationOAuthCallbackRequest {
  code: string
  state: string
}
