<script setup lang="ts">
import { Box } from 'lucide-vue-next'
import { computed } from 'vue'
import { Badge } from '@/components/ui/badge'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { useContainerTypeLabel } from '../composables/useContainerTypeLabel'
import { GearRoutePath } from '../routes'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import PublicContainerAuthorBadge from './badges/PublicContainerAuthorBadge.vue'
import PublicContainerBadge from './badges/PublicContainerBadge.vue'

const props = defineProps<{
  container: IGearItemV2
  withAuthor?: boolean
}>()

const store = useGearStoreV2()
const { isAuthenticated } = useAuth()
const { typeLabel } = useContainerTypeLabel(computed(() => props.container.containerType || 'backpack'))

// Find all containers that contain this container as an item
const parentContainers = computed<IGearItemV2[]>(() => {
  const parents: IGearItemV2[] = []
  const containerId = props.container.id

  // Add direct parent if exists
  if (props.container.parentItemId) {
    const directParent = store.getItemById(props.container.parentItemId)
    if (directParent) {
      parents.push(directParent)
    }
  }

  // Find all containers that have this container as a child
  const allContainers = store.getAllItems.filter((item: IGearItemV2) => item.itemType === 'container')
  for (const container of allContainers) {
    if (container.id === containerId) continue // Skip self
    const children = store.getChildrenOfItem(container.id)
    if (children.some(child => child.id === containerId)) {
      // Avoid duplicates
      if (!parents.some(p => p.id === container.id)) {
        parents.push(container)
      }
    }
  }

  return parents
})

// Get first parent container
const firstParentContainer = computed<IGearItemV2 | undefined>(() => {
  return parentContainers.value[0]
})

// Get count of additional parents (beyond the first one)
const additionalParentsCount = computed<number>(() => {
  return Math.max(0, parentContainers.value.length - 1)
})
</script>

<template>
  <div class="flex items-center justify-between gap-2 flex-wrap">
    <div class="flex items-center flex-wrap gap-2">
      <Badge class="h-5" variant="outline">
        {{ typeLabel }}
      </Badge>
      <PublicContainerBadge v-if="container.isPublic" />
      <template v-if="withAuthor">
        <PublicContainerAuthorBadge
          v-if="container.authorName"
          :author-name="container.authorName"
          :author-id="container.authorId"
          :as-link="isAuthenticated"
        />
      </template>
    </div>
    <div v-if="firstParentContainer" class="flex items-center gap-1">
      <ButtonLink
        :to="GearRoutePath.ContainerDetailById(firstParentContainer.id)"
        variant="outline"
        size="sm"
        class="h-5 px-2! text-xs text-muted-foreground"
        @click.stop
      >
        <Box class="size-3" />
        {{ firstParentContainer.name }}
      </ButtonLink>
      <Badge
        v-if="additionalParentsCount > 0"
        variant="secondary"
        class="h-5 text-xs px-1.5"
      >
        +{{ additionalParentsCount }}
      </Badge>
    </div>
  </div>
</template>

