<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import StorageUsageCard from '@/modules/settings/components/StorageUsageCard.vue'

const { t } = useI18n()
</script>

<template>
  <div class="space-y-6">
    <div class="space-y-1">
      <h2 class="text-xl font-semibold">
        {{ t('settings.nav.storage') }}
      </h2>
      <p class="text-sm text-muted-foreground">
        {{ t('settings.storage.subtitle', 'View your storage usage') }}
      </p>
    </div>
    <StorageUsageCard />
  </div>
</template>
