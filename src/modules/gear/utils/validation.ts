import { z } from 'zod'
import { weightUnitEnum } from './weightUnits'

/**
 * Check if a string is a valid ULID (26 characters, base32)
 * ULID format: 26 characters using Crockford's Base32 (0-9, A-Z without I, L, O, U)
 */
export function isValidULID(value: string): boolean {
  // ULID is exactly 26 characters
  if (value.length !== 26) return false
  // ULID uses Crockford's Base32: 0-9, A-Z without I, L, O, U
  const ulidPattern = /^[0-9A-HJKMNP-TV-Z]{26}$/
  return ulidPattern.test(value.toUpperCase())
}

/**
 * Check if a string is a valid UUID (8-4-4-4-12 hex format)
 */
export function isValidUUID(value: string): boolean {
  const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
  return uuidPattern.test(value)
}

/**
 * Zod schema that accepts both ULID (backend) and UUID (frontend offline)
 * Backend uses ULID, frontend offline uses UUID
 */
const ulidOrUuidSchema = z.string().refine(
  (val) => !val || isValidULID(val) || isValidUUID(val),
  {
    message: 'Must be a valid ULID (26 chars) or UUID (8-4-4-4-12 format)',
  },
).optional().nullable()

// Schema dla kontenera
// Type can be a default type or any string (for custom container types)
export const containerSchema = z.object({
  name: z.string().min(1, 'Nazwa jest wymagana'),
  description: z.string().optional(),
  type: z.string().min(1, 'Typ jest wymagany'), // Allow any string for custom container types
  color: z.enum(['default', 'coyote', 'khaki', 'olive', 'forestGreen', 'tan', 'brown', 'black', 'navy', 'jeans', 'gray', 'orange']).optional(),
  parentContainerId: ulidOrUuidSchema,
  hideWhenNested: z.boolean().optional(),
  isPublic: z.boolean().optional(),
  favorite: z.boolean().optional(),
  brand: z.string().optional(),
  price: z.number().min(0, 'Cena nie może być ujemna').optional(),
  currency: z.string().optional(),
  weight: z.number().min(0, 'Waga nie może być ujemna').optional(),
  weightUnit: weightUnitEnum.optional(),
  maxWeight: z.number().min(0, 'Maksymalna waga nie może być ujemna').optional(),
  maxWeightUnit: weightUnitEnum.optional(),
  url: z.string().url('Nieprawidłowy URL').optional().or(z.literal('')),
  showItemImages: z.boolean().optional(),
})

// Schema dla przedmiotu
// Category can be a default category or any string (for custom categories)
export const itemSchema = z.object({
  name: z.string().min(1, 'Nazwa jest wymagana'),
  category: z.string().min(1, 'Kategoria jest wymagana'), // Allow any string for custom categories
  quantity: z.number().int().min(1, 'Ilość musi być większa od 0'),
  weight: z.number().min(0, 'Waga nie może być ujemna'),
  weightUnit: weightUnitEnum,
  notes: z.string().optional(),
  expirationDate: z.string().optional(),
  shelfLifeValue: z.number().int().min(1, 'Wartość okresu przydatności musi być większa od 0').optional(),
  shelfLifeUnit: z.enum(['days', 'months', 'years']).optional(),
  priority: z.enum(['critical', 'high', 'medium', 'low']),
  status: z.enum(['owned', 'missing', 'toBuy']),
  containerId: z.union([ulidOrUuidSchema, z.literal('')]).optional(), // Reference to nested container (empty string = no container), accepts ULID (backend) or UUID (frontend offline)
  price: z.number().min(0, 'Cena nie może być ujemna').optional(),
  currency: z.string().optional(),
  url: z.string().url('Nieprawidłowy URL').optional().or(z.literal('')),
  brand: z.string().optional(),
  color: z.string().optional(),
  quality: z.enum(['low', 'medium', 'high']).optional(),
  wearable: z.boolean().optional(),
  consumable: z.boolean().optional(),
  showOnContainer: z.boolean().optional(),
})

// Type inference dla TypeScript
export type ContainerFormData = z.infer<typeof containerSchema>
export type ItemFormData = z.infer<typeof itemSchema>

/**
 * Validation result for safe validation
 */
export type ValidationResult<T> =
  | { success: true; data: T }
  | { success: false; errors: string[] }

/**
 * M6 FIX: Validate container data before service call
 *
 * Use this when calling service methods directly (not through forms).
 * Examples: ImportMarkdownDialog, sampleSetGenerator, dataMigrationService
 *
 * @param data - Data to validate
 * @returns Validated container data
 * @throws ZodError with validation details
 *
 * @example
 * ```typescript
 * const validated = validateContainerDto({
 *   name: 'My Container',
 *   type: 'backpack',
 *   weight: 1500,
 *   weightUnit: 'g'
 * })
 * await createContainer(validated)
 * ```
 */
export function validateContainerDto(data: unknown): ContainerFormData {
  return containerSchema.parse(data)
}

/**
 * M6 FIX: Validate item data before service call
 *
 * Use this when calling service methods directly (not through forms).
 * Examples: ImportMarkdownDialog, sampleSetGenerator, dataMigrationService
 *
 * @param data - Data to validate
 * @returns Validated item data
 * @throws ZodError with validation details
 *
 * @example
 * ```typescript
 * const validated = validateItemDto({
 *   name: 'Water Bottle',
 *   category: 'water',
 *   quantity: 2,
 *   weight: 300,
 *   weightUnit: 'g',
 *   priority: 'high',
 *   status: 'owned'
 * })
 * await createItem(containerId, validated)
 * ```
 */
export function validateItemDto(data: unknown): ItemFormData {
  return itemSchema.parse(data)
}

/**
 * M6 FIX: Safe validation for container data
 *
 * Returns a result object instead of throwing errors.
 * Useful when you want to collect validation errors without stopping execution.
 *
 * @param data - Data to validate
 * @returns Validation result with success flag and data or errors
 *
 * @example
 * ```typescript
 * const result = safeValidateContainer(containerData)
 * if (result.success) {
 *   await createContainer(result.data)
 * } else {
 *   console.error('Validation failed:', result.errors)
 *   toast.error(result.errors.join(', '))
 * }
 * ```
 */
export function safeValidateContainer(data: unknown): ValidationResult<ContainerFormData> {
  const result = containerSchema.safeParse(data)
  if (result.success) {
    return { success: true, data: result.data }
  }
  return {
    success: false,
    errors: result.error.errors.map(e => `${e.path.join('.')}: ${e.message}`),
  }
}

/**
 * M6 FIX: Safe validation for item data
 *
 * Returns a result object instead of throwing errors.
 * Useful when you want to collect validation errors without stopping execution.
 *
 * @param data - Data to validate
 * @returns Validation result with success flag and data or errors
 *
 * @example
 * ```typescript
 * const result = safeValidateItem(itemData)
 * if (result.success) {
 *   await createItem(containerId, result.data)
 * } else {
 *   console.error('Validation failed:', result.errors)
 *   toast.error(result.errors.join(', '))
 * }
 * ```
 */
export function safeValidateItem(data: unknown): ValidationResult<ItemFormData> {
  const result = itemSchema.safeParse(data)
  if (result.success) {
    return { success: true, data: result.data }
  }
  return {
    success: false,
    errors: result.error.errors.map(e => `${e.path.join('.')}: ${e.message}`),
  }
}

