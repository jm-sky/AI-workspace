<script setup lang="ts">
import { Bot, History } from 'lucide-vue-next'
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ButtonLink } from '@/components/ui/button-link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import Separator from '@/components/ui/separator/Separator.vue'
import AiModelSelector from '@/modules/ai/components/settings/AiModelSelector.vue'
import AiTokenManager from '@/modules/ai/components/settings/AiTokenManager.vue'
import AiUsageDisplay from '@/modules/ai/components/settings/AiUsageDisplay.vue'
import { useAiModels } from '@/modules/ai/composables/useAiModels'
import { AiRoutePath } from '@/modules/ai/config/routes'
import { useAiStore } from '@/modules/ai/store/useAiStore'
import { useUser } from '@/modules/user/composables/useUser'
import { useUserStore } from '@/modules/user/store/useUserStore'
import { useHandleError } from '@/shared/composables/useHandleError'
import { usePermissions } from '@/shared/composables/usePermissions'
import { useAi } from '../composables/useAi'

const { t } = useI18n()
const { isAuthenticated } = usePermissions()

const aiStore = useAiStore()
const userStore = useUserStore()
const { canUseAi } = useAi()
const { models, loadModels } = useAiModels()
const { loadProfile } = useUser()
const { handleError } = useHandleError()

const loadAiSettings = async () => {
  try {
    await aiStore.loadSettings()
  } catch (error) {
    handleError(error, { fallbackMessage: t('ai.settings.loadError') })
    console.warn('Failed to load AI settings:', error)
  }
}

const loadAiModels = async () => {
  try {
    await loadModels()
  } catch (error) {
    handleError(error, { fallbackMessage: t('ai.models.loadError') })
    console.warn('Failed to load AI models:', error)
  }
}

const loadUserProfile = async () => {
  try {
    await loadProfile()
  } catch (error) {
    // Silently fail if user profile can't be loaded
    console.warn('Failed to load user profile for features:', error)
  }
}

const initialize = async () => {
  if (!isAuthenticated.value) return

  await loadAiSettings()

  if (models.value.length === 0) {
    await loadAiModels()
  }

  // Load user profile to get features if not already loaded
  if (!userStore.user?.features) {
    await loadUserProfile()
  }
}

onMounted(async () => {
  await initialize()
})
</script>

<template>
  <Card>
    <CardHeader>
      <div class="flex items-center gap-2">
        <Bot :size="20" />
        <CardTitle>{{ t('gear.settings.ai.title') }}</CardTitle>
      </div>
      <CardDescription>
        {{ t('gear.settings.ai.description') }}
      </CardDescription>
    </CardHeader>
    <CardContent class="space-y-6">
      <div :class="{ 'opacity-50 pointer-events-none': !isAuthenticated }">
        <!-- AI Model Selector -->
        <AiModelSelector :is-authenticated :class="{ 'opacity-50 pointer-events-none': !canUseAi }" />

        <Separator class="my-4" />

        <!-- API Token Manager -->
        <AiTokenManager :is-authenticated />

        <Separator class="my-4" />

        <!-- Usage Display -->
        <AiUsageDisplay />

        <Separator class="my-4" />

        <!-- History Link -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <History class="size-4 text-muted-foreground" />
            <div>
              <div class="text-sm font-medium">
                {{ t('ai.history.title') }}
              </div>
              <div class="text-xs text-muted-foreground">
                {{ t('ai.history.details') }}
              </div>
            </div>
          </div>
          <ButtonLink :to="AiRoutePath.History" variant="outline" size="sm">
            <History class="size-4 mr-2" />
            {{ t('ai.history.title') }}
          </ButtonLink>
        </div>
      </div>
    </CardContent>
  </Card>
</template>

