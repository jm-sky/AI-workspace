<script setup lang="ts">
import { Check } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import type { BillingInterval, PlanFeatures } from '../types'
import { getTranslatedFeatures } from '../utils/planTranslations'

const { t } = useI18n()

const { plan, billingInterval, isCurrentPlan, onSelectPlan, isLoading } = defineProps<{
  plan: PlanFeatures
  billingInterval: BillingInterval
  isCurrentPlan?: boolean
  onSelectPlan?: () => void
  isLoading?: boolean
}>()

const monthlyPrice = computed(() => plan.price.monthly)
const annualMonthlyPrice = computed(() => plan.price.annualMonthly)
const annualPrice = computed(() => plan.price.annual)

const displayedPrice = computed(() =>
  billingInterval === 'annual' ? annualMonthlyPrice.value : monthlyPrice.value
)

const originalPrice = computed(() =>
  billingInterval === 'annual' ? monthlyPrice.value : null
)

const translatedFeatures = computed(() => getTranslatedFeatures(plan.tier, plan.features, t))
</script>

<template>
  <Card class="hover:shadow-lg hover:scale-101 hover:-translate-y-1 transition-all duration-300" :class="{ 'border-primary': plan.popular }">
    <CardHeader>
      <div class="flex items-center justify-between">
        <CardTitle>{{ plan.name }}</CardTitle>
        <div class="flex flex-col md:flex-row items-center gap-2">
          <Badge v-if="isCurrentPlan" variant="primary-outline">
            {{ t('billing.currentPlan') }}
          </Badge>
          <Badge v-if="plan.popular" variant="default">
            {{ t('billing.popular') }}
          </Badge>
        </div>
      </div>
      <CardDescription>
        <div class="mt-4 flex items-baseline gap-2">
          <span class="text-3xl font-bold">${{ displayedPrice }}</span>
          <span class="text-muted-foreground">{{ t('billing.perMonth') }}</span>
        </div>
        <div v-if="originalPrice" class="text-sm text-muted-foreground">
          <span class="line-through">${{ originalPrice }}{{ t('billing.perMonth') }}</span>
          <span class="ml-2 text-green-600">{{ t('billing.savePercent', { percent: 17 }) }}</span>
        </div>
        <div class="mt-1 text-sm text-muted-foreground">
          ${{ annualPrice }}{{ t('billing.perYear') }}
        </div>
      </CardDescription>
    </CardHeader>

    <CardContent>
      <ul class="space-y-2">
        <li v-for="(feature, index) in translatedFeatures" :key="index" class="flex items-start gap-2">
          <Check class="mt-0.5 size-4 shrink-0 text-green-600" />
          <span class="text-sm">{{ feature }}</span>
        </li>
      </ul>
    </CardContent>

    <CardFooter>
      <Button
        v-if="isCurrentPlan"
        variant="outline"
        class="w-full"
        disabled
      >
        {{ t('billing.currentPlan') }}
      </Button>
      <Button
        v-else-if="onSelectPlan"
        class="w-full"
        :disabled="isLoading"
        @click="onSelectPlan"
      >
        {{ t('billing.selectPlan', { plan: plan.name }) }}
      </Button>
    </CardFooter>
  </Card>
</template>
