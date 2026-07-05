/**
 * Export container data to JSON format (V2 - Unified Model)
 *
 * Produces a nested tree of gear items (containers + their children) that can be
 * inspected or re-imported. Each node is the full gear item plus a `children` array.
 */

import type { IGearItemV2 } from '../types/gear.types.v2'

export interface JSONExportOptionsV2 {
  getChildrenOfItem: (id: string) => IGearItemV2[]
  includeNestedContainers: boolean
}

export interface JSONExportNodeV2 extends IGearItemV2 {
  children: JSONExportNodeV2[]
}

export interface JSONExportDocumentV2 {
  version: 2
  exportedAt: string
  containers: JSONExportNodeV2[]
}

/**
 * Recursively build an export node (item + its children) from the store.
 */
function buildNodeV2(
  item: IGearItemV2,
  getChildrenOfItem: (id: string) => IGearItemV2[],
  includeNested: boolean,
): JSONExportNodeV2 {
  const children = getChildrenOfItem(item.id)
    .filter(child => includeNested || child.itemType === 'item')
    .map(child => buildNodeV2(child, getChildrenOfItem, includeNested))

  return { ...item, children }
}

/**
 * Export multiple containers to a JSON string (V2).
 */
export function exportContainersToJSONV2(
  containers: IGearItemV2[],
  options: JSONExportOptionsV2,
): string {
  const document: JSONExportDocumentV2 = {
    version: 2,
    exportedAt: new Date().toISOString(),
    containers: containers.map(container =>
      buildNodeV2(container, options.getChildrenOfItem, options.includeNestedContainers),
    ),
  }

  return JSON.stringify(document, null, 2)
}

/**
 * Sanitize a name for use in a file name.
 */
function sanitizeFileName(name: string): string {
  return name
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '') // Remove diacritics
    .replace(/[^a-z0-9\s-]/g, '') // Remove special chars
    .trim()
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/-+/g, '-') // Collapse multiple hyphens
}

/**
 * Generate JSON file name from container name.
 */
export function generateJSONFileName(containerName: string): string {
  const date = new Date().toISOString().split('T')[0] // YYYY-MM-DD
  return `gear-export-${sanitizeFileName(containerName)}-${date}.json`
}

/**
 * Generate JSON file name for multiple containers.
 */
export function generateAllContainersJSONFileName(): string {
  const date = new Date().toISOString().split('T')[0] // YYYY-MM-DD
  return `gear-export-all-${date}.json`
}
