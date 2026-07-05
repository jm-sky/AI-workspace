<script setup lang="ts">
import { AlertCircle, Check, Crown } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { useSubscription } from '../composables/useSubscription'
import { PLAN_FEATURES } from '../types'
import { getTranslatedFeatures, getTranslatedPlanName } from '../utils/planTranslations'

const { t } = useI18n()

const {
  subscription,
  currentPlan,
  currentPlanFeatures,
  isGrandfathered,
  isCanceled,
  isPastDue,
  cancelAtPeriodEnd,
  isPaidTier,
  openBillingPortal,
  isOpeningPortal,
} = useSubscription()

const statusBadgeVariant = computed(() => {
  if (isPastDue.value) return 'destructive'
  if (isCanceled.value || cancelAtPeriodEnd.value) return 'secondary'
  return 'default'
})

const statusText = computed(() => {
  if (isPastDue.value) return t('billing.status.pastDue')
  if (isCanceled.value) return t('billing.status.canceled')
  if (cancelAtPeriodEnd.value) return t('billing.status.canceling')
  if (isGrandfathered.value) return t('billing.status.grandfathered')
  return t('billing.status.active')
})

const formatDate = (dateString: string | null) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const planFeatures = computed(() => {
  const features = PLAN_FEATURES[currentPlan.value]?.features || []
  return getTranslatedFeatures(currentPlan.value, features, t)
})

const translatedPlanName = computed(() => getTranslatedPlanName(currentPlan.value, t))
</script>

<template>
  <Card>
    <CardHeader>
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <CardTitle class="text-2xl">
            {{ translatedPlanName }}
          </CardTitle>
          <Crown v-if="isGrandfathered" class="size-5 text-yellow-500" />
        </div>
        <Badge :variant="statusBadgeVariant">
          {{ statusText }}
        </Badge>
      </div>
      <CardDescription v-if="currentPlanFeatures">
        <span v-if="subscription?.billingInterval === 'monthly'">
          ${{ currentPlanFeatures.price.monthly }}{{ t('billing.perMonth') }}
        </span>
        <span v-else-if="subscription?.billingInterval === 'annual'">
          ${{ currentPlanFeatures.price.annualMonthly }}{{ t('billing.perMonth') }} {{ t('billing.billedAnnually') }}
        </span>
        <span v-else>{{ translatedPlanName }}</span>
      </CardDescription>
    </CardHeader>

    <CardContent class="space-y-4">
      <div class="space-y-2">
        <h3 class="text-sm font-medium">
          {{ t('billing.features') }}
        </h3>
        <ul class="space-y-1">
          <li v-for="(feature, index) in planFeatures" :key="index" class="flex items-center gap-2 text-sm">
            <Check class="size-4 text-green-600" />
            <span>{{ feature }}</span>
          </li>
        </ul>
      </div>

      <div v-if="isPaidTier && subscription" class="space-y-2">
        <h3 class="text-sm font-medium">
          {{ t('billing.billingInfo') }}
        </h3>
        <div class="space-y-1 text-sm text-muted-foreground">
          <div class="flex justify-between">
            <span>{{ t('billing.currentPeriodLabel') }}</span>
            <span>{{ formatDate(subscription.currentPeriodStart) }} - {{ formatDate(subscription.currentPeriodEnd) }}</span>
          </div>
          <div v-if="cancelAtPeriodEnd" class="flex items-center gap-2 text-amber-600">
            <AlertCircle class="size-4" />
            <span>{{ t('billing.subscriptionWillCancel') }} {{ formatDate(subscription.currentPeriodEnd) }}</span>
          </div>
        </div>
      </div>

      <div v-if="isGrandfathered" class="rounded-lg bg-yellow-50 p-3 text-sm">
        <div class="flex items-center gap-2 font-medium text-yellow-800">
          <Crown class="size-4" />
          <span>{{ t('billing.grandfathered.title') }}</span>
        </div>
        <p class="mt-1 text-yellow-700">
          {{ t('billing.grandfathered.message') }}
        </p>
      </div>
    </CardContent>

    <CardFooter v-if="isPaidTier && !isGrandfathered">
      <Button
        variant="outline"
        class="w-full"
        :disabled="isOpeningPortal"
        @click="openBillingPortal"
      >
        {{ t('billing.manageSubscription') }}
      </Button>
    </CardFooter>
  </Card>
</template>
