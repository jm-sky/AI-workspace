import {
  Backpack,
  Compass,        // navigation
  Droplet,        // water
  Flame,          // fire
  HeartPulse,     // firstAid
  Lightbulb,      // light
  Package,        // other (default)
  PocketKnife,    // blades
  Radio,          // communication
  Shirt,          // clothing
  Sparkles,       // hygiene
  Tent,           // shelter
  UtensilsCrossed, // food
  Wrench,         // tools
} from 'lucide-vue-next'
import type { TGearItemCategory } from '../types/gear.types'
import type { Component } from 'vue'

export const CATEGORY_ICONS: Record<string, Component> = {
  water: Droplet,
  food: UtensilsCrossed,
  shelter: Tent,
  fire: Flame,
  firstAid: HeartPulse,
  blades: PocketKnife,
  tools: Wrench,
  light: Lightbulb,
  navigation: Compass,
  communication: Radio,
  clothing: Shirt,
  hygiene: Sparkles,
  container: Backpack,
  other: Package,
}

/**
 * Get icon component for a category
 * @param category - Category key
 * @returns Icon component, defaults to Package icon for unknown categories
 */
export function getCategoryIcon(category: TGearItemCategory): Component {
  return CATEGORY_ICONS[category] ?? (CATEGORY_ICONS.other as Component)
}

