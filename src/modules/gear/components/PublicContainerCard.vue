<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import type { IGearItemV2, TContainerColor } from '../types/gear.types.v2'
import ColorDot from '../components/ColorDot.vue'
import { GearRoutePath } from '../routes'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import { getContainerIcon } from '../utils/containerIcons'
import ContainerCardBadges from './ContainerCardBadges.vue'
import ContainerCardCreatedDate from './ContainerCardCreatedDate.vue'
import MarkdownRenderer from './MarkdownRenderer.vue'
import RatingStars from './RatingStars.vue'

const { t } = useI18n()
const store = useGearStoreV2()

const props = defineProps<{
  container: IGearItemV2
}>()

// Get container icon based on type
const ContainerIcon = computed(() => getContainerIcon(props.container.containerType))

// Get items count from V2 store
const itemsCount = computed(() => {
  const children = store.getChildrenOfItem(props.container.id)
  return children.filter(child => child.itemType === 'item').length
})
</script>

<template>
  <RouterLink v-slot="{ navigate, href }" :to="GearRoutePath.PublicContainerDetailById(container.id)" custom>
    <Card
      as="a"
      :href
      class="gap-2 hover:shadow-lg hover:bg-current/5 hover:scale-102 hover:-translate-y-1 transition-all duration-300 cursor-pointer"
      @click.stop="navigate"
    >
      <CardHeader class="h-8 text-card-foreground flex items-center justify-between">
        <div class="flex items-center gap-2">
          <ColorDot :color="(container.color as TContainerColor | undefined)" :icon="ContainerIcon" />
          <CardTitle>{{ container.name }}</CardTitle>
        </div>
      </CardHeader>

      <CardContent class="flex flex-col flex-1 gap-3 px-6 pb-4 text-card-foreground">
        <ContainerCardBadges :container with-author />

        <CardDescription v-if="container.description" class="flex-1">
          <MarkdownRenderer
            :content="container.description"
            class="text-sm"
          />
        </CardDescription>

        <div class="text-sm text-muted-foreground">
          {{ t('gear.container.itemsCount', { count: itemsCount }) }}
        </div>

        <!-- Rating Display -->
        <div v-if="container.averageUserRating != null" class="flex items-center gap-2">
          <RatingStars
            :rating="container.averageUserRating"
            :show-number="true"
            size="sm"
            :interactive="false"
          />
          <span class="text-xs text-muted-foreground">
            ({{ container.userRatingCount }})
          </span>
        </div>

        <div class="-mb-6 mt-2 flex items-center justify-end">
          <ContainerCardCreatedDate :created-at="container.createdAt" />
        </div>
      </CardContent>
    </Card>
  </RouterLink>
</template>
