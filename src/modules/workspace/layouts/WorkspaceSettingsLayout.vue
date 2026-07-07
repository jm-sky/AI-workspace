<script setup lang="ts">
import { Bot, Plug } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'
import ChatLayout from '@/layouts/ChatLayout.vue'
import { cn } from '@/lib/utils'
import { WorkspaceRoutePath } from '@/modules/workspace/routes'

const { t } = useI18n()
const route = useRoute()

const navItems = computed(() => [
  {
    to: WorkspaceRoutePath.SettingsModels,
    label: t('workspace.settings.models'),
    icon: Bot,
  },
  {
    to: WorkspaceRoutePath.SettingsIntegrations,
    label: t('workspace.settings.integrations'),
    icon: Plug,
  },
])
</script>

<template>
  <ChatLayout>
    <div class="flex min-h-0 flex-1 flex-col gap-6 overflow-y-auto px-4 py-6 sm:px-6">
      <div class="space-y-1">
        <h1 class="text-2xl font-bold tracking-tight">
          {{ t('workspace.nav.workspaceSettings') }}
        </h1>
        <p class="text-sm text-muted-foreground">
          {{ t('workspace.settings.subtitle') }}
        </p>
      </div>

      <div class="flex flex-col gap-6 lg:flex-row lg:gap-10">
        <nav class="shrink-0 lg:w-52">
          <ul class="flex flex-row gap-1 overflow-x-auto lg:flex-col">
            <li v-for="item in navItems" :key="item.to">
              <RouterLink
                :to="item.to"
                :class="cn(
                  'flex items-center gap-2 rounded-md px-3 py-2 text-sm whitespace-nowrap transition-colors',
                  route.path === item.to
                    ? 'bg-accent font-medium text-accent-foreground'
                    : 'text-muted-foreground hover:bg-accent/50 hover:text-foreground',
                )"
              >
                <component :is="item.icon" class="size-4 shrink-0" />
                {{ item.label }}
              </RouterLink>
            </li>
          </ul>
        </nav>

        <div class="min-w-0 flex-1">
          <RouterView />
        </div>
      </div>
    </div>
  </ChatLayout>
</template>
