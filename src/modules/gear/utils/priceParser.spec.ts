import { beforeEach, describe, expect, it } from 'vitest'
import { PriceParser, priceParser } from './priceParser'

describe('priceParser', () => {
  describe('PLN (Polish Zloty) parsing', () => {
    it('should parse "100PLN" format', () => {
      const result = priceParser.parse('100PLN')
      expect(result).toEqual({ price: 100, currency: 'PLN' })
    })

    it('should parse "100 PLN" format with space', () => {
      const result = priceParser.parse('100 PLN')
      expect(result).toEqual({ price: 100, currency: 'PLN' })
    })

    it('should parse "100zł" format', () => {
      const result = priceParser.parse('100zł')
      expect(result).toEqual({ price: 100, currency: 'PLN' })
    })

    it('should parse "100 zł" format with space', () => {
      const result = priceParser.parse('100 zł')
      expect(result).toEqual({ price: 100, currency: 'PLN' })
    })

    it('should parse "100zl" format (l instead of ł)', () => {
      const result = priceParser.parse('100zl')
      expect(result).toEqual({ price: 100, currency: 'PLN' })
    })

    it('should parse decimals "10,00 PLN"', () => {
      const result = priceParser.parse('10,00 PLN')
      expect(result).toEqual({ price: 10.00, currency: 'PLN' })
    })

    it('should parse thousands separator "1 000 PLN"', () => {
      const result = priceParser.parse('1 000 PLN')
      expect(result).toEqual({ price: 1000, currency: 'PLN' })
    })

    it('should parse complex format "1 234,56 PLN"', () => {
      const result = priceParser.parse('1 234,56 PLN')
      expect(result).toEqual({ price: 1234.56, currency: 'PLN' })
    })

    it('should be case insensitive', () => {
      expect(priceParser.parse('100pln')).toEqual({ price: 100, currency: 'PLN' })
      expect(priceParser.parse('100Pln')).toEqual({ price: 100, currency: 'PLN' })
      expect(priceParser.parse('100PLN')).toEqual({ price: 100, currency: 'PLN' })
    })
  })

  describe('USD (US Dollar) parsing', () => {
    it('should parse "$50" format (symbol before)', () => {
      const result = priceParser.parse('$50')
      expect(result).toEqual({ price: 50, currency: 'USD' })
    })

    it('should parse "50$" format (symbol after)', () => {
      const result = priceParser.parse('50$')
      expect(result).toEqual({ price: 50, currency: 'USD' })
    })

    it('should parse "$ 50" format with space', () => {
      const result = priceParser.parse('$ 50')
      expect(result).toEqual({ price: 50, currency: 'USD' })
    })

    it('should parse "50 $" format with space', () => {
      const result = priceParser.parse('50 $')
      expect(result).toEqual({ price: 50, currency: 'USD' })
    })

    it('should parse "100 USD" format', () => {
      const result = priceParser.parse('100 USD')
      expect(result).toEqual({ price: 100, currency: 'USD' })
    })

    it('should parse "100USD" format without space', () => {
      const result = priceParser.parse('100USD')
      expect(result).toEqual({ price: 100, currency: 'USD' })
    })

    it('should parse decimals "$19.99"', () => {
      const result = priceParser.parse('$19.99')
      expect(result).toEqual({ price: 19.99, currency: 'USD' })
    })

    it('should parse thousands "$1,234.56"', () => {
      const result = priceParser.parse('$1,234.56')
      expect(result).toEqual({ price: 1234.56, currency: 'USD' })
    })

    it('should be case insensitive', () => {
      expect(priceParser.parse('100usd')).toEqual({ price: 100, currency: 'USD' })
      expect(priceParser.parse('100Usd')).toEqual({ price: 100, currency: 'USD' })
      expect(priceParser.parse('100USD')).toEqual({ price: 100, currency: 'USD' })
    })
  })

  describe('EUR (Euro) parsing', () => {
    it('should parse "€100" format (symbol before)', () => {
      const result = priceParser.parse('€100')
      expect(result).toEqual({ price: 100, currency: 'EUR' })
    })

    it('should parse "100€" format (symbol after)', () => {
      const result = priceParser.parse('100€')
      expect(result).toEqual({ price: 100, currency: 'EUR' })
    })

    it('should parse "€ 100" format with space', () => {
      const result = priceParser.parse('€ 100')
      expect(result).toEqual({ price: 100, currency: 'EUR' })
    })

    it('should parse "100 €" format with space', () => {
      const result = priceParser.parse('100 €')
      expect(result).toEqual({ price: 100, currency: 'EUR' })
    })

    it('should parse "100 EUR" format', () => {
      const result = priceParser.parse('100 EUR')
      expect(result).toEqual({ price: 100, currency: 'EUR' })
    })

    it('should parse "100EUR" format without space', () => {
      const result = priceParser.parse('100EUR')
      expect(result).toEqual({ price: 100, currency: 'EUR' })
    })

    it('should parse decimals "€49,99"', () => {
      const result = priceParser.parse('€49,99')
      expect(result).toEqual({ price: 49.99, currency: 'EUR' })
    })

    it('should be case insensitive', () => {
      expect(priceParser.parse('100eur')).toEqual({ price: 100, currency: 'EUR' })
      expect(priceParser.parse('100Eur')).toEqual({ price: 100, currency: 'EUR' })
      expect(priceParser.parse('100EUR')).toEqual({ price: 100, currency: 'EUR' })
    })
  })

  describe('GBP (British Pound) parsing', () => {
    it('should parse "£75" format (symbol before)', () => {
      const result = priceParser.parse('£75')
      expect(result).toEqual({ price: 75, currency: 'GBP' })
    })

    it('should parse "75£" format (symbol after)', () => {
      const result = priceParser.parse('75£')
      expect(result).toEqual({ price: 75, currency: 'GBP' })
    })

    it('should parse "£ 75" format with space', () => {
      const result = priceParser.parse('£ 75')
      expect(result).toEqual({ price: 75, currency: 'GBP' })
    })

    it('should parse "75 £" format with space', () => {
      const result = priceParser.parse('75 £')
      expect(result).toEqual({ price: 75, currency: 'GBP' })
    })

    it('should parse "100 GBP" format', () => {
      const result = priceParser.parse('100 GBP')
      expect(result).toEqual({ price: 100, currency: 'GBP' })
    })

    it('should parse "100GBP" format without space', () => {
      const result = priceParser.parse('100GBP')
      expect(result).toEqual({ price: 100, currency: 'GBP' })
    })

    it('should parse decimals "£29.99"', () => {
      const result = priceParser.parse('£29.99')
      expect(result).toEqual({ price: 29.99, currency: 'GBP' })
    })

    it('should be case insensitive', () => {
      expect(priceParser.parse('100gbp')).toEqual({ price: 100, currency: 'GBP' })
      expect(priceParser.parse('100Gbp')).toEqual({ price: 100, currency: 'GBP' })
      expect(priceParser.parse('100GBP')).toEqual({ price: 100, currency: 'GBP' })
    })
  })

  describe('parsing text with embedded prices', () => {
    it('should extract price from longer text', () => {
      const result = priceParser.parse('Backpack costs 150 PLN and is great')
      expect(result).toEqual({ price: 150, currency: 'PLN' })
    })

    it('should extract first matching price', () => {
      const result = priceParser.parse('Was $100, now $80')
      expect(result).toEqual({ price: 100, currency: 'USD' })
    })

    it('should work with URLs in text', () => {
      const result = priceParser.parse('https://example.com/product 99 EUR')
      expect(result).toEqual({ price: 99, currency: 'EUR' })
    })
  })

  describe('no match scenarios', () => {
    it('should return undefined for text without price', () => {
      const result = priceParser.parse('No price here')
      expect(result).toBeUndefined()
    })

    it('should return undefined for empty string', () => {
      const result = priceParser.parse('')
      expect(result).toBeUndefined()
    })

    it('should return undefined for only numbers', () => {
      const result = priceParser.parse('12345')
      expect(result).toBeUndefined()
    })

    it('should return undefined for unsupported currency', () => {
      const result = priceParser.parse('100 JPY')
      expect(result).toBeUndefined()
    })

    it('should return undefined for invalid number', () => {
      const result = priceParser.parse('abc PLN')
      expect(result).toBeUndefined()
    })
  })

  describe('edge cases', () => {
    it('should handle zero price', () => {
      const result = priceParser.parse('0 PLN')
      expect(result).toEqual({ price: 0, currency: 'PLN' })
    })

    it('should handle very large numbers', () => {
      const result = priceParser.parse('999999 PLN')
      expect(result).toEqual({ price: 999999, currency: 'PLN' })
    })

    it('should handle very small decimals', () => {
      const result = priceParser.parse('$0.01')
      expect(result).toEqual({ price: 0.01, currency: 'USD' })
    })

    it('should handle price at start of text', () => {
      const result = priceParser.parse('100 PLN for this item')
      expect(result).toEqual({ price: 100, currency: 'PLN' })
    })

    it('should handle price at end of text', () => {
      const result = priceParser.parse('This item costs 100 PLN')
      expect(result).toEqual({ price: 100, currency: 'PLN' })
    })
  })

  describe('PriceParser registry pattern', () => {
    it('should be extensible with custom parsers', () => {
      // Create custom parser instance
      const customParser = new PriceParser()

      // Register default parsers
      customParser.register({
        currency: 'PLN',
        parse: (text: string) => {
          const match = text.match(/(\d+)\s*PLN/)
          if (match) {
            return { price: Number.parseFloat(match[1] ?? '0'), currency: 'PLN' }
          }
          return undefined
        },
      })

      const result = customParser.parse('100 PLN')
      expect(result).toEqual({ price: 100, currency: 'PLN' })
    })

    it('should support priority ordering', () => {
      const customParser = new PriceParser()

      // Register high priority parser first
      customParser.register({
        currency: 'TEST',
        priority: 10,
        parse: (text: string) => {
          if (text.includes('TEST')) {
            return { price: 999, currency: 'TEST' }
          }
          return undefined
        },
      })

      // Register low priority parser
      customParser.register({
        currency: 'PLN',
        priority: 1,
        parse: (text: string) => {
          const match = text.match(/(\d+)\s*PLN/)
          if (match) {
            return { price: Number.parseFloat(match[1] ?? '0'), currency: 'PLN' }
          }
          return undefined
        },
      })

      // High priority should match first
      const result1 = customParser.parse('100 PLN TEST')
      expect(result1).toEqual({ price: 999, currency: 'TEST' })

      // Low priority should work when high priority doesn't match
      const result2 = customParser.parse('100 PLN')
      expect(result2).toEqual({ price: 100, currency: 'PLN' })
    })

    it('should allow clearing parsers', () => {
      const customParser = new PriceParser()
      customParser.register({
        currency: 'PLN',
        parse: (text: string) => {
          const match = text.match(/(\d+)\s*PLN/)
          if (match) {
            return { price: Number.parseFloat(match[1] ?? '0'), currency: 'PLN' }
          }
          return undefined
        },
      })

      // Should work before clearing
      expect(customParser.parse('100 PLN')).toEqual({ price: 100, currency: 'PLN' })

      // Clear all parsers
      customParser.clear()

      // Should not work after clearing
      expect(customParser.parse('100 PLN')).toBeUndefined()
    })

    it('should expose registered parsers', () => {
      const customParser = new PriceParser()
      customParser.register({
        currency: 'PLN',
        parse: () => undefined,
      })
      customParser.register({
        currency: 'USD',
        parse: () => undefined,
      })

      const parsers = customParser.getParsers()
      expect(parsers).toHaveLength(2)
      expect(parsers[0]?.currency).toBeDefined()
      expect(parsers[1]?.currency).toBeDefined()
    })
  })

  describe('singleton instance (priceParser)', () => {
    it('should have PLN parser registered', () => {
      const result = priceParser.parse('100 PLN')
      expect(result).toBeDefined()
      expect(result?.currency).toBe('PLN')
    })

    it('should have USD parser registered', () => {
      const result = priceParser.parse('$100')
      expect(result).toBeDefined()
      expect(result?.currency).toBe('USD')
    })

    it('should have EUR parser registered', () => {
      const result = priceParser.parse('€100')
      expect(result).toBeDefined()
      expect(result?.currency).toBe('EUR')
    })

    it('should have GBP parser registered', () => {
      const result = priceParser.parse('£100')
      expect(result).toBeDefined()
      expect(result?.currency).toBe('GBP')
    })

    it('should have 4 parsers registered by default', () => {
      const parsers = priceParser.getParsers()
      expect(parsers.length).toBeGreaterThanOrEqual(4)
    })
  })

  describe('real-world examples from markdown import', () => {
    it('should parse price from container header', () => {
      const headerText = '## Bug-Out Bag [#bug-out-bag] (Backpack) 150 PLN - 2000g'
      const result = priceParser.parse(headerText)
      expect(result).toEqual({ price: 150, currency: 'PLN' })
    })

    it('should parse price from item line', () => {
      const itemLine = '- **Tactical Knife** (Victorinox, Black) $75.50 - 200g'
      const result = priceParser.parse(itemLine)
      expect(result).toEqual({ price: 75.50, currency: 'USD' })
    })

    it('should parse price with URL present', () => {
      const text = 'Backpack <https://example.com/product> 99.99 EUR - 1500g'
      const result = priceParser.parse(text)
      expect(result).toEqual({ price: 99.99, currency: 'EUR' })
    })

    it('should parse price before weight', () => {
      const text = 'Item costs 49 PLN - weighs 300g'
      const result = priceParser.parse(text)
      expect(result).toEqual({ price: 49, currency: 'PLN' })
    })
  })

  describe('OCP compliance verification', () => {
    let customParser: PriceParser

    beforeEach(() => {
      customParser = new PriceParser()
    })

    it('should allow adding new currency without modifying existing code', () => {
      // Add JPY parser WITHOUT modifying PriceParser class
      customParser.register({
        currency: 'JPY',
        parse: (text: string) => {
          const match = text.match(/(\d+)\s*JPY/i)
          if (match) {
            return { price: Number.parseFloat(match[1] ?? '0'), currency: 'JPY' }
          }
          return undefined
        },
      })

      const result = customParser.parse('1000 JPY')
      expect(result).toEqual({ price: 1000, currency: 'JPY' })
    })

    it('should allow adding cryptocurrency parser', () => {
      customParser.register({
        currency: 'BTC',
        priority: 10,
        parse: (text: string) => {
          const match = text.match(/(\d+(?:\.\d+)?)\s*BTC/i)
          if (match) {
            return { price: Number.parseFloat(match[1] ?? '0'), currency: 'BTC' }
          }
          return undefined
        },
      })

      const result = customParser.parse('0.5 BTC')
      expect(result).toEqual({ price: 0.5, currency: 'BTC' })
    })

    it('should allow custom parser with different regex pattern', () => {
      // Custom parser that only matches exact format "PRICE:100:PLN"
      customParser.register({
        currency: 'CUSTOM',
        parse: (text: string) => {
          const match = text.match(/PRICE:(\d+):(\w+)/)
          if (match) {
            return {
              price: Number.parseFloat(match[1] ?? '0'),
              currency: match[2] ?? 'CUSTOM',
            }
          }
          return undefined
        },
      })

      const result = customParser.parse('PRICE:100:PLN')
      expect(result).toEqual({ price: 100, currency: 'PLN' })
    })
  })
})
