import type { IGearItem } from './gear.types'

// Item with container ID for navigation (used in shopping planning)
export interface IItemWithContainerId extends IGearItem {
  _containerId: string // Internal field to track container ID
}
