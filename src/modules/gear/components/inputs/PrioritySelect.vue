<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { TGearItemPriority } from '../../types/gear.types.v2'

const { t } = useI18n()

const modelValue = defineModel<TGearItemPriority>()

defineProps<{
  placeholder?: string
}>()

const priorities: TGearItemPriority[] = ['critical', 'high', 'medium', 'low']
</script>

<template>
  <Select v-model="modelValue">
    <SelectTrigger class="min-w-36">
      <SelectValue :placeholder="placeholder ?? t('gear.item.priority')" />
    </SelectTrigger>
    <SelectContent>
      <SelectItem v-for="priority in priorities" :key="priority" :value="priority">
        {{ t(`gear.item.priorities.${priority}`) }}
      </SelectItem>
    </SelectContent>
  </Select>
</template>
