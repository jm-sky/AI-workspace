<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { TGearItemQuality } from '../../types/gear.types.v2'

const { t } = useI18n()

const modelValue = defineModel<TGearItemQuality>()

defineProps<{
  placeholder?: string
}>()

const qualities: TGearItemQuality[] = ['low', 'medium', 'high']
</script>

<template>
  <Select v-model="modelValue">
    <SelectTrigger class="w-full min-w-36">
      <SelectValue :placeholder="placeholder ?? t('gear.item.quality')" />
    </SelectTrigger>
    <SelectContent>
      <SelectItem v-for="quality in qualities" :key="quality" :value="quality">
        {{ t(`gear.item.qualities.${quality}`) }}
      </SelectItem>
    </SelectContent>
  </Select>
</template>
