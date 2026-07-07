<script setup lang="ts">
import { ArrowRight, Plug } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import OAuthConnectionsCard from '@/modules/settings/components/OAuthConnectionsCard.vue'
import { WorkspaceRoutePath } from '@/modules/workspace/routes'

const { t } = useI18n()
</script>

<template>
  <div class="space-y-6">
    <div class="space-y-1">
      <h2 class="text-xl font-semibold">
        {{ t('settings.nav.connections') }}
      </h2>
      <p class="text-sm text-muted-foreground">
        {{ t('settings.nav.connectionsDescription') }}
      </p>
    </div>

    <OAuthConnectionsCard />

    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2 text-base">
          <Plug class="size-4" />
          {{ t('settings.nav.workspaceIntegrationsTitle') }}
        </CardTitle>
        <CardDescription>
          {{ t('settings.nav.workspaceIntegrationsDescription') }}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Button as-child variant="outline">
          <RouterLink :to="WorkspaceRoutePath.SettingsIntegrations">
            {{ t('settings.nav.workspaceIntegrationsLink') }}
            <ArrowRight class="size-4" />
          </RouterLink>
        </Button>
      </CardContent>
    </Card>
  </div>
</template>
