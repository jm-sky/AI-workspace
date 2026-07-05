/**
 * Helper functions for gear module
 */

/**
 * Check if a value is set (not undefined and not null)
 * Useful for checking optional fields that can be undefined or null
 * @param value - Value to check
 * @returns True if value is set (not undefined and not null)
 */
export function isSet<T>(value: T | undefined | null): value is T {
  return value !== undefined && value !== null
}

