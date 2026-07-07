import { adminRoutes } from '@/modules/admin/routes'
import { authRoutes } from '@/modules/auth/config/routes'
import { billingRoutes } from '@/modules/billing/routes'
import { settingsRoutes } from '@/modules/settings/routes'
import { userRoutes } from '@/modules/user/routes'
import { workspaceRoutes } from '@/modules/workspace/routes'
import { publicRoutes } from '@/router/publicRoutes'
import type { RouteRecordRaw } from 'vue-router'

export const routes: RouteRecordRaw[] = [
  // Landing page (public)
  ...publicRoutes.filter(route => route.name === 'landing'),
  // Other public pages (about, cookies, privacy, terms, contact)
  ...publicRoutes.filter(route => route.name !== 'landing' && route.name !== 'not-found'),
  // Module routes
  ...authRoutes,
  ...adminRoutes,
  ...workspaceRoutes,
  ...billingRoutes,
  ...settingsRoutes,
  ...userRoutes,
  // 404 catch-all route - must be last
  ...publicRoutes.filter(route => route.name === 'not-found'),
]
