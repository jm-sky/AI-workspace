<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { useAi } from '@/modules/ai/composables/useAi'
import { useAiStore } from '@/modules/ai/store/useAiStore'
import { useUserStore } from '@/modules/user/store/useUserStore'

const { t } = useI18n()
const aiStore = useAiStore()
const userStore = useUserStore()
const { canUseAi } = useAi()

const monthlyUsage = computed(() => aiStore.monthlyUsage)
const hasOwnToken = computed(() => aiStore.hasOwnToken)

// Get features from user store
const userFeatures = computed(() => userStore.user?.features)

// Calculate limits based on features
const costLimit = computed(() => {
  // Use limit from features if available, otherwise fallback to aiStore
  if (userFeatures.value?.ai?.limit !== undefined) {
    return userFeatures.value.ai.limit
  }
  return monthlyUsage.value.costLimit
})

const progressPercentage = computed(() => {
  // Token limits are not used from features, keep existing logic
  if (!monthlyUsage.value.tokenLimit) return 0
  return Math.min((monthlyUsage.value.tokens / monthlyUsage.value.tokenLimit) * 100, 100)
})

const costProgressPercentage = computed(() => {
  const limit = costLimit.value
  if (!limit || limit === 0) return 0
  return Math.min((monthlyUsage.value.cost / limit) * 100, 100)
})

const progressColorClass = computed(() => {
  const percentage = progressPercentage.value
  if (percentage >= 90) return '[&>div]:bg-red-500'
  if (percentage >= 70) return '[&>div]:bg-yellow-500'
  return '[&>div]:bg-green-500'
})

const costProgressColorClass = computed(() => {
  const percentage = costProgressPercentage.value
  if (percentage >= 90) return '[&>div]:bg-red-500'
  if (percentage >= 70) return '[&>div]:bg-yellow-500'
  return '[&>div]:bg-green-500'
})
</script>

<template>
  <div class="space-y-4" :class="{ 'opacity-50 pointer-events-none': !canUseAi }">
    <div>
      <Label>
        {{ t('gear.settings.ai.usage.label') }}
      </Label>
      <p class="text-sm text-muted-foreground">
        {{ t('gear.settings.ai.usage.subtitle') }}
      </p>
    </div>

    <!-- Token Usage -->
    <div class="space-y-2">
      <div class="flex items-center justify-between text-sm">
        <span class="text-muted-foreground">{{ t('gear.settings.ai.usage.tokens') }}</span>
        <span class="font-medium">
          {{ monthlyUsage.tokens.toLocaleString() }}
          <span v-if="!canUseAi" class="text-muted-foreground">
            ({{ t('gear.settings.ai.usage.unavailable') }})
          </span>
          <span v-else-if="monthlyUsage.tokenLimit">
            / {{ monthlyUsage.tokenLimit.toLocaleString() }}
          </span>
          <span v-else class="text-muted-foreground">
            ({{ t('gear.settings.ai.usage.unlimited') }})
          </span>
        </span>
      </div>
      <Progress
        v-if="monthlyUsage.tokenLimit"
        :model-value="progressPercentage"
        :class="progressColorClass"
      />
      <div v-else class="h-2 w-full rounded-full bg-green-500/20" />
    </div>

    <!-- Cost Usage -->
    <div class="space-y-2">
      <div class="flex items-center justify-between text-sm">
        <span class="text-muted-foreground">{{ t('gear.settings.ai.usage.cost') }}</span>
        <span class="font-medium">
          ${{ monthlyUsage.cost.toFixed(4) }}
          <span v-if="!canUseAi" class="text-muted-foreground">
            ({{ t('gear.settings.ai.usage.unavailable') }})
          </span>
          <span v-else-if="costLimit && costLimit > 0">
            / ${{ costLimit.toFixed(4) }}
          </span>
          <span v-else-if="costLimit === 0" class="text-muted-foreground">
            ({{ t('gear.settings.ai.usage.noLimit') }})
          </span>
          <span v-else class="text-muted-foreground">
            ({{ t('gear.settings.ai.usage.unlimited') }})
          </span>
        </span>
      </div>
      <Progress
        v-if="costLimit && costLimit > 0"
        :model-value="costProgressPercentage"
        :class="costProgressColorClass"
      />
      <div v-else-if="costLimit === 0" class="h-2 w-full rounded-full bg-red-500/20" />
      <div v-else class="h-2 w-full rounded-full bg-green-500/20" />
    </div>

    <p v-if="hasOwnToken" class="text-xs text-muted-foreground">
      {{ t('gear.settings.ai.usage.ownTokenNote') }}
    </p>
    <p v-else class="text-xs text-muted-foreground">
      {{ t('gear.settings.ai.usage.systemTokenNote') }}
    </p>
  </div>
</template>
