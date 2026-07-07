<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useIntegrationOAuth } from '@/modules/settings/composables/useIntegrationOAuth'
import { integrationService } from '@/modules/settings/services/integrationService'
import { WorkspaceRoutePath } from '@/modules/workspace/routes'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const { clearStoredState, getStoredState } = useIntegrationOAuth()

const isProcessing = ref(false)
const error = ref<string | null>(null)
const provider = ref('')

onMounted(async () => {
  if (isProcessing.value) {
    return
  }
  isProcessing.value = true

  try {
    const code = route.query.code as string
    const state = route.query.state as string
    const errorParam = route.query.error as string
    const providerParam = (route.params.provider as string) || ''

    provider.value = providerParam

    if (errorParam) {
      error.value = t('settings.integrations.callback.cancelled')
      setTimeout(() => router.push(WorkspaceRoutePath.SettingsIntegrations), 2000)
      return
    }

    if (!providerParam || !code || !state) {
      error.value = t('settings.integrations.callback.invalid_parameters')
      setTimeout(() => router.push(WorkspaceRoutePath.SettingsIntegrations), 2000)
      return
    }

    const storedState = getStoredState()
    if (!storedState || storedState !== state) {
      error.value = t('settings.integrations.callback.invalid_state')
      setTimeout(() => router.push(WorkspaceRoutePath.SettingsIntegrations), 2000)
      return
    }

    clearStoredState()

    await integrationService.completeCallback(providerParam, { code, state })
    toast.success(t('settings.integrations.callback.success', { provider: providerParam }))
    await router.push(WorkspaceRoutePath.SettingsIntegrations)
  }
  catch (err) {
    console.error('Integration OAuth callback error:', err)
    error.value = t('settings.integrations.callback.failed')
    setTimeout(() => router.push(WorkspaceRoutePath.SettingsIntegrations), 2500)
  }
})
</script>

<template>
  <div class="flex min-h-[50vh] items-center justify-center p-4">
    <Card class="w-full max-w-md">
      <CardHeader>
        <CardTitle>
          {{ error
            ? t('settings.integrations.callback.failed_title')
            : t('settings.integrations.callback.processing_title') }}
        </CardTitle>
        <CardDescription>
          {{ error ?? t('settings.integrations.callback.processing', { provider }) }}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p
          v-if="error"
          class="text-sm text-destructive"
        >
          {{ error }}
        </p>
      </CardContent>
    </Card>
  </div>
</template>
