<!--
  AI Premium Feature Alert Component
  Shows a premium feature notice for non-premium users
-->
<script setup lang="ts">
import { Crown, Key } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

const { t } = useI18n()

const props = defineProps<{
  title?: string
  description?: string
  showTokenOption?: boolean
}>()
</script>

<template>
  <Alert variant="premium">
    <Crown />
    <AlertTitle>
      {{ props.title ?? t('ai.premium.title') }}
    </AlertTitle>
    <AlertDescription class="space-y-2">
      <p>{{ props.description ?? t('ai.premium.description') }}</p>
      <p v-if="showTokenOption" class="flex items-center gap-2 text-sm">
        <Key class="size-4" />
        {{ t('ai.premium.ownTokenOption') }}
      </p>
    </AlertDescription>
  </Alert>
</template>
