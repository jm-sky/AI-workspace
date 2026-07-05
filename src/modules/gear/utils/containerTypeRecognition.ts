import type { TGearContainerType } from '../types/gear.types'

/**
 * Keywords for container type recognition
 * Supports both Polish and English keywords
 */
export const CONTAINER_TYPE_KEYWORDS: Record<string, string[]> = {
  backpack: [
    // English
    'backpack', 'rucksack', 'pack',
    // Polish
    'plecak', 'tornister',
  ],
  bag: [
    // English
    'bag', 'sack', 'pouch',
    // Polish
    'torba', 'worek', 'sakwa',
  ],
  pouch: [
    // English
    'pouch', 'pocket', 'case', 'small',
    // Polish
    'pouch', 'kieszeń', 'etui', 'mały',
  ],
  box: [
    // English
    'box', 'container', 'storage',
    // Polish
    'skrzynka', 'pojemnik', 'magazyn',
  ],
  cabinet: [
    // English
    'cabinet', 'closet', 'wardrobe',
    // Polish
    'szafa', 'szafka', 'garderoba',
  ],
  vehicle: [
    // English
    'vehicle', 'car', 'truck', 'van',
    // Polish
    'pojazd', 'samochód', 'auto', 'furgonetka',
  ],
  shelf: [
    // English
    'shelf', 'rack',
    // Polish
    'półka', 'regał',
  ],
  drawer: [
    // English
    'drawer',
    // Polish
    'szuflada',
  ],
  case: [
    // English
    'case', 'suitcase', 'briefcase',
    // Polish
    'walizka', 'kufer', 'teczka',
  ],
  trunk: [
    // English
    'trunk', 'boot',
    // Polish
    'bagażnik', 'kufer',
  ],
  ubranie: [
    // English
    'clothing', 'garment', 'wear',
    // Polish
    'ubranie', 'odzież', 'odzienie',
  ],
  naczynie: [
    // English
    'vessel', 'dish', 'bowl', 'pot', 'pan',
    // Polish
    'naczynie', 'miska', 'garnek', 'patelnia',
  ],
}

/**
 * Recognize container type from name
 * Checks keywords from longest to shortest to avoid false matches
 * (e.g., "bagażnik" should match "bagażnik" not "bag")
 * @param name - Container name to analyze
 * @returns Detected container type or null if no match
 */
export function recognizeContainerType(name: string): TGearContainerType | null {
  if (!name || name.trim().length === 0) {
    return null
  }

  const normalizedName = name.toLowerCase().trim()

  // Collect all (type, keyword) pairs with keyword length
  const typeKeywordPairs: Array<{ type: string; keyword: string; length: number }> = []
  for (const [type, keywords] of Object.entries(CONTAINER_TYPE_KEYWORDS)) {
    for (const keyword of keywords) {
      typeKeywordPairs.push({
        type,
        keyword: keyword.toLowerCase(),
        length: keyword.length,
      })
    }
  }

  // Sort by keyword length (longest first) to check longer matches first
  typeKeywordPairs.sort((a, b) => b.length - a.length)

  // Check matches starting from longest keywords
  for (const { type, keyword } of typeKeywordPairs) {
    if (normalizedName.includes(keyword)) {
      return type as TGearContainerType
    }
  }

  return null
}

