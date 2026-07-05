<script setup lang="ts">
import { useQueryClient } from '@tanstack/vue-query'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useContainerOperationsV2 } from '../composables/internal/v2/useContainerOperationsV2'
import { GearRoutePath } from '../routes'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import { getActionIcon } from '../utils/actionIcons'
import { gearQueryKeys } from '../utils/queryKeys'

// Action icons
const MoreActionsIcon = getActionIcon('moreActions')
const CreateIcon = getActionIcon('create')
const ImportFromMarkdownIcon = getActionIcon('importFromMarkdown')
const ExportAllToMarkdownIcon = getActionIcon('exportAllToMarkdown')
const ExportToCSVIcon = getActionIcon('exportToCSV')
const ExportToJsonIcon = getActionIcon('exportToJson')
const DeleteAllIcon = getActionIcon('deleteAll')

const router = useRouter()
const { t } = useI18n()
const queryClient = useQueryClient()
const storeV2 = useGearStoreV2()
// Visibility and deletion both go through V2 (same source as the page list).
const { containers, deleteAllContainers } = useContainerOperationsV2()

const emit = defineEmits<{
  exportAllToMarkdown: [],
  exportAllToCsv: [],
  exportAllToJson: [],
  import: [],
}>()

const handleCreate = () => {
  router.push(GearRoutePath.ContainerNew)
}

const handleImport = () => {
  emit('import')
}

const handleDeleteAll = async () => {
  if (confirm(t('gear.container.deleteAllConfirm'))) {
    try {
      await deleteAllContainers()
      // Keep the V2 store and TanStack Query cache (used by the page list) in sync
      storeV2.clearAll()
      await queryClient.invalidateQueries({ queryKey: gearQueryKeys.all })
      toast.success(t('gear.container.deleteAllSuccess'))
    } catch {
      toast.error(t('common.error'))
    }
  }
}

const handleExportAllToMarkdown = () => {
  emit('exportAllToMarkdown')
}

const handleExportAllToCsv = () => {
  emit('exportAllToCsv')
}

const handleExportAllToJson = () => {
  emit('exportAllToJson')
}
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button
        v-tooltip.bottom="t('gear.actions.moreActions')"
        variant="ghost"
        size="sm"
        class="sm:shrink-0"
        :aria-label="t('gear.actions.moreActions')"
      >
        <MoreActionsIcon class="size-4" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end">
      <DropdownMenuItem @click="handleCreate">
        <CreateIcon class="size-4 mr-2" />
        {{ t('gear.container.create.new') }}
      </DropdownMenuItem>
      <DropdownMenuItem @click="handleImport">
        <ImportFromMarkdownIcon class="size-4 mr-2" />
        {{ t('gear.import.fromMarkdown') }}
      </DropdownMenuItem>
      <DropdownMenuSeparator v-if="containers.length > 0" />
      <DropdownMenuItem
        v-if="containers.length > 0"
        @click="handleExportAllToMarkdown"
      >
        <ExportAllToMarkdownIcon class="size-4 mr-2" />
        {{ t('gear.export.allToMarkdown') }}
      </DropdownMenuItem>
      <DropdownMenuItem
        v-if="containers.length > 0"
        @click="handleExportAllToCsv"
      >
        <ExportToCSVIcon class="size-4 mr-2" />
        {{ t('gear.export.allToCSV') }}
      </DropdownMenuItem>
      <DropdownMenuItem
        v-if="containers.length > 0"
        @click="handleExportAllToJson"
      >
        <ExportToJsonIcon class="size-4 mr-2" />
        {{ t('gear.export.allToJson') }}
      </DropdownMenuItem>
      <DropdownMenuSeparator v-if="containers.length > 0" />
      <DropdownMenuItem
        v-if="containers.length > 0"
        class="text-destructive focus:text-destructive"
        @click="handleDeleteAll"
      >
        <DeleteAllIcon class="size-4 mr-2" />
        {{ t('gear.container.deleteAll') }}
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
