<script setup lang="ts">
import { Brain, Info, Settings as SettingsIcon } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  useSidebar,
} from '@/components/ui/sidebar'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { SettingsRoutePaths } from '@/modules/settings/routes'
import SessionHistoryList from '@/modules/workspace/components/SessionHistoryList.vue'
import { useChatSessionNavContext } from '@/modules/workspace/composables/useChatSessionNav'
import { PublicRoutePaths } from '@/router/publicRoutes'

const { t } = useI18n()
const { isMobile, setOpenMobile } = useSidebar()

const {
  runsLoading,
  searchQuery,
  filteredRuns,
  activeRunId,
  selectRun,
  newChat,
} = useChatSessionNavContext()

const closeMobileIfNeeded = () => {
  if (isMobile.value) {
    setOpenMobile(false)
  }
}

const handleSelect = async (runId: string) => {
  await selectRun(runId)
  closeMobileIfNeeded()
}

const handleNewChat = async () => {
  await newChat()
  closeMobileIfNeeded()
}
</script>

<template>
  <Sidebar collapsible="offcanvas">
    <SidebarContent class="flex min-h-0 flex-col overflow-hidden p-0">
      <SidebarGroup class="flex min-h-0 flex-1 flex-col p-0">
        <SidebarGroupContent class="flex min-h-0 flex-1 flex-col">
          <SessionHistoryList
            :runs="filteredRuns"
            :active-run-id="activeRunId"
            :is-loading="runsLoading"
            :search-query="searchQuery"
            @update:search-query="searchQuery = $event"
            @select="handleSelect"
            @new-chat="handleNewChat"
          />
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <SidebarFooter>
      <SidebarMenu>
        <SidebarMenuItem>
          <Tooltip>
            <TooltipTrigger as-child>
              <SidebarMenuButton disabled>
                <Brain class="size-4" />
                <span>{{ t('workspace.nav.memory') }}</span>
              </SidebarMenuButton>
            </TooltipTrigger>
            <TooltipContent side="top">
              {{ t('workspace.nav.memorySoon') }}
            </TooltipContent>
          </Tooltip>
        </SidebarMenuItem>

        <SidebarMenuItem>
          <RouterLink v-slot="{ href, navigate, isActive }" :to="SettingsRoutePaths.settings" custom>
            <SidebarMenuButton
              :is-active="isActive"
              as="a"
              :href="href"
              @click="navigate"
            >
              <SettingsIcon class="size-4" />
              <span>{{ t('workspace.nav.settings') }}</span>
            </SidebarMenuButton>
          </RouterLink>
        </SidebarMenuItem>

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
