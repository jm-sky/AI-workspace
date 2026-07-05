// modules/billing/routes.ts
// Configurable route paths for billing module
// This allows the billing module to be used in different apps with different route structures

import { CreditCard } from 'lucide-vue-next'
import type { Component } from 'vue'
import type { RouteRecordRaw } from 'vue-router'

export const BILLING_BASE_PATH = import.meta.env.VITE_BILLING_BASE_PATH ?? '/billing'

export const BillingRoutePaths = {
  billing: import.meta.env.VITE_BILLING_PATH ?? `${BILLING_BASE_PATH}`,
  success: import.meta.env.VITE_BILLING_SUCCESS_PATH ?? `${BILLING_BASE_PATH}/success`,
  cancel: import.meta.env.VITE_BILLING_CANCEL_PATH ?? `${BILLING_BASE_PATH}/cancel`,
} as const

// Named route versions (when using Vue Router named routes)
export const BillingRouteNames = {
  billing: 'Billing',
  success: 'BillingSuccess',
  cancel: 'BillingCancel',
} as const

export const BillingRouteIcon: Record<keyof typeof BillingRouteNames, Component> = {
  billing: CreditCard,
  success: CreditCard,
  cancel: CreditCard,
}

export const billingRoutes: RouteRecordRaw[] = [
  {
    path: BillingRoutePaths.billing,
    name: BillingRouteNames.billing,
    component: () => import('./pages/BillingPage.vue'),
    meta: {
      layout: 'authenticated',
      requiresAuth: true,
      title: 'billing.title',
    },
  },
  {
    path: BillingRoutePaths.success,
    name: BillingRouteNames.success,
    component: () => import('./pages/BillingSuccessPage.vue'),
    meta: {
      layout: 'authenticated',
      requiresAuth: true,
      title: 'billing.success.title',
    },
  },
  {
    path: BillingRoutePaths.cancel,
    name: BillingRouteNames.cancel,
    component: () => import('./pages/BillingCancelPage.vue'),
    meta: {
      layout: 'authenticated',
      requiresAuth: true,
      title: 'billing.cancel.title',
    },
  },
]
