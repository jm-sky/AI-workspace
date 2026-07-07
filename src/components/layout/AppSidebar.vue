<script setup lang="ts">
import { Info, Settings as SettingsIcon, Sparkles } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from '@/components/ui/sidebar'
import { SettingsRoutePaths } from '@/modules/settings/routes'
import { WorkspaceRoutePath } from '@/modules/workspace/routes'
import { PublicRoutePaths } from '@/router/publicRoutes'

const { t } = useI18n()

const workspaceLinks = computed(() => [
  {
    to: WorkspaceRoutePath.Chat,
    label: t('workspace.nav.chat'),
    icon: Sparkles,
  },
  {
    to: SettingsRoutePaths.settings,
    label: t('workspace.nav.settings'),
    icon: SettingsIcon,
  },
])
</script>

<template>
  <Sidebar collapsible="icon">
    <SidebarContent class="max-h-[90vh] overflow-x-hidden overflow-y-auto">
      <SidebarGroup>
        <SidebarGroupLabel>{{ t('workspace.nav.section') }}</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="link in workspaceLinks" :key="link.to">
              <RouterLink v-slot="{ href, navigate, isActive }" :to="link.to" custom>
                <SidebarMenuButton
                  :is-active="isActive"
                  as="a"
                  :href="href"
                  @click="navigate"
                >
                  <component :is="link.icon" />
                  <span>{{ link.label }}</span>
                </SidebarMenuButton>
              </RouterLink>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <SidebarFooter>
      <SidebarMenu>
        <SidebarMenuItem>
          <RouterLink v-slot="{ href, navigate, isActive }" :to="PublicRoutePaths.about" custom>
            <SidebarMenuButton
              :is-active="isActive"
              as="a"
              :href="href"
              @click="navigate"
            >
              <Info class="size-4" />
              <span>{{ t('common.pages.about', 'About') }}</span>
            </SidebarMenuButton>
          </RouterLink>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarFooter>

    <SidebarRail />
  </Sidebar>
</template>
