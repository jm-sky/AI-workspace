<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { SUPPORTED_CURRENCIES } from '@/modules/gear/utils/currencyFormatter'

const { t } = useI18n()
</script>

<template>
  <Select v-bind="$attrs">
    <SelectTrigger>
      <SelectValue :placeholder="t('settings.preferences.defaultCurrency.placeholder')" />
    </SelectTrigger>
    <SelectContent>
      <SelectItem
        v-for="curr in SUPPORTED_CURRENCIES"
        :key="curr.value"
        :value="curr.value"
      >
        {{ curr.label }}
      </SelectItem>
    </SelectContent>
  </Select>
</template>

