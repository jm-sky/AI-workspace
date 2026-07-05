<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import {
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar'
import ContainerIcon from '@/modules/gear/components/ContainerIcon.vue'
import { GearRoutePath } from '@/modules/gear/routes'
import type { IGearItemV2, TContainerColor, TGearContainerType } from '@/modules/gear/types/gear.types.v2'

const props = defineProps<{
  container: IGearItemV2
}>()

const route = useRoute()

const iconType = computed<TGearContainerType>(() => props.container.containerType ?? 'backpack')
const iconColor = computed<TContainerColor | null>(() => (props.container.color ?? null) as TContainerColor | null)

// Sprawdzanie czy kontener jest aktywny
const isActive = (containerId: string): boolean => {
  return route.params.id === containerId || route.params.containerId === containerId
}
</script>

<template>
  <SidebarMenuItem>
    <SidebarMenuButton :is-active="isActive(container.id)" as-child>
      <RouterLink :to="GearRoutePath.ContainerDetailById(container.id)">
        <ContainerIcon :type="iconType" :color="iconColor" :size="4" />
        <span>{{ container.name }}</span>
      </RouterLink>
    </SidebarMenuButton>
  </SidebarMenuItem>
</template>

