<script setup lang="ts">
import { ArrowLeft, CalendarPlus } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import { smallDateTime } from '@/shared/utils/smallDateTime'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { useContainerTypeLabel } from '../composables/useContainerTypeLabel'
import { useIsContainerOwner } from '../composables/useIsContainerOwner'
import { GearRoutePath } from '../routes'
import { getActionIcon } from '../utils/actionIcons'
import PublicContainerAuthorBadge from './badges/PublicContainerAuthorBadge.vue'
import MarkdownRenderer from './MarkdownRenderer.vue'
import ReportContainerButton from './ReportContainerButton.vue'

const props = defineProps<{
  container: IGearItemV2
  backPath?: string
}>()

const emit = defineEmits<{
  back: []
}>()

const router = useRouter()
const { t } = useI18n()
const { typeLabel } = useContainerTypeLabel(computed(() => props.container.containerType ?? 'other'))

const EditIcon = getActionIcon('edit')

// Check if current user is the author
const isAuthor = useIsContainerOwner(props.container, false)

const handleBack = () => {
  if (props.backPath) {
    router.push(props.backPath)
  } else {
    emit('back')
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between gap-3">
      <Button variant="ghost" size="sm" @click="handleBack">
        <ArrowLeft class="size-4" />
        {{ t('common.back') }}
      </Button>
      <div class="flex items-center gap-2">
        <ReportContainerButton :container-id="container.id" />
        <ButtonLink
          v-if="isAuthor"
          :to="GearRoutePath.ContainerEditById(container.id)"
          variant="outline"
          size="sm"
        >
          <EditIcon class="size-4" />
          <span class="hidden sm:inline">{{ t('gear.actions.edit') }}</span>
        </ButtonLink>
      </div>
    </div>

    <div>
      <h1 class="wrap-break-word mb-2 text-2xl font-bold sm:text-3xl">
        {{ container.name }}
      </h1>
      <div v-if="container.description" class="mb-3 text-muted-foreground">
        <MarkdownRenderer
          :content="container.description"
          class="text-sm sm:text-base"
        />
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <Badge variant="outline">
          {{ typeLabel }}
        </Badge>
        <PublicContainerAuthorBadge
          v-if="container.authorName"
          :author-name="container.authorName"
          :author-id="container.authorId"
          :as-link="!!container.authorId"
        />
        <Badge variant="secondary" class="text-xs">
          <CalendarPlus class="size-3" />
          {{ smallDateTime(container.createdAt) }}
        </Badge>
      </div>
    </div>
  </div>
</template>
