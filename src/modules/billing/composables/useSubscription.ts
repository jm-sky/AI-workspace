/**
 * Composable for managing subscription state with TanStack Query
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useHandleError } from '@/shared/composables/useHandleError'
import type {
  BillingInterval,
  CreateCheckoutSessionRequest,
  PlanTier,
  UpdateOpenRouterTokenRequest,
} from '../types'
import { BillingRoutePaths } from '../routes'
import { billingService } from '../services/billingService'
import { PLAN_FEATURES } from '../types'

export function useSubscription() {
  const queryClient = useQueryClient()
  const { t } = useI18n()
  const { handleError } = useHandleError()

  // Get current subscription
  const {
    data: subscription,
    isLoading: isLoadingSubscription,
    error: subscriptionError,
    refetch: refetchSubscription,
  } = useQuery({
    queryKey: ['subscription'],
    queryFn: () => billingService.getSubscription(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Get subscription limits
  const {
    data: limits,
    isLoading: isLoadingLimits,
    error: limitsError,
  } = useQuery({
    queryKey: ['subscription', 'limits'],
    queryFn: () => billingService.getSubscriptionLimits(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Create checkout session mutation
  const createCheckoutMutation = useMutation({
    mutationFn: (request: CreateCheckoutSessionRequest) =>
      billingService.createCheckoutSession(request),
    onSuccess: (data) => {
      // Redirect to Stripe Checkout
      window.location.href = data.sessionUrl
    },
    onError: (error) => {
      handleError(error, {
        fallbackMessage: t('billing.errors.checkoutFailed', 'Failed to create checkout session. Please try again.'),
      })
    },
  })

  // Create portal session mutation
  const createPortalMutation = useMutation({
    mutationFn: () =>
      billingService.createPortalSession({
        returnUrl: window.location.href,
      }),
    onSuccess: (data) => {
      // Redirect to Stripe Billing Portal
      window.location.href = data.sessionUrl
    },
    onError: (error) => {
      handleError(error, {
        fallbackMessage: t('billing.errors.portalFailed', 'Failed to open billing portal. Please try again.'),
      })
    },
  })

  // Cancel subscription mutation
  const cancelSubscriptionMutation = useMutation({
    mutationFn: () => billingService.cancelSubscription(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription'] })
    },
  })

  // Update OpenRouter token mutation
  const updateOpenRouterTokenMutation = useMutation({
    mutationFn: (request: UpdateOpenRouterTokenRequest) =>
      billingService.updateOpenRouterToken(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription'] })
    },
  })

  // Computed properties
  const currentPlan = computed(() => subscription.value?.planTier || 'free')
  const currentPlanFeatures = computed(() => PLAN_FEATURES[currentPlan.value])
  const isFreeTier = computed(() => currentPlan.value === 'free')
  const isProTier = computed(() => currentPlan.value === 'pro')
  const isProPlusTier = computed(() => currentPlan.value === 'pro_plus')
  const isPaidTier = computed(() => isProTier.value || isProPlusTier.value)
  const isGrandfathered = computed(() => subscription.value?.isGrandfathered || false)
  const isCanceled = computed(() => subscription.value?.status === 'canceled')
  const isPastDue = computed(() => subscription.value?.status === 'past_due')
  const cancelAtPeriodEnd = computed(() => subscription.value?.cancelAtPeriodEnd || false)

  const hasActiveSubscription = computed(
    () => subscription.value?.status === 'active' && !cancelAtPeriodEnd.value,
  )

  // Helper functions
  const canUpgradeTo = (targetPlan: PlanTier) => {
    if (isGrandfathered.value) return false
    if (currentPlan.value === 'free') return targetPlan !== 'free'
    if (currentPlan.value === 'pro') return targetPlan === 'pro_plus'
    return false
  }

  const canDowngradeTo = (targetPlan: PlanTier) => {
    if (isGrandfathered.value) return false
    if (currentPlan.value === 'pro_plus') return targetPlan !== 'pro_plus'
    if (currentPlan.value === 'pro') return targetPlan === 'free'
    return false
  }

  const upgradeToPlan = async (planTier: Exclude<PlanTier, 'free'>, billingInterval: BillingInterval) => {
    const successUrl = `${window.location.origin}${BillingRoutePaths.success}`
    const cancelUrl = `${window.location.origin}${BillingRoutePaths.cancel}`

    await createCheckoutMutation.mutateAsync({
      planTier,
      billingInterval,
      successUrl,
      cancelUrl,
    })
  }

  const openBillingPortal = async () => {
    await createPortalMutation.mutateAsync()
  }

  const cancelSubscription = async () => {
    await cancelSubscriptionMutation.mutateAsync()
  }

  const updateOpenRouterToken = async (token: string | null) => {
    await updateOpenRouterTokenMutation.mutateAsync({
      openrouterApiToken: token,
    })
  }

  return {
    // Data
    subscription,
    limits,
    currentPlan,
    currentPlanFeatures,

    // Loading states
    isLoadingSubscription,
    isLoadingLimits,
    isLoading: computed(() => isLoadingSubscription.value || isLoadingLimits.value),

    // Errors
    subscriptionError,
    limitsError,
    error: computed(() => subscriptionError.value || limitsError.value),

    // Computed flags
    isFreeTier,
    isProTier,
    isProPlusTier,
    isPaidTier,
    isGrandfathered,
    isCanceled,
    isPastDue,
    cancelAtPeriodEnd,
    hasActiveSubscription,

    // Helper functions
    canUpgradeTo,
    canDowngradeTo,

    // Actions
    upgradeToPlan,
    openBillingPortal,
    cancelSubscription,
    updateOpenRouterToken,
    refetchSubscription,

    // Mutation states
    isUpgrading: computed(() => createCheckoutMutation.isPending.value),
    isOpeningPortal: computed(() => createPortalMutation.isPending.value),
    isCanceling: computed(() => cancelSubscriptionMutation.isPending.value),
    isUpdatingToken: computed(() => updateOpenRouterTokenMutation.isPending.value),
  }
}
