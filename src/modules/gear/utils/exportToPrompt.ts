/**
 * Export container data to markdown format for AI prompts
 */

import type { IGearContainer, IGearItem } from '../types/gear.types'
import { formatCurrency, getCurrency } from './currencyFormatter'
import { formatWeight, formatWeightFromGrams } from './formatWeight'
import { isSet } from './helpers'

interface ExportOptions {
  t?: (key: string, ...args: unknown[]) => string
  getContainerTypeLabel?: (type: string) => string
  getContainerById?: (id: string) => IGearContainer | undefined
  calculateTotalWeight?: (containerId: string) => number
  showUuid?: boolean // Whether to show UUID in export (default: true)
  showWeight?: boolean // Whether to show weight in export (default: true)
  showColor?: boolean // Whether to show color in export (default: true)
  showBrand?: boolean // Whether to show brand in export (default: true)
  showNestedContainer?: boolean // Whether to show nested container reference [#id] (default: true)
  showLegend?: boolean // Whether to show legend at the end (default: true)
  showPrices?: boolean // Whether to show prices in export (default: false)
  descriptionFormat?: 'off' | 'inline' | 'newline' // Description format (default: 'off')
  defaultCurrency?: string // Default currency to use when item/container doesn't have currency
  locale?: string // Locale for formatting numbers (default: 'pl-PL')
}

/**
 * Convert container name to slug for ID
 * Example: "First Aid Pouch" -> "first-aid-pouch"
 */
function slugify(text: string): string {
  return text
    .toLowerCase()
    .normalize('NFD') // Normalize unicode characters
    .replace(/[\u0300-\u036f]/g, '') // Remove diacritics
    .replace(/[^a-z0-9\s-]/g, '') // Remove special chars
    .trim()
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/-+/g, '-') // Replace multiple hyphens with single
}

/**
 * Generate ID for container from its name
 */
function generateContainerId(name: string): string {
  return `#${slugify(name)}`
}

/**
 * Format notes as indented block (for newline format)
 * Preserves Markdown and multiline structure
 */
function formatNotesAsIndentedBlock(notes: string, indent: number): string {
  const indentStr = '  '.repeat(indent)
  const noteIndent = '  ' // 2 spaces for note indentation
  const lines = notes.split('\n')
  return lines.map(line => `${indentStr}${noteIndent}${line}`).join('\n')
}

/**
 * Format item for markdown export (compact format)
 */
function formatItem(
  item: IGearItem,
  options: ExportOptions,
  indent = 0,
  defaultCurrency: string = 'PLN',
): string {
  const indentStr = '  '.repeat(indent)
  const parts: string[] = []

  // Item name
  parts.push(`**${item.name}**`)

  // Description in inline format (immediately after name, before other fields)
  // Only if descriptionFormat is inline
  if (item.notes && options.descriptionFormat === 'inline') {
    parts.push(`*(${item.notes})*`)
  }

  // UUID (for stable references) - only if showUuid is true (default: true)
  if (options.showUuid !== false) {
    parts.push(`[uuid:${item.id}]`)
  }

  // Quantity after name (x4 format)
  if (item.quantity > 1) {
    parts.push(`x${item.quantity}`)
  }

  // Brand and color in first parentheses
  const brandColorParts: string[] = []
  if (options.showBrand !== false && item.brand) {
    brandColorParts.push(item.brand)
  }
  if (options.showColor !== false && item.color) {
    brandColorParts.push(item.color)
  }
  if (brandColorParts.length > 0) {
    parts.push(`(${brandColorParts.join(', ')})`)
  }

  // Expiration and status in second parentheses
  const statusParts: string[] = []
  if (item.expirationDate) {
    const date = new Date(item.expirationDate)
    const dateStr = date.toLocaleDateString('pl-PL', { day: '2-digit', month: '2-digit', year: 'numeric' })
    statusParts.push(`Expiration: ${dateStr}`)
  }
  if (item.status && options.t) {
    const statusLabel = options.t(`gear.item.statuses.${item.status}`)
    // Only show status if it's not "owned"
    if (statusLabel !== options.t('gear.item.statuses.owned')) {
      statusParts.push(statusLabel)
    }
  }
  // Add wearable/consumable flags
  if (item.wearable) {
    statusParts.push('Wearable')
  }
  if (item.consumable) {
    statusParts.push('Consumable')
  }
  if (statusParts.length > 0) {
    parts.push(`(${statusParts.join(', ')})`)
  }

  // Container ID if this item is a nested container (only if showNestedContainer is true, default: true)
  if (options.showNestedContainer !== false && item.containerId && options.getContainerById) {
    const nestedContainer = options.getContainerById(item.containerId)
    if (nestedContainer) {
      const containerId = generateContainerId(nestedContainer.name)
      parts.push(`[${containerId}]`)
    }
  }

  // URL if provided
  if (item.url) {
    parts.push(`<${item.url}>`)
  }

  // Weight at the end (only if showWeight is true, default: true)
  if (options.showWeight !== false) {
    let totalWeight: number
    let weightText: string

    // If item is a nested container, use calculated total weight
    if (item.containerId && options.calculateTotalWeight) {
      const containerWeightInGrams = options.calculateTotalWeight(item.containerId)
      totalWeight = containerWeightInGrams * item.quantity
      weightText = formatWeightFromGrams(totalWeight, options.locale)
    } else {
      // Regular item weight
      totalWeight = item.weight * item.quantity
      weightText = formatWeight(totalWeight, item.weightUnit ?? 'g', options.locale)
    }

    parts.push(`- ${weightText}`)
  }

  // Price at the end (only if showPrices is true and item has price)
  if (options.showPrices && item.price) {
    const currency = getCurrency(item.currency, defaultCurrency)
    const totalPrice = item.price * (item.quantity || 1)
    const formattedPrice = formatCurrency(totalPrice, currency)
    parts.push(`- ${formattedPrice}`)
  }

  // For newline format, split the line: name + metadata on first line, description alone on second line
  // Only if descriptionFormat is newline
  if (item.notes && options.descriptionFormat === 'newline') {
    const namePart = `**${item.name}**`

    // Build first line with name and all metadata EXCEPT description and weight
    const firstLineParts: string[] = [namePart]

    // UUID
    if (options.showUuid !== false) {
      firstLineParts.push(`[uuid:${item.id}]`)
    }

    // Quantity
    if (item.quantity > 1) {
      firstLineParts.push(`x${item.quantity}`)
    }

    // Brand and color
    const brandColorParts: string[] = []
    if (options.showBrand !== false && item.brand) {
      brandColorParts.push(item.brand)
    }
    if (options.showColor !== false && item.color) {
      brandColorParts.push(item.color)
    }
    if (brandColorParts.length > 0) {
      firstLineParts.push(`(${brandColorParts.join(', ')})`)
    }

    // Status, expiration, wearable, consumable
    const statusParts: string[] = []
    if (item.expirationDate) {
      const date = new Date(item.expirationDate)
      const dateStr = date.toLocaleDateString('pl-PL', { day: '2-digit', month: '2-digit', year: 'numeric' })
      statusParts.push(`Expiration: ${dateStr}`)
    }
    if (item.status && options.t) {
      const statusLabel = options.t(`gear.item.statuses.${item.status}`)
      if (statusLabel !== options.t('gear.item.statuses.owned')) {
        statusParts.push(statusLabel)
      }
    }
    if (item.wearable) {
      statusParts.push('Wearable')
    }
    if (item.consumable) {
      statusParts.push('Consumable')
    }
    if (statusParts.length > 0) {
      firstLineParts.push(`(${statusParts.join(', ')})`)
    }

    // Nested container ID
    if (options.showNestedContainer !== false && item.containerId && options.getContainerById) {
      const nestedContainer = options.getContainerById(item.containerId)
      if (nestedContainer) {
        const containerId = generateContainerId(nestedContainer.name)
        firstLineParts.push(`[${containerId}]`)
      }
    }

    // URL
    if (item.url) {
      firstLineParts.push(`<${item.url}>`)
    }

    // Weight
    if (options.showWeight !== false) {
      let totalWeight: number
      let weightText: string

      if (item.containerId && options.calculateTotalWeight) {
        const containerWeightInGrams = options.calculateTotalWeight(item.containerId)
        totalWeight = containerWeightInGrams * item.quantity
        weightText = formatWeightFromGrams(totalWeight, options.locale)
      } else {
        totalWeight = item.weight * item.quantity
        weightText = formatWeight(totalWeight, item.weightUnit ?? 'g', options.locale)
      }

      firstLineParts.push(`- ${weightText}`)
    }

    // Price at the end (only if showPrices is true and item has price)
    if (options.showPrices && item.price) {
      const currency = getCurrency(item.currency, defaultCurrency)
      const totalPrice = item.price * (item.quantity || 1)
      const formattedPrice = formatCurrency(totalPrice, currency)
      firstLineParts.push(`- ${formattedPrice}`)
    }

    // Build output: first line with name and metadata, notes as indented block below
    const formattedNotes = formatNotesAsIndentedBlock(item.notes, indent)
    return `${indentStr}- ${firstLineParts.join(' ')}\n${formattedNotes}`
  }

  return `${indentStr}- ${parts.join(' ')}`
}

/**
 * Format nested container items separately
 */
function formatNestedContainer(
  container: IGearContainer,
  options: ExportOptions,
  indent = 0,
  defaultCurrency: string = 'PLN',
): string {
  const indentStr = '  '.repeat(indent)
  const lines: string[] = []

  // Container header with ID and UUID
  const typeLabel = options.getContainerTypeLabel
    ? options.getContainerTypeLabel(container.type)
    : container.type
  const containerId = generateContainerId(container.name)
  const containerIdPart = options.showNestedContainer !== false ? ` [${containerId}]` : ''
  const uuidPart = options.showUuid !== false ? ` [uuid:${container.id}]` : ''
  const favoritePart = container.favorite ? ' [favorite]' : ''

  // Build container header parts
  const headerParts: string[] = [`${indentStr}## ${container.name}${containerIdPart}${uuidPart} (${typeLabel})${favoritePart}`]

  // Add price to header if enabled
  if (options.showPrices && container.price) {
    const currency = getCurrency(container.currency, defaultCurrency)
    const formattedPrice = formatCurrency(container.price, currency)
    headerParts.push(`- ${formattedPrice}`)
  }

  lines.push(headerParts.join(' '))

  // Add container description as indented block (if description format is not off)
  if (container.description && options.descriptionFormat !== 'off') {
    const formattedDescription = formatNotesAsIndentedBlock(container.description, indent)
    lines.push(formattedDescription)
  }

  // Container items
  if (container.items.length === 0) {
    lines.push(`${indentStr}*Brak przedmiotów w kontenerze.*`)
  } else {
    container.items.forEach(item => {
      lines.push(formatItem(item, options, indent, defaultCurrency))
    })
  }

  return lines.join('\n')
}

/**
 * Generate "To Buy" summary section
 */
function generateToBuySummary(
  containers: IGearContainer[],
  options: ExportOptions,
  defaultCurrency: string = 'PLN',
): string {
  const { t } = options

  const toBuyItems: Array<{
    name: string
    price: number
    quantity: number
    currency: string
  }> = []

  containers.forEach(container => {
    container.items
      .filter(item => item.status === 'toBuy' && item.price)
      .forEach(item => {
        toBuyItems.push({
          name: item.name,
          price: item.price!,
          quantity: item.quantity || 1,
          currency: getCurrency(item.currency, getCurrency(container.currency, defaultCurrency)),
        })
      })
  })

  if (toBuyItems.length === 0) {
    return ''
  }

  // Group by currency
  const byCurrency = new Map<string, typeof toBuyItems>()
  toBuyItems.forEach(item => {
    const existing = byCurrency.get(item.currency) ?? []
    existing.push(item)
    byCurrency.set(item.currency, existing)
  })

  // Generate summary
  const toBuyTitle = t ? t('gear.export.toBuyTitle', 'To Buy') : 'To Buy'
  const toBuyTotalCost = t ? t('gear.export.toBuyTotalCost', 'Total Cost') : 'Total Cost'
  const toBuyItemsToPurchase = t ? t('gear.export.toBuyItemsToPurchase', 'Items to purchase') : 'Items to purchase'

  let summary = '\n---\n\n'
  summary += `## ${toBuyTitle}\n\n`

  byCurrency.forEach((items, currency) => {
    const total = items.reduce((sum, item) => sum + (item.price * item.quantity), 0)
    const formattedTotal = formatCurrency(total, currency)

    summary += `**${toBuyTotalCost} (${currency}):** ${formattedTotal}\n\n`
    summary += `${toBuyItemsToPurchase}:\n`
    items.forEach(item => {
      const itemTotal = item.price * item.quantity
      const formattedPrice = formatCurrency(itemTotal, currency)
      summary += `- **${item.name}**${item.quantity > 1 ? ` x${item.quantity}` : ''} - ${formattedPrice}\n`
    })
    summary += '\n'
  })

  return summary
}

/**
 * Export single container to markdown (compact format)
 */
export function exportContainerToPrompt(
  container: IGearContainer,
  options: ExportOptions = {},
): string {
  const {
    t,
    getContainerTypeLabel,
    getContainerById,
  } = options

  const lines: string[] = []

  // Header
  const titleText = t ? t('gear.export.title', 'Lista sprzętu') : 'Lista sprzętu'
  const descriptionText = t ? t('gear.export.description', 'Lista mojego sprzętu w różnych kontenerach, wygenerowana przez Gear Stack') : 'Lista mojego sprzętu w różnych kontenerach, wygenerowana przez Gear Stack'

  lines.push(`# ${titleText}`)
  lines.push(descriptionText)
  lines.push('')
  lines.push('---')
  lines.push('')

  // Container header with ID and UUID
  const typeLabel = getContainerTypeLabel
    ? getContainerTypeLabel(container.type)
    : container.type
  const containerId = generateContainerId(container.name)

  // Build container header parts
  const containerHeaderParts: string[] = []
  containerHeaderParts.push(`## ${container.name}`)
  // Container ID only if showNestedContainer is true (default: true)
  if (options.showNestedContainer !== false) {
    containerHeaderParts.push(`[${containerId}]`)
  }
  // UUID only if showUuid is true (default: true)
  if (options.showUuid !== false) {
    containerHeaderParts.push(`[uuid:${container.id}]`)
  }
  containerHeaderParts.push(`(${typeLabel})`)
  // Add favorite flag if container is marked as favorite
  if (container.favorite) {
    containerHeaderParts.push('[favorite]')
  }

  // Add URL if provided
  if (container.url) {
    containerHeaderParts.push(`<${container.url}>`)
  }

  // Add weight if provided
  if (isSet(container.weight) && isSet(container.weightUnit)) {
    const weightText = formatWeight(container.weight, container.weightUnit, options.locale)
    // Extract just the number and unit (e.g., "1.50 kg" -> "1.50kg" or "500 g" -> "500g")
    const weightValue = weightText.replace(/\s/g, '')
    containerHeaderParts.push(`- ${weightValue}`)
  }

  // Add price if enabled
  const defaultCurrency = options.defaultCurrency || 'PLN'
  if (options.showPrices && container.price) {
    const currency = getCurrency(container.currency, defaultCurrency)
    const formattedPrice = formatCurrency(container.price, currency)
    containerHeaderParts.push(`- ${formattedPrice}`)
  }

  lines.push(containerHeaderParts.join(' '))

  // Add container description as indented block (if description format is not off)
  if (container.description && options.descriptionFormat !== 'off') {
    const formattedDescription = formatNotesAsIndentedBlock(container.description, 0)
    lines.push(formattedDescription)
  }

  // Collect nested containers to show separately
  const nestedContainers: Array<{ item: IGearItem; container: IGearContainer }> = []

  // Items
  const emptyText = t ? t('gear.export.emptyContainer', '*Brak przedmiotów w kontenerze.*') : '*Brak przedmiotów w kontenerze.*'
  if (container.items.length === 0) {
    lines.push(emptyText)
  } else {
    container.items.forEach(item => {
      // Check if item is a nested container
      if (item.containerId && getContainerById) {
        const nestedContainer = getContainerById(item.containerId)
        if (nestedContainer) {
          // Add as regular item (without content, but with calculated weight)
          lines.push(formatItem(item, options, 0, defaultCurrency))
          // Store for later display
          nestedContainers.push({ item, container: nestedContainer })
        } else {
          // Regular item
          lines.push(formatItem(item, options, 0, defaultCurrency))
        }
      } else {
        // Regular item
        lines.push(formatItem(item, options, 0, defaultCurrency))
      }
    })
  }

  // Add nested containers with full content below
  if (nestedContainers.length > 0) {
    lines.push('')
    nestedContainers.forEach(({ container: nestedContainer }) => {
      lines.push('')
      lines.push(formatNestedContainer(nestedContainer, options, 0, defaultCurrency))
    })
  }

  // Legend for AI (only if showLegend is true, default: true)
  if (options.showLegend !== false) {
    lines.push('')
    lines.push('---')
    lines.push('')
    const legendTitle = t ? t('gear.export.legendTitle', '## Legenda dla AI') : '## Legenda dla AI'
    const legendIntro = t ? t('gear.export.legendIntro', 'To jest system zarządzania sprzętem/ekwipunkiem. Oto co oznaczają dane:') : 'To jest system zarządzania sprzętem/ekwipunkiem. Oto co oznaczają dane:'
    const legendContainer = t ? t('gear.export.legendContainer', '- **Kontener**: Plecak, torba, saszetka lub inna jednostka przechowywania przedmiotów') : '- **Kontener**: Plecak, torba, saszetka lub inna jednostka przechowywania przedmiotów'
    const legendItems = t ? t('gear.export.legendItems', '- **Przedmioty**: Pojedyncze elementy wyposażenia przechowywane w kontenerze') : '- **Przedmioty**: Pojedyncze elementy wyposażenia przechowywane w kontenerze'
    const legendWeight = t ? t('gear.export.legendWeight', '- **Waga**: Całkowita waga uwzględniająca ilość') : '- **Waga**: Całkowita waga uwzględniająca ilość'
    const legendBrand = t ? t('gear.export.legendBrand', '- **Marka**: Producent/marka przedmiotu') : '- **Marka**: Producent/marka przedmiotu'
    const legendColor = t ? t('gear.export.legendColor', '- **Kolor**: Kolor przedmiotu') : '- **Kolor**: Kolor przedmiotu'
    const legendNested = t ? t('gear.export.legendNested', '- **Zagnieżdżone kontenery**: Kontener może zawierać inny kontener jako przedmiot. Zagnieżdżone kontenery są wyświetlane jako pozycja w liście oraz osobno z pełną zawartością poniżej.') : '- **Zagnieżdżone kontenery**: Kontener może zawierać inny kontener jako przedmiot. Zagnieżdżone kontenery są wyświetlane jako pozycja w liście oraz osobno z pełną zawartością poniżej.'

    lines.push(legendTitle)
    lines.push('')
    lines.push(legendIntro)
    lines.push('')
    lines.push(legendContainer)
    lines.push(legendItems)
    lines.push('- **Status**:')
    if (t) {
      const ownedDesc = t('gear.export.legendStatusOwned', 'Przedmiot jest posiadany i dostępny')
      const missingDesc = t('gear.export.legendStatusMissing', 'Przedmiot jest brakujący lub niedostępny')
      const toBuyDesc = t('gear.export.legendStatusToBuy', 'Przedmiot należy zakupić')
      lines.push(`  - ${t('gear.item.statuses.owned')}: ${ownedDesc}`)
      lines.push(`  - ${t('gear.item.statuses.missing')}: ${missingDesc}`)
      lines.push(`  - ${t('gear.item.statuses.toBuy')}: ${toBuyDesc}`)
    } else {
      lines.push('  - owned: Przedmiot jest posiadany i dostępny')
      lines.push('  - missing: Przedmiot jest brakujący lub niedostępny')
      lines.push('  - toBuy: Przedmiot należy zakupić')
    }
    lines.push(legendWeight)
    lines.push(legendBrand)
    lines.push(legendColor)
    lines.push(legendNested)
    lines.push('')
  }

  // Add "To Buy" summary if prices enabled
  if (options.showPrices) {
    const summary = generateToBuySummary([container], options, defaultCurrency)
    if (summary) {
      lines.push(summary)
    }
  }

  return lines.join('\n')
}

/**
 * Export multiple containers to markdown
 */
export function exportContainersToPrompt(
  containers: IGearContainer[],
  options: ExportOptions = {},
): string {
  const { t } = options
  const lines: string[] = []

  const titleText = t ? t('gear.export.title', 'Lista sprzętu') : 'Lista sprzętu'
  lines.push(`# ${titleText}`)
  lines.push('')
  lines.push('---')
  lines.push('')

  // Export each container without legend (legend will be added once at the end)
  const exportOptionsWithoutLegend = { ...options, showLegend: false }

  containers.forEach((container, index) => {
    if (index > 0) {
      lines.push('')
      lines.push('---')
      lines.push('')
    }
    const containerMarkdown = exportContainerToPrompt(container, exportOptionsWithoutLegend)
    // Remove the header and description from nested containers
    const containerLines = containerMarkdown.split('\n')
    const titleLine = `# ${titleText}`
    if (containerLines[0] === titleLine) {
      containerLines.shift() // Remove title
      containerLines.shift() // Remove description
      if (containerLines[0] === '') {
        containerLines.shift() // Remove empty line
      }
    }
    lines.push(...containerLines)
  })

  // Add legend only once at the end (if showLegend is true, default: true)
  if (options.showLegend !== false) {
    lines.push('')
    lines.push('---')
    lines.push('')
    const legendTitle = t ? t('gear.export.legendTitle', '## Legenda dla AI') : '## Legenda dla AI'
    const legendIntro = t ? t('gear.export.legendIntro', 'To jest system zarządzania sprzętem/ekwipunkiem. Oto co oznaczają dane:') : 'To jest system zarządzania sprzętem/ekwipunkiem. Oto co oznaczają dane:'
    const legendContainer = t ? t('gear.export.legendContainer', '- **Kontener**: Plecak, torba, saszetka lub inna jednostka przechowywania przedmiotów') : '- **Kontener**: Plecak, torba, saszetka lub inna jednostka przechowywania przedmiotów'
    const legendItems = t ? t('gear.export.legendItems', '- **Przedmioty**: Pojedyncze elementy wyposażenia przechowywane w kontenerze') : '- **Przedmioty**: Pojedyncze elementy wyposażenia przechowywane w kontenerze'
    const legendWeight = t ? t('gear.export.legendWeight', '- **Waga**: Całkowita waga uwzględniająca ilość') : '- **Waga**: Całkowita waga uwzględniająca ilość'
    const legendBrand = t ? t('gear.export.legendBrand', '- **Marka**: Producent/marka przedmiotu') : '- **Marka**: Producent/marka przedmiotu'
    const legendColor = t ? t('gear.export.legendColor', '- **Kolor**: Kolor przedmiotu') : '- **Kolor**: Kolor przedmiotu'
    const legendNested = t ? t('gear.export.legendNested', '- **Zagnieżdżone kontenery**: Kontener może zawierać inny kontener jako przedmiot. Zagnieżdżone kontenery są wyświetlane jako pozycja w liście oraz osobno z pełną zawartością poniżej.') : '- **Zagnieżdżone kontenery**: Kontener może zawierać inny kontener jako przedmiot. Zagnieżdżone kontenery są wyświetlane jako pozycja w liście oraz osobno z pełną zawartością poniżej.'

    lines.push(legendTitle)
    lines.push('')
    lines.push(legendIntro)
    lines.push('')
    lines.push(legendContainer)
    lines.push(legendItems)
    lines.push('- **Status**:')
    if (t) {
      const ownedDesc = t('gear.export.legendStatusOwned', 'Przedmiot jest posiadany i dostępny')
      const missingDesc = t('gear.export.legendStatusMissing', 'Przedmiot jest brakujący lub niedostępny')
      const toBuyDesc = t('gear.export.legendStatusToBuy', 'Przedmiot należy zakupić')
      lines.push(`  - ${t('gear.item.statuses.owned')}: ${ownedDesc}`)
      lines.push(`  - ${t('gear.item.statuses.missing')}: ${missingDesc}`)
      lines.push(`  - ${t('gear.item.statuses.toBuy')}: ${toBuyDesc}`)
    } else {
      lines.push('  - owned: Przedmiot jest posiadany i dostępny')
      lines.push('  - missing: Przedmiot jest brakujący lub niedostępny')
      lines.push('  - toBuy: Przedmiot należy zakupić')
    }
    lines.push(legendWeight)
    lines.push(legendBrand)
    lines.push(legendColor)
    lines.push(legendNested)
    lines.push('')
  }

  // Add "To Buy" summary if prices enabled
  if (options.showPrices) {
    const defaultCurrency = options.defaultCurrency || 'PLN'
    const summary = generateToBuySummary(containers, options, defaultCurrency)
    if (summary) {
      lines.push(summary)
    }
  }

  return lines.join('\n')
}
