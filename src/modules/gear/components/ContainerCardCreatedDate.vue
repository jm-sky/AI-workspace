<script setup lang="ts">
import { formatDistanceToNow } from 'date-fns'
import { enUS, pl } from 'date-fns/locale'
import { CalendarPlus } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { smallDateTime } from '@/shared/utils/smallDateTime'
import type { SupportedLocale } from '@/shared/config/config'

const { createdAt } = defineProps<{
  createdAt: string
}>()

const { locale, t } = useI18n()

const dateFnsLocale = computed(() => {
  const currentLocale = locale.value as SupportedLocale
  return currentLocale === 'pl' ? pl : enUS
})

const timeAgo = computed(() => {
  return formatDistanceToNow(new Date(createdAt), {
    addSuffix: true,
    locale: dateFnsLocale.value,
  })
})

const formattedDateTime = computed(() => {
  return smallDateTime(createdAt)
})
</script>

<template>
  <div
    v-tooltip:bottom="`${t('common.created')}: ${formattedDateTime}`"
    class="flex items-center gap-1 text-xs text-muted-foreground"
  >
    <CalendarPlus class="size-3" />
    {{ timeAgo }}
  </div>
</template>
