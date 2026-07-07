/**
 * App Initialization Utilities
 *
 * Helper functions for application initialization tasks such as:
 * - Setting HTML lang attribute based on i18n locale
 * - Other initialization utilities
 */

import type { I18n } from 'vue-i18n'

/**
 * Get current locale from i18n instance
 */
function getCurrentLocale(i18n: I18n): string {
  return typeof i18n.global.locale === 'string' ? i18n.global.locale : i18n.global.locale.value
}

/**
 * Set HTML lang attribute based on current i18n locale
 */
export function setHtmlLangAttribute(i18n: I18n): void {
  if (typeof document === 'undefined') {
    return
  }

  const currentLocale = getCurrentLocale(i18n)
  document.documentElement.setAttribute('lang', currentLocale)
}

/**
 * Optional async store/bootstrap hooks (reserved for future use).
 */
export async function initializeStores(): Promise<void> {
  // No-op — gear localStorage bootstrap removed with gear module
}
