import { apiClient } from '@/shared/services/apiClient'
import type {
  IAdminSubscription,
  IAdminSubscriptionStats,
  IAdminUpdateSubscriptionRequest,
  IAdminUser,
} from '../types/admin.types'
import type { TUUID } from '@/shared/types/base.type'

class AdminApiService {
  async getUsers(skip = 0, limit = 100): Promise<IAdminUser[]> {
    const response = await apiClient.get<IAdminUser[]>('/admin/users', {
      params: { skip, limit },
    })
    return response.data
  }

  async getUser(id: TUUID): Promise<IAdminUser> {
    const response = await apiClient.get<IAdminUser>(`/admin/users/${id}`)
    return response.data
  }

  async updateUser(id: TUUID, data: { role?: 'user' | 'admin' | 'premium'; name?: string; email?: string; isActive?: boolean }): Promise<IAdminUser> {
    const response = await apiClient.patch<IAdminUser>(`/admin/users/${id}`, data)
    return response.data
  }

  async deleteUser(id: TUUID): Promise<void> {
    await apiClient.delete(`/admin/users/${id}`)
  }

  async getSubscriptions(skip = 0, limit = 100): Promise<IAdminSubscription[]> {
    const response = await apiClient.get<IAdminSubscription[]>('/billing/admin/subscriptions', {
      params: { skip, limit },
    })
    return response.data
  }

  async getSubscriptionStats(): Promise<IAdminSubscriptionStats> {
    const response = await apiClient.get<IAdminSubscriptionStats>('/billing/admin/subscriptions/stats')
    return response.data
  }

  async updateSubscription(subscriptionId: TUUID, data: IAdminUpdateSubscriptionRequest): Promise<IAdminSubscription> {
    const response = await apiClient.patch<IAdminSubscription>(`/billing/admin/subscriptions/${subscriptionId}`, data)
    return response.data
  }

  async cancelSubscription(subscriptionId: TUUID, reason?: string): Promise<IAdminSubscription> {
    const response = await apiClient.post<IAdminSubscription>(`/billing/admin/subscriptions/${subscriptionId}/cancel`, {
      reason,
    })
    return response.data
  }
}

export const adminApiService = new AdminApiService()
