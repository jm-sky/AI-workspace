<script setup lang="ts">
import type { IGlobalCatalogueItem } from '../../types/catalogue.types'
import CategoryIcon from '../CategoryIcon.vue'

defineProps<{
  catalogueItem: IGlobalCatalogueItem
  selected: boolean
  isLinking: boolean
}>()

const emit = defineEmits<{
  select: [catalogueItemId: string]
}>()
</script>

<template>
  <button
    type="button"
    :class="[
      'w-full rounded-lg border p-3 text-left transition-colors',
      selected
        ? 'border-primary bg-primary/10'
        : 'border-border bg-background hover:bg-accent',
    ]"
    :disabled="isLinking"
    @click="emit('select', catalogueItem.id)"
  >
    <div class="flex items-start gap-3">
      <div
        :class="[
          'mt-0.5 size-4 shrink-0 rounded-full border-2 transition-colors',
          selected
            ? 'border-primary bg-primary'
            : 'border-muted-foreground',
        ]"
      >
        <div
          v-if="selected"
          class="size-full rounded-full bg-primary"
        />
      </div>
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <CategoryIcon :category="catalogueItem.category" :size="16" />
          <span class="font-medium">{{ catalogueItem.name }}</span>
        </div>
        <div v-if="catalogueItem.brand" class="mt-1 text-sm text-muted-foreground">
          {{ catalogueItem.brand }}
        </div>
        <div class="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
          <span>
            {{ catalogueItem.weight }} {{ catalogueItem.weightUnit }}
          </span>
          <span v-if="catalogueItem.brand && catalogueItem.model">
            •
          </span>
          <span v-if="catalogueItem.model">
            {{ catalogueItem.model }}
          </span>
        </div>
      </div>
      <div v-if="catalogueItem.primaryImageUrl" class="shrink-0">
        <img
          :src="catalogueItem.primaryImageUrl"
          :alt="catalogueItem.name"
          class="size-16 rounded object-cover"
        />
      </div>
    </div>
  </button>
</template>
