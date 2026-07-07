import type { RouteRecordRaw } from 'vue-router'

export const WorkspaceRouteName = {
  Chat: 'workspace-chat',
  Memory: 'workspace-memory',
} as const

export const WorkspaceRoutePath = {
  Chat: '/workspace',
  Memory: '/workspace/memory',
} as const

export const workspaceRoutes: RouteRecordRaw[] = [
  {
    path: WorkspaceRoutePath.Chat,
    name: WorkspaceRouteName.Chat,
    component: () => import('../pages/WorkspaceChatPage.vue'),
    meta: { layout: 'authenticated', title: 'workspace.chat.title' },
  },
  {
    path: WorkspaceRoutePath.Memory,
    name: WorkspaceRouteName.Memory,
    component: () => import('../pages/WorkspaceMemoryPage.vue'),
    meta: { layout: 'authenticated', title: 'workspace.memory.title' },
  },
]
