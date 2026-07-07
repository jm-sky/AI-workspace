<script setup lang="ts">
import { LogInIcon, Sparkles, UserPlusIcon } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import AppIcon from '@/components/ui/AppIcon.vue'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import LandingLayout from '@/layouts/LandingLayout.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { AuthRoutePaths } from '@/modules/auth/config/routes'
import { WorkspaceRoutePath } from '@/modules/workspace/routes'
import { config } from '@/shared/config/config'

const { t } = useI18n()
const router = useRouter()
const { isAuthenticated, user } = useAuth()

if (!config.backend.enabled) {
  router.replace({ name: 'home' })
}
</script>

<template>
  <LandingLayout>
    <div class="max-w-2xl w-full space-y-8 text-center">
      <div class="flex justify-center">
        <div class="rounded-full bg-primary/10 p-8">
          <AppIcon class="size-20" />
        </div>
      </div>

      <div class="space-y-4">
        <p v-if="isAuthenticated && user" class="text-2xl font-semibold text-muted-foreground">
          {{ t('landing.welcomeBack', { name: user.name }) }}
        </p>
        <h1 class="text-5xl font-bold tracking-tight">
          {{ t('landing.title', config.app.name) }}
        </h1>
        <p class="text-xl text-muted-foreground max-w-lg mx-auto">
          {{ t('landing.subtitle', config.app.description) }}
        </p>
      </div>
    </div>

    <div class="max-w-2xl w-full space-y-8 text-center">
      <div class="grid grid-cols-1 md:grid-cols-3 py-4 gap-6">
        <div class="space-y-2">
          <h3 class="font-semibold text-lg">
            {{ t('landing.feature1.title', 'Chat') }}
          </h3>
          <p class="text-sm text-muted-foreground">
            {{ t('landing.feature1.description', 'Interact naturally with AI agents through a unified chat interface') }}
          </p>
        </div>
        <div class="space-y-2">
          <h3 class="font-semibold text-lg">
            {{ t('landing.feature2.title', 'Agents') }}
          </h3>
          <p class="text-sm text-muted-foreground">
            {{ t('landing.feature2.description', 'Orchestrate tools, workflows, and organizational knowledge') }}
          </p>
        </div>
        <div class="space-y-2">
          <h3 class="font-semibold text-lg">
            {{ t('landing.feature3.title', 'Integrate') }}
          </h3>
          <p class="text-sm text-muted-foreground">
            {{ t('landing.feature3.description', 'Connect Jira, GitLab, and more via MCP integrations') }}
          </p>
        </div>
      </div>

      <div class="flex flex-col items-center justify-center gap-4">
        <ButtonLink
          v-if="isAuthenticated"
          size="lg"
          class="w-full sm:w-auto"
          :to="WorkspaceRoutePath.Chat"
        >
          <Sparkles class="size-5" />
          {{ t('workspace.nav.chat', 'Open AI Workspace') }}
        </ButtonLink>

        <template v-else-if="config.backend.enabled">
          <ButtonLink
            size="lg"
            class="w-full sm:w-auto"
            :to="AuthRoutePaths.login"
          >
            <LogInIcon class="size-5" />
            {{ t('auth.login', 'Log In') }}
          </ButtonLink>
          <ButtonLink
            size="lg"
            variant="outline"
            class="w-full sm:w-auto"
            :to="AuthRoutePaths.register"
          >
            <UserPlusIcon class="size-5" />
            {{ t('auth.register', 'Sign Up') }}
          </ButtonLink>
        </template>
      </div>
    </div>
  </LandingLayout>
</template>
