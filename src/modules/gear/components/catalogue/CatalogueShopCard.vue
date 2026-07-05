<script setup lang="ts">
import { ExternalLink, ShoppingCart } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ICatalogueShop } from '../../types/catalogue.types'
import { formatCurrency } from '../../utils/currencyFormatter'

const { t } = useI18n()

const props = defineProps<{
  shop: ICatalogueShop
  itemName: string
  itemCreatedAt?: string
}>()

// Extract domain from URL with ellipsis if there's a path
const getUrlDisplay = (url: string): string => {
  try {
    const urlObj = new URL(url)
    const domain = urlObj.hostname.replace(/^www\./, '')
    const hasPath = urlObj.pathname !== '/' || urlObj.search || urlObj.hash
    return hasPath ? `${domain}/...` : domain
  } catch {
    return url
  }
}

const urlDisplay = computed<string>(() => getUrlDisplay(props.shop.url))

const displayName = computed<string>(() => {
  if (props.shop.variant) {
    return `${props.itemName} • ${props.shop.variant}`
  }
  return props.itemName
})

// Get price update date with fallback to item createdAt
const priceDate = computed<string | null>(() => {
  if (typeof props.shop.price !== 'number') {
    return null
  }
  const dateStr = props.shop.updatedAt ?? props.itemCreatedAt
  return dateStr ?? null
})

// Format date in Polish locale
const formattedPriceDate = computed<string | null>(() => {
  if (!priceDate.value) {
    return null
  }
  try {
    const date = new Date(priceDate.value)
    return date.toLocaleDateString('pl-PL', { day: '2-digit', month: '2-digit', year: 'numeric' })
  } catch {
    return null
  }
})
</script>

<template>
  <a
    :href="shop.url"
    target="_blank"
    rel="noopener noreferrer"
    class="flex flex-col items-start gap-1 rounded-md border p-4 hover:bg-muted hover:scale-102 hover:shadow-lg transition-all duration-300"
  >
    <div class="flex flex-row items-center justify-between gap-2 w-full">
      <div class="font-medium">
        {{ displayName }}
      </div>
      <ExternalLink class="size-4 shrink-0 text-muted-foreground" />
    </div>
    <div class="flex flex-row gap-2 items-center">
      <ShoppingCart class="size-4 shrink-0 text-muted-foreground" />
      <div class="truncate text-base font-medium">
        {{ urlDisplay }}
      </div>
    </div>
    <span v-if="typeof shop.price === 'number'" class="text-xs text-muted-foreground">
      {{ formatCurrency(shop.price, shop.currency ?? 'PLN') }}
    </span>
    <span v-if="formattedPriceDate" class="text-xs text-muted-foreground">
      {{ t('gear.catalogue.priceDate', { date: formattedPriceDate }) }}
    </span>
  </a>
</template>
