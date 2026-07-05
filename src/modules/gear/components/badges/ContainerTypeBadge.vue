<script setup lang="ts">
import { computed } from 'vue'
import { Badge } from '@/components/ui/badge'
import type { IGearItemV2, TContainerColor } from '../../types/gear.types.v2'
import { useContainerTypeLabel } from '../../composables/useContainerTypeLabel'
import { COLOR_BORDER_CLASSES, COLOR_TEXT_CLASSES } from '../../utils/containerColors'
import ContainerIcon from '../ContainerIcon.vue'

const props = defineProps<{
  container: IGearItemV2
}>()

const { typeLabel } = useContainerTypeLabel(computed(() => props.container.containerType || 'backpack'))
</script>

<template>
  <Badge
    variant="outline"
    :class="[
      COLOR_TEXT_CLASSES[(container.color ?? 'default') as TContainerColor],
      COLOR_BORDER_CLASSES[(container.color ?? 'default') as TContainerColor],
    ]"
  >
    <ContainerIcon
      :color="(container.color as TContainerColor | undefined)"
      :type="container.containerType ?? 'other'"
      :size="4"
      class="mr-0.5"
    />
    {{ typeLabel }}
  </Badge>
</template>
