<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { IAdminSubscriptionStats } from '../types/admin.types'

const { stats } = defineProps<{
  stats: IAdminSubscriptionStats | undefined
}>()

const { t } = useI18n()

const totalRevenue = computed(() => {
  if (!stats) return 0
  return stats.monthlyRevenue + stats.annualRevenue
})

const formattedMonthlyRevenue = computed(() => {
  if (!stats) return '$0'
  return `$${stats.monthlyRevenue.toFixed(2)}`
})

const formattedAnnualRevenue = computed(() => {
  if (!stats) return '$0'
  return `$${stats.annualRevenue.toFixed(2)}`
})

const formattedTotalRevenue = computed(() => {
  return `$${totalRevenue.value.toFixed(2)}`
})
</script>

<template>
  <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
    <!-- Total Users -->
    <Card>
      <CardHeader class="pb-2">
        <CardTitle class="text-sm font-medium">
          {{ t('admin.subscriptions.stats.totalUsers', 'Total Users') }}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div class="text-2xl font-bold">
          {{ stats?.totalUsers ?? 0 }}
        </div>
      </CardContent>
    </Card>

    <!-- Active Subscriptions -->
    <Card>
      <CardHeader class="pb-2">
        <CardTitle class="text-sm font-medium">
          {{ t('admin.subscriptions.stats.activeSubscriptions', 'Active Subscriptions') }}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div class="text-2xl font-bold">
          {{ stats?.activeSubscriptions ?? 0 }}
        </div>
        <p v-if="stats" class="text-xs text-muted-foreground">
          {{ t('admin.subscriptions.stats.ofTotal', { count: stats.totalSubscriptions }, 'of {count} total') }}
        </p>
      </CardContent>
    </Card>

    <!-- Plan Distribution -->
    <Card>
      <CardHeader class="pb-2">
        <CardTitle class="text-sm font-medium">
          {{ t('admin.subscriptions.stats.planDistribution', 'Plan Distribution') }}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div class="space-y-1 text-sm">
          <div class="flex justify-between">
            <span class="text-muted-foreground">Free:</span>
            <span class="font-medium">{{ stats?.freeUsers ?? 0 }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-muted-foreground">Pro:</span>
            <span class="font-medium">{{ stats?.proUsers ?? 0 }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-muted-foreground">Pro Plus:</span>
            <span class="font-medium">{{ stats?.proPlusUsers ?? 0 }}</span>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Revenue -->
    <Card>
      <CardHeader class="pb-2">
        <CardTitle class="text-sm font-medium">
          {{ t('admin.subscriptions.stats.revenue', 'Revenue') }}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div class="text-2xl font-bold">
          {{ formattedTotalRevenue }}
        </div>
        <div class="mt-2 space-y-1 text-xs text-muted-foreground">
          <div class="flex justify-between">
            <span>{{ t('admin.subscriptions.stats.monthly', 'Monthly') }}:</span>
            <span>{{ formattedMonthlyRevenue }}</span>
          </div>
          <div class="flex justify-between">
            <span>{{ t('admin.subscriptions.stats.annual', 'Annual') }}:</span>
            <span>{{ formattedAnnualRevenue }}</span>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Grandfathered Users -->
    <Card v-if="stats && stats.grandfatheredUsers > 0">
      <CardHeader class="pb-2">
        <CardTitle class="text-sm font-medium">
          {{ t('admin.subscriptions.stats.grandfathered', 'Grandfathered Users') }}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div class="text-2xl font-bold">
          {{ stats.grandfatheredUsers }}
        </div>
        <p class="text-xs text-muted-foreground">
          {{ t('admin.subscriptions.stats.lifetimePro', 'Lifetime Pro access') }}
        </p>
      </CardContent>
    </Card>

    <!-- Past Due -->
    <Card v-if="stats && stats.pastDueSubscriptions > 0">
      <CardHeader class="pb-2">
        <CardTitle class="text-sm font-medium text-destructive">
          {{ t('admin.subscriptions.stats.pastDue', 'Past Due') }}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div class="text-2xl font-bold text-destructive">
          {{ stats.pastDueSubscriptions }}
        </div>
        <p class="text-xs text-muted-foreground">
          {{ t('admin.subscriptions.stats.requiresAttention', 'Requires attention') }}
        </p>
      </CardContent>
    </Card>
  </div>
</template>
