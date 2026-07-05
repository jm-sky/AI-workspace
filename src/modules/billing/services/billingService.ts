/**
 * Billing API service
 */

import { apiClient } from '@/shared/services/apiClient'
import type {
  CheckoutSessionResponse,
  CreateCheckoutSessionRequest,
  CreatePortalSessionRequest,
  PortalSessionResponse,
  Subscription,
  SubscriptionLimits,
  UpdateOpenRouterTokenRequest,
} from '../types'

export const billingService = {
  /**
   * Get current user's subscription
   */
  async getSubscription(): Promise<Subscription> {
    const response = await apiClient.get<Subscription>('/billing/subscription')
    return response.data
  },

  /**
   * Get subscription feature limits
   */
  async getSubscriptionLimits(): Promise<SubscriptionLimits> {
    const response = await apiClient.get<SubscriptionLimits>('/billing/limits')
    return response.data
  },

  /**
   * Create Stripe Checkout session
   */
  async createCheckoutSession(
    request: CreateCheckoutSessionRequest,
  ): Promise<CheckoutSessionResponse> {
    const response = await apiClient.post<CheckoutSessionResponse>(
      '/billing/checkout',
      request,
    )
    return response.data
  },

  /**
   * Create Stripe Billing Portal session
   */
  async createPortalSession(
    request: CreatePortalSessionRequest,
  ): Promise<PortalSessionResponse> {
    const response = await apiClient.post<PortalSessionResponse>('/billing/portal', request)
    return response.data
  },

  /**
   * Cancel subscription (at period end)
   */
  async cancelSubscription(): Promise<Subscription> {
    const response = await apiClient.post<Subscription>('/billing/cancel')
    return response.data
  },

  /**
   * Update OpenRouter API token (Free tier BYOK)
   */
  async updateOpenRouterToken(
    request: UpdateOpenRouterTokenRequest,
  ): Promise<{ message: string }> {
    const response = await apiClient.put<{ message: string }>(
      '/billing/openrouter-token',
      request,
    )
    return response.data
  },
}
