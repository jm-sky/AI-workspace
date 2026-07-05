<script setup lang="ts">
import { Box } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Badge } from '@/components/ui/badge'
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import CardContent from '@/components/ui/card/CardContent.vue'
import type { IGearItemV2, TContainerColor } from '../types/gear.types.v2'
import { useGearSettings } from '../composables/useGearSettings'
import { GearRoutePath } from '../routes'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import {
  READINESS_EXCELLENT_THRESHOLD,
  READINESS_GOOD_THRESHOLD,
} from '../utils/constants'
import {
  calculateReadinessPercentageSyncV2,
  calculateTotalWeightSyncV2,
} from '../utils/containerCalculationsV2'
import { COLOR_BORDER_CLASSES, COLOR_TEXT_CLASSES } from '../utils/containerColors'
import { getContainerIcon } from '../utils/containerIcons'
import { formatWeightToPreferredUnit } from '../utils/formatWeight'
import ColorDot from './ColorDot.vue'
import ContainerCardActions from './ContainerCardActions.vue'
import ContainerCardBadges from './ContainerCardBadges.vue'
import ContainerCardCreatedDate from './ContainerCardCreatedDate.vue'
import ContainerCardStats from './ContainerCardStats.vue'
import ContainerReadinessProgressBar from './ContainerReadinessProgressBar.vue'
import FavoriteContainerButton from './FavoriteContainerButton.vue'
import MarkdownRenderer from './MarkdownRenderer.vue'

const props = defineProps<{
  container: IGearItemV2
}>()

const emit = defineEmits<{
  delete: [id: string]
}>()

const router = useRouter()
const { t, locale } = useI18n()
const store = useGearStoreV2()
const { settings: gearSettings } = useGearSettings()
const settings = computed(() => ({ preferredWeightUnit: gearSettings.value.preferredWeightUnit }))

// Computed properties - use sync helpers for computed
const totalWeight = computed<number>(() => {
  return calculateTotalWeightSyncV2(props.container.id, store.getItemById, store.getChildrenOfItem)
})
const readinessPercentage = computed<number>(() => {
  return calculateReadinessPercentageSyncV2(props.container.id, store.getItemById, store.getChildrenOfItem)
})
const itemsCount = computed<number>(() => {
  const children = store.getChildrenOfItem(props.container.id)
  return children.filter(child => child.itemType === 'item').length
})

// Format weight (totalWeight is in grams)
const formattedWeight = computed<string>(() => formatWeightToPreferredUnit(totalWeight.value, settings.value.preferredWeightUnit, locale.value))

// Readiness color
const readinessColor = computed<string>(() => {
  if (readinessPercentage.value >= READINESS_EXCELLENT_THRESHOLD) return 'text-green-600'
  if (readinessPercentage.value >= READINESS_GOOD_THRESHOLD) return 'text-yellow-600'
  return 'text-red-600'
})

// Check if container is nested
const isNested = computed<boolean>(() => {
  return !!props.container.parentItemId
})

// Get container icon based on type
const ContainerIcon = computed(() => getContainerIcon(props.container.containerType))

// Navigate to container detail
const handleShow = () => {
  router.push(GearRoutePath.ContainerDetailById(props.container.id))
}
</script>

<template>
  <Card
    class="gap-2 hover:shadow-lg hover:bg-current/5 hover:scale-102 hover:-translate-y-1 transition-all duration-300 cursor-pointer"
    :class="[
      container.color ? COLOR_BORDER_CLASSES[container.color as TContainerColor] : '',
      container.color ? COLOR_TEXT_CLASSES[container.color as TContainerColor] : '',
      container.color && container.color !== 'default' ? 'outline-2 outline-current/15' : '',
    ]"
    @click="handleShow"
  >
    <CardHeader class="h-8 text-card-foreground flex items-center justify-between">
      <div class="flex items-center gap-2">
        <ColorDot :color="(container.color as TContainerColor | undefined)" :icon="ContainerIcon" />
        <CardTitle>{{ container.name }}</CardTitle>
        <Badge v-if="isNested" variant="outline" class="ml-auto text-xs">
          <Box :size="12" class="mr-1" />
          {{ t('gear.container.nested') }}
        </Badge>
      </div>
      <div class="flex items-center gap-1">
        <FavoriteContainerButton :container />
        <ContainerCardActions :container @delete="emit('delete', $event)" />
      </div>
    </CardHeader>

    <CardContent class="flex flex-col flex-1 gap-3 px-6 pb-4 text-card-foreground">
      <ContainerCardBadges :container />

      <CardDescription v-if="container.description" class="flex-1">
        <MarkdownRenderer
          :content="container.description"
          class="text-sm"
        />
      </CardDescription>

      <ContainerCardStats
        :items-count
        :formatted-weight
        :readiness-percentage
        :readiness-color
      />

      <ContainerReadinessProgressBar :readiness-percentage />

      <div class="-mb-6 mt-2 flex items-center justify-end">
        <ContainerCardCreatedDate :created-at="container.createdAt" />
      </div>
    </CardContent>
  </Card>
</template>

