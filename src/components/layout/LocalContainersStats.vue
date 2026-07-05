<script setup lang="ts">
import { LogIn, UserPlus } from 'lucide-vue-next'
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import LandingPageContainerCard from '@/components/layout/LandingPageContainerCard.vue'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { AuthRoutePaths } from '@/modules/auth/config/routes'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import { GearRoutePath } from '@/modules/gear/routes'
import { useGearStoreV2 } from '@/modules/gear/store/useGearStoreV2'
import { READINESS_EXCELLENT_THRESHOLD } from '@/modules/gear/utils/constants'

const { t } = useI18n()
const authStore = useAuthStore()
const gearStore = useGearStoreV2()
const { isAuthenticated } = useAuth()

// Load containers from localStorage (V2 store; migrateV1ToV2 runs on store init)
onMounted(() => {
  if (!authStore.isAuthenticated) {
    gearStore.loadFromStorage()
  }
})

// Check if user is not logged in but has containers in localStorage
const localContainers = computed(() => {
  if (authStore.isAuthenticated) return []
  return gearStore.getAllContainers
})

const hasLocalContainers = computed(() => localContainers.value.length > 0)

// Regular items (V2 store is flat; exclude nested containers)
const localItems = computed(() => gearStore.getAllItems.filter(i => i.itemType === 'item'))

// Calculate stats similar to HomePage
const containersCount = computed(() => localContainers.value.length)

const itemsCount = computed(() => (hasLocalContainers.value ? localItems.value.length : 0))

const readyContainersCount = computed(() => {
  return localContainers.value.filter(c => {
    const items = gearStore.getChildrenOfItem(c.id).filter(i => i.itemType === 'item')
    const totalItems = items.length
    if (totalItems === 0) return false
    const ownedItems = items.filter(i => i.status === 'owned').length
    return (ownedItems / totalItems) * 100 >= READINESS_EXCELLENT_THRESHOLD
  }).length
})
</script>

<template>
  <div class="bg-card/50 backdrop-blur-sm rounded-lg border p-6 space-y-4">
    <div class="text-center space-y-2">
      <h2 class="text-2xl font-semibold">
        {{ t('landing.localData.title', 'Masz kontenery w przeglądarce') }}
      </h2>
      <p class="text-muted-foreground">
        {{ t('landing.localData.description', 'Zaloguj się lub zarejestruj, aby zsynchronizować swoje dane') }}
      </p>
    </div>

    <!-- Container Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <LandingPageContainerCard
        :to="GearRoutePath.Containers"
        :label="t('gear.page.containers', 'Containers')"
        :containers-count="containersCount"
      />
      <LandingPageContainerCard
        :to="GearRoutePath.AllItems"
        :label="t('gear.page.items', 'Items')"
        :containers-count="itemsCount"
      />
      <LandingPageContainerCard
        :to="GearRoutePath.Containers"
        :label="t('gear.page.readyContainers', 'Ready Containers')"
        :containers-count="readyContainersCount"
      />
    </div>

    <!-- Login/Register CTA -->
    <div v-if="!isAuthenticated" class="flex flex-col gap-6 justify-center items-center pt-4">
      <ButtonLink size="lg" class="w-full sm:w-auto" :to="AuthRoutePaths.login">
        <LogIn class="size-5" />
        {{ t('landing.login', 'Log In') }}
      </ButtonLink>
      <ButtonLink
        size="lg"
        variant="outline"
        class="w-full sm:w-auto"
        :to="AuthRoutePaths.register"
      >
        <UserPlus class="size-5" />
        {{ t('landing.register', 'Sign Up') }}
      </ButtonLink>
    </div>
  </div>
</template>

