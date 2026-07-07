<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import PreferencesSettingsCard from '@/modules/settings/components/PreferencesSettingsCard.vue'

const { t } = useI18n()
</script>

<template>
  <div class="space-y-4">
    <div class="space-y-1">
      <h2 class="text-xl font-semibold">
        {{ t('settings.nav.account') }}
      </h2>
      <p class="text-sm text-muted-foreground">
        {{ t('settings.page.sections.preferences.description') }}
      </p>
    </div>
    <PreferencesSettingsCard />
  </div>
</template>
