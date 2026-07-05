import {
  Archive,      // cabinet, drawer
  Backpack,     // backpack
  Box,          // box
  Briefcase,    // case
  Car,          // vehicle
  CookingPot,   // naczynie
  Layers,       // shelf
  Luggage,      // trunk
  Package,      // other (default)
  Shirt,        // ubranie
  ShoppingBag,  // bag, pouch
} from 'lucide-vue-next'
import type { TGearContainerType } from '../types/gear.types'
import type { Component } from 'vue'

export const CONTAINER_ICONS: Record<string, Component> = {
  backpack: Backpack,
  bag: ShoppingBag,
  pouch: ShoppingBag,
  box: Box,
  cabinet: Archive,
  vehicle: Car,
  shelf: Layers,
  drawer: Archive,
  case: Briefcase,
  trunk: Luggage,
  ubranie: Shirt,
  naczynie: CookingPot,
  other: Package,
}

/**
 * Get icon component for a container type
 * @param type - Container type key
 * @returns Icon component, defaults to Package icon for unknown types
 */
export function getContainerIcon(type: TGearContainerType | null | undefined): Component {
  return CONTAINER_ICONS[type ?? 'other'] ?? (CONTAINER_ICONS.other as Component)
}

