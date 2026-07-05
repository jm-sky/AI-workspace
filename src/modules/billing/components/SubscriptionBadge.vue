<script setup lang="ts">
import { Crown, Sparkles } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import { useSubscription } from '../composables/useSubscription'

const { t } = useI18n()
const { currentPlan, isGrandfathered, isLoadingSubscription } = useSubscription()

const badgeVariant = computed(() => {
  if (isGrandfathered.value) return 'premium'
  if (currentPlan.value === 'pro_plus') return 'premium'
  if (currentPlan.value === 'pro') return 'default'
  return 'secondary'
})

const planName = computed(() => {
  return t(`billing.plans.${currentPlan.value}.name`)
})

const showIcon = computed(() => {
  return isGrandfathered.value || currentPlan.value !== 'free'
})
</script>

<template>
  <Badge v-if="!isLoadingSubscription" :variant="badgeVariant" class="gap-1.5">
    <Crown v-if="isGrandfathered" class="size-3.5" />
    <Sparkles v-else-if="showIcon" class="size-3.5" />
    {{ planName }}
    <template v-if="isGrandfathered">
      ({{ t('billing.status.grandfathered') }})
    </template>
  </Badge>
</template>
