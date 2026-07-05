<script setup lang="ts">
import { ChevronDown, ChevronUp } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'

const { t } = useI18n()

const { canMoveUp, canMoveDown } = defineProps<{
  canMoveUp: boolean
  canMoveDown: boolean
}>()

const emit = defineEmits<{
  moveUp: []
  moveDown: []
}>()
</script>

<template>
  <div class="flex flex-col gap-0.5 shrink-0">
    <Button
      v-tooltip.bottom="t('gear.actions.moveUp')"
      variant="ghost"
      size="sm"
      class="size-5 p-0 h-4"
      :aria-label="t('gear.actions.moveUp')"
      :disabled="!canMoveUp"
      @click.stop="emit('moveUp')"
    >
      <ChevronUp :size="12" class="text-muted-foreground" />
    </Button>
    <Button
      v-tooltip.bottom="t('gear.actions.moveDown')"
      variant="ghost"
      size="sm"
      class="size-5 p-0 h-4"
      :aria-label="t('gear.actions.moveDown')"
      :disabled="!canMoveDown"
      @click.stop="emit('moveDown')"
    >
      <ChevronDown :size="12" class="text-muted-foreground" />
    </Button>
  </div>
</template>
