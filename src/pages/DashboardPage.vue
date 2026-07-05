<script setup lang="ts">
import { BackpackIcon, Globe, LogIn, Plus, UserPlus } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import WelcomeQuickActions from '@/components/layout/WelcomeQuickActions.vue'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { AuthRoutePaths } from '@/modules/auth/config/routes'
import UpgradePromptBanner from '@/modules/billing/components/UpgradePromptBanner.vue'
import DashboardContainerCard from '@/modules/gear/components/dashboard/DashboardContainerCard.vue'
import GenerateExampleGearButton from '@/modules/gear/components/GenerateExampleGearButton.vue'
import { useGearV2 } from '@/modules/gear/composables/useGearV2'
import { GearRoutePath } from '@/modules/gear/routes'
import { useGearStoreV2 } from '@/modules/gear/store/useGearStoreV2'
import { READINESS_EXCELLENT_THRESHOLD } from '@/modules/gear/utils/constants'
import { config } from '@/shared/config/config'
import { apiClient } from '@/shared/services/apiClient'
import type { IGearItemV2 } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()
const store = useGearStoreV2()
const { getItems } = useGearV2()
const { isAuthenticated } = useAuth()

const containers = computed(() => store.getAllContainers)
const itemsCount = computed(() => store.getAllItems.filter(i => i.itemType === 'item').length)

const publicContainersCount = ref<number>(0)
const isLoadingPublicContainers = ref(false)

// Load gear from the active V2 service (API or localStorage) on mount
onMounted(async () => {
  try {
    await getItems()
  } catch (error) {
    console.error('Failed to load gear:', error)
  }

  // Load public containers count
  if (config.backend.enabled) {
    try {
      isLoadingPublicContainers.value = true
      const response = await apiClient.get<IGearItemV2[]>('/gear/public/containers')
      publicContainersCount.value = response.data.length
    } catch (error) {
      console.error('Failed to load public containers count:', error)
    } finally {
      isLoadingPublicContainers.value = false
    }
  }
})

const readyContainersCount = computed(() => {
  return containers.value.filter(c => {
    const items = store.getChildrenOfItem(c.id).filter(i => i.itemType === 'item')
    const totalItems = items.length
    if (totalItems === 0) return false
    const ownedItems = items.filter(i => i.status === 'owned').length
    return ownedItems / totalItems * 100 >= READINESS_EXCELLENT_THRESHOLD
  }).length
})
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-8">
      <!-- Upgrade Prompt Banner (only for authenticated FREE users) -->
      <UpgradePromptBanner v-if="isAuthenticated && config.backend.enabled" />

      <!-- Header -->
      <div class="text-center space-y-4">
        <div class="flex justify-center">
          <div class="rounded-full bg-primary/10 p-6">
            <BackpackIcon class="size-16 text-primary" />
          </div>
        </div>
        <h1 class="text-4xl font-bold">
          {{ t('gear.page.title', 'Gear Stack') }}
        </h1>
        <p class="text-muted-foreground text-lg max-w-2xl mx-auto">
          {{ t('gear.page.subtitle', 'Organize and manage your gear collections') }}
        </p>
      </div>

      <!-- Quick Stats -->
      <div v-if="containers.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <DashboardContainerCard
          :to="GearRoutePath.Containers"
          :count="containers.length"
          :label="t('gear.page.containers', 'Containers')"
        />
        <DashboardContainerCard
          :to="GearRoutePath.AllItems"
          :count="itemsCount"
          :label="t('gear.page.items', 'Items')"
        />
        <DashboardContainerCard
          :to="GearRoutePath.Containers"
          :count="readyContainersCount"
          :label="t('gear.page.readyContainers', 'Ready Containers')"
        />
        <DashboardContainerCard
          v-if="config.backend.enabled"
          :to="GearRoutePath.PublicContainers"
          :count="isLoadingPublicContainers ? '...' : publicContainersCount"
          :label="t('gear.publicContainers.navTitle', 'Public Browser')"
          :icon="Globe"
        />
      </div>

      <!-- Actions -->
      <div class="flex flex-col items-center gap-4">
        <div v-if="containers.length > 0" class="flex flex-col items-center gap-4 w-full max-w-md">
          <ButtonLink size="lg" class="w-full" :to="GearRoutePath.Containers">
            <BackpackIcon class="size-5" />
            {{ t('gear.page.viewContainers', 'View Containers') }}
          </ButtonLink>
          <!-- Row 1: Create Container, Generate Sample Set -->
          <div class="flex flex-col sm:flex-row gap-4 w-full">
            <ButtonLink
              size="lg"
              variant="outline"
              class="flex-1"
              :to="GearRoutePath.ContainerNew"
            >
              <Plus class="size-5" />
              {{ t('gear.container.create.title', 'Create Container') }}
            </ButtonLink>
            <GenerateExampleGearButton class="flex-1" />
          </div>
          <!-- Row 2: Login, Register (only if not authenticated) -->
          <div v-if="!isAuthenticated && config.backend.enabled" class="flex flex-col sm:flex-row gap-4 w-full">
            <ButtonLink
              size="lg"
              variant="outline"
              class="flex-1"
              :to="AuthRoutePaths.login"
            >
              <LogIn class="size-5" />
              {{ t('auth.login', 'Log In') }}
            </ButtonLink>
            <ButtonLink
              size="lg"
              variant="outline"
              class="flex-1"
              :to="AuthRoutePaths.register"
            >
              <UserPlus class="size-5" />
              {{ t('auth.register', 'Sign Up') }}
            </ButtonLink>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="containers.length === 0" class="text-center py-12 max-w-md">
          <p class="text-muted-foreground mb-6">
            {{ t('gear.page.emptyDescription', 'Get started by creating your first gear container.') }}
          </p>

          <!-- Create, Generate Sample Set, Import from Markdown, Login, Register -->
          <WelcomeQuickActions />
        </div>
      </div>
    </div>
  </AuthenticatedLayout>
</template>
