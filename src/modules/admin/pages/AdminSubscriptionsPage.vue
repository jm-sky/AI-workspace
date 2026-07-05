<script setup lang="ts">
import { CreditCard, Crown, MoreHorizontal, Shield, User, X } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import DataTable from '@/components/data-table/DataTable.vue'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import Button from '@/components/ui/button/Button.vue'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import TableEmptyDecorated from '@/components/ui/table/TableEmptyDecorated.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { IAdminSubscription, IAdminSubscriptionStats } from '../types/admin.types'
import SubscriptionStatsCard from '../components/SubscriptionStatsCard.vue'
import { adminApiService } from '../services/adminApiService'
import type { ColumnDef } from '@tanstack/vue-table'

const { t } = useI18n()
const { handleError } = useHandleError()

const subscriptions = ref<IAdminSubscription[]>([])
const stats = ref<IAdminSubscriptionStats>()
const loading = ref(false)

async function loadData() {
  loading.value = true
  try {
    const [subs, statsData] = await Promise.all([
      adminApiService.getSubscriptions(0, 1000),
      adminApiService.getSubscriptionStats(),
    ])
    subscriptions.value = subs
    stats.value = statsData
  } catch (error) {
    console.error('Failed to load subscriptions:', error)
    handleError(error, { fallbackMessage: t('admin.subscriptions.loadError', 'Failed to load subscriptions') })
  } finally {
    loading.value = false
  }
}

async function updateSubscriptionPlan(subscription: IAdminSubscription, newPlan: 'free' | 'pro' | 'pro_plus') {
  const planName = t(`admin.subscriptions.plans.${newPlan}`, newPlan)

  if (!confirm(t('admin.subscriptions.changePlan.confirm', { plan: planName }, `Are you sure you want to change plan to ${planName}?`))) {
    return
  }

  try {
    await adminApiService.updateSubscription(subscription.id, {
      planTier: newPlan,
      reason: `Admin changed plan to ${newPlan}`,
    })
    toast.success(t('admin.subscriptions.changePlan.success', { plan: planName }, `Plan changed to ${planName}`))
    await loadData()
  } catch (error) {
    console.error('Failed to update subscription:', error)
    handleError(error, { fallbackMessage: t('admin.subscriptions.changePlan.error', 'Failed to change plan') })
  }
}

async function toggleGrandfathered(subscription: IAdminSubscription) {
  const action = subscription.isGrandfathered
    ? t('admin.subscriptions.grandfathered.remove', 'remove grandfathered status')
    : t('admin.subscriptions.grandfathered.add', 'grant grandfathered status')

  if (!confirm(t('admin.subscriptions.grandfathered.confirm', { action }, `Are you sure you want to ${action}?`))) {
    return
  }

  try {
    await adminApiService.updateSubscription(subscription.id, {
      isGrandfathered: !subscription.isGrandfathered,
      reason: subscription.isGrandfathered
        ? 'Admin removed grandfathered status'
        : 'Admin granted grandfathered status',
    })
    toast.success(t('admin.subscriptions.grandfathered.success', 'Grandfathered status updated'))
    await loadData()
  } catch (error) {
    console.error('Failed to update grandfathered status:', error)
    handleError(error, { fallbackMessage: t('admin.subscriptions.grandfathered.error', 'Failed to update status') })
  }
}

async function cancelSubscription(subscription: IAdminSubscription) {
  const planName = t(`admin.subscriptions.plans.${subscription.planTier}`, subscription.planTier)

  if (
    !confirm(
      t(
        'admin.subscriptions.cancel.confirm',
        { plan: planName },
        `Are you sure you want to cancel ${planName} subscription? This will immediately cancel the subscription, downgrade to Free, and cancel in Stripe if applicable.`,
      ),
    )
  ) {
    return
  }

  if (!subscription.id) {
    handleError(new Error('Subscription ID is missing'), { fallbackMessage: t('admin.subscriptions.cancel.error', 'Failed to cancel subscription') })
    return
  }

  try {
    await adminApiService.cancelSubscription(subscription.id, `Admin canceled ${planName} subscription`)
    toast.success(
      t('admin.subscriptions.cancel.success', { plan: planName }, `${planName} subscription canceled successfully`),
    )
    await loadData()
  } catch (error) {
    console.error('Failed to cancel subscription:', error)
    handleError(error, { fallbackMessage: t('admin.subscriptions.cancel.error', 'Failed to cancel subscription') })
  }
}

const columns = computed<ColumnDef<IAdminSubscription>[]>(() => [
  {
    id: 'user',
    accessorKey: 'userName',
    header: () => t('admin.subscriptions.columns.user', 'User'),
    enableSorting: true,
  },
  {
    id: 'email',
    accessorKey: 'userEmail',
    header: () => t('admin.subscriptions.columns.email', 'Email'),
    enableSorting: true,
  },
  {
    id: 'planTier',
    accessorKey: 'planTier',
    header: () => t('admin.subscriptions.columns.plan', 'Plan'),
    enableSorting: true,
  },
  {
    id: 'billingInterval',
    accessorKey: 'billingInterval',
    header: () => t('admin.subscriptions.columns.billing', 'Billing'),
    enableSorting: true,
  },
  {
    id: 'status',
    accessorKey: 'status',
    header: () => t('admin.subscriptions.columns.status', 'Status'),
    enableSorting: true,
  },
  {
    id: 'grandfathered',
    accessorKey: 'isGrandfathered',
    header: () => t('admin.subscriptions.columns.grandfathered', 'Grandfathered'),
    enableSorting: true,
  },
  {
    id: 'actions',
    header: () => t('admin.subscriptions.columns.actions', 'Actions'),
    enableSorting: false,
    meta: {
      pinned: 'right',
    },
  },
])

const globalFilterFn = (row: IAdminSubscription, filterValue: string) => {
  const query = filterValue.toLowerCase()
  return (
    row.userName?.toLowerCase().includes(query) ||
    row.userEmail?.toLowerCase().includes(query) ||
    row.planTier.toLowerCase().includes(query) ||
    row.status.toLowerCase().includes(query)
  )
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <AuthenticatedLayout>
    <div class="w-full max-w-full space-y-6">
      <!-- Header -->
      <CommonPageHeader
        :icon="CreditCard"
        :label="t('admin.subscriptions.title', 'Subscription Management')"
        :description="t('admin.subscriptions.subtitle', 'Manage user subscriptions and billing')"
      />

      <!-- Stats Cards -->
      <SubscriptionStatsCard :stats />

      <!-- Table -->
      <DataTable
        :columns
        :data="subscriptions"
        :enable-filtering="true"
        :enable-pagination="true"
        :enable-sorting="true"
        :global-filter-fn
        :initial-page-size="20"
        :loading
        :search-placeholder="t('admin.subscriptions.search', 'Search subscriptions...')"
      >
        <template #user="{ row }">
          <div class="flex items-center gap-2">
            <div
              class="flex size-8 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary"
            >
              {{ row.original.userName?.charAt(0).toUpperCase() ?? '?' }}
            </div>
            <span class="font-medium">{{ row.original.userName ?? 'Unknown' }}</span>
          </div>
        </template>

        <template #email="{ row }">
          <span class="text-muted-foreground">{{ row.original.userEmail ?? 'N/A' }}</span>
        </template>

        <template #planTier="{ row }">
          <Badge
            :variant="row.original.planTier === 'pro_plus' ? 'default' : row.original.planTier === 'pro' ? 'secondary' : 'outline'"
          >
            {{ t(`admin.subscriptions.plans.${row.original.planTier}`, row.original.planTier) }}
          </Badge>
        </template>

        <template #billingInterval="{ row }">
          <span v-if="row.original.billingInterval" class="text-sm text-muted-foreground">
            {{ t(`admin.subscriptions.billing.${row.original.billingInterval}`, row.original.billingInterval) }}
          </span>
          <span v-else class="text-sm text-muted-foreground">—</span>
        </template>

        <template #status="{ row }">
          <Badge
            :variant="row.original.status === 'active' ? 'default' : row.original.status === 'past_due' ? 'destructive' : 'secondary'"
          >
            {{ t(`admin.subscriptions.status.${row.original.status}`, row.original.status) }}
          </Badge>
        </template>

        <template #grandfathered="{ row }">
          <Crown v-if="row.original.isGrandfathered" class="size-5 text-yellow-500" />
          <span v-else class="text-sm text-muted-foreground">—</span>
        </template>

        <template #actions="{ row }">
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button size="sm" variant="ghost">
                <MoreHorizontal class="size-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <!-- Change to Free -->
              <DropdownMenuItem
                :disabled="row.original.planTier === 'free'"
                @click="updateSubscriptionPlan(row.original, 'free')"
              >
                <User class="size-4" />
                <span>{{ t('admin.subscriptions.changeTo.free', 'Change to Free') }}</span>
              </DropdownMenuItem>
              <!-- Change to Pro -->
              <DropdownMenuItem
                :disabled="row.original.planTier === 'pro'"
                @click="updateSubscriptionPlan(row.original, 'pro')"
              >
                <Shield class="size-4" />
                <span>{{ t('admin.subscriptions.changeTo.pro', 'Change to Pro') }}</span>
              </DropdownMenuItem>
              <!-- Change to Pro Plus -->
              <DropdownMenuItem
                :disabled="row.original.planTier === 'pro_plus'"
                @click="updateSubscriptionPlan(row.original, 'pro_plus')"
              >
                <CreditCard class="size-4" />
                <span>{{ t('admin.subscriptions.changeTo.pro_plus', 'Change to Pro Plus') }}</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <!-- Cancel Subscription -->
              <DropdownMenuItem
                :disabled="row.original.planTier === 'free' || row.original.status === 'canceled'"
                @click="cancelSubscription(row.original)"
              >
                <X class="size-4" />
                <span>{{ t('admin.subscriptions.cancel.action', 'Cancel Subscription') }}</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <!-- Toggle Grandfathered -->
              <DropdownMenuItem @click="toggleGrandfathered(row.original)">
                <Crown class="size-4" />
                <span>{{
                  row.original.isGrandfathered
                    ? t('admin.subscriptions.removeGrandfathered', 'Remove Grandfathered')
                    : t('admin.subscriptions.makeGrandfathered', 'Make Grandfathered')
                }}</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </template>

        <template #empty>
          <TableEmptyDecorated
            :colspan="columns.length"
            :description="t('admin.subscriptions.emptyDescription', 'No subscriptions match your search.')"
            :title="t('admin.subscriptions.empty', 'No subscriptions found')"
          />
        </template>
      </DataTable>
    </div>
  </AuthenticatedLayout>
</template>
