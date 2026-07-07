<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import DeleteAccountCard from '@/modules/settings/components/DeleteAccountCard.vue'
import SecuritySettingsCard from '@/modules/settings/components/SecuritySettingsCard.vue'

const { t } = useI18n()
</script>

<template>
  <div class="space-y-6">
    <div class="space-y-1">
      <h2 class="text-xl font-semibold">
        {{ t('settings.nav.security') }}
      </h2>
      <p class="text-sm text-muted-foreground">
        {{ t('settings.security.subtitle', 'Manage authentication and account security') }}
      </p>
    </div>
    <SecuritySettingsCard />
    <DeleteAccountCard />
  </div>
</template>
