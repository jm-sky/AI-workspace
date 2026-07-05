<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import Separator from '@/components/ui/separator/Separator.vue'
import { useLocale } from '@/shared/i18n/composables/useLocale'
import { downloadBlob } from '@/shared/utils/downloadBlob'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { useGearStoreV2 } from '../store/useGearStoreV2'
import { exportContainersToCSVV2, exportContainerToCSVV2, generateAllContainersCSVFileName, generateCSVFileName, getDefaultSeparator } from '../utils/exportToCSVV2'

const open = defineModel<boolean>('open', { required: true })

const props = defineProps<{
  container?: IGearItemV2
  containers?: IGearItemV2[]
}>()

const { t } = useI18n()
const { currentLocale } = useLocale()
const store = useGearStoreV2()

// Available columns with categories (computed for reactivity)
// Basic: standardowo widoczne kolumny
// Additional: standardowo ukryte kolumny
const availableColumns = computed(() => [
  { key: 'name', label: t('gear.export.csv.columnName', 'Name'), category: 'basic' },
  { key: 'category', label: t('gear.export.csv.columnCategory', 'Category'), category: 'basic' },
  { key: 'quantity', label: t('gear.export.csv.columnQuantity', 'Quantity'), category: 'basic' },
  { key: 'weight', label: t('gear.export.csv.columnWeight', 'Weight'), category: 'basic' },
  { key: 'weightUnit', label: t('gear.export.csv.columnWeightUnit', 'Weight Unit'), category: 'basic' },
  { key: 'status', label: t('gear.export.csv.columnStatus', 'Status'), category: 'basic' },
  { key: 'priority', label: t('gear.export.csv.columnPriority', 'Priority'), category: 'basic' },
  { key: 'price', label: t('gear.export.csv.columnPrice', 'Price'), category: 'additional' },
  { key: 'currency', label: t('gear.export.csv.columnCurrency', 'Currency'), category: 'additional' },
  { key: 'brand', label: t('gear.export.csv.columnBrand', 'Brand'), category: 'additional' },
  { key: 'color', label: t('gear.export.csv.columnColor', 'Color'), category: 'additional' },
  { key: 'url', label: t('gear.export.csv.columnUrl', 'URL'), category: 'additional' },
  { key: 'notes', label: t('gear.export.csv.columnNotes', 'Notes'), category: 'additional' },
  { key: 'containerName', label: t('gear.export.csv.columnContainerName', 'Container Name'), category: 'additional' },
  { key: 'containerType', label: t('gear.export.csv.columnContainerType', 'Container Type'), category: 'additional' },
])

// Column selection state - default: all selected
const selectedColumns = ref<string[]>(availableColumns.value.map(col => col.key))

// Separator selection - default based on locale
const selectedSeparator = ref<',' | ';'>(getDefaultSeparator(currentLocale.value))

// Encoding option - default: true (for Excel compatibility)
const useBOM = ref(true)

// Include nested containers - default: true
const includeNestedContainers = ref(true)

// Calculate item count
const itemCount = computed(() => {
  if (props.container) {
    const children = store.getChildrenOfItem(props.container.id)
    let count = children.filter(child => child.itemType === 'item').length

    if (includeNestedContainers.value) {
      children.forEach(child => {
        if (child.itemType === 'container') {
          const nestedChildren = store.getChildrenOfItem(child.id)
          count += nestedChildren.filter(nc => nc.itemType === 'item').length
        }
      })
    }

    return count
  } else if (props.containers && props.containers.length > 0) {
    let totalCount = 0
    props.containers.forEach(container => {
      const children = store.getChildrenOfItem(container.id)
      totalCount += children.filter(child => child.itemType === 'item').length

      if (includeNestedContainers.value) {
        children.forEach(child => {
          if (child.itemType === 'container') {
            const nestedChildren = store.getChildrenOfItem(child.id)
            totalCount += nestedChildren.filter(nc => nc.itemType === 'item').length
          }
        })
      }
    })
    return totalCount
  }
  return 0
})

// Select all columns
const selectAllColumns = () => {
  selectedColumns.value = availableColumns.value.map(col => col.key)
}

// Deselect all columns
const deselectAllColumns = () => {
  selectedColumns.value = []
}

// Toggle column selection
const toggleColumn = (columnKey: string) => {
  const index = selectedColumns.value.indexOf(columnKey)
  if (index > -1) {
    selectedColumns.value.splice(index, 1)
  } else {
    selectedColumns.value.push(columnKey)
  }
}

// Handle export
const handleExport = () => {
  if (selectedColumns.value.length === 0) {
    toast.error(t('gear.export.csv.noColumnsSelected', 'Please select at least one column'))
    return
  }

  try {
    let csv: string
    let fileName: string

    if (props.container) {
      csv = exportContainerToCSVV2(
        props.container,
        {
          columns: selectedColumns.value,
          separator: selectedSeparator.value,
          useBOM: useBOM.value,
          includeNestedContainers: includeNestedContainers.value,
          getChildrenOfItem: store.getChildrenOfItem,
        },
      )
      fileName = generateCSVFileName(props.container.name)
    } else if (props.containers && props.containers.length > 0) {
      csv = exportContainersToCSVV2(
        props.containers,
        {
          columns: selectedColumns.value,
          separator: selectedSeparator.value,
          useBOM: useBOM.value,
          includeNestedContainers: includeNestedContainers.value,
          getChildrenOfItem: store.getChildrenOfItem,
        },
      )
      fileName = generateAllContainersCSVFileName()
    } else {
      toast.error(t('gear.export.noContainers', 'No containers to export'))
      return
    }

    // Create blob and download
    const blob = new Blob(
      [csv],
      { type: 'text/csv;charset=utf-8;' },
    )

    downloadBlob(blob, fileName)

    open.value = false
    toast.success(t('gear.export.csv.success', 'CSV exported successfully'))
  } catch (error) {
    toast.error(t('common.error'))
    console.error('Error exporting CSV:', error)
  }
}

// Handle cancel
const handleCancel = () => {
  open.value = false
}

// Group columns by category
const columnsByCategory = computed(() => {
  const groups: Record<string, typeof availableColumns.value> = {}
  availableColumns.value.forEach(col => {
    if (!groups[col.category]) {
      groups[col.category] = []
    }
    groups[col.category]!.push(col)
  })
  return groups
})

// Category labels
const categoryLabels: Record<string, string> = {
  basic: t('gear.export.csv.categoryBasic', 'Podstawowe'),
  additional: t('gear.export.csv.categoryAdditional', 'Dodatkowe'),
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="min-w-full md:min-w-3xl max-w-screen md:max-w-5xl max-h-[90vh] flex flex-col">
      <DialogHeader>
        <DialogTitle>
          {{ t('gear.export.csv.title', 'Export to CSV') }}
        </DialogTitle>
        <DialogDescription>
          {{ t('gear.export.csv.description', 'Configure CSV export options') }}
        </DialogDescription>
      </DialogHeader>

      <div class="flex flex-col gap-4 overflow-y-auto flex-1">
        <!-- Column Selection -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <Label class="text-sm font-medium">
              {{ t('gear.export.csv.columns', 'Columns to Export') }}
            </Label>
            <div class="flex gap-2">
              <Button variant="outline" size="sm" @click="selectAllColumns">
                {{ t('gear.export.csv.selectAll', 'Select All') }}
              </Button>
              <Button variant="outline" size="sm" @click="deselectAllColumns">
                {{ t('gear.export.csv.deselectAll', 'Deselect All') }}
              </Button>
            </div>
          </div>
          <div class="space-y-4">
            <div
              v-for="(columns, category) in columnsByCategory"
              :key="category"
              class="space-y-2"
            >
              <Label class="text-xs font-medium text-muted-foreground">
                {{ categoryLabels[category] }}
              </Label>
              <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                <div
                  v-for="column in columns"
                  :key="column.key"
                  class="flex items-center space-x-2"
                >
                  <Checkbox
                    :id="`column-${column.key}`"
                    :model-value="selectedColumns.includes(column.key)"
                    @update:model-value="() => toggleColumn(column.key)"
                  />
                  <Label
                    :for="`column-${column.key}`"
                    class="text-sm font-normal cursor-pointer"
                  >
                    {{ column.label }}
                  </Label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <Separator />

        <!-- Separator Selection -->
        <div class="space-y-3">
          <Label class="text-sm font-medium">
            {{ t('gear.export.csv.separator', 'Separator') }}
          </Label>
          <RadioGroup v-model="selectedSeparator" class="gap-3">
            <div class="flex items-center space-x-2">
              <RadioGroupItem id="separator-comma" value="," />
              <Label for="separator-comma" class="font-normal cursor-pointer">
                {{ t('gear.export.csv.separatorComma', 'Comma (,)') }}
              </Label>
            </div>
            <div class="flex items-center space-x-2">
              <RadioGroupItem id="separator-semicolon" value=";" />
              <Label for="separator-semicolon" class="font-normal cursor-pointer">
                {{ t('gear.export.csv.separatorSemicolon', 'Semicolon (;)') }}
              </Label>
            </div>
          </RadioGroup>
        </div>

        <!-- Encoding Option -->
        <div class="flex items-center space-x-2">
          <Checkbox id="useBOM" v-model="useBOM" />
          <Label for="useBOM" class="text-sm font-normal cursor-pointer">
            {{ t('gear.export.csv.useBOM', 'UTF-8 with BOM (for Excel compatibility)') }}
          </Label>
        </div>

        <!-- Include Nested Containers -->
        <div class="flex items-center space-x-2">
          <Checkbox id="includeNested" v-model="includeNestedContainers" />
          <Label for="includeNested" class="text-sm font-normal cursor-pointer">
            {{ t('gear.export.csv.includeNested', 'Include nested containers') }}
          </Label>
        </div>
      </div>

      <Separator />

      <!-- Preview Info -->
      <div class="text-sm text-foreground">
        {{ t('gear.export.csv.itemsCount', { count: itemCount }) }}
      </div>

      <DialogFooter>
        <Button variant="outline" @click="handleCancel">
          {{ t('common.cancel') }}
        </Button>
        <Button @click="handleExport">
          {{ t('gear.export.csv.export', 'Export') }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

