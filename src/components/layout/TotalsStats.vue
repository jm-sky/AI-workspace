<script setup lang="ts">
import { Package, PackageCheck, Users } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import { useGearStoreV2 } from '@/modules/gear/store/useGearStoreV2'
import { statsService } from '@/modules/stats/services/statsService'

const { t } = useI18n()
const gearStore = useGearStoreV2()
const authStore = useAuthStore()

// Stats state
const totalUsers = ref(0)
const newUsersThisMonth = ref(0)
const totalContainers = ref(0)
const newContainersThisMonth = ref(0)
const totalItems = ref(0)
const newItemsThisMonth = ref(0)
const loading = ref(true)

// Fetch stats using statsService
const fetchStats = async () => {
  // Load containers from storage if not authenticated (needed for local stats)
  if (!authStore.isAuthenticated) {
    gearStore.loadFromStorage()
  }

  try {
    const service = statsService()
    const stats = await service.getAllStats()

    totalUsers.value = stats.users.total
    newUsersThisMonth.value = stats.users.newThisMonth
    totalContainers.value = stats.containers.total
    newContainersThisMonth.value = stats.containers.newThisMonth
    totalItems.value = stats.items.total
    newItemsThisMonth.value = stats.items.newThisMonth
  } catch (error) {
    console.error('Error fetching stats:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <!-- Total Users -->
    <div class="bg-card/50 backdrop-blur-sm rounded-lg border p-6 text-center">
      <div class="flex justify-center mb-3">
        <div class="rounded-full bg-primary/10 p-3">
          <Users class="size-6 text-primary" />
        </div>
      </div>
      <div class="text-3xl font-bold text-primary mb-1">
        {{ loading ? '...' : totalUsers.toLocaleString() }}
      </div>
      <div class="text-sm text-muted-foreground mb-2">
        {{ t('landing.stats.totalUsers', 'Total Users') }}
      </div>
      <div v-if="!loading && newUsersThisMonth > 0" class="text-xs text-muted-foreground">
        +{{ newUsersThisMonth }} {{ t('landing.stats.newThisMonth', 'this month') }}
      </div>
    </div>

    <!-- Total Containers -->
    <div class="bg-card/50 backdrop-blur-sm rounded-lg border p-6 text-center">
      <div class="flex justify-center mb-3">
        <div class="rounded-full bg-primary/10 p-3">
          <Package class="size-6 text-primary" />
        </div>
      </div>
      <div class="text-3xl font-bold text-primary mb-1">
        {{ loading ? '...' : totalContainers.toLocaleString() }}
      </div>
      <div class="text-sm text-muted-foreground mb-2">
        {{ t('landing.stats.totalContainers', 'Total Containers') }}
      </div>
      <div v-if="!loading && newContainersThisMonth > 0" class="text-xs text-muted-foreground">
        +{{ newContainersThisMonth }} {{ t('landing.stats.newThisMonth', 'this month') }}
      </div>
    </div>

    <!-- Total Items -->
    <div class="bg-card/50 backdrop-blur-sm rounded-lg border p-6 text-center">
      <div class="flex justify-center mb-3">
        <div class="rounded-full bg-primary/10 p-3">
          <PackageCheck class="size-6 text-primary" />
        </div>
      </div>
      <div class="text-3xl font-bold text-primary mb-1">
        {{ loading ? '...' : totalItems.toLocaleString() }}
      </div>
      <div class="text-sm text-muted-foreground mb-2">
        {{ t('landing.stats.totalItems', 'Total Items') }}
      </div>
      <div v-if="!loading && newItemsThisMonth > 0" class="text-xs text-muted-foreground">
        +{{ newItemsThisMonth }} {{ t('landing.stats.newThisMonth', 'this month') }}
      </div>
    </div>
  </div>
</template>
