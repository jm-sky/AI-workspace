import { describe, expect, it } from 'vitest'
import { markdownImportService } from './markdownImportService'

describe('markdownImportService', () => {
  describe('Basic parsing', () => {
    it('should parse a simple container with items', () => {
      const markdown = `
## Bug-Out Bag [#bug-out-bag]
- **Water Bottle** - 300g
- **Knife** - 150g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)

      expect(result.errors).toHaveLength(0)
      expect(result.containers).toHaveLength(1)
      expect(result.containers[0]?.name).toBe('Bug-Out Bag')
      expect(result.containers[0]?.id).toBe('bug-out-bag')
      expect(result.containers[0]?.items).toHaveLength(2)
      expect(result.containers[0]?.items[0]?.name).toBe('Water Bottle')
      expect(result.containers[0]?.items[0]?.weight).toBe(300)
      expect(result.containers[0]?.items[0]?.weightUnit).toBe('g')
      expect(result.containers[0]?.items[1]?.name).toBe('Knife')
      expect(result.containers[0]?.items[1]?.weight).toBe(150)
    })

    it('should parse multiple containers', () => {
      const markdown = `
## Container 1 [#container-1]
- **Item 1** - 100g

## Container 2 [#container-2]
- **Item 2** - 200g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)

      expect(result.errors).toHaveLength(0)
      expect(result.containers).toHaveLength(2)
      expect(result.containers[0]?.name).toBe('Container 1')
      expect(result.containers[1]?.name).toBe('Container 2')
    })
  })

  describe('Item quantity parsing', () => {
    it('should parse quantity with x prefix', () => {
      const markdown = `
## Container [#container]
- **Batteries** x4 - 50g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.name).toBe('Batteries')
      expect(item?.quantity).toBe(4)
      expect(item?.weight).toBe(50)
    })

    it('should default quantity to 1 if not specified', () => {
      const markdown = `
## Container [#container]
- **Item** - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.quantity).toBe(1)
    })
  })

  describe('Brand and color parsing', () => {
    it('should parse brand and color from parentheses', () => {
      const markdown = `
## Container [#container]
- **Flashlight** (Petzl, Black) - 90g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.name).toBe('Flashlight')
      expect(item?.brand).toBe('Petzl')
      expect(item?.color).toBe('Black')
    })

    it('should parse only brand if color is not provided', () => {
      const markdown = `
## Container [#container]
- **Knife** (Victorinox) - 150g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.brand).toBe('Victorinox')
      expect(item?.color).toBeUndefined()
    })
  })

  describe('Status parsing', () => {
    it('should parse Missing status', () => {
      const markdown = `
## Container [#container]
- **Item** (Missing) - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.status).toBe('missing')
    })

    it('should parse To Buy status', () => {
      const markdown = `
## Container [#container]
- **Item** (To Buy) - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.status).toBe('toBuy')
    })

    it('should default to owned status', () => {
      const markdown = `
## Container [#container]
- **Item** - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.status).toBe('owned')
    })
  })

  describe('Expiration date parsing', () => {
    it('should parse expiration date in DD.MM.YYYY format', () => {
      const markdown = `
## Container [#container]
- **Medicine** (Expiration: 31.12.2025) - 50g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.expirationDate).toBe('2025-12-31')
    })

    it('should parse expiration date with status', () => {
      const markdown = `
## Container [#container]
- **Food** (Missing, Expiration: 15.06.2024) - 200g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.status).toBe('missing')
      expect(item?.expirationDate).toBe('2024-06-15')
    })
  })

  describe('Weight unit parsing', () => {
    it('should parse weight in grams', () => {
      const markdown = `
## Container [#container]
- **Item** - 500g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.weight).toBe(500)
      expect(item?.weightUnit).toBe('g')
    })

    it('should parse weight in kilograms', () => {
      const markdown = `
## Container [#container]
- **Item** - 2.5kg
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.weight).toBe(2.5)
      expect(item?.weightUnit).toBe('kg')
    })

    it('should parse weight in ounces', () => {
      const markdown = `
## Container [#container]
- **Item** - 16oz
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.weight).toBe(16)
      expect(item?.weightUnit).toBe('oz')
    })

    it('should parse weight in pounds', () => {
      const markdown = `
## Container [#container]
- **Item** - 2.5lb
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.weight).toBe(2.5)
      expect(item?.weightUnit).toBe('lb')
    })

    it('should default weight to 100g if not specified', () => {
      const markdown = `
## Container [#container]
- **Item**
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.weight).toBe(100)
      expect(item?.weightUnit).toBe('g')
    })
  })

  describe('URL parsing', () => {
    it('should parse URL in angle brackets', () => {
      const markdown = `
## Container [#container]
- **Item** <https://example.com/product> - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.url).toBe('https://example.com/product')
    })

    it('should parse plain URL with https', () => {
      const markdown = `
## Container [#container]
- **Item** https://example.com/product - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.url).toBe('https://example.com/product')
    })

    it('should add https to www URLs', () => {
      const markdown = `
## Container [#container]
- **Item** www.example.com/product - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.url).toBe('https://www.example.com/product')
    })
  })

  describe('Container properties parsing', () => {
    it('should parse container weight', () => {
      const markdown = `
## Backpack [#backpack] - 2000g
- **Item** - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const container = result.containers[0]

      expect(container?.name).toBe('Backpack')
      expect(container?.weight).toBe(2000)
      expect(container?.weightUnit).toBe('g')
    })

    it('should parse container weight in kg', () => {
      const markdown = `
## Backpack [#backpack] - 2kg
- **Item** - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const container = result.containers[0]

      expect(container?.weight).toBe(2)
      expect(container?.weightUnit).toBe('kg')
    })

    it('should parse container URL', () => {
      const markdown = `
## Backpack [#backpack] <https://example.com/backpack> - 2000g
- **Item** - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const container = result.containers[0]

      expect(container?.url).toBe('https://example.com/backpack')
    })

    it('should parse container with UUID', () => {
      const markdown = `
## Backpack [#backpack] [uuid:123e4567-e89b-12d3-a456-426614174000]
- **Item** - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const container = result.containers[0]

      expect(container?.uuid).toBe('123e4567-e89b-12d3-a456-426614174000')
    })
  })

  describe('Nested containers parsing', () => {
    it('should parse nested container reference', () => {
      const markdown = `
## Backpack [#backpack]
- **First Aid Pouch** [#first-aid-pouch] - 350g

## First Aid Pouch [#first-aid-pouch]
- **Bandages** - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)

      expect(result.containers).toHaveLength(2)
      const backpack = result.containers[0]
      const firstAidItem = backpack?.items[0]

      expect(firstAidItem?.name).toBe('First Aid Pouch')
      expect(firstAidItem?.nestedContainerId).toBe('first-aid-pouch')
      expect(firstAidItem?.weight).toBe(350)

      const firstAidPouch = result.containers[1]
      expect(firstAidPouch?.id).toBe('first-aid-pouch')
      expect(firstAidPouch?.items).toHaveLength(1)
    })
  })

  describe('Wearable and Consumable flags', () => {
    it('should parse Wearable flag', () => {
      const markdown = `
## Container [#container]
- **Jacket** (Wearable) - 800g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.wearable).toBe(true)
    })

    it('should parse Consumable flag', () => {
      const markdown = `
## Container [#container]
- **Energy Bar** (Consumable) - 50g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.consumable).toBe(true)
    })

    it('should parse both Wearable and Consumable flags with status', () => {
      const markdown = `
## Container [#container]
- **Item** (Missing, Wearable, Consumable) - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.status).toBe('missing')
      expect(item?.wearable).toBe(true)
      expect(item?.consumable).toBe(true)
    })
  })

  describe('Item notes/description parsing', () => {
    it('should parse description in italic format', () => {
      const markdown = `
## Container [#container]
- **Knife** *(small, foldable)* - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.name).toBe('Knife')
      expect(item?.notes).toBe('small, foldable')
      expect(item?.weight).toBe(100)
    })

    it('should parse description separately from brand/color', () => {
      const markdown = `
## Container [#container]
- **Knife** *(good quality)* (Victorinox, Black) - 150g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.notes).toBe('good quality')
      expect(item?.brand).toBe('Victorinox')
      expect(item?.color).toBe('Black')
    })
  })

  describe('UUID parsing for items', () => {
    it('should parse item UUID', () => {
      const markdown = `
## Container [#container]
- **Item** [uuid:123e4567-e89b-12d3-a456-426614174000] - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      expect(item?.uuid).toBe('123e4567-e89b-12d3-a456-426614174000')
    })
  })

  describe('Complex parsing scenarios', () => {
    it('should parse item with all fields', () => {
      const markdown = `
## Backpack [#backpack] [uuid:container-uuid] <https://example.com/backpack> - 2kg
- **Tactical Knife** [uuid:item-uuid] *(military grade)* x2 (Victorinox, Black) [#nested] (Missing, Expiration: 31.12.2025, Wearable, Consumable) <https://example.com/knife> - 200g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)

      // Container assertions
      const container = result.containers[0]
      expect(container?.name).toBe('Backpack')
      expect(container?.id).toBe('backpack')
      expect(container?.uuid).toBe('container-uuid')
      expect(container?.url).toBe('https://example.com/backpack')
      expect(container?.weight).toBe(2)
      expect(container?.weightUnit).toBe('kg')

      // Item assertions
      const item = container?.items[0]
      expect(item?.name).toBe('Tactical Knife')
      expect(item?.uuid).toBe('item-uuid')
      expect(item?.notes).toBe('military grade')
      expect(item?.quantity).toBe(2)
      expect(item?.brand).toBe('Victorinox')
      expect(item?.color).toBe('Black')
      expect(item?.nestedContainerId).toBe('nested')
      expect(item?.status).toBe('missing')
      expect(item?.expirationDate).toBe('2025-12-31')
      expect(item?.wearable).toBe(true)
      expect(item?.consumable).toBe(true)
      expect(item?.url).toBe('https://example.com/knife')
      expect(item?.weight).toBe(200)
      expect(item?.weightUnit).toBe('g')
    })

    it('should parse example from docs/examples/example-gear-formatted.md', () => {
      const markdown = `
## Samochód Opel Zafira [#samochod-opel-zafira] [uuid:7f6af1c1-7c6b-4b0d-9dd9-8c36f3d1b100] (Vehicle)
- **Bagażnik** [uuid:4cb16eaf-daa5-4d34-bce4-4aa390a94545] [#bagaznik] - 500g
- **Schowek samochodowy** [uuid:8e0b0c1a-5f03-4eff-af5c-dde3a9859c6f] [#schowek-samochodowy] - 300g

## Bagażnik [#bagaznik] [uuid:4cb16eaf-daa5-4d34-bce4-4aa390a94545] (Trunk)
- **Piła składana BAHCO 396-LAP** [uuid:5e6aec34-82a7-4fdc-9fa5-8b92b6dc7051] (BAHCO) - 250g
- **Paracord Badger Outdoor 550 Type III** [uuid:5bf72f62-61c2-4d0a-a11c-2b67a4bb53fd] (Badger Outdoor, Olive) - 40g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)

      expect(result.errors).toHaveLength(0)
      expect(result.containers).toHaveLength(2)

      // First container
      const vehicle = result.containers[0]
      expect(vehicle?.name).toBe('Samochód Opel Zafira')
      expect(vehicle?.id).toBe('samochod-opel-zafira')
      expect(vehicle?.uuid).toBe('7f6af1c1-7c6b-4b0d-9dd9-8c36f3d1b100')
      expect(vehicle?.items).toHaveLength(2)

      // Nested items
      const trunk = vehicle?.items[0]
      expect(trunk?.name).toBe('Bagażnik')
      expect(trunk?.nestedContainerId).toBe('bagaznik')
      expect(trunk?.uuid).toBe('4cb16eaf-daa5-4d34-bce4-4aa390a94545')

      // Second container
      const trunkContainer = result.containers[1]
      expect(trunkContainer?.name).toBe('Bagażnik')
      expect(trunkContainer?.id).toBe('bagaznik')
      expect(trunkContainer?.items).toHaveLength(2)

      const saw = trunkContainer?.items[0]
      expect(saw?.name).toBe('Piła składana BAHCO 396-LAP')
      expect(saw?.brand).toBe('Bahco') // Brand matching returns normalized case
      expect(saw?.weight).toBe(250)

      const paracord = trunkContainer?.items[1]
      expect(paracord?.brand).toBe('Badger') // Brand matching splits on first comma
      expect(paracord?.color).toBe('Olive')
    })
  })

  describe('Container description parsing', () => {
    it('should parse simple container description', () => {
      const markdown = `
## Backpack [#backpack]
This is a high-quality tactical backpack.
- **Item 1** - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const container = result.containers[0]

      expect(container?.description).toBe('This is a high-quality tactical backpack.')
    })

    it('should parse multi-line container description', () => {
      const markdown = `
## Backpack [#backpack]
This is a high-quality tactical backpack.
It has multiple compartments and is very durable.
Perfect for outdoor adventures.
- **Item 1** - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const container = result.containers[0]

      expect(container?.description).toBe(
        'This is a high-quality tactical backpack.\nIt has multiple compartments and is very durable.\nPerfect for outdoor adventures.'
      )
    })

    it('should handle container without description', () => {
      const markdown = `
## Backpack [#backpack]
- **Item 1** - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const container = result.containers[0]

      expect(container?.description).toBeUndefined()
    })

    it('should parse description with empty lines', () => {
      const markdown = `
## Backpack [#backpack]
This is a description.

With an empty line in between.
- **Item 1** - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const container = result.containers[0]

      expect(container?.description).toBe('This is a description.\n\nWith an empty line in between.')
    })

    it('should parse multiple containers with descriptions', () => {
      const markdown = `
## Container 1 [#container-1]
Description for container 1.
- **Item 1** - 100g

## Container 2 [#container-2]
Description for container 2.
- **Item 2** - 200g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)

      expect(result.containers[0]?.description).toBe('Description for container 1.')
      expect(result.containers[1]?.description).toBe('Description for container 2.')
    })

    it('should not treat parentheses in description as metadata', () => {
      const markdown = `
## Backpack [#backpack]
This backpack (model XYZ) is great.
- **Item 1** - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const container = result.containers[0]

      expect(container?.description).toBe('This backpack (model XYZ) is great.')
    })

    it('should parse description in italic format from container header', () => {
      const markdown = `
## Apteczka Blackhawk [#apteczka-blackhawk] [uuid:bd404a57-4c08-46c4-9c93-162fd047dca1] *(Łączna waga 470 g)* (Pouch)
- **Scyzoryk** - 40g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const container = result.containers[0]

      expect(container?.name).toBe('Apteczka Blackhawk')
      expect(container?.description).toBe('Łączna waga 470 g')
      expect(container?.id).toBe('apteczka-blackhawk')
      expect(container?.uuid).toBe('bd404a57-4c08-46c4-9c93-162fd047dca1')
    })

    it('should prioritize description from header over description from lines below', () => {
      const markdown = `
## Backpack [#backpack] *(Header description)*
This description should be ignored.
- **Item 1** - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const container = result.containers[0]

      expect(container?.description).toBe('Header description')
    })
  })

  describe('Price parsing', () => {
    describe('Container prices', () => {
      it('should parse price in PLN format (100PLN)', () => {
        const markdown = `
## Backpack [#backpack] 200PLN - 2000g
- **Item** - 100g
        `.trim()

        const result = markdownImportService.parseMarkdown(markdown)
        const container = result.containers[0]

        expect(container?.price).toBe(200)
        expect(container?.currency).toBe('PLN')
      })

      it('should parse price with space (100 PLN)', () => {
        const markdown = `
## Backpack [#backpack] 200 PLN - 2000g
- **Item** - 100g
        `.trim()

        const result = markdownImportService.parseMarkdown(markdown)
        const container = result.containers[0]

        expect(container?.price).toBe(200)
        expect(container?.currency).toBe('PLN')
      })

      it('should parse price with comma (100,50 PLN)', () => {
        const markdown = `
## Backpack [#backpack] 199,99 PLN - 2000g
- **Item** - 100g
        `.trim()

        const result = markdownImportService.parseMarkdown(markdown)
        const container = result.containers[0]

        expect(container?.price).toBe(199.99)
        expect(container?.currency).toBe('PLN')
      })

      it('should parse price with spaces in number (1 000,00 PLN)', () => {
        const markdown = `
## Backpack [#backpack] 1 250,00 PLN - 2000g
- **Item** - 100g
        `.trim()

        const result = markdownImportService.parseMarkdown(markdown)
        const container = result.containers[0]

        expect(container?.price).toBe(1250)
        expect(container?.currency).toBe('PLN')
      })

      it('should parse price with zł symbol', () => {
        const markdown = `
## Backpack [#backpack] 200zł - 2000g
- **Item** - 100g
        `.trim()

        const result = markdownImportService.parseMarkdown(markdown)
        const container = result.containers[0]

        expect(container?.price).toBe(200)
        expect(container?.currency).toBe('PLN')
      })

      it('should parse USD price with $ prefix', () => {
        const markdown = `
## Backpack [#backpack] $150 - 2000g
- **Item** - 100g
        `.trim()

        const result = markdownImportService.parseMarkdown(markdown)
        const container = result.containers[0]

        expect(container?.price).toBe(150)
        expect(container?.currency).toBe('USD')
      })

      it('should parse USD price with $ suffix', () => {
        const markdown = `
## Backpack [#backpack] 150$ - 2000g
- **Item** - 100g
        `.trim()

        const result = markdownImportService.parseMarkdown(markdown)
        const container = result.containers[0]

        expect(container?.price).toBe(150)
        expect(container?.currency).toBe('USD')
      })

      it('should parse EUR price with € prefix', () => {
        const markdown = `
## Backpack [#backpack] €120 - 2000g
- **Item** - 100g
        `.trim()

        const result = markdownImportService.parseMarkdown(markdown)
        const container = result.containers[0]

        expect(container?.price).toBe(120)
        expect(container?.currency).toBe('EUR')
      })

      it('should parse EUR price with € suffix', () => {
        const markdown = `
## Backpack [#backpack] 120€ - 2000g
- **Item** - 100g
        `.trim()

        const result = markdownImportService.parseMarkdown(markdown)
        const container = result.containers[0]

        expect(container?.price).toBe(120)
        expect(container?.currency).toBe('EUR')
      })

      it('should parse GBP price with £ prefix', () => {
        const markdown = `
## Backpack [#backpack] £100 - 2000g
- **Item** - 100g
        `.trim()

        const result = markdownImportService.parseMarkdown(markdown)
        const container = result.containers[0]

        expect(container?.price).toBe(100)
        expect(container?.currency).toBe('GBP')
      })
    })

    describe('Item prices', () => {
      it('should parse item price in PLN', () => {
        const markdown = `
## Container [#container]
- **Knife** 50PLN - 150g
        `.trim()

        const result = markdownImportService.parseMarkdown(markdown)
        const item = result.containers[0]?.items[0]

        expect(item?.price).toBe(50)
        expect(item?.currency).toBe('PLN')
      })

      it('should parse item price with comma', () => {
        const markdown = `
## Container [#container]
- **Knife** 49,99 PLN - 150g
        `.trim()

        const result = markdownImportService.parseMarkdown(markdown)
        const item = result.containers[0]?.items[0]

        expect(item?.price).toBe(49.99)
        expect(item?.currency).toBe('PLN')
      })

      it('should parse item price in USD', () => {
        const markdown = `
## Container [#container]
- **Knife** $75 - 150g
        `.trim()

        const result = markdownImportService.parseMarkdown(markdown)
        const item = result.containers[0]?.items[0]

        expect(item?.price).toBe(75)
        expect(item?.currency).toBe('USD')
      })

      it('should parse item price with all other fields', () => {
        const markdown = `
## Container [#container]
- **Tactical Knife** 299,99 PLN x2 (Victorinox, Black) (Missing) - 200g
        `.trim()

        const result = markdownImportService.parseMarkdown(markdown)
        const item = result.containers[0]?.items[0]

        expect(item?.name).toBe('Tactical Knife')
        expect(item?.price).toBe(299.99)
        expect(item?.currency).toBe('PLN')
        expect(item?.quantity).toBe(2)
        expect(item?.brand).toBe('Victorinox')
        expect(item?.color).toBe('Black')
        expect(item?.status).toBe('missing')
        expect(item?.weight).toBe(200)
      })
    })

    describe('Price without currency should not be parsed', () => {
      it('should not parse plain numbers as price', () => {
        const markdown = `
## Container [#container]
- **Item** 100 - 100g
        `.trim()

        const result = markdownImportService.parseMarkdown(markdown)
        const item = result.containers[0]?.items[0]

        expect(item?.price).toBeUndefined()
        expect(item?.currency).toBeUndefined()
      })
    })
  })

  describe('Edge cases and error handling', () => {
    it('should handle empty markdown', () => {
      const result = markdownImportService.parseMarkdown('')

      expect(result.containers).toHaveLength(0)
      expect(result.errors).toHaveLength(0)
    })

    it('should handle container without items', () => {
      const markdown = `
## Empty Container [#empty]
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)

      expect(result.containers).toHaveLength(0)
    })

    it('should handle items without container header', () => {
      const markdown = `
- **Item** - 100g
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)

      expect(result.containers).toHaveLength(0)
    })

    it('should handle malformed weight', () => {
      const markdown = `
## Container [#container]
- **Item** - abc
      `.trim()

      const result = markdownImportService.parseMarkdown(markdown)
      const item = result.containers[0]?.items[0]

      // Should default to 100g when weight cannot be parsed
      expect(item?.weight).toBe(100)
    })
  })
})
