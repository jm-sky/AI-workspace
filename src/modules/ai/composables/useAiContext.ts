/**
 * AI Context Composable
 * Handles context building for AI requests
 */

import { computed, ref } from 'vue'
import { useGearStoreV2 } from '@/modules/gear/store/useGearStoreV2'
import { useAiStore } from '../store/useAiStore'
import type { IGearItemV2 } from '@/modules/gear/types/gear.types.v2'

export interface IAiContext {
  container_ids?: string[]
  fields?: string[]
}

export function useAiContext() {
  const aiStore = useAiStore()
  const gearStore = useGearStoreV2()

  const selectedContainerIds = ref<string[]>([])
  const selectedFields = ref<string[]>(['name', 'category', 'weight'])

  const availableFields = computed<string[]>(() => {
    // Common fields that can be sent to AI
    return [
      'name',
      'notes',
      'category',
      'weight',
      'quantity',
      'price',
      'url',
      'brand',
      'color',
      'quality',
      'wearable',
      'consumable',
    ]
  })

  const contextFields = computed<string[]>(() => {
    const settingsFields = aiStore.settings?.contextFields
    // Convert Record<string, any> to string[] by taking the keys
    if (settingsFields && typeof settingsFields === 'object' && !Array.isArray(settingsFields)) {
      return Object.keys(settingsFields)
    }
    // Fallback to selectedFields if no settings or if it's already an array (backward compatibility)
    return Array.isArray(settingsFields) ? settingsFields : selectedFields.value
  })

  const buildContext = (): IAiContext => {
    return {
      container_ids: selectedContainerIds.value.length > 0 ? selectedContainerIds.value : undefined,
      fields: selectedFields.value.length > 0 ? selectedFields.value : undefined,
    }
  }

  const getContainerData = (containerId: string): IGearItemV2 | undefined => {
    const item = gearStore.getItemById(containerId)
    return item && item.itemType === 'container' ? item : undefined
  }

  const getItemsData = (containerId: string): IGearItemV2[] => {
    return gearStore.getChildrenOfItem(containerId).filter(child => child.itemType === 'item')
  }

  const buildContextData = (containerIds?: string[]): Record<string, unknown> => {
    const data: Record<string, unknown> = {}

    const ids = containerIds && containerIds.length > 0 ? containerIds : selectedContainerIds.value

    if (ids.length === 0) {
      return data
    }

    const fields = selectedFields.value

    for (const containerId of ids) {
      const container = getContainerData(containerId)
      if (!container) continue

      const containerData: Record<string, unknown> = {
        id: container.id,
        name: container.name,
      }

      // Always include items for context
      const items = getItemsData(containerId)
      containerData.items = items.map((item: IGearItemV2) => {
        const itemData: Record<string, unknown> = { id: item.id }

        if (fields.includes('name')) itemData.name = item.name
        if (fields.includes('notes') && item.notes) itemData.notes = item.notes
        if (fields.includes('category')) itemData.category = item.category
        if (fields.includes('weight') && item.weight) itemData.weight = item.weight
        if (fields.includes('quantity') && item.quantity) itemData.quantity = item.quantity
        if (fields.includes('price') && item.price) itemData.price = item.price
        if (fields.includes('url') && item.url) itemData.url = item.url
        if (fields.includes('wearable')) itemData.wearable = item.wearable
        if (fields.includes('consumable')) itemData.consumable = item.consumable

        return itemData
      })

      data[containerId] = containerData
    }

    return data
  }

  const setContainerIds = (ids: string[]): void => {
    selectedContainerIds.value = ids
  }

  const setFields = (fields: string[]): void => {
    selectedFields.value = fields
  }

  const toggleField = (field: string): void => {
    const index = selectedFields.value.indexOf(field)
    if (index > -1) {
      selectedFields.value.splice(index, 1)
    } else {
      selectedFields.value.push(field)
    }
  }

  return {
    selectedContainerIds,
    selectedFields,
    availableFields,
    contextFields,
    buildContext,
    getContainerData,
    getItemsData,
    buildContextData,
    setContainerIds,
    setFields,
    toggleField,
  }
}

