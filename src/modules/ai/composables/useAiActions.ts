/**
 * AI Actions Composable
 * Handles executing actions from AI structured output
 */

import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { useGearMutations } from '@/modules/gear/composables/useGearMutations'
import { useGearStoreV2 } from '@/modules/gear/store/useGearStoreV2'
import { recognizeCategory } from '@/modules/gear/utils/categoryRecognition'
import type { IAiStructuredOutput } from '../types'
import type { ICreateGearItemV2Dto, IUpdateGearItemV2Dto, TGearWeightUnit } from '@/modules/gear/types/gear.types.v2'

export function useAiActions() {
  const { t } = useI18n()
  const gearStore = useGearStoreV2()
  const { createItem, updateItem, deleteItem } = useGearMutations()

  const containerExists = (containerId: string): boolean => {
    const item = gearStore.getItemById(containerId)
    return !!item && item.itemType === 'container'
  }

  const executeAction = async (
    structuredOutput: IAiStructuredOutput | null,
    containerId?: string,
  ): Promise<boolean> => {
    if (!structuredOutput || !structuredOutput.action || structuredOutput.action === 'None') {
      return false
    }

    const { action, data } = structuredOutput

    try {
      switch (action) {
        case 'create_container':
          return await handleCreateContainer(data)

        case 'create_item':
          return await handleCreateItem(data, containerId)

        case 'delete_item':
          return await handleDeleteItem(data, containerId)

        case 'update_item':
          return await handleUpdateItem(data, containerId)

        default:
          console.warn(`Unknown AI action: ${action}`)
          return false
      }
    } catch (error) {
      console.error('Error executing AI action:', error)
      toast.error(t('ai.actions.error'))
      return false
    }
  }

  const handleCreateItem = async (
    data: Record<string, unknown>,
    containerId?: string,
  ): Promise<boolean> => {
    if (!containerId) {
      toast.error(t('ai.actions.noContainer'))
      return false
    }

    const name = data.name as string

    // Validate required fields
    if (!name) {
      toast.error(t('ai.actions.invalidData'))
      return false
    }

    // Parse weight - handle both string ("5g") and number formats
    let weight: number = 0
    let weightUnit: TGearWeightUnit = 'g'

    const weightValue = data.weight
    if (typeof weightValue === 'string') {
      // Parse weight string like "5g", "2.5kg", "16oz", "2lb"
      const weightMatch = weightValue.match(/^(\d+(?:[.,]\d+)?)\s*(g|kg|oz|lb)$/i)
      if (weightMatch) {
        weight = Number.parseFloat((weightMatch[1] ?? '0').replace(',', '.'))
        const unit = weightMatch[2]?.toLowerCase() ?? 'g'
        weightUnit = (unit === 'kg' ? 'kg' : unit === 'oz' ? 'oz' : unit === 'lb' ? 'lb' : 'g') as TGearWeightUnit
      } else {
        // If string doesn't match pattern, try to parse as number
        const parsed = Number.parseFloat(weightValue.replace(',', '.'))
        if (!Number.isNaN(parsed)) {
          weight = parsed
        }
      }
    } else if (typeof weightValue === 'number') {
      weight = weightValue
      // If weightUnit is provided separately, use it
      if (data.weightUnit) {
        weightUnit = data.weightUnit as TGearWeightUnit
      }
    }

    // Default weight to 100g if not provided or invalid
    if (weight <= 0 || Number.isNaN(weight)) {
      weight = 100
      weightUnit = 'g'
    }

    // Determine category - use provided category, recognize from name, or default to 'other'
    let category: string = (data.category as string) ?? ''
    if (!category) {
      const recognized = recognizeCategory(name)
      category = recognized ?? 'other'
    }

    // Check if container exists
    if (!containerExists(containerId)) {
      toast.error(t('ai.actions.containerNotFound'))
      return false
    }

    // Build item from AI data with all required fields
    const newItem: ICreateGearItemV2Dto = {
      itemType: 'item',
      parentItemId: containerId,
      name,
      category: category as ICreateGearItemV2Dto['category'],
      weight,
      weightUnit,
      quantity: (data.quantity as number) ?? 1,
      priority: (data.priority as ICreateGearItemV2Dto['priority']) ?? 'medium',
      status: (data.status as ICreateGearItemV2Dto['status']) ?? 'owned',
      price: (data.price as number) ?? null,
      url: (data.url as string) ?? null,
      notes: (data.notes as string) ?? null,
      description: (data.notes as string) ?? null,
      brand: (data.brand as string) ?? null,
      color: (data.color as string) ?? null,
      wearable: (data.wearable as boolean) ?? null,
      consumable: (data.consumable as boolean) ?? null,
    }

    // Create item via V2 (API or localStorage based on backend status) + cache invalidation
    await createItem(newItem)
    toast.success(t('ai.actions.itemCreated', { name }))

    return true
  }

  const handleUpdateItem = async (
    data: Record<string, unknown>,
    containerId?: string,
  ): Promise<boolean> => {
    if (!containerId) {
      toast.error(t('ai.actions.noContainer'))
      return false
    }

    const itemId = data.id as string
    const updates = data.updates as Record<string, unknown>

    if (!itemId || !updates) {
      toast.error(t('ai.actions.invalidData'))
      return false
    }

    // Check if container exists
    if (!containerExists(containerId)) {
      toast.error(t('ai.actions.containerNotFound'))
      return false
    }

    // Update item via V2 (API or localStorage based on backend status) + cache invalidation
    await updateItem(itemId, updates as IUpdateGearItemV2Dto)
    toast.success(t('ai.actions.itemUpdated'))

    return true
  }

  const handleDeleteItem = async (
    data: Record<string, unknown>,
    containerId?: string,
  ): Promise<boolean> => {
    if (!containerId) {
      toast.error(t('ai.actions.noContainer'))
      return false
    }

    const itemId = data.id as string

    if (!itemId) {
      toast.error(t('ai.actions.invalidData'))
      return false
    }

    // Check if container exists
    if (!containerExists(containerId)) {
      toast.error(t('ai.actions.containerNotFound'))
      return false
    }

    // Delete item via V2 (API or localStorage based on backend status) + cache invalidation
    await deleteItem(itemId)
    toast.success(t('ai.actions.itemDeleted'))

    return true
  }

  const handleCreateContainer = async (data: Record<string, unknown>): Promise<boolean> => {
    const name = data.name as string

    if (!name) {
      toast.error(t('ai.actions.invalidData'))
      return false
    }

    // Create container via V2 (API or localStorage based on backend status) + cache invalidation
    await createItem({
      itemType: 'container',
      parentItemId: null,
      name,
      description: (data.description as string) ?? null,
      containerType: (data.container_type as ICreateGearItemV2Dto['containerType']) ?? 'backpack',
    })

    toast.success(t('ai.actions.containerCreated', { name }))

    return true
  }

  return {
    executeAction,
  }
}
