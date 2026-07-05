import type {
  TGearContainerType,
  TGearItemCategory,
  TGearItemPriority,
  TGearItemQuality,
  TGearItemStatus,
  TGearWeightUnit,
} from '../types/gear.types'
import type { ICreateGearItemV2Dto, IGearItemV2 } from '../types/gear.types.v2'
import {
  bugOutBagFirePouchItems,
  bugOutBagItems,
  edcItems,
  firePouchItems,
  type IExampleSetItem,
} from './exampleSets'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Function that creates a gear item (container or item) — injected from the caller so this
 * service stays decoupled from Vue composables and works with the active V2 service.
 */
export type CreateGearItemFn = (data: ICreateGearItemV2Dto) => Promise<IGearItemV2>

export type SampleSetVariant = 'firePouch' | 'bugOutBag' | 'edc' | 'budgetEdc' | 'mediumEdc'

interface ISampleSetItem {
  name: string
  catalogueItemId?: string
  category: TGearItemCategory
  weight: number
  weightUnit: TGearWeightUnit
  quantity?: number
  priority?: TGearItemPriority
  status?: TGearItemStatus
  brand?: string
  notes?: string
  color?: string
  price?: number
  currency?: string
  url?: string
  quality?: TGearItemQuality
  consumable?: boolean
}

interface ISampleSetContainer {
  name: string
  type: 'backpack' | 'bag' | 'pouch' | 'box' | 'cabinet' | 'vehicle' | 'shelf' | 'drawer' | 'case' | 'trunk' | 'other'
  description?: string
  items: ISampleSetItem[]
  nestedContainers?: ISampleSetContainer[]
}

/**
 * Generates a sample gear set with containers and items
 * @param t - Translation function from vue-i18n
 * @param variant - Variant of the sample set to generate
 * @returns Array of created container IDs
 */
export async function generateSampleSet(
  t: (key: string) => string,
  variant: SampleSetVariant = 'bugOutBag',
  createItem?: CreateGearItemFn,
): Promise<TUUID[]> {
  if (!createItem) {
    throw new Error('generateSampleSet requires a createItem function')
  }

  const setDefinition = getSampleSetDefinition(t, variant)
  const containerIds: TUUID[] = []

  // Create main container
  const mainContainer = await createItem({
    itemType: 'container',
    parentItemId: null,
    name: setDefinition.name,
    containerType: setDefinition.type as TGearContainerType,
    description: setDefinition.description ?? null,
  })
  containerIds.push(mainContainer.id)

  // Recursively create nested containers and items
  await createContainerWithItems(mainContainer.id, setDefinition, createItem)

  return containerIds
}

async function createContainerWithItems(
  containerId: TUUID,
  containerDef: ISampleSetContainer,
  createItem: CreateGearItemFn,
): Promise<void> {
  // Create nested containers first (V2-native: parentItemId links them to this container)
  const nestedContainerNames = new Set<string>()
  if (containerDef.nestedContainers) {
    for (const nestedDef of containerDef.nestedContainers) {
      const nestedContainer = await createItem({
        itemType: 'container',
        parentItemId: containerId,
        name: nestedDef.name,
        containerType: nestedDef.type as TGearContainerType,
        description: nestedDef.description ?? null,
      })
      nestedContainerNames.add(nestedDef.name)
      // Recursively create items in nested container
      await createContainerWithItems(nestedContainer.id, nestedDef, createItem)
    }
  }

  // Create items in this container
  for (const item of containerDef.items) {
    // Skip placeholder items that just mirror a nested container (V1 dual-model artifact)
    if (nestedContainerNames.has(item.name)) {
      continue
    }

    await createItem({
      itemType: 'item',
      parentItemId: containerId,
      name: item.name,
      catalogueItemId: item.catalogueItemId ?? null,
      category: item.category,
      weight: item.weight,
      weightUnit: item.weightUnit,
      quantity: item.quantity ?? 1,
      priority: item.priority ?? 'medium',
      status: item.status ?? 'owned',
      brand: item.brand ?? null,
      notes: item.notes ?? null,
      description: item.notes ?? null,
      color: item.color ?? null,
      price: item.price ?? null,
      currency: item.currency ?? null,
      url: item.url ?? null,
      quality: item.quality ?? null,
      consumable: item.consumable ?? null,
    })
  }
}

/**
 * Helper function to translate with fallback
 * If translation returns the key (meaning translation not found), use fallback
 */
function translateWithFallback(
  t: (key: string, ...args: unknown[]) => string,
  key: string,
  fallback: string
): string {
  const translated = t(key)
  // If translation returns the key itself (or starts with the key pattern), it means translation was not found
  // vue-i18n may return the key with some prefix or modification when not found
  if (translated === key || translated.startsWith(key + '.') || translated.includes('[') && translated.includes(key)) {
    return fallback
  }
  return translated
}

/**
 * Converts example set items to sample set items with translated names and notes
 */
function translateItems(
  items: IExampleSetItem[],
  t: (key: string) => string
): ISampleSetItem[] {
  return items.map(item => {
    // Extract item key from full path (e.g., 'gear.sampleSet.items.lightMyFireFiresteel' -> 'lightMyFireFiresteel')
    const itemKey = item.nameKey.split('.').pop() || item.nameKey

    // Get translated name using new nested structure: gear.sampleSet.items.{itemKey}.name
    const nameKey = `${item.nameKey}.name`
    const fallbackName = itemKey
    const translatedName = translateWithFallback(t, nameKey, fallbackName)

    // Get translated notes using new nested structure: gear.sampleSet.items.{itemKey}.notes
    const notesKey = item.notesKey ? item.notesKey.replace('.notes', '.notes') : undefined
    const translatedNotes = notesKey
      ? translateWithFallback(t, notesKey, '')
      : undefined

    return {
      name: translatedName,
      catalogueItemId: item.catalogueItemId,
      category: item.category,
      weight: item.weight,
      weightUnit: item.weightUnit,
      quantity: item.quantity,
      priority: item.priority ?? 'medium',
      status: item.status ?? 'owned',
      brand: item.brand,
      notes: translatedNotes,
      color: item.color,
      price: item.price,
      currency: item.currency ?? 'USD',
      url: item.url,
      quality: item.quality,
      consumable: item.consumable,
    }
  })
}

function getSampleSetDefinition(
  t: (key: string) => string,
  variant: SampleSetVariant
): ISampleSetContainer {
  switch (variant) {
    case 'bugOutBag': {
      const firePouchName = translateWithFallback(
        t,
        'gear.sampleSet.variants.bugOutBag.firePouch',
        'Fire Pouch'
      )
      return {
        name: translateWithFallback(
          t,
          'gear.sampleSet.variants.bugOutBag.name',
          'Bug Out Bag'
        ),
        type: 'backpack',
        description: translateWithFallback(
          t,
          'gear.sampleSet.variants.bugOutBag.description',
          'Complete survival kit for emergency situations'
        ),
        nestedContainers: [
          {
            name: firePouchName,
            type: 'pouch',
            items: translateItems(bugOutBagFirePouchItems, t),
          },
        ],
        items: [
          ...translateItems(bugOutBagItems, t),
          {
            name: firePouchName,
            category: 'tools' as const,
            weight: 80,
            weightUnit: 'g' as const,
            quantity: 1,
            priority: 'high' as const,
            status: 'owned' as const,
          },
        ],
      }
    }

    case 'edc':
      return {
        name: translateWithFallback(
          t,
          'gear.sampleSet.variants.edc.name',
          'EDC (Every Day Carry)'
        ),
        type: 'bag',
        description: translateWithFallback(
          t,
          'gear.sampleSet.variants.edc.description',
          'Essential items for daily carry'
        ),
        items: translateItems(edcItems, t),
      }

    case 'firePouch':
      return {
        name: translateWithFallback(
          t,
          'gear.sampleSet.variants.firePouch.name',
          'Fire Pouch'
        ),
        type: 'pouch',
        description: translateWithFallback(
          t,
          'gear.sampleSet.variants.firePouch.description',
          'Minimalist fire starting kit'
        ),
        items: translateItems(firePouchItems, t),
      }

    default:
      throw new Error(`Unknown sample set variant: ${variant}`)
  }
}
