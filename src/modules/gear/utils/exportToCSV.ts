/**
 * Export container data to CSV format
 */

import type { IGearContainer, IGearItem } from '../types/gear.types'

export interface CSVExportOptions {
  columns: string[] // Selected column names
  separator: ',' | ';'
  useBOM: boolean
  includeNestedContainers: boolean
}

type ColumnMapper = (item: IGearItem, container: IGearContainer) => string | number

/**
 * Column mapping functions
 */
const columnMap: Record<string, ColumnMapper> = {
  name: (item) => item.name,
  category: (item) => item.category,
  quantity: (item) => item.quantity,
  weight: (item) => item.weight,
  weightUnit: (item) => item.weightUnit,
  price: (item) => item.price ?? '',
  currency: (item) => item.currency ?? '',
  brand: (item) => item.brand ?? '',
  color: (item) => item.color ?? '',
  status: (item) => item.status,
  priority: (item) => item.priority,
  url: (item) => item.url ?? '',
  notes: (item) => item.notes ?? '',
  containerName: (item, container) => container.name,
  containerType: (item, container) => container.type,
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
 * Collect all items from container and nested containers
 */
function collectAllItems(
  container: IGearContainer,
  allContainers: IGearContainer[],
  includeNested: boolean,
): Array<{ item: IGearItem; container: IGearContainer }> {
  const items: Array<{ item: IGearItem; container: IGearContainer }> = []
  
  // Add items from current container
  container.items.forEach(item => {
    items.push({ item, container })
    
    // If item references nested container and includeNested is true, recurse
    if (includeNested && item.containerId) {
      const nestedContainer = allContainers.find(c => c.id === item.containerId)
      if (nestedContainer) {
        items.push(...collectAllItems(nestedContainer, allContainers, includeNested))
      }
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
 * Generate CSV data row for an item
 */
function generateDataRow(
  item: IGearItem,
  container: IGearContainer,
  columns: string[],
  separator: ',' | ';',
): string {
  return columns.map(col => {
    const mapper = columnMap[col]
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
 * Export container to CSV format
 */
export function exportContainerToCSV(
  container: IGearContainer,
  allContainers: IGearContainer[],
  options: CSVExportOptions,
): string {
  // Collect all items (including nested if enabled)
  const items = collectAllItems(container, allContainers, options.includeNestedContainers)
  
  // Generate header row
  const header = generateHeaderRow(options.columns, options.separator)
  
  // Generate data rows
  const rows = items.map(({ item, container: itemContainer }) =>
    generateDataRow(item, itemContainer, options.columns, options.separator),
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
 * Export multiple containers to CSV format
 */
export function exportContainersToCSV(
  containers: IGearContainer[],
  allContainers: IGearContainer[],
  options: CSVExportOptions,
): string {
  // Collect all items from all containers
  const allItems: Array<{ item: IGearItem; container: IGearContainer }> = []
  
  containers.forEach(container => {
    const items = collectAllItems(container, allContainers, options.includeNestedContainers)
    allItems.push(...items)
  })
  
  // Generate header row
  const header = generateHeaderRow(options.columns, options.separator)
  
  // Generate data rows
  const rows = allItems.map(({ item, container }) =>
    generateDataRow(item, container, options.columns, options.separator),
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

