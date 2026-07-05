/**
 * M7 FIX: Price parser with registry pattern (OCP compliance)
 *
 * This module implements a price parsing system following the Open-Closed Principle:
 * - Open for extension: New currency parsers can be added without modifying existing code
 * - Closed for modification: Core PriceParser class remains unchanged when adding currencies
 *
 * Usage:
 * ```typescript
 * import { priceParser } from './priceParser'
 *
 * // Parse price from text
 * const result = priceParser.parse('100 PLN')
 * // { price: 100, currency: 'PLN' }
 *
 * // Register custom currency
 * priceParser.register(new CustomCurrencyParser())
 * ```
 */

/**
 * Interface for currency parsers
 * Each currency parser implements its own pattern matching and price extraction
 */
export interface ICurrencyParser {
  /**
   * Currency code (e.g., 'PLN', 'USD', 'EUR')
   */
  currency: string

  /**
   * Priority for matching (higher = checked first)
   * Useful when multiple parsers might match the same text
   */
  priority?: number

  /**
   * Parse price from text
   * @param text - Text to parse
   * @returns Parsed price and currency, or undefined if not found
   */
  parse(text: string): { price: number; currency: string } | undefined
}

/**
 * Price parser with registry pattern
 * Manages registered currency parsers and delegates parsing to them
 */
class PriceParser {
  private parsers: ICurrencyParser[] = []

  /**
   * Register a currency parser
   * @param parser - Currency parser to register
   */
  register(parser: ICurrencyParser): void {
    this.parsers.push(parser)
    // Sort by priority (higher priority first)
    this.parsers.sort((a, b) => (b.priority ?? 0) - (a.priority ?? 0))
  }

  /**
   * Parse price from text using registered parsers
   * @param text - Text to parse
   * @returns Parsed price and currency, or undefined if not found
   */
  parse(text: string): { price: number; currency: string } | undefined {
    for (const parser of this.parsers) {
      const result = parser.parse(text)
      if (result) {
        return result
      }
    }
    return undefined
  }

  /**
   * Get all registered parsers
   * @returns Array of registered parsers
   */
  getParsers(): ICurrencyParser[] {
    return [...this.parsers]
  }

  /**
   * Clear all registered parsers
   */
  clear(): void {
    this.parsers = []
  }
}

/**
 * Base class for regex-based currency parsers
 * Provides common functionality for pattern matching and price extraction
 */
abstract class RegexCurrencyParser implements ICurrencyParser {
  abstract currency: string
  abstract patterns: RegExp[]
  priority?: number

  parse(text: string): { price: number; currency: string } | undefined {
    for (const pattern of this.patterns) {
      const match = text.match(pattern)
      if (match && match[1]) {
        let priceStr = match[1].replace(/\s/g, '')

        // Smart separator handling:
        // If both comma and dot present, determine which is decimal separator
        const hasComma = priceStr.includes(',')
        const hasDot = priceStr.includes('.')

        if (hasComma && hasDot) {
          // Find last separator - that's the decimal separator
          const lastCommaIndex = priceStr.lastIndexOf(',')
          const lastDotIndex = priceStr.lastIndexOf('.')

          if (lastDotIndex > lastCommaIndex) {
            // Dot is decimal separator (e.g., "$1,234.56")
            // Remove commas (thousands separator)
            priceStr = priceStr.replace(/,/g, '')
          } else {
            // Comma is decimal separator (e.g., "1.234,56 EUR")
            // Remove dots (thousands separator) and replace comma with dot
            priceStr = priceStr.replace(/\./g, '').replace(',', '.')
          }
        } else if (hasComma) {
          // Only comma present - treat as decimal separator (e.g., "10,50 PLN")
          priceStr = priceStr.replace(',', '.')
        }
        // If only dot or no separators, leave as is

        const price = Number.parseFloat(priceStr)
        if (!Number.isNaN(price)) {
          return { price, currency: this.currency }
        }
      }
    }
    return undefined
  }
}

/**
 * PLN (Polish Zloty) currency parser
 * Supports: 100PLN, 100 PLN, 10,00 PLN, 1 000,00 PLN, 10zł
 */
class PLNCurrencyParser extends RegexCurrencyParser {
  currency = 'PLN'
  patterns = [
    /(\d+(?:[\s,.]\d+)*)\s*PLN/i,
    /(\d+(?:[\s,.]\d+)*)\s*zł/i,
    /(\d+(?:[\s,.]\d+)*)\s*z[lł]/i,
  ]
}

/**
 * USD (US Dollar) currency parser
 * Supports: $50, 50$, 100 USD
 */
class USDCurrencyParser extends RegexCurrencyParser {
  currency = 'USD'
  patterns = [
    /\$\s*(\d+(?:[\s,.]\d+)*)/i,
    /(\d+(?:[\s,.]\d+)*)\s*\$/i,
    /(\d+(?:[\s,.]\d+)*)\s*USD/i,
  ]
}

/**
 * EUR (Euro) currency parser
 * Supports: €100, 100€, 100 EUR
 */
class EURCurrencyParser extends RegexCurrencyParser {
  currency = 'EUR'
  patterns = [
    /€\s*(\d+(?:[\s,.]\d+)*)/i,
    /(\d+(?:[\s,.]\d+)*)\s*€/i,
    /(\d+(?:[\s,.]\d+)*)\s*EUR/i,
  ]
}

/**
 * GBP (British Pound) currency parser
 * Supports: £75, 75£, 100 GBP
 */
class GBPCurrencyParser extends RegexCurrencyParser {
  currency = 'GBP'
  patterns = [
    /£\s*(\d+(?:[\s,.]\d+)*)/i,
    /(\d+(?:[\s,.]\d+)*)\s*£/i,
    /(\d+(?:[\s,.]\d+)*)\s*GBP/i,
  ]
}

/**
 * Singleton instance with default currency parsers
 * Pre-registered with PLN, USD, EUR, and GBP parsers
 */
export const priceParser = new PriceParser()
priceParser.register(new PLNCurrencyParser())
priceParser.register(new USDCurrencyParser())
priceParser.register(new EURCurrencyParser())
priceParser.register(new GBPCurrencyParser())

/**
 * Export PriceParser class for custom instances
 * Useful for testing or creating isolated parser instances
 */
export { PriceParser }
