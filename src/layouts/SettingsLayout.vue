<script setup lang="ts">
import { HardDrive, Link2, Shield, User } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { cn } from '@/lib/utils'
import { SettingsRoutePaths } from '@/modules/settings/routes'

const { t } = useI18n()
const route = useRoute()

const navItems = computed(() => [
  {
    to: SettingsRoutePaths.account,
    label: t('settings.nav.account'),
    icon: User,
  },
  {
    to: SettingsRoutePaths.security,
    label: t('settings.nav.security'),
    icon: Shield,
  },
  {
    to: SettingsRoutePaths.connections,
    label: t('settings.nav.connections'),
    icon: Link2,
  },
  {
    to: SettingsRoutePaths.storage,
    label: t('settings.nav.storage'),
    icon: HardDrive,
  },
])
</script>

<template>
  <AuthenticatedLayout>
    <div class="mx-auto flex w-full max-w-5xl flex-col gap-6 lg:flex-row lg:gap-10">
      <nav class="shrink-0 lg:w-52">
        <h1 class="mb-4 text-2xl font-bold tracking-tight">
          {{ t('settings.page.title') }}
        </h1>
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
  </AuthenticatedLayout>
</template>
