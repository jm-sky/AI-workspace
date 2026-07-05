import type { RouteRecordRaw } from 'vue-router'

export const AiRouteName = {
  History: 'ai-history',
} as const

export const AiRoutePath = {
  History: '/ai/history',
} as const

export const aiRoutes: RouteRecordRaw[] = [
  {
    path: AiRoutePath.History,
    name: AiRouteName.History,
    component: () => import('../pages/AiHistoryPage.vue'),
    meta: { layout: 'authenticated', title: 'ai.history.title' },
  },
]

