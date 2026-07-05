<script setup lang="ts">
import { useQueryClient } from '@tanstack/vue-query'
import { HttpStatusCode, isAxiosError } from 'axios'
import { FileText, Info } from 'lucide-vue-next'
import { computed, nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import DialogProgressOverlay from '@/components/ui/dialog/DialogProgressOverlay.vue'
import Textarea from '@/components/ui/textarea/Textarea.vue'
import { useHandleError } from '@/shared/composables/useHandleError'
import { logger } from '@/shared/utils/logger'
import type { ICreateGearItemV2Dto, IGearItemV2, IUpdateGearItemV2Dto } from '../types/gear.types.v2'
import { useGearSettings } from '../composables/useGearSettings'
import { useGearV2 } from '../composables/useGearV2'
import { markdownImportService } from '../services/markdownImportService'
import { gearQueryKeys } from '../utils/queryKeys'
import { safeValidateContainer, safeValidateItem } from '../utils/validation'
import GuidelinesDialog from './GuidelinesDialog.vue'
import MarkdownImportOptions from './import-markdown/MarkdownImportOptions.vue'
import MarkdownImportPreview from './import-markdown/MarkdownImportPreview.vue'

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'import-complete': []
}>()

const { t } = useI18n()
const queryClient = useQueryClient()
const { createItem, updateItem } = useGearV2()
const { customBrands } = useGearSettings()
const { handleError } = useHandleError()

const markdownContent = ref('')
const importing = ref(false)
const parsing = ref(false) // M5 FIX: Track parsing progress
const parseProgress = ref(0) // M5 FIX: Parse progress percentage (0-100)
const importMode = ref<'create' | 'update'>('update') // Default to update mode
const recognizeFromName = ref(false) // Option to recognize brand and color from item name
const previewResult = ref<ReturnType<typeof markdownImportService.parseMarkdown> | null>(null)
const isGuidelinesDialogOpen = ref(false)
const importProgress = ref({
  current: 0,
  total: 0,
  phase: 'containers' as 'containers' | 'items',
  currentItem: '',
})
const previewRef = ref<HTMLElement | null>(null)


// Check if any containers/items have UUIDs
const hasUuids = computed(() => {
  if (!previewResult.value) return false
  return previewResult.value.containers.some(c => c.uuid || c.items.some(i => i.uuid))
})

// Calculate import progress percentage
const importProgressPercentage = computed(() => {
  if (importProgress.value.total === 0) return 0
  return Math.round((importProgress.value.current / importProgress.value.total) * 100)
})

const handleClose = () => {
  markdownContent.value = ''
  previewResult.value = null
  importProgress.value = {
    current: 0,
    total: 0,
    phase: 'containers',
    currentItem: '',
  }
  emit('update:open', false)
}

/**
 * M5 FIX: Use async parsing with progress indicator
 * Prevents UI freezing on large markdown files
 */
const handlePreview = async () => {
  if (!markdownContent.value.trim()) {
    toast.error(t('gear.import.emptyContent'))
    return
  }

  parsing.value = true
  parseProgress.value = 0

  try {
    const result = await markdownImportService.parseMarkdownAsync(markdownContent.value, {
      recognizeFromName: recognizeFromName.value,
      customBrands: customBrands.value,
      onProgress: (percent) => {
        parseProgress.value = percent
      },
    })
    previewResult.value = result

    if (result.containers.length === 0) {
      toast.warning(t('gear.import.noContainersFound'))
    } else {
      toast.success(t('gear.import.previewSuccess', { count: result.containers.length }))
      // Scroll to preview section after DOM update
      await nextTick()
      previewRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  } catch (error) {
    console.error('Parse error:', error)
    handleError(error)
  } finally {
    parsing.value = false
    parseProgress.value = 0
  }
}

const handleOpenGuidelines = () => {
  isGuidelinesDialogOpen.value = true
}

/**
 * Detect "entity does not exist" errors from either the API (404) or the local service.
 */
const isNotFoundError = (error: unknown): boolean => {
  if (isAxiosError(error)) {
    return error.response?.status === HttpStatusCode.NotFound
  }
  return error instanceof Error && /not found/i.test(error.message)
}

/**
 * Upsert a gear item by UUID.
 *
 * In 'update' mode with a UUID we try to PATCH the existing entity and, if the backend
 * doesn't have it (404 / not found), fall back to creating it with the same UUID. This is
 * resilient to stale local store state (e.g. items left over from older imports that were
 * never persisted to the backend). In 'create' mode we always create a fresh entity.
 */
const upsertGearItem = async (
  uuid: string | undefined,
  createDto: ICreateGearItemV2Dto,
  updateDto: IUpdateGearItemV2Dto,
): Promise<{ item: IGearItemV2; created: boolean }> => {
  if (importMode.value === 'update' && uuid) {
    try {
      const item = await updateItem(uuid, updateDto)
      return { item, created: false }
    } catch (error) {
      if (!isNotFoundError(error)) throw error
      const item = await createItem({ ...createDto, id: uuid })
      return { item, created: true }
    }
  }

  // Create mode (or no UUID): always create. Reuse the UUID only in update mode above.
  const item = await createItem(createDto)
  return { item, created: true }
}

const handleImport = async () => {
  if (!previewResult.value || previewResult.value.containers.length === 0) {
    toast.error(t('gear.import.noPreview'))
    return
  }

  importing.value = true

  try {
    let importedCount = 0
    let updatedCount = 0
    let itemCount = 0
    let itemUpdatedCount = 0

    // Calculate total items for progress tracking
    const totalContainers = previewResult.value.containers.length
    const totalItems = previewResult.value.containers.reduce((sum, c) => sum + c.items.length, 0)
    const totalOperations = totalContainers + totalItems

    // Initialize progress
    importProgress.value = {
      current: 0,
      total: totalOperations,
      phase: 'containers',
      currentItem: '',
    }

    // Map to store container slug/id -> container UUID for nested container resolution
    const containerIdMap = new Map<string, string>()

    // Phase 1: Create/update all containers first (persisted via API when authenticated)
    const createdContainers: Array<{ containerData: typeof previewResult.value.containers[0]; container: IGearItemV2 }> = []

    for (const containerData of previewResult.value.containers) {
      importProgress.value.currentItem = containerData.name

      // M6 FIX: Validate container data before service call
      const containerDto = {
        name: containerData.name,
        type: 'other' as const,
        description: containerData.description || t('gear.import.importedDescription'),
        weight: containerData.weight,
        weightUnit: containerData.weightUnit,
        url: containerData.url,
        price: containerData.price,
        currency: containerData.currency,
        favorite: containerData.favorite ?? false,
      }

      const validation = safeValidateContainer(containerDto)
      if (!validation.success) {
        logger.warn(`Container validation failed: ${containerData.name}`, validation.errors)
        toast.warning(t('gear.import.containerValidationFailed', { name: containerData.name, errors: validation.errors.join(', ') }))
        importProgress.value.current++
        continue // Skip invalid container
      }

      const commonContainerFields = {
        name: validation.data.name,
        description: validation.data.description || null,
        containerType: validation.data.type,
        weight: validation.data.weight ?? null,
        weightUnit: validation.data.weightUnit ?? null,
        url: validation.data.url ?? null,
        price: validation.data.price ?? null,
        currency: validation.data.currency ?? null,
        favorite: validation.data.favorite ?? false,
      }

      // Upsert by UUID (update in update-mode, otherwise create). Resilient to stale
      // local state: a UUID present in the store but missing on the backend falls back
      // to create-with-UUID instead of failing with "Item not found".
      const { item: container, created } = await upsertGearItem(
        containerData.uuid,
        {
          itemType: 'container',
          parentItemId: null,
          ...commonContainerFields,
        },
        commonContainerFields,
      )

      if (created) {
        importedCount++
      } else {
        updatedCount++
      }

      // Store mapping: slug/id -> container UUID
      if (containerData.id) {
        containerIdMap.set(containerData.id, container.id)
      }

      // Also map UUID if available (for update mode)
      if (containerData.uuid) {
        containerIdMap.set(containerData.uuid, container.id)
      }

      createdContainers.push({ containerData, container })
      importProgress.value.current++
    }

    // Phase 2: Create/update items with nested container resolution
    importProgress.value.phase = 'items'
    for (const { containerData, container } of createdContainers) {
      // Import/update items
      for (const itemData of containerData.items) {
        importProgress.value.currentItem = itemData.name || t('gear.import.importingItem', 'Importing item')
        // Extract nestedContainerId before destructuring
        const { uuid: itemUuid, nestedContainerId, ...itemDto } = itemData

        // Nested container reference: re-parent the already-created container under
        // this one (V2-native hierarchy) instead of creating a placeholder item.
        if (nestedContainerId) {
          const nestedContainerUuid = containerIdMap.get(nestedContainerId)
          if (nestedContainerUuid) {
            try {
              await updateItem(nestedContainerUuid, { parentItemId: container.id })
            } catch (error) {
              logger.warn(`Failed to nest container "${nestedContainerId}" under "${container.name}"`, error)
            }
          } else {
            logger.warn(`Nested container with id "${nestedContainerId}" not found`)
          }
          importProgress.value.current++
          continue
        }

        // M6 FIX: Validate item data before service call
        const validation = safeValidateItem(itemDto)
        if (!validation.success) {
          logger.warn(`Item validation failed: ${itemData.name}`, validation.errors)
          toast.warning(t('gear.import.itemValidationFailed', { name: itemData.name || 'Unknown', errors: validation.errors.join(', ') }))
          importProgress.value.current++
          continue // Skip invalid item
        }

        const commonItemFields = {
          name: validation.data.name,
          category: validation.data.category,
          quantity: validation.data.quantity,
          weight: validation.data.weight ?? null,
          weightUnit: validation.data.weightUnit ?? null,
          status: validation.data.status || 'owned',
          priority: validation.data.priority ?? null,
          price: validation.data.price ?? null,
          currency: validation.data.currency ?? null,
          url: validation.data.url ?? null,
          brand: validation.data.brand ?? null,
          color: validation.data.color ?? null,
          quality: validation.data.quality ?? null,
          wearable: validation.data.wearable ?? null,
          consumable: validation.data.consumable ?? null,
          showOnContainer: validation.data.showOnContainer ?? null,
          expirationDate: validation.data.expirationDate ?? null,
          notes: validation.data.notes ?? null,
          description: validation.data.notes ?? null,
        }

        const { created } = await upsertGearItem(
          itemUuid,
          {
            itemType: 'item',
            parentItemId: container.id,
            ...commonItemFields,
          },
          commonItemFields,
        )

        if (created) {
          itemCount++
        } else {
          itemUpdatedCount++
        }
        importProgress.value.current++
      }
    }

    // Refresh the page list (TanStack Query cache) so imported data appears immediately
    await queryClient.invalidateQueries({ queryKey: gearQueryKeys.all })

    const message = importMode.value === 'update'
      ? t('gear.import.successWithUpdates', {
          created: importedCount,
          updated: updatedCount,
          items: itemCount,
          itemsUpdated: itemUpdatedCount,
        })
      : t('gear.import.success', {
          containers: importedCount,
          items: itemCount,
        })

    toast.success(message)

    emit('import-complete')
    handleClose()
  } catch (error) {
    console.error('Import error:', error)
    handleError(error)
  } finally {
    importing.value = false
  }
}
</script>

<template>
  <Dialog :open="props.open" @update:open="handleClose">
    <DialogContent class="min-w-full md:min-w-2xl max-w-screen md:max-w-6xl min-h-[70vh] max-h-[90vh] flex flex-col">
      <!-- M5 FIX: Progress overlay for parsing -->
      <DialogProgressOverlay
        :visible="parsing"
        :progress-percentage="parseProgress"
        :title="t('gear.import.parsing', 'Parsing markdown...')"
        :progress-text="t('gear.import.parseProgress', 'Parse progress')"
        :current-item-text="''"
        :current="parseProgress"
        :total="100"
      />
      <!-- Import progress overlay -->
      <DialogProgressOverlay
        :visible="importing"
        :progress-percentage="importProgressPercentage"
        :title="t('gear.import.importing', 'Importing...')"
        :progress-text="t('gear.import.progress', 'Progress')"
        :current-item-text="importProgress.currentItem"
        :current="importProgress.current"
        :total="importProgress.total"
      />
      <DialogHeader>
        <DialogTitle>{{ t('gear.import.title') }}</DialogTitle>
        <DialogDescription>
          {{ t('gear.import.description') }}
        </DialogDescription>
      </DialogHeader>

      <div class="flex flex-col flex-1 overflow-y-auto space-y-4" :class="{ 'opacity-50': importing || parsing }">
        <!-- Markdown Input -->
        <div class="flex flex-col flex-1">
          <label class="text-sm font-medium mb-2 block">
            {{ t('gear.import.markdownContent') }}
          </label>
          <Textarea
            v-model="markdownContent"
            :placeholder="t('gear.import.placeholder')"
            :disabled="importing || parsing"
            rows="12"
            class="flex flex-1 min-h-[200px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 font-mono"
          />
        </div>

        <!-- Recognition Options & Import Mode -->
        <MarkdownImportOptions
          v-model:recognize-from-name="recognizeFromName"
          v-model:import-mode="importMode"
          :has-uuids="hasUuids"
          :show-preview="!!previewResult"
        />

        <!-- Preview Result -->
        <div ref="previewRef">
          <MarkdownImportPreview :preview-result="previewResult" />
        </div>
      </div>

      <DialogFooter class="flex-col sm:flex-row gap-2">
        <Button variant="secondary" class="sm:mr-auto" @click="handleOpenGuidelines">
          <Info class="size-4" />
          {{ t('gear.export.guidelines', 'Guidelines') }}
        </Button>
        <div class="flex gap-2">
          <Button type="button" variant="outline" @click="handleClose">
            {{ t('gear.actions.cancel') }}
          </Button>
          <Button
            type="button"
            :variant="previewResult ? 'outline' : 'default'"
            :disabled="markdownContent.trim().length < 4 || parsing || importing"
            :loading="parsing"
            @click="handlePreview"
          >
            <FileText class="size-4" />
            {{ t('gear.import.preview') }}
          </Button>
          <Button
            type="button"
            :variant="previewResult ? 'default' : 'outline'"
            :disabled="!previewResult || previewResult.containers.length === 0 || importing || parsing"
            :loading="importing"
            @click="handleImport"
          >
            {{ t('gear.import.import') }}
          </Button>
        </div>
      </DialogFooter>
    </DialogContent>
  </Dialog>

  <!-- Guidelines Dialog -->
  <GuidelinesDialog v-model:open="isGuidelinesDialogOpen" />
</template>
