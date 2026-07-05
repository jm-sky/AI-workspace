import { useI18n } from 'vue-i18n'
import type { TCataloguePriceTier } from '@/modules/gear/types/catalogue.types'

/**
 * Composable for translating price tier labels with fallback to qualities
 * Falls back to gear.item.qualities.{tier} if gear.catalogue.priceTiers.{tier} is not found
 */
export const usePriceTierLabel = () => {
  const { t } = useI18n()

  const getPriceTierLabel = (tier: TCataloguePriceTier | string): string => {
    const priceTierKey = `gear.catalogue.priceTiers.${tier}`
    const fallbackKey = `gear.item.qualities.${tier}`
    const translated = t(priceTierKey)
    // If translation returns the key itself, use fallback
    return translated === priceTierKey ? t(fallbackKey) : translated
  }

  return {
    getPriceTierLabel,
  }
}

