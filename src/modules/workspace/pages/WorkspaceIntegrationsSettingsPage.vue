<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import IntegrationConnectionsCard from '@/modules/settings/components/IntegrationConnectionsCard.vue'

const { t } = useI18n()
</script>

<template>
  <div class="space-y-6">
    <div class="space-y-1">
      <h2 class="text-xl font-semibold">
        {{ t('workspace.settings.integrations') }}
      </h2>
      <p class="text-sm text-muted-foreground">
        {{ t('workspace.settings.integrationsDescription') }}
      </p>
    </div>
    <IntegrationConnectionsCard />
  </div>
</template>
