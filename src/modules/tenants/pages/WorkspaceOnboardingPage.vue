<script setup lang="ts">
import { Building2, Loader2 } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import GuestLayoutCard from '@/components/layout/GuestLayoutCard.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import GuestLayoutCentered from '@/layouts/GuestLayoutCentered.vue'
import { AuthRoutePaths } from '@/modules/auth/config/routes'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import { useTenantWorkspace } from '@/modules/tenants/composables/useTenantWorkspace'
import { getApiErrorMessage } from '@/shared/utils/apiError'
import type { ITenant } from '@/modules/tenants/types/tenant'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { createWorkspace, selectWorkspace, loadTenants } = useTenantWorkspace()

const isLoading = ref(true)
const isSubmitting = ref(false)
const tenants = ref<ITenant[]>([])
const selectedTenantId = ref<string | null>(null)
const name = ref('')
const description = ref('')

const mode = computed<'create' | 'select'>(() => (tenants.value.length > 1 ? 'select' : 'create'))

const redirectTarget = computed(() => {
  if (typeof route.query.redirectTo === 'string' && route.query.redirectTo.length > 0) {
    return route.query.redirectTo
  }
  return AuthRoutePaths.dashboard
})

const defaultWorkspaceName = computed(() => {
  const userName = authStore.user?.name?.trim()
  if (!userName) return ''
  return `${userName}'s Workspace`
})

onMounted(async () => {
  try {
    tenants.value = await loadTenants()
    if (tenants.value.length === 1) {
      selectedTenantId.value = tenants.value[0].id
    }
    if (tenants.value.length === 0) {
      name.value = defaultWorkspaceName.value
    }
  } catch (error) {
    toast.error(getApiErrorMessage(error, t('errors.generic')))
  } finally {
    isLoading.value = false
  }
})

const finishOnboarding = async () => {
  await router.replace(redirectTarget.value)
}

const handleCreate = async () => {
  const trimmedName = name.value.trim()
  if (!trimmedName) return

  isSubmitting.value = true
  try {
    await createWorkspace({
      name: trimmedName,
      description: description.value.trim() || null,
    })
    toast.success(t('tenants.onboarding.created'))
    await finishOnboarding()
  } catch (error) {
    toast.error(getApiErrorMessage(error, t('tenants.onboarding.createFailed')))
  } finally {
    isSubmitting.value = false
  }
}

const handleSelect = async () => {
  if (!selectedTenantId.value) return

  isSubmitting.value = true
  try {
    await selectWorkspace(selectedTenantId.value)
    await finishOnboarding()
  } catch (error) {
    toast.error(getApiErrorMessage(error, t('tenants.onboarding.selectFailed')))
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <GuestLayoutCentered>
    <GuestLayoutCard :title="t('tenants.onboarding.title')">
      <template #header-description>
        <p class="mt-2 text-center text-sm text-muted-foreground">
          {{ t('tenants.onboarding.subtitle') }}
        </p>
      </template>

      <div
        v-if="isLoading"
        class="flex items-center justify-center gap-2 py-10 text-sm text-muted-foreground"
      >
        <Loader2 class="size-4 animate-spin" />
        {{ t('tenants.onboarding.loading') }}
      </div>

      <div
        v-else-if="mode === 'create'"
        class="space-y-4"
      >
        <div class="space-y-1">
          <h2 class="text-base font-medium">
            {{ t('tenants.onboarding.createTitle') }}
          </h2>
          <p class="text-sm text-muted-foreground">
            {{ t('tenants.onboarding.createSubtitle') }}
          </p>
        </div>

        <div class="space-y-2">
          <Label for="workspace-name">{{ t('tenants.onboarding.name') }}</Label>
          <Input
            id="workspace-name"
            v-model="name"
            :placeholder="t('tenants.onboarding.namePlaceholder')"
            autocomplete="organization"
          />
        </div>

        <div class="space-y-2">
          <Label for="workspace-description">{{ t('tenants.onboarding.description') }}</Label>
          <Textarea
            id="workspace-description"
            v-model="description"
            :placeholder="t('tenants.onboarding.descriptionPlaceholder')"
            rows="3"
          />
        </div>

        <Button
          class="w-full"
          :disabled="!name.trim()"
          :loading="isSubmitting"
          @click="handleCreate"
        >
          {{ t('tenants.onboarding.createAction') }}
        </Button>
      </div>

      <div
        v-else
        class="space-y-4"
      >
        <div class="space-y-1">
          <h2 class="text-base font-medium">
            {{ t('tenants.onboarding.selectTitle') }}
          </h2>
          <p class="text-sm text-muted-foreground">
            {{ t('tenants.onboarding.selectSubtitle') }}
          </p>
        </div>

        <div class="space-y-2">
          <button
            v-for="tenant in tenants"
            :key="tenant.id"
            type="button"
            class="flex w-full items-start gap-3 rounded-lg border p-3 text-left transition-colors hover:bg-accent"
            :class="selectedTenantId === tenant.id && 'border-primary bg-accent'"
            @click="selectedTenantId = tenant.id"
          >
            <Building2 class="mt-0.5 size-4 shrink-0 text-muted-foreground" />
            <div class="min-w-0">
              <p class="font-medium">
                {{ tenant.name }}
              </p>
              <p
                v-if="tenant.description"
                class="text-sm text-muted-foreground"
              >
                {{ tenant.description }}
              </p>
              <p class="text-xs text-muted-foreground">
                {{ t('tenants.onboarding.role', { role: tenant.role }) }}
              </p>
            </div>
          </button>
        </div>

        <Button
          class="w-full"
          :disabled="!selectedTenantId"
          :loading="isSubmitting"
          @click="handleSelect"
        >
          {{ t('tenants.onboarding.selectAction') }}
        </Button>
      </div>
    </GuestLayoutCard>
  </GuestLayoutCentered>
</template>
