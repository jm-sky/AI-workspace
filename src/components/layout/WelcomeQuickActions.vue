<script setup lang="ts">
import { BackpackIcon, FileInput, LogInIcon, Plus, UserPlusIcon } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { cn } from '@/lib/utils'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { AuthRoutePaths } from '@/modules/auth/config/routes'
import GenerateExampleGearButton from '@/modules/gear/components/GenerateExampleGearButton.vue'
import { GearRoutePath } from '@/modules/gear/routes'
import { config } from '@/shared/config/config'
import ButtonLink from '../ui/button-link/ButtonLink.vue'
import Separator from '../ui/separator/Separator.vue'
import type { HTMLAttributes } from 'vue'

const { t } = useI18n()
const { isAuthenticated } = useAuth()

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()
</script>

<template>
  <div :class="cn('flex flex-col gap-4 items-center justify-center', props.class)">
    <!-- Row: Create Container, Generate Sample Set -->
    <ButtonLink size="lg" class="w-full sm:w-auto" :to="GearRoutePath.ContainerNew">
      <Plus class="size-5" />
      {{ t('gear.container.create.title', 'Create Container') }}
    </ButtonLink>

    <ButtonLink
      variant="outline"
      size="lg"
      class="w-full sm:w-auto"
      :to="GearRoutePath.Containers"
    >
      <BackpackIcon class="size-5" />
      {{ t('gear.page.viewContainers', 'View Containers') }}
    </ButtonLink>

    <div class="flex items-center gap-2 text-muted-foreground">
      <span>{{ t('common.or', 'or') }}</span>
    </div>

    <div class="flex flex-col sm:flex-row gap-4 w-full">
      <ButtonLink
        size="lg"
        variant="outline"
        :to="GearRoutePath.Import"
      >
        <FileInput class="size-4" />
        {{ t('gear.import.fromMarkdown', 'Import from Markdown') }}
      </ButtonLink>

      <GenerateExampleGearButton class="lg:flex-1" />
    </div>

    <Separator v-if="!isAuthenticated && config.backend.enabled" />

    <!-- Row 2: Login, Register (only if not authenticated) -->
    <div v-if="!isAuthenticated && config.backend.enabled" class="flex flex-col items-center justify-center sm:flex-row gap-4 w-full mt-2">
      <ButtonLink
        size="lg"
        variant="outline"
        class="flex-1"
        :to="AuthRoutePaths.login"
      >
        <LogInIcon class="size-5" />
        {{ t('auth.login', 'Log In') }}
      </ButtonLink>
      <ButtonLink
        size="lg"
        variant="outline"
        class="flex-1"
        :to="AuthRoutePaths.register"
      >
        <UserPlusIcon class="size-5" />
        {{ t('auth.register', 'Sign Up') }}
      </ButtonLink>
    </div>
  </div>
</template>
