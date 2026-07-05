<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const { t } = useI18n()
</script>

<template>
  <Select v-bind="$attrs">
    <SelectTrigger>
      <SelectValue :placeholder="t('settings.preferences.preferredWeightUnit.placeholder')" />
    </SelectTrigger>
    <SelectContent>
      <SelectItem value="g">
        {{ t('settings.preferences.preferredWeightUnit.options.g') }}
      </SelectItem>
      <SelectItem value="kg">
        {{ t('settings.preferences.preferredWeightUnit.options.kg') }}
      </SelectItem>
      <SelectItem value="oz">
        {{ t('settings.preferences.preferredWeightUnit.options.oz') }}
      </SelectItem>
      <SelectItem value="lb">
        {{ t('settings.preferences.preferredWeightUnit.options.lb') }}
      </SelectItem>
      <SelectItem value="auto-g-kg">
        {{ t('settings.preferences.preferredWeightUnit.options.auto-g-kg') }}
      </SelectItem>
      <SelectItem value="auto-oz-lb">
        {{ t('settings.preferences.preferredWeightUnit.options.auto-oz-lb') }}
      </SelectItem>
    </SelectContent>
  </Select>
</template>

