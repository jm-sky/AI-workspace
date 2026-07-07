import type { RouteRecordRaw } from 'vue-router'

export const WorkspaceRouteName = {
  Chat: 'workspace-chat',
} as const

export const WorkspaceRoutePath = {
  Chat: '/workspace',
} as const

export const workspaceRoutes: RouteRecordRaw[] = [
  {
    path: WorkspaceRoutePath.Chat,
    name: WorkspaceRouteName.Chat,
    component: () => import('../pages/WorkspaceChatPage.vue'),
    meta: { layout: 'authenticated', title: 'workspace.chat.title' },
  },
]
