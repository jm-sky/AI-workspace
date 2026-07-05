<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { IItemWithContainerId } from '../../types/shopping.types'
import DeletedItemCard from './DeletedItemCard.vue'

const { t } = useI18n()

const { deletedItems } = defineProps<{
  deletedItems: IItemWithContainerId[]
}>()

const emit = defineEmits<{
  restore: [item: IItemWithContainerId]
}>()
</script>

<template>
  <div
    v-if="deletedItems.length > 0"
    class="space-y-4"
  >
    <h2 class="text-xl font-semibold text-muted-foreground">
      {{ t('gear.shopping.deletedItems', 'Deleted Items') }}
    </h2>

    <div class="space-y-2">
      <DeletedItemCard
        v-for="item in deletedItems"
        :key="item.id"
        :item="item"
        @restore="emit('restore', item)"
      />
    </div>
  </div>
</template>
