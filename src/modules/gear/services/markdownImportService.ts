import type { ICreateItemDto } from '../types/gear.types'
import { recognizeParameters } from '../utils/parameterRecognition'
import { priceParser } from '../utils/priceParser'
import { SUGGESTED_BRANDS, SUGGESTED_COLORS } from '../utils/suggestedValues'

// Markdown template for AI guidelines
export const guidelinesTemplate = `# Gear List Formatting Guidelines

When generating or updating gear lists, use this format:

## Standard Format
\`\`\`markdown
## [Container Name] [#container-id] [uuid:xxx] ([Container Type]) [favorite] <URL> - [weight]g
- **[Item Name]** x[qty] ([Brand], [Color]) [#nested-id] ([Status]) <URL> - [weight]g
\`\`\`

## Format Rules

### Item Name (Required)
- **Bold formatting** using \`**Item Name**\`
- Always at the start of the line after \`- \`

### Quantity (Optional)
- Format: \`x[number]\` (e.g., x2, x10)
- If omitted, quantity = 1

### Brand and Color (Optional)
- First parentheses: \`([Brand], [Color])\`
- Brand comes first, color second
- Examples: \`(Victorinox)\`, \`(Petzl, Black)\`

### Status (Optional)
- Second parentheses: \`Missing\`, \`To Buy\` (omit if Owned)
- Expiration: \`Expiration: DD.MM.YYYY\`
- Wearable: \`Wearable\` - item is worn/carried on person (e.g., clothing, watch)
- Consumable: \`Consumable\` - item is consumed/used up (e.g., food, medicine, fuel)
- Can combine: \`(Missing, Expiration: 31.12.2025, Wearable)\`

### Container ID (Required for containers)
- Format: \`[#slug-id]\` in header and nested item reference
- ID is generated from container name as slug
- Example: \`Bug-Out Bag\` → \`[#bug-out-bag]\`

### UUID (Optional, recommended for updates)
- Format: \`[uuid:xxx]\` in container header
- Used for stable references when updating existing containers
- Example: \`[uuid:7f6af1c1-7c6b-4b0d-9dd9-8c36f3d1b100]\`

### Favorite Flag (Optional)
- Format: \`[favorite]\` in container header
- Marks container as favorite (will appear first in lists)
- Only shown if container is marked as favorite
- Example: \`## Bug-Out Bag [#bug-out-bag] [uuid:xxx] (Backpack) [favorite]\`

### URL (Optional)
- Format: \`<URL>\` in angle brackets or plain URL
- Recognized by \`http://\`, \`https://\`, or \`www.\`

### Weight (Optional)
- **For containers:** Format: \`- [number]g\` or \`- [number]kg\` or \`- [number]oz\` or \`- [number]lb\` in container header
- **For items:** Format: \`- [number]g\` or \`- [number]kg\` or \`- [number]oz\` or \`- [number]lb\` at the end after a dash
- Always at the end after a dash
- If omitted for items, default weight will be assigned (100g)
- Container weight is optional but recommended for accurate total weight calculations

## Example
\`\`\`markdown
## Bug-Out Bag [#bug-out-bag] [uuid:7f6af1c1-7c6b-4b0d-9dd9-8c36f3d1b100] (Backpack) [favorite] <https://example.com/backpack> - 2000g
- **Water Bottle** x2 (Nalgene) - 300g
- **Tactical Knife** (Victorinox, Black) - 200g
- **Headlamp** (Petzl, Red) (Missing) - 90g
- **Hiking Boots** (Salomon) (Wearable) - 1200g
- **Energy Bar** (Consumable) - 50g
- **First Aid Pouch** (Pouch) [#first-aid-pouch] - 350g

## First Aid Pouch [#first-aid-pouch] [uuid:9c4fc7c8-95b2-46cd-bb09-ef3ca52a3f45] (Pouch) - 500g
- **Bandages** x5 - 100g
- **Pain Pills** (Expiration: 31.12.2025, Consumable) - 50g
\`\`\`

## Nested Containers
When a container is inside another container:
1. Add item with container name and \`[#id]\` reference
2. Define the nested container separately with same \`[#id]\`
3. Parser will create the relationship automatically

## Important Notes
1. **Only item name is required** (bold \`**text**\`)
2. Container headers must have \`[#id]\` for proper identification
3. Parentheses order: (Brand, Color) then (Status/Expiration)
4. All fields except item name are optional
5. Use metric units (grams/kilograms)
`


/**
 * Result of parsing markdown content
 */
export interface IMarkdownImportResult {
  containers: Array<{
    name: string
    id?: string // Container ID from [#id] in header
    uuid?: string // Container UUID from [uuid:xxx] in header
    weight?: number // Container weight
    weightUnit?: 'g' | 'kg' | 'oz' | 'lb' // Container weight unit
    url?: string // Container URL
    description?: string // Container description (text between header and first item)
    price?: number // Container price
    currency?: string // Container currency (PLN, USD, EUR, GBP, etc.)
    favorite?: boolean // Container favorite flag from [favorite] in header
    items: Array<ICreateItemDto & { nestedContainerId?: string; uuid?: string }> // nestedContainerId is temporary slug reference, uuid for updates
  }>
  errors: string[]
}

/**
 * Parsed item parameters from parentheses
 */
interface IItemParams {
  brand?: string
  color?: string
  category?: string
  quantity?: number
  weight?: number
  weightUnit?: 'g' | 'kg' | 'oz' | 'lb'
}

/**
 * Service for parsing markdown format into gear containers and items
 *
 * Format:
 * ## Container Name
 * - Item name **Brand Name** (param1, param2) x5
 * - Another item **Brand** ~25 m (color)
 *
 * Supported parameters in parentheses:
 * - Brand names (matched against SUGGESTED_BRANDS)
 * - Colors (matched against SUGGESTED_COLORS)
 * - Categories (matched against category keywords)
 * - Measurements like "~25 m", "195×60 cm"
 *
 * Supported patterns:
 * - xN or ×N at the end = quantity
 * - **Brand** in bold = brand name
 * - ~N m/cm/kg/g = weight/measurement
 */
class MarkdownImportService {
  /**
   * M7 FIX: Use PriceParser with registry pattern (OCP compliance)
   * Price parsing is now delegated to the priceParser singleton
   */

  private categoryKeywords: Record<string, string[]> = {
    water: ['butelka', 'bottle', 'water', 'woda', 'filtr'],
    food: ['racje', 'jedzenie', 'food', 'menażka', 'kubek', 'kuchenka', 'palnik', 'gaz'],
    shelter: ['namiot', 'tent', 'tarp', 'poncho', 'płaszcz', 'materac', 'mata', 'śpiwór', 'sleeping bag', 'worek', 'folia'],
    fire: ['zapalniczka', 'lighter', 'krzesiwo', 'fire', 'zapałki', 'matches', 'świeczka'],
    firstAid: ['apteczka', 'first aid', 'bandaż', 'plaster', 'gazik', 'elektrolity', 'tabletki', 'maseczka', 'rękawiczki nitrylowe'],
    tools: ['nóż', 'knife', 'multitool', 'scyzoryk', 'siekiera', 'axe', 'piła', 'saw', 'saperka', 'ostrzałka', 'osełka', 'kompas', 'compass', 'linijka'],
    navigation: ['kompas', 'compass', 'mapa', 'map', 'gps', 'lornetka', 'luneta'],
    communication: ['radio', 'telefon', 'phone', 'powerbank', 'ładowarka'],
    clothing: ['rękawice', 'gloves', 'chusta', 'bandana'],
    hygiene: ['chusteczki', 'tissues', 'szczoteczka', 'toothbrush', 'mydło'],
    light: ['latarka', 'flashlight', 'czołówka', 'headlamp', 'baterie', 'batteries', 'akumulator'],
    other: [],
  }

  /**
   * M5 FIX: Asynchronous markdown parsing with chunked processing
   * Prevents UI freezing on large markdown files by yielding to event loop
   *
   * @param markdown - Markdown content to parse
   * @param options - Parsing options
   * @param options.recognizeFromName - Whether to recognize brand and color from item name (default: false)
   * @param options.customBrands - Custom user brands to include in recognition
   * @param options.onProgress - Progress callback (percentage 0-100)
   * @param options.chunkSize - Lines per chunk (default: 50)
   */
  async parseMarkdownAsync(
    markdown: string,
    options?: {
      recognizeFromName?: boolean
      customBrands?: Array<{ value: string }>
      onProgress?: (percent: number) => void
      chunkSize?: number
    }
  ): Promise<IMarkdownImportResult> {
    const CHUNK_SIZE = options?.chunkSize ?? 50
    const lines = markdown.split('\n')
    const result: IMarkdownImportResult = {
      containers: [],
      errors: [],
    }

    let currentContainer: { name: string; id?: string; uuid?: string; weight?: number; weightUnit?: 'g' | 'kg' | 'oz' | 'lb'; url?: string; description?: string; price?: number; currency?: string; favorite?: boolean; items: ICreateItemDto[] } | null = null
    let descriptionLines: string[] = []
    let isCollectingDescription = false

    // Process lines in chunks
    for (let chunkStart = 0; chunkStart < lines.length; chunkStart += CHUNK_SIZE) {
      // Yield to event loop to keep UI responsive
      await new Promise(resolve => setTimeout(resolve, 0))

      // Report progress
      if (options?.onProgress) {
        const progress = Math.round((chunkStart / lines.length) * 100)
        options.onProgress(progress)
      }

      const chunkEnd = Math.min(chunkStart + CHUNK_SIZE, lines.length)

      // Process current chunk
      for (let i = chunkStart; i < chunkEnd; i++) {
        const line = lines[i]?.trim()
        if (!line) {
          // Keep empty lines in description
          if (isCollectingDescription) {
            descriptionLines.push('')
          }
          continue
        }

        // Container header (## Header [#id] [uuid:xxx] (Type) <URL> - weight)
        if (line.startsWith('## ')) {
          // Save previous container with description
          if (currentContainer && currentContainer.items.length > 0) {
            // Trim and save description (only if not already set from header)
            if (descriptionLines.length > 0 && !currentContainer.description) {
              const description = descriptionLines.join('\n').trim()
              if (description) {
                currentContainer.description = description
              }
            }
            result.containers.push(currentContainer)
          }

          // Reset description collection
          descriptionLines = []
          isCollectingDescription = true

          // Parse container header (inline logic from sync version)
          let headerText = line.substring(3).trim()
          let containerId: string | undefined
          let containerUuid: string | undefined
          let containerUrl: string | undefined
          let containerWeight: number | undefined
          let containerWeightUnit: 'g' | 'kg' | 'oz' | 'lb' | undefined
          let containerPrice: number | undefined
          let containerCurrency: string | undefined
          let containerFavorite: boolean | undefined
          let containerDescription: string | undefined

          // Extract price (before other patterns to avoid conflicts)
          const priceResult = priceParser.parse(headerText)
          if (priceResult) {
            containerPrice = priceResult.price
            containerCurrency = priceResult.currency
            // Remove price from header text
            headerText = headerText.replace(/(\d+(?:[\s,.]\d+)*)\s*(PLN|zł|z[lł]|\$|USD|€|EUR|£|GBP)/gi, '').trim()
          }

          // Extract ID from [#id]
          const idMatch = headerText.match(/\[#([^\]]+)\]/)
          if (idMatch) {
            containerId = idMatch[1]?.trim()
            headerText = headerText.replace(idMatch[0] ?? '', '').trim()
          }

          // Extract UUID from [uuid:xxx]
          const uuidMatch = headerText.match(/\[uuid:([^\]]+)\]/)
          if (uuidMatch) {
            containerUuid = uuidMatch[1]?.trim()
            headerText = headerText.replace(uuidMatch[0] ?? '', '').trim()
          }

          // Extract favorite flag from [favorite]
          const favoriteMatch = headerText.match(/\[favorite\]/i)
          if (favoriteMatch) {
            containerFavorite = true
            headerText = headerText.replace(favoriteMatch[0] ?? '', '').trim()
          }

          // Extract description/notes in italic format *(text)* BEFORE parsing name
          const italicDescriptionMatch = headerText.match(/\*\(([^)]+)\)\*/)
          if (italicDescriptionMatch) {
            containerDescription = italicDescriptionMatch[1]?.trim()
            headerText = headerText.replace(italicDescriptionMatch[0] ?? '', '').trim()
          }

          // Extract URL from <URL> or plain URL
          const urlAngleMatch = headerText.match(/<([^>]+)>/)
          if (urlAngleMatch) {
            containerUrl = urlAngleMatch[1]?.trim()
            headerText = headerText.replace(urlAngleMatch[0] ?? '', '').trim()
          } else {
            // Try plain URL (http://, https://, www.)
            const urlPlainMatch = headerText.match(/(https?:\/\/[^\s]+|www\.[^\s]+)/i)
            if (urlPlainMatch && urlPlainMatch[1]) {
              containerUrl = urlPlainMatch[1].trim()
              if (containerUrl.startsWith('www.')) {
                containerUrl = `https://${containerUrl}`
              }
              headerText = headerText.replace(urlPlainMatch[0] ?? '', '').trim()
            }
          }

          // Extract weight from - weightg, - weightkg, - weightoz, - weightlb (at the end)
          const weightMatch = headerText.match(/-?\s*([\d.]+)\s*(g|kg|oz|lb)\s*$/i)
          if (weightMatch) {
            containerWeight = parseFloat(weightMatch[1] ?? '0')
            const unit = weightMatch[2]?.toLowerCase() ?? 'g'
            containerWeightUnit = (unit === 'kg' ? 'kg' : unit === 'oz' ? 'oz' : unit === 'lb' ? 'lb' : 'g') as 'g' | 'kg' | 'oz' | 'lb'
            headerText = headerText.replace(weightMatch[0] ?? '', '').trim()
          }

          // Extract container name (remove type in parentheses if present)
          const nameMatch = headerText.match(/^([^(]+)/)
          const containerName = (nameMatch ? nameMatch[1]?.trim() : headerText) || headerText

          currentContainer = {
            name: containerName,
            id: containerId,
            uuid: containerUuid,
            weight: containerWeight,
            weightUnit: containerWeightUnit,
            url: containerUrl,
            description: containerDescription, // Description from *(text)* in header
            price: containerPrice,
            currency: containerCurrency,
            favorite: containerFavorite,
            items: [],
          }
          continue
        }

        // Item line (- Item...)
        if (line.startsWith('- ')) {
          // Stop collecting description when first item is found
          isCollectingDescription = false
          if (!currentContainer) {
            result.errors.push(`Line ${i + 1}: Item found before container header`)
            continue
          }

          try {
            const item = this.parseItemLine(line.substring(2).trim(), {
              recognizeFromName: options?.recognizeFromName,
              customBrands: options?.customBrands,
            })
            if (item) {
              // Collect indented notes after the item line
              const noteLines: string[] = []
              let j = i + 1
              while (j < lines.length) {
                const nextLine = lines[j]
                if (!nextLine) {
                  // Empty line - keep it in notes
                  noteLines.push('')
                  j++
                  continue
                }

                // Check if line starts with exactly 2 spaces (indented note)
                if (nextLine.startsWith('  ') && !nextLine.startsWith('   ')) {
                  // Remove the 2-space indent and add to notes
                  const noteLine = nextLine.substring(2)
                  noteLines.push(noteLine)
                  j++
                  continue
                }

                // Stop if we encounter another item or container
                const trimmedNextLine = nextLine.trim()
                if (trimmedNextLine.startsWith('- ') || trimmedNextLine.startsWith('## ')) {
                  break
                }

                // If line doesn't start with 2 spaces, it's not a note
                break
              }

              // Join note lines and set as item notes (if any)
              if (noteLines.length > 0) {
                // Remove trailing empty lines but preserve empty lines in the middle
                while (noteLines.length > 0 && noteLines[noteLines.length - 1] === '') {
                  noteLines.pop()
                }
                const notes = noteLines.join('\n')
                if (notes.trim()) {
                  item.notes = notes
                }
                // Skip the lines we've processed
                const linesProcessed = j - i - 1
                i += linesProcessed
                // IMPORTANT: Adjust chunkEnd if we processed notes beyond current chunk
                if (i >= chunkEnd) {
                  // Continue from where we left off in next iteration
                  chunkStart = i
                  currentContainer.items.push(item)
                  break
                }
              }
              // If no indented lines found, keep notes from parseItemLine (*(text)* format as fallback)

              currentContainer.items.push(item)
            }
          } catch (error) {
            result.errors.push(`Line ${i + 1}: ${error instanceof Error ? error.message : 'Unknown error'}`)
          }
          continue
        }

        // Description line (between header and first item)
        if (isCollectingDescription && currentContainer) {
          descriptionLines.push(line)
        }
      }
    }

    // Add last container with description
    if (currentContainer && currentContainer.items.length > 0) {
      // Save description if still collecting (only if not already set from header)
      if (descriptionLines.length > 0 && !currentContainer.description) {
        const description = descriptionLines.join('\n').trim()
        if (description) {
          currentContainer.description = description
        }
      }
      result.containers.push(currentContainer)
    }

    // Report 100% completion
    if (options?.onProgress) {
      options.onProgress(100)
    }

    return result
  }

  /**
   * Parse markdown content into containers and items (synchronous version)
   *
   * NOTE: For large files (>100 lines), prefer parseMarkdownAsync() to avoid UI freezing
   *
   * @param markdown - Markdown content to parse
   * @param options - Parsing options
   * @param options.recognizeFromName - Whether to recognize brand and color from item name (default: false)
   * @param options.customBrands - Custom user brands to include in recognition
   */
  parseMarkdown(
    markdown: string,
    options?: {
      recognizeFromName?: boolean
      customBrands?: Array<{ value: string }>
    }
  ): IMarkdownImportResult {
    const result: IMarkdownImportResult = {
      containers: [],
      errors: [],
    }

    const lines = markdown.split('\n')
    let currentContainer: { name: string; id?: string; uuid?: string; weight?: number; weightUnit?: 'g' | 'kg' | 'oz' | 'lb'; url?: string; description?: string; price?: number; currency?: string; favorite?: boolean; items: ICreateItemDto[] } | null = null
    let descriptionLines: string[] = []
    let isCollectingDescription = false

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]?.trim()
      if (!line) {
        // Keep empty lines in description
        if (isCollectingDescription) {
          descriptionLines.push('')
        }
        continue
      }

      // Container header (## Header [#id] [uuid:xxx] (Type) <URL> - weight)
      if (line.startsWith('## ')) {
        // Save previous container with description
        if (currentContainer && currentContainer.items.length > 0) {
          // Trim and save description (only if not already set from header)
          if (descriptionLines.length > 0 && !currentContainer.description) {
            const description = descriptionLines.join('\n').trim()
            if (description) {
              currentContainer.description = description
            }
          }
          result.containers.push(currentContainer)
        }

        // Reset description collection
        descriptionLines = []
        isCollectingDescription = true

        let headerText = line.substring(3).trim()
        let containerId: string | undefined
        let containerUuid: string | undefined
        let containerUrl: string | undefined
        let containerWeight: number | undefined
        let containerWeightUnit: 'g' | 'kg' | 'oz' | 'lb' | undefined
        let containerPrice: number | undefined
        let containerCurrency: string | undefined
        let containerFavorite: boolean | undefined

        // Extract price (before other patterns to avoid conflicts)
        const priceResult = priceParser.parse(headerText)
        if (priceResult) {
          containerPrice = priceResult.price
          containerCurrency = priceResult.currency
          // Remove price from header text
          headerText = headerText.replace(/(\d+(?:[\s,.]\d+)*)\s*(PLN|zł|z[lł]|\$|USD|€|EUR|£|GBP)/gi, '').trim()
        }

        // Extract ID from [#id]
        const idMatch = headerText.match(/\[#([^\]]+)\]/)
        if (idMatch) {
          containerId = idMatch[1]?.trim()
          headerText = headerText.replace(idMatch[0] ?? '', '').trim()
        }

        // Extract UUID from [uuid:xxx]
        const uuidMatch = headerText.match(/\[uuid:([^\]]+)\]/)
        if (uuidMatch) {
          containerUuid = uuidMatch[1]?.trim()
          headerText = headerText.replace(uuidMatch[0] ?? '', '').trim()
        }

        // Extract favorite flag from [favorite]
        const favoriteMatch = headerText.match(/\[favorite\]/i)
        if (favoriteMatch) {
          containerFavorite = true
          headerText = headerText.replace(favoriteMatch[0] ?? '', '').trim()
        }

        // Extract description/notes in italic format *(text)* BEFORE parsing name
        // This prevents description from being included in the container name
        let containerDescription: string | undefined
        const italicDescriptionMatch = headerText.match(/\*\(([^)]+)\)\*/)
        if (italicDescriptionMatch) {
          containerDescription = italicDescriptionMatch[1]?.trim()
          headerText = headerText.replace(italicDescriptionMatch[0] ?? '', '').trim()
        }

        // Extract URL from <URL> or plain URL
        const urlAngleMatch = headerText.match(/<([^>]+)>/)
        if (urlAngleMatch) {
          containerUrl = urlAngleMatch[1]?.trim()
          headerText = headerText.replace(urlAngleMatch[0] ?? '', '').trim()
        } else {
          // Try plain URL (http://, https://, www.)
          const urlPlainMatch = headerText.match(/(https?:\/\/[^\s]+|www\.[^\s]+)/i)
          if (urlPlainMatch && urlPlainMatch[1]) {
            containerUrl = urlPlainMatch[1].trim()
            if (containerUrl.startsWith('www.')) {
              containerUrl = `https://${containerUrl}`
            }
            headerText = headerText.replace(urlPlainMatch[0] ?? '', '').trim()
          }
        }

        // Extract weight from - weightg, - weightkg, - weightoz, - weightlb (at the end)
        const weightMatch = headerText.match(/-?\s*([\d.]+)\s*(g|kg|oz|lb)\s*$/i)
        if (weightMatch) {
          containerWeight = parseFloat(weightMatch[1] ?? '0')
          const unit = weightMatch[2]?.toLowerCase() ?? 'g'
          containerWeightUnit = (unit === 'kg' ? 'kg' : unit === 'oz' ? 'oz' : unit === 'lb' ? 'lb' : 'g') as 'g' | 'kg' | 'oz' | 'lb'
          headerText = headerText.replace(weightMatch[0] ?? '', '').trim()
        }

        // Extract container name (remove type in parentheses if present)
        const nameMatch = headerText.match(/^([^(]+)/)
        const containerName = (nameMatch ? nameMatch[1]?.trim() : headerText) || headerText

        currentContainer = {
          name: containerName,
          id: containerId,
          uuid: containerUuid,
          weight: containerWeight,
          weightUnit: containerWeightUnit,
          url: containerUrl,
          description: containerDescription, // Description from *(text)* in header
          price: containerPrice,
          currency: containerCurrency,
          favorite: containerFavorite,
          items: [],
        }
        continue
      }

      // Item line (- Item)
      if (line.startsWith('- ') && currentContainer) {
        // First item encountered - stop collecting description
        if (isCollectingDescription) {
          // Save collected description (only if not already set from header)
          if (descriptionLines.length > 0 && !currentContainer.description) {
            const description = descriptionLines.join('\n').trim()
            if (description) {
              currentContainer.description = description
            }
          }
          descriptionLines = []
          isCollectingDescription = false
        }

        try {
          const item = this.parseItemLine(line.substring(2).trim(), {
            recognizeFromName: options?.recognizeFromName ?? false,
            customBrands: options?.customBrands,
          })
          if (item) {
            // Collect indented lines (notes) after the item line
            const noteLines: string[] = []
            let j = i + 1
            while (j < lines.length) {
              const nextLine = lines[j]
              if (!nextLine) {
                // Empty line - keep it in notes
                noteLines.push('')
                j++
                continue
              }

              // Check if line starts with exactly 2 spaces (indented note)
              if (nextLine.startsWith('  ') && !nextLine.startsWith('   ')) {
                // Remove the 2-space indent and add to notes
                const noteLine = nextLine.substring(2)
                noteLines.push(noteLine)
                j++
                continue
              }

              // Stop if we encounter another item or container
              const trimmedNextLine = nextLine.trim()
              if (trimmedNextLine.startsWith('- ') || trimmedNextLine.startsWith('## ')) {
                break
              }

              // If line doesn't start with 2 spaces, it's not a note
              break
            }

            // Join note lines and set as item notes (if any)
            // Indented lines take priority over inline *(text)* format
            if (noteLines.length > 0) {
              // Remove trailing empty lines but preserve empty lines in the middle
              while (noteLines.length > 0 && noteLines[noteLines.length - 1] === '') {
                noteLines.pop()
              }
              const notes = noteLines.join('\n')
              if (notes.trim()) {
                item.notes = notes
              }
              // Skip the lines we've processed
              i = j - 1
            }
            // If no indented lines found, keep notes from parseItemLine (*(text)* format as fallback)

            currentContainer.items.push(item)
          }
        } catch (error) {
          result.errors.push(`Line ${i + 1}: ${error instanceof Error ? error.message : 'Unknown error'}`)
        }
        continue
      }

      // Description line (between header and first item)
      if (isCollectingDescription && currentContainer) {
        descriptionLines.push(line)
      }
    }

    // Add last container with description
    if (currentContainer && currentContainer.items.length > 0) {
      // Save description if still collecting (only if not already set from header)
      if (descriptionLines.length > 0 && !currentContainer.description) {
        const description = descriptionLines.join('\n').trim()
        if (description) {
          currentContainer.description = description
        }
      }
      result.containers.push(currentContainer)
    }

    return result
  }

  /**
   * Parse a single item line
   * New format: - **Item Name** [uuid:xxx] x2 (Brand, Color) [#container-id] (Status) - 500g
   * Old format: - Item name **Brand** (params) x5
   * Flexible: Parser will try to guess all fields
   * @param options - Parsing options
   * @param options.recognizeFromName - Whether to recognize brand and color from item name
   * @param options.customBrands - Custom user brands to include in recognition
   */
  private parseItemLine(
    line: string,
    options?: {
      recognizeFromName?: boolean
      customBrands?: Array<{ value: string }>
    }
  ): (ICreateItemDto & { nestedContainerId?: string; uuid?: string }) | null {
    if (!line) return null

    let workingLine = line
    let name = ''
    let brand: string | undefined
    let color: string | undefined
    let status: 'owned' | 'missing' | 'toBuy' = 'owned'
    let quantity = 1
    let weight = 100 // Default weight
    let weightUnit: 'g' | 'kg' | 'oz' | 'lb' = 'g'
    let expirationDate: string | undefined
    let url: string | undefined
    let nestedContainerId: string | undefined
    let uuid: string | undefined
    let wearable: boolean | undefined
    let consumable: boolean | undefined
    let notes: string | undefined
    let price: number | undefined
    let currency: string | undefined

    // 0. Extract price first (before other patterns to avoid conflicts)
    const priceResult = priceParser.parse(workingLine)
    if (priceResult) {
      price = priceResult.price
      currency = priceResult.currency
      // Remove price from working line
      workingLine = workingLine.replace(/(\d+(?:[\s,.]\d+)*)\s*(PLN|zł|z[lł]|\$|USD|€|EUR|£|GBP)/gi, '').trim()
    }

    // 1. Extract bold text as item name (new format: **Item Name**)
    const boldMatch = workingLine.match(/\*\*([^*]+)\*\*/)
    if (boldMatch) {
      name = boldMatch[1]?.trim() ?? ''
      workingLine = workingLine.replace(boldMatch[0] ?? '', '').trim()
    }

    // 1.5. Extract description/notes in italic format *(text)* BEFORE parsing parentheses
    // This prevents description from being mistaken for brand/color
    const italicDescriptionMatch = workingLine.match(/\*\(([^)]+)\)\*/)
    if (italicDescriptionMatch) {
      notes = italicDescriptionMatch[1]?.trim()
      workingLine = workingLine.replace(italicDescriptionMatch[0] ?? '', '').trim()
    }

    // 2. Extract UUID from [uuid:xxx]
    const uuidMatch = workingLine.match(/\[uuid:([^\]]+)\]/)
    if (uuidMatch) {
      uuid = uuidMatch[1]?.trim()
      workingLine = workingLine.replace(uuidMatch[0] ?? '', '').trim()
    }

    // 3. Extract weight at the end (- 500g, - 2.5kg, - 16oz, - 2.5lb)
    const weightMatch = workingLine.match(/[-–—]\s*(\d+(?:[.,]\d+)?)\s*(g|kg|oz|lb)\s*$/i)
    if (weightMatch) {
      weight = Number.parseFloat((weightMatch[1] ?? '100').replace(',', '.'))
      const unit = weightMatch[2]?.toLowerCase() ?? 'g'
      weightUnit = (unit === 'kg' ? 'kg' : unit === 'oz' ? 'oz' : unit === 'lb' ? 'lb' : 'g') as 'g' | 'kg' | 'oz' | 'lb'
      workingLine = workingLine.substring(0, weightMatch.index).trim()
    }

    // 4. Extract container ID [#id] (for nested containers)
    const containerIdMatch = workingLine.match(/\[#([^\]]+)\]/)
    if (containerIdMatch) {
      nestedContainerId = containerIdMatch[1]?.trim()
      workingLine = workingLine.replace(containerIdMatch[0] ?? '', '').trim()
    }

    // 4. Extract URL (in angle brackets <url> or plain http://|https://|www.)
    const urlMatch = workingLine.match(/<([^>]+)>|(\bhttps?:\/\/[^\s]+)|(\bwww\.[^\s]+)/)
    if (urlMatch) {
      url = (urlMatch[1] ?? urlMatch[2] ?? urlMatch[3])?.trim()
      // Add protocol if missing (www. case)
      if (url && url.startsWith('www.') && !url.startsWith('http')) {
        url = `https://${url}`
      }
      workingLine = workingLine.replace(urlMatch[0] ?? '', '').trim()
    }

    // 4. Extract quantity (xN or ×N anywhere in the line)
    const quantityMatch = workingLine.match(/[x×](\d+)/i)
    if (quantityMatch) {
      quantity = Number.parseInt(quantityMatch[1] ?? '1', 10)
      workingLine = workingLine.replace(quantityMatch[0] ?? '', '').trim()
    }

    // 4. Extract all parentheses groups
    const parenthesesGroups: string[] = []
    let parenthesesMatch
    const parenthesesRegex = /\(([^)]+)\)/g
    while ((parenthesesMatch = parenthesesRegex.exec(workingLine)) !== null) {
      parenthesesGroups.push(parenthesesMatch[1] ?? '')
    }
    workingLine = workingLine.replace(/\([^)]*\)/g, '').trim()

    // 5. Parse parentheses groups
    // First group is typically (Brand, Color)
    // Second group is typically (Status) or (Expiration: date)
    if (parenthesesGroups.length > 0) {
      const firstGroup = parenthesesGroups[0] ?? ''
      const parts = firstGroup.split(',').map(p => p.trim())

      for (const part of parts) {
        // Check for expiration
        if (part.toLowerCase().includes('expiration:')) {
          const dateMatch = part.match(/expiration:\s*(\d{2}[./-]\d{2}[./-]\d{4})/i)
          if (dateMatch) {
            // Convert DD.MM.YYYY to ISO format
            const dateParts = dateMatch[1]?.split(/[./-]/)
            if (dateParts && dateParts.length === 3) {
              expirationDate = `${dateParts[2]}-${dateParts[1]}-${dateParts[0]}`
            }
          }
          continue
        }

        // Check for status
        const statusLower = part.toLowerCase()
        if (statusLower.includes('missing') || statusLower.includes('brakuje')) {
          status = 'missing'
          continue
        }
        if (statusLower.includes('to buy') || statusLower.includes('do kupienia')) {
          status = 'toBuy'
          continue
        }
        if (statusLower.includes('owned') || statusLower.includes('posiadane')) {
          status = 'owned'
          continue
        }

        // Check for wearable/consumable flags
        if (statusLower.includes('wearable') || statusLower.includes('noszony')) {
          wearable = true
          continue
        }
        if (statusLower.includes('consumable') || statusLower.includes('zużywalny')) {
          consumable = true
          continue
        }

        // Check if it's a brand
        const matchedBrand = this.matchBrand(part)
        if (matchedBrand && !brand) {
          brand = matchedBrand
          continue
        }

        // Check if it's a color
        const matchedColor = this.matchColor(part)
        if (matchedColor && !color) {
          color = matchedColor
          continue
        }
      }
    }

    // Check second parentheses group for status/expiration
    if (parenthesesGroups.length > 1) {
      const secondGroup = parenthesesGroups[1] ?? ''
      const parts = secondGroup.split(',').map(p => p.trim())

      for (const part of parts) {
        // Check for expiration
        if (part.toLowerCase().includes('expiration:')) {
          const dateMatch = part.match(/expiration:\s*(\d{2}[./-]\d{2}[./-]\d{4})/i)
          if (dateMatch) {
            const dateParts = dateMatch[1]?.split(/[./-]/)
            if (dateParts && dateParts.length === 3) {
              expirationDate = `${dateParts[2]}-${dateParts[1]}-${dateParts[0]}`
            }
          }
          continue
        }

        // Check for status
        const statusLower = part.toLowerCase()
        if (statusLower.includes('missing') || statusLower.includes('brakuje')) {
          status = 'missing'
          continue
        }
        if (statusLower.includes('to buy') || statusLower.includes('do kupienia')) {
          status = 'toBuy'
          continue
        }

        // Check for wearable/consumable flags
        if (statusLower.includes('wearable') || statusLower.includes('noszony')) {
          wearable = true
          continue
        }
        if (statusLower.includes('consumable') || statusLower.includes('zużywalny')) {
          consumable = true
          continue
        }
      }
    }

    // 6. If name is still empty, try old format (brand in bold)
    if (!name) {
      name = workingLine.trim()
      // In old format, bold was brand, so if we have bold text already extracted,
      // and name is empty, use the remaining line as name
    }

    // 7. Fallback: if still no name from bold, use remaining line
    if (!name) {
      name = workingLine.trim()
    }

    // 8. Recognize brand and color from name if option is enabled and not already set
    if (options?.recognizeFromName && name) {
      const recognizedParams = recognizeParameters(name, options.customBrands)
      // Only use recognized values if brand/color weren't already found in parentheses
      if (!brand && recognizedParams.brand) {
        brand = recognizedParams.brand
      }
      if (!color && recognizedParams.color) {
        color = recognizedParams.color
      }
    }

    // 9. Determine category from name
    const category = this.matchCategory(name)

    const item: ICreateItemDto & { nestedContainerId?: string; uuid?: string } = {
      name,
      category,
      quantity,
      weight,
      weightUnit,
      priority: 'medium',
      status,
      brand,
      color,
      expirationDate,
      url,
      wearable,
      consumable,
      notes,
      price,
      currency,
      nestedContainerId, // Temporary slug reference to container
      uuid, // UUID for update workflow
    }

    return item
  }

  /**
   * Parse content inside parentheses for parameters
   * Example: (olive, knife, 500g, x2)
   */
  private parseParentheses(line: string): IItemParams {
    const params: IItemParams = {}
    const match = line.match(/\(([^)]+)\)/)

    if (!match || !match[1]) {
      return params
    }

    const content = match[1].trim()
    const parts = content.split(',').map(p => p.trim())

    for (const part of parts) {
      // Try to match brand
      const brand = this.matchBrand(part)
      if (brand && !params.brand) {
        params.brand = brand
        continue
      }

      // Try to match color
      const color = this.matchColor(part)
      if (color && !params.color) {
        params.color = color
        continue
      }

      // Try to match category
      const category = this.matchCategory(part)
      if (category !== 'other' && !params.category) {
        params.category = category
        continue
      }

      // Try to match quantity (xN)
      const qtyMatch = part.match(/^[x×]?(\d+)$/i)
      if (qtyMatch) {
        params.quantity = Number.parseInt(qtyMatch[1] ?? '1', 10)
        continue
      }

      // Try to match weight (Ng, Nkg, Noz, Nlb)
      const weightMatch = part.match(/^(\d+(?:[.,]\d+)?)\s*(g|kg|oz|lb)$/i)
      if (weightMatch) {
        params.weight = Number.parseFloat((weightMatch[1] ?? '0').replace(',', '.'))
        const unit = weightMatch[2]?.toLowerCase() ?? 'g'
        params.weightUnit = (unit === 'kg' ? 'kg' : unit === 'oz' ? 'oz' : unit === 'lb' ? 'lb' : 'g') as 'g' | 'kg' | 'oz' | 'lb'
        continue
      }
    }

    return params
  }

  /**
   * Match text against known brands (case-insensitive, fuzzy)
   */
  private matchBrand(text: string): string | undefined {
    const normalized = text.toLowerCase().trim()

    // Exact match
    for (const brand of SUGGESTED_BRANDS) {
      if (brand.toLowerCase() === normalized) {
        return brand
      }
    }

    // Fuzzy match (contains)
    for (const brand of SUGGESTED_BRANDS) {
      if (normalized.includes(brand.toLowerCase()) || brand.toLowerCase().includes(normalized)) {
        return brand
      }
    }

    // If not matched, return as-is (custom brand)
    return text.trim() || undefined
  }

  /**
   * Match text against known colors (case-insensitive)
   */
  private matchColor(text: string): string | undefined {
    const normalized = text.toLowerCase().trim()

    for (const color of SUGGESTED_COLORS) {
      if (color.toLowerCase() === normalized) {
        return color
      }
    }

    // If not in suggested colors, return as-is (custom color)
    return text.trim() || undefined
  }

  /**
   * Match text against category keywords
   */
  private matchCategory(text: string): string {
    const normalized = text.toLowerCase()

    for (const [category, keywords] of Object.entries(this.categoryKeywords)) {
      for (const keyword of keywords) {
        if (normalized.includes(keyword)) {
          return category
        }
      }
    }

    return 'other'
  }
}

export const markdownImportService = new MarkdownImportService()
