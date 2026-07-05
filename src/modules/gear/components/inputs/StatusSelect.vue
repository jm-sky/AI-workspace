<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { TGearItemStatus } from '../../types/gear.types.v2'

const { t } = useI18n()

const modelValue = defineModel<TGearItemStatus>()

defineProps<{
  placeholder?: string
}>()

const statuses: TGearItemStatus[] = ['owned', 'missing', 'toBuy']
</script>

<template>
  <Select v-model="modelValue">
    <SelectTrigger class="min-w-36">
      <SelectValue :placeholder="placeholder ?? t('gear.item.status')" />
    </SelectTrigger>
    <SelectContent>
      <SelectItem v-for="status in statuses" :key="status" :value="status">
        {{ t(`gear.item.statuses.${status}`) }}
      </SelectItem>
    </SelectContent>
  </Select>
</template>
