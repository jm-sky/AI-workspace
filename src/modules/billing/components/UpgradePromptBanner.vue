<script setup lang="ts">
import { Sparkles, X } from 'lucide-vue-next'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Alert from '@/components/ui/alert/Alert.vue'
import AlertDescription from '@/components/ui/alert/AlertDescription.vue'
import AlertTitle from '@/components/ui/alert/AlertTitle.vue'
import { Button } from '@/components/ui/button'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import { useSubscription } from '../composables/useSubscription'
import { BillingRoutePaths } from '../routes'

const { t } = useI18n()
const { isFreeTier, isLoadingSubscription } = useSubscription()

// Local storage key for dismissed banner
const DISMISSED_KEY = 'upgrade-prompt-dismissed'
const isDismissed = ref(localStorage.getItem(DISMISSED_KEY) === 'true')

const dismissBanner = () => {
  isDismissed.value = true
  localStorage.setItem(DISMISSED_KEY, 'true')
}

// Show banner only if: not loading, is free tier, and not dismissed
const shouldShow = () => {
  return !isLoadingSubscription.value && isFreeTier.value && !isDismissed.value
}
</script>

<template>
  <Alert v-if="shouldShow()" class="border-violet-200 dark:border-violet-800 bg-linear-to-r from-violet-50 to-purple-50 dark:from-violet-950/30 dark:to-purple-950/30">
    <Sparkles class="size-5 text-violet-600 dark:text-violet-400" />
    <div class="flex flex-1 flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex-1">
        <AlertTitle class="text-violet-900 dark:text-violet-100">
          {{ t('billing.upgradeBanner.title', 'Unlock Premium Features') }}
        </AlertTitle>
        <AlertDescription class="text-violet-700 dark:text-violet-300">
          {{ t('billing.upgradeBanner.description', 'Upgrade to Pro for AI-powered recommendations, advanced features, and more storage.') }}
        </AlertDescription>
      </div>
      <div class="flex items-center gap-2">
        <ButtonLink
          size="sm"
          variant="default"
          class="shrink-0 bg-violet-600 hover:bg-violet-700 dark:bg-violet-600 dark:hover:bg-violet-700"
          :to="BillingRoutePaths.billing"
        >
          <Sparkles class="size-4" />
          {{ t('billing.upgradeBanner.button', 'View Plans') }}
        </ButtonLink>
        <Button
          size="sm"
          variant="ghost"
          class="shrink-0 text-violet-700 hover:text-violet-900 dark:text-violet-300 dark:hover:text-violet-100"
          @click="dismissBanner"
        >
          <X class="size-4" />
        </Button>
      </div>
    </div>
  </Alert>
</template>
