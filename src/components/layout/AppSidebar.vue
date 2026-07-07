<script setup lang="ts">
import { BackpackIcon, BookIcon, Globe, Info, Package, ShoppingCart, Sparkles } from 'lucide-vue-next'
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import SidebarMenuContainerItem from '@/components/layout/SidebarMenuContainerItem.vue'
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
  SidebarSeparator,
} from '@/components/ui/sidebar'
import { useGearV2 } from '@/modules/gear/composables/useGearV2'
import { GearRoutePath } from '@/modules/gear/routes'
import { WorkspaceRoutePath } from '@/modules/workspace/routes'
import { PublicRoutePaths } from '@/router/publicRoutes'
import type { IGearItemV2 } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()
// Load containers through the active V2 service (API or localStorage) into the store
const { rootContainers: rootContainersV2, getItems } = useGearV2()
onMounted(() => {
  getItems({ itemType: 'container' }).catch(() => {})
})

const workspaceLinks = computed(() => [
  {
    to: WorkspaceRoutePath.Chat,
    label: t('workspace.nav.chat', 'AI Workspace'),
    icon: Sparkles,
  },
])

// Linki: Mój sprzęt
const myGearLinks = computed(() => [
  {
    to: GearRoutePath.Containers,
    label: t('gear.page.title', 'Gear'),
    icon: BackpackIcon,
  },
  {
    to: GearRoutePath.AllItems,
    label: t('gear.allItems.navTitle', 'All Items'),
    icon: Package,
  },
  {
    to: GearRoutePath.ShoppingPlanning,
    label: t('gear.shopping.navTitle', 'Shopping'),
    icon: ShoppingCart,
  },
])

// Linki: Publiczne
const publicLinks = computed(() => [
  {
    to: GearRoutePath.PublicContainers,
    label: t('gear.publicContainers.navTitle', 'Public Browser'),
    icon: Globe,
  },
  {
    to: GearRoutePath.CatalogueBrowser,
    label: t('gear.catalogue.navTitle', 'Catalogue'),
    icon: BookIcon,
  },
])

// Root kontenery posortowane: ulubione + alfabetycznie
const rootContainers = computed<IGearItemV2[]>(() => {
  // Sortowanie: najpierw ulubione, potem alfabetycznie
  return [...rootContainersV2.value].sort((a, b) => {
    // Najpierw ulubione
    if (a.favorite && !b.favorite) return -1
    if (!a.favorite && b.favorite) return 1
    // Potem alfabetycznie
    return a.name.localeCompare(b.name)
  })
})
</script>

<template>
  <Sidebar collapsible="icon">
    <SidebarContent class="overflow-x-hidden max-h-[90vh] overflow-y-auto">
      <!-- Sekcja: AI Workspace -->
      <SidebarGroup>
        <SidebarGroupLabel>{{ t('workspace.nav.section', 'Workspace') }}</SidebarGroupLabel>
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

      <SidebarSeparator />

      <!-- Sekcja: Mój sprzęt -->
      <SidebarGroup>
        <SidebarGroupLabel>{{ t('navigation.myGear', 'My Gear') }}</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="link in myGearLinks" :key="link.to">
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

      <!-- Separator -->
      <SidebarSeparator class="group-data-[collapsible=icon]:w-auto!" />

      <!-- Sekcja: Publiczne -->
      <SidebarGroup>
        <SidebarGroupLabel>{{ t('navigation.public', 'Public') }}</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="link in publicLinks" :key="link.to">
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

      <!-- Separator -->
      <SidebarSeparator class="group-data-[collapsible=icon]:w-auto!" />

      <!-- Sekcja: Lista kontenerów -->
      <SidebarGroup class="max-h-[50vh] overflow-y-auto">
        <SidebarGroupLabel>{{ t('gear.page.containers', 'Containers') }}</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu v-if="rootContainers.length > 0">
            <SidebarMenuContainerItem
              v-for="container in rootContainers"
              :key="container.id"
              :container="container"
            />
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

