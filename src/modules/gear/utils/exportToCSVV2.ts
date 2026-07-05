/**
 * Export container data to CSV format (V2 - Unified Model)
 */

import type { IGearItemV2 } from '../types/gear.types.v2'

export interface CSVExportOptionsV2 {
  columns: string[] // Selected column names
  separator: ',' | ';'
  useBOM: boolean
  includeNestedContainers: boolean
  getChildrenOfItem?: (id: string) => IGearItemV2[]
}

type ColumnMapperV2 = (item: IGearItemV2, container: IGearItemV2) => string | number

/**
 * Column mapping functions for V2
 */
const columnMapV2: Record<string, ColumnMapperV2> = {
  name: (item) => item.name,
  category: (item) => item.category ?? '',
  quantity: (item) => item.quantity ?? 1,
  weight: (item) => item.weight ?? 0,
  weightUnit: (item) => item.weightUnit ?? '',
  price: (item) => item.price ?? '',
  currency: (item) => item.currency ?? '',
  brand: (item) => item.brand ?? '',
  color: (item) => item.color ?? '',
  status: (item) => item.status ?? 'owned',
  priority: (item) => item.priority ?? '',
  url: (item) => item.url ?? '',
  notes: (item) => item.notes ?? '',
  containerName: (item, container) => container.name,
  containerType: (item, container) => container.containerType ?? 'backpack',
}

/**
 * Escape CSV value according to RFC 4180
 */
function escapeCSVValue(value: string | number | null | undefined, separator: ',' | ';'): string {
  if (value === null || value === undefined) {
    return ''
  }
  const str = String(value)

  // If contains separator, quote, or newline, wrap in quotes and escape quotes
  if (str.includes(separator) || str.includes('"') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`
  }
  return str
}

/**
 * Collect all items from container and nested containers (V2)
 */
function collectAllItemsV2(
  container: IGearItemV2,
  getChildrenOfItem: (id: string) => IGearItemV2[],
  includeNested: boolean,
): Array<{ item: IGearItemV2; container: IGearItemV2 }> {
  const items: Array<{ item: IGearItemV2; container: IGearItemV2 }> = []

  // Get children of this container
  const children = getChildrenOfItem(container.id)

  children.forEach(child => {
    if (child.itemType === 'item') {
      // Regular item
      items.push({ item: child, container })
    } else if (child.itemType === 'container' && includeNested) {
      // Nested container - recurse
      items.push(...collectAllItemsV2(child, getChildrenOfItem, includeNested))
    }
  })

  return items
}

/**
 * Generate CSV header row
 */
function generateHeaderRow(columns: string[], separator: ',' | ';'): string {
  return columns.map(col => escapeCSVValue(col, separator)).join(separator)
}

/**
 * Generate CSV data row for an item (V2)
 */
function generateDataRowV2(
  item: IGearItemV2,
  container: IGearItemV2,
  columns: string[],
  separator: ',' | ';',
): string {
  return columns.map(col => {
    const mapper = columnMapV2[col]
    if (!mapper) {
      return ''
    }
    const value = mapper(item, container)
    return escapeCSVValue(value, separator)
  }).join(separator)
}

/**
 * Add UTF-8 BOM to CSV string
 */
function addBOM(csv: string): string {
  return '\uFEFF' + csv
}

/**
 * Export container to CSV format (V2)
 */
export function exportContainerToCSVV2(
  container: IGearItemV2,
  options: CSVExportOptionsV2,
): string {
  if (!options.getChildrenOfItem) {
    throw new Error('getChildrenOfItem function is required for V2 export')
  }

  // Collect all items (including nested if enabled)
  const items = collectAllItemsV2(container, options.getChildrenOfItem, options.includeNestedContainers)

  // Generate header row
  const header = generateHeaderRow(options.columns, options.separator)

  // Generate data rows
  const rows = items.map(({ item, container: itemContainer }) =>
    generateDataRowV2(item, itemContainer, options.columns, options.separator),
  )

  // Combine header and rows
  const csv = [header, ...rows].join('\n')

  // Add BOM if enabled
  return options.useBOM ? addBOM(csv) : csv
}

/**
 * Generate CSV file name from container name
 */
export function generateCSVFileName(containerName: string): string {
  const sanitized = containerName
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Remove diacritics
    .replace(/[^a-z0-9\s-]/g, '') // Remove special chars
    .trim()
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/-+/g, '-') // Collapse multiple hyphens

  const date = new Date().toISOString().split('T')[0] // YYYY-MM-DD
  return `gear-export-${sanitized}-${date}.csv`
}

/**
 * Export multiple containers to CSV format (V2)
 */
export function exportContainersToCSVV2(
  containers: IGearItemV2[],
  options: CSVExportOptionsV2,
): string {
  if (!options.getChildrenOfItem) {
    throw new Error('getChildrenOfItem function is required for V2 export')
  }

  // Collect all items from all containers
  const allItems: Array<{ item: IGearItemV2; container: IGearItemV2 }> = []
  const getChildrenOfItem = options.getChildrenOfItem // Non-null assertion safe due to check above

  containers.forEach(container => {
    const items = collectAllItemsV2(container, getChildrenOfItem, options.includeNestedContainers)
    allItems.push(...items)
  })

  // Generate header row
  const header = generateHeaderRow(options.columns, options.separator)

  // Generate data rows
  const rows = allItems.map(({ item, container }) =>
    generateDataRowV2(item, container, options.columns, options.separator),
  )

  // Combine header and rows
  const csv = [header, ...rows].join('\n')

  // Add BOM if enabled
  return options.useBOM ? addBOM(csv) : csv
}

/**
 * Generate CSV file name for multiple containers
 */
export function generateAllContainersCSVFileName(): string {
  const date = new Date().toISOString().split('T')[0] // YYYY-MM-DD
  return `gear-export-all-${date}.csv`
}

/**
 * Get default separator based on locale
 */
export function getDefaultSeparator(locale: string): ',' | ';' {
  // Polish locale uses semicolon, others use comma
  return locale.startsWith('pl') ? ';' : ','
}
