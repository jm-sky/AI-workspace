<script setup lang="ts">
import { CalendarPlus, CalendarSync, ExternalLink, Link2, RefreshCcw } from 'lucide-vue-next'
import { computed, defineAsyncComponent, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import DropdownMenuSeparator from '@/components/ui/dropdown-menu/DropdownMenuSeparator.vue'
import { useAi } from '@/modules/ai/composables/useAi'
import { useBackend } from '@/shared/composables/useBackend'
import { useHandleError } from '@/shared/composables/useHandleError'
import { smallDateTime } from '@/shared/utils/smallDateTime'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { useGearMutations } from '../composables/useGearMutations'
import { GearRoutePath } from '../routes'
import { getActionIcon } from '../utils/actionIcons'
import { formatWeight } from '../utils/formatWeight'
import { isSet } from '../utils/helpers'
import { getFrom } from '../utils/navigationParams'
import ContainerRatingBadge from './badges/ContainerRatingBadge.vue'
import ContainerTypeBadge from './badges/ContainerTypeBadge.vue'
import PublicContainerBadge from './badges/PublicContainerBadge.vue'
import WeightLimitBadge from './badges/WeightLimitBadge.vue'
import ContainerHeaderName from './ContainerHeaderName.vue'
import ContainerHeaderStats from './ContainerHeaderStats.vue'
import FavoriteContainerButton from './FavoriteContainerButton.vue'
import ItemsTableEditModeToggle from './ItemsTableEditModeToggle.vue'
import MarkdownRenderer from './MarkdownRenderer.vue'
import PremiumFeatureLockButton from './PremiumFeatureLockButton.vue'

// Lazy load dialog to reduce initial bundle size
const CloneContainerDialog = defineAsyncComponent(() => import('./CloneContainerDialog.vue'))

// Action icons
const BackIcon = getActionIcon('back')
const ExportToPromptIcon = getActionIcon('exportToPrompt')
const EditIcon = getActionIcon('edit')
const CloneIcon = getActionIcon('clone')
const AddContainerIcon = getActionIcon('addContainer')
const AddItemIcon = getActionIcon('addItem')
const MoreActionsIcon = getActionIcon('moreActions')
const ExportIcon = getActionIcon('export')
const ExportToCSVIcon = getActionIcon('exportToCSV')
const ImportIcon = getActionIcon('import')
const RecognizeParametersAllIcon = getActionIcon('recognizeParametersAll')
const DeleteIcon = getActionIcon('delete')
const PublishIcon = getActionIcon('publish')

const props = defineProps<{
  container: IGearItemV2
}>()

const emit = defineEmits<{
  export: []
  import: []
  addContainer: []
  exportToPrompt: []
  exportToCsv: []
  recognizeParametersAll: []
  aiChat: []
  manageShareTokens: []
  refresh: []
}>()

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()
const { canUseAi } = useAi()
const { shouldUseAPI } = useBackend()
const { deleteItem, updateItem } = useGearMutations()
const { handleError } = useHandleError()

const isCloneDialogOpen = ref(false)
const isDeleteDialogOpen = ref(false)
const isDeleting = ref(false)

const backTo = computed<string>(() => {
  const from = getFrom(route)
  if (from === 'all-items') {
    return GearRoutePath.AllItems
  }
  // Domyślnie wracamy do ContainersList
  return GearRoutePath.Containers
})

const handleEdit = () => {
  router.push(GearRoutePath.ContainerEditById(props.container.id))
}

const handleClone = () => {
  isCloneDialogOpen.value = true
}

const handleAddItem = () => {
  router.push(GearRoutePath.ItemNew.replace(':containerId', props.container.id))
}

const handleAddContainer = () => {
  emit('addContainer')
}

const handleExport = () => {
  emit('export')
}

const handleImport = () => {
  emit('import')
}

const handleExportToPrompt = () => {
  emit('exportToPrompt')
}

const handleExportToCSV = () => {
  emit('exportToCsv')
}

const handleBack = () => {
  router.push(backTo.value)
}

const handleDelete = () => {
  isDeleteDialogOpen.value = true
}

const handleDeleteConfirm = async () => {
  if (isDeleting.value) return

  try {
    isDeleting.value = true
    await deleteItem(props.container.id)
    toast.success(t('common.success'))
    router.push(GearRoutePath.Containers)
  } catch (error) {
    console.error('Error deleting container:', error)
    handleError(error, { fallbackMessage: t('common.error') })
  } finally {
    isDeleting.value = false
    isDeleteDialogOpen.value = false
  }
}

const handlePublish = async () => {
  try {
    await updateItem(props.container.id, { isPublic: true })
    toast.success(t('common.success'))
    emit('refresh')
  } catch (error) {
    console.error('Error publishing container:', error)
    handleError(error, { fallbackMessage: t('common.error') })
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-4">
      <div class="flex items-center justify-between gap-3">
        <Button
          variant="ghost"
          size="sm"
          @click="handleBack"
        >
          <BackIcon class="size-4" />
          {{ t('common.back') }}
        </Button>
        <div class="flex items-center gap-2">
          <Button
            v-if="shouldUseAPI"
            v-tooltip.bottom="t('common.refresh')"
            variant="ghost"
            size="sm"
            :aria-label="t('common.refresh')"
            @click="$emit('refresh')"
          >
            <RefreshCcw class="size-4" />
          </Button>
          <PremiumFeatureLockButton
            :has-access="canUseAi"
            icon="ai"
            :tooltip="t('gear.actions.aiAssistant')"
            :aria-label="t('gear.actions.aiAssistant')"
            @click="$emit('aiChat')"
          />
          <Button
            v-tooltip.bottom="t('gear.actions.exportToPrompt')"
            variant="ghost"
            size="sm"
            :aria-label="t('gear.actions.exportToPrompt')"
            @click="handleExportToPrompt"
          >
            <ExportToPromptIcon class="size-4" />
          </Button>
          <FavoriteContainerButton :container />
        </div>
      </div>

      <div class="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
        <div class="flex-1">
          <ContainerHeaderName :container />
          <div v-if="container.description" class="text-muted-foreground mb-3">
            <MarkdownRenderer
              :content="container.description"
              class="text-sm"
            />
          </div>
          <div class="flex items-center gap-2 flex-wrap">
            <ContainerTypeBadge :container />
            <PublicContainerBadge v-if="container.isPublic" />
            <Badge
              v-tooltip.bottom="t('common.created')"
              variant="secondary"
              class="text-xs"
            >
              <CalendarPlus class="size-4" />
              {{ smallDateTime(container.createdAt) }}
            </Badge>
            <Badge
              v-if="container.updatedAt !== container.createdAt"
              v-tooltip.bottom="t('common.updated')"
              variant="secondary"
              class="text-xs"
            >
              <CalendarSync class="size-4" /> {{ smallDateTime(container.updatedAt) }}
            </Badge>
            <Badge v-if="container.brand" variant="secondary" class="normal-case">
              {{ container.brand }}
            </Badge>
            <Badge v-if="isSet(container.weight) && isSet(container.weightUnit)" variant="secondary">
              {{ formatWeight(container.weight, container.weightUnit, locale) }}
            </Badge>
            <WeightLimitBadge :container />
            <ContainerRatingBadge :container />
            <ExternalLink
              v-if="container.url"
              :href="container.url"
              @click.stop
            >
              {{ t('gear.container.url') }}
            </ExternalLink>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <ItemsTableEditModeToggle />
          <Button
            variant="outline"
            size="sm"
            class="shrink-0"
            @click="handleEdit"
          >
            <EditIcon class="size-4" />
            <span class="hidden sm:inline">{{ t('gear.actions.edit') }}</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            class="shrink-0"
            @click="handleAddContainer"
          >
            <AddContainerIcon class="size-4" />
            <span class="hidden sm:inline">{{ t('gear.container.addNested') }}</span>
          </Button>
          <Button size="sm" class="shrink-0 flex-1 sm:flex-none" @click="handleAddItem">
            <AddItemIcon class="size-4" />
            {{ t('gear.item.create') }}
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button
                v-tooltip.bottom="t('gear.actions.moreActions')"
                variant="outline"
                size="sm"
                class="shrink-0"
                :aria-label="t('gear.actions.moreActions')"
              >
                <MoreActionsIcon class="size-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem @click="handleClone">
                <CloneIcon class="size-4" />
                {{ t('gear.container.clone') }}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="handleImport">
                <ImportIcon class="size-4" />
                {{ t('gear.actions.import') }}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="handleExport">
                <ExportIcon class="size-4" />
                {{ t('gear.actions.exportToJSON') }}
              </DropdownMenuItem>
              <DropdownMenuItem @click="handleExportToCSV">
                <ExportToCSVIcon class="size-4" />
                {{ t('gear.actions.exportToCSV') }}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="handleExportToPrompt">
                <ExportToPromptIcon class="size-4" />
                {{ t('gear.actions.exportToPrompt') }}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="$emit('recognizeParametersAll')">
                <RecognizeParametersAllIcon class="size-4" />
                {{ t('gear.actions.recognizeParametersAll') }}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                v-if="!container.isPublic && shouldUseAPI"
                @click="handlePublish"
              >
                <PublishIcon class="size-4" />
                {{ t('gear.actions.publishContainer') }}
              </DropdownMenuItem>
              <DropdownMenuItem v-if="shouldUseAPI" @click="$emit('manageShareTokens')">
                <Link2 class="size-4" />
                {{ t('gear.actions.manageShareTokens') }}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                class="text-destructive focus:text-destructive"
                @click="handleDelete"
              >
                <DeleteIcon class="size-4" />
                {{ t('gear.container.delete') }}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </div>

    <ContainerHeaderStats :container />

    <!-- Clone Dialog -->
    <CloneContainerDialog
      v-model:open="isCloneDialogOpen"
      :container="container"
    />

    <!-- Delete Confirmation Dialog -->
    <Dialog :open="isDeleteDialogOpen" @update:open="(open) => { isDeleteDialogOpen = open }">
      <DialogContent class="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>
            {{ t('gear.container.delete') }}
          </DialogTitle>
          <DialogDescription>
            {{ t('gear.container.deleteConfirm') }}
          </DialogDescription>
        </DialogHeader>
        <DialogFooter class="flex-col sm:flex-row gap-2">
          <Button
            variant="outline"
            :disabled="isDeleting"
            @click="isDeleteDialogOpen = false"
          >
            {{ t('common.cancel') }}
          </Button>
          <Button
            variant="destructive"
            :disabled="isDeleting"
            @click="handleDeleteConfirm"
          >
            {{ isDeleting ? t('common.loading') : t('common.delete') }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
