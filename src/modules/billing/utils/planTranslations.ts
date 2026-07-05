/**
 * Utility functions for translating plan-related content
 */

import type { PlanTier } from '../types'

type TranslateFunction = (key: string, ...args: unknown[]) => string

/**
 * Maps feature strings from PLAN_FEATURES to translation keys
 */
const featureKeyMap: Record<PlanTier, Record<string, string>> = {
  free: {
    'Basic gear management': 'billing.plans.free.features.basicGearManagement',
    'Data export (JSON/Markdown)': 'billing.plans.free.features.dataExport',
    'BYOK: Bring Your Own API Key (OpenRouter)': 'billing.plans.free.features.byok',
    '100 MB storage': 'billing.plans.free.features.storage',
    '2,000 items limit': 'billing.plans.free.features.itemsLimit',
    '100 containers limit': 'billing.plans.free.features.containersLimit',
  },
  pro: {
    'Everything in Free': 'billing.plans.pro.features.everythingInFree',
    'AI-powered gear recommendations': 'billing.plans.pro.features.aiRecommendations',
    '~$1 worth of AI tokens/month': 'billing.plans.pro.features.aiTokens',
    'Advanced features': 'billing.plans.pro.features.advancedFeatures',
    '5 GB storage': 'billing.plans.pro.features.storage',
    '10,000 items limit': 'billing.plans.pro.features.itemsLimit',
    '250 containers limit': 'billing.plans.pro.features.containersLimit',
  },
  pro_plus: {
    'Everything in Pro': 'billing.plans.pro_plus.features.everythingInPro',
    'Priority AI processing': 'billing.plans.pro_plus.features.priorityAi',
    '~$10 worth of AI tokens/month': 'billing.plans.pro_plus.features.aiTokens',
    'Premium support': 'billing.plans.pro_plus.features.premiumSupport',
    '50 GB storage': 'billing.plans.pro_plus.features.storage',
    '50,000 items limit': 'billing.plans.pro_plus.features.itemsLimit',
    '500 containers limit': 'billing.plans.pro_plus.features.containersLimit',
  },
}

/**
 * Get translated features for a plan tier
 */
export function getTranslatedFeatures(
  planTier: PlanTier,
  features: string[],
  t: TranslateFunction,
): string[] {
  const keyMap = featureKeyMap[planTier]
  
  return features.map((feature) => {
    const translationKey = keyMap[feature]
    return translationKey ? t(translationKey) : feature
  })
}

/**
 * Get translated plan name with suffix
 */
export function getTranslatedPlanName(planTier: PlanTier, t: TranslateFunction): string {
  const planKey = `billing.plans.${planTier}.fullName` as const
  return t(planKey)
}

