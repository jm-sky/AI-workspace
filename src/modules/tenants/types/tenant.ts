export interface ITenant {
  id: string
  name: string
  description?: string | null
  role: string
  createdAt: string
}

export interface ITenantListResponse {
  tenants: ITenant[]
}

export interface ITenantCreateRequest {
  name: string
  description?: string | null
}

export interface ISwitchTenantResponse {
  accessToken: string
  refreshToken: string
  tokenType: string
  expiresIn: number
  tenant: ITenant
  teamId?: string | null
}
