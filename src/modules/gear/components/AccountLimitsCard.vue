<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { Package, Shield } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { limitsApiService } from '../services/limitsApiService'

const { t } = useI18n()

const { data: limits, isLoading } = useQuery({
  queryKey: ['user-limits'],
  queryFn: () => limitsApiService.getUserLimits(),
  staleTime: 5 * 60 * 1000, // 5 minutes
})

const getProgressColor = (percentage: number): string => {
  if (percentage >= 90) return '[&>div]:bg-red-500'
  if (percentage >= 75) return '[&>div]:bg-yellow-500'
  return '[&>div]:bg-green-500'
}

const tierLabel = computed(() => {
  if (!limits.value) return ''
  const tier = limits.value.tier
  if (tier === 'pro') return t('gear.settings.accountLimits.tier.pro', 'Pro')
  if (tier === 'pro_plus') return t('gear.settings.accountLimits.tier.proPlus', 'Pro Plus')
  return t('gear.settings.accountLimits.tier.free', 'Free')
})

const tierVariant = computed(() => {
  if (!limits.value) return 'secondary'
  const tier = limits.value.tier
  if (tier === 'pro' || tier === 'pro_plus') return 'default'
  return 'secondary'
})
</script>

<template>
  <Card>
    <CardHeader>
      <div class="flex items-center gap-2">
        <Shield :size="20" />
        <CardTitle>{{ t('gear.settings.accountLimits.title', 'Account Limits') }}</CardTitle>
      </div>
      <CardDescription>
        {{ t('gear.settings.accountLimits.description', 'Your account limits and current usage') }}
      </CardDescription>
    </CardHeader>
    <CardContent v-if="limits && !isLoading" class="space-y-6">
      <!-- Tier Badge -->
      <div class="flex items-center gap-2">
        <span class="text-sm text-muted-foreground">
          {{ t('gear.settings.accountLimits.plan', 'Plan') }}:
        </span>
        <Badge :variant="tierVariant">
          {{ tierLabel }}
        </Badge>
      </div>

      <!-- Items Limit -->
      <div class="space-y-2">
        <div class="flex items-center justify-between text-sm">
          <div class="flex items-center gap-2">
            <Package :size="16" class="text-muted-foreground" />
            <span class="font-medium">
              {{ t('gear.settings.accountLimits.items', 'Items') }}
            </span>
          </div>
          <span class="font-medium">
            {{ limits.usage.items.toLocaleString() }}
            <span class="text-muted-foreground">
              / {{ limits.limits.items.toLocaleString() }}
            </span>
          </span>
        </div>
        <Progress
          :model-value="limits.percentage.items"
          :class="getProgressColor(limits.percentage.items)"
        />
        <p class="text-xs text-muted-foreground">
          {{ Math.round(limits.percentage.items) }}% {{ t('gear.settings.accountLimits.used', 'used') }}
        </p>
      </div>

      <!-- Containers Limit -->
      <div class="space-y-2">
        <div class="flex items-center justify-between text-sm">
          <div class="flex items-center gap-2">
            <Package :size="16" class="text-muted-foreground" />
            <span class="font-medium">
              {{ t('gear.settings.accountLimits.containers', 'Containers') }}
            </span>
          </div>
          <span class="font-medium">
            {{ limits.usage.containers.toLocaleString() }}
            <span class="text-muted-foreground">
              / {{ limits.limits.containers.toLocaleString() }}
            </span>
          </span>
        </div>
        <Progress
          :model-value="limits.percentage.containers"
          :class="getProgressColor(limits.percentage.containers)"
        />
        <p class="text-xs text-muted-foreground">
          {{ Math.round(limits.percentage.containers) }}% {{ t('gear.settings.accountLimits.used', 'used') }}
        </p>
      </div>

      <!-- Upgrade Prompt -->
      <div
        v-if="limits.percentage.items >= 80 || limits.percentage.containers >= 80"
        class="rounded-md border border-yellow-500/50 bg-yellow-500/10 p-3"
      >
        <p class="text-sm text-yellow-700 dark:text-yellow-400">
          {{ t('gear.settings.accountLimits.upgradePrompt', 'You are approaching your account limits. Consider upgrading to Pro for more storage.') }}
        </p>
      </div>
    </CardContent>
    <CardContent v-else-if="isLoading" class="py-8 text-center text-sm text-muted-foreground">
      {{ t('common.loading', 'Loading...') }}
    </CardContent>
  </Card>
</template>

