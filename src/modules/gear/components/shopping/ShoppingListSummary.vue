<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { IItemWithContainerId } from '../../types/shopping.types'
import { formatCurrency } from '../../utils/currencyFormatter'

const props = defineProps<{
  shoppingList: IItemWithContainerId[]
  totalPriceByCurrency: Record<string, number>
}>()

const { t } = useI18n()

const totalItemsCount = computed(() => {
  return props.shoppingList.reduce((sum, item) => sum + item.quantity, 0)
})
</script>

<template>
  <div
    v-if="shoppingList.length > 0"
    class="p-4 border rounded-lg bg-primary/5"
  >
    <div class="flex items-center justify-between">
      <div>
        <h3 class="font-semibold">
          {{ t('gear.shopping.summary', 'Summary') }}
        </h3>
        <p class="text-sm text-muted-foreground">
          {{ t('gear.shopping.itemsCount', { count: shoppingList.length }) }}
          ({{ t('gear.shopping.totalQuantity', { count: totalItemsCount }) }})
          <span v-if="Object.keys(totalPriceByCurrency).length > 0">
            -
            <span
              v-for="(amount, currency) in totalPriceByCurrency"
              :key="currency"
              class="ml-1"
            >
              {{ formatCurrency(amount, currency) }}
            </span>
          </span>
        </p>
      </div>
    </div>
  </div>
</template>
