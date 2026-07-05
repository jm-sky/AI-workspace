<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import BrandsSettingsCard from '@/modules/settings/components/BrandsSettingsCard.vue'
import CategoriesSettingsCard from '@/modules/settings/components/CategoriesSettingsCard.vue'
import ContainerTypesSettingsCard from '@/modules/settings/components/ContainerTypesSettingsCard.vue'
import GearPreferencesCard from '../components/GearPreferencesCard.vue'

const { t } = useI18n()
</script>

<template>
  <AuthenticatedLayout>
    <div class="mx-auto space-y-6">
      <div class="space-y-1">
        <h1 class="text-3xl font-bold tracking-tight">
          {{ t('gear.settings.page.title') }}
        </h1>
        <p class="text-sm text-muted-foreground">
          {{ t('gear.settings.page.subtitle') }}
        </p>
      </div>

      <div class="space-y-6">
        <!-- Gear Preferences -->
        <GearPreferencesCard />

        <!-- Additional Settings from other modules (via slot) -->
        <slot name="after-preferences" />

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Custom Container Types -->
          <ContainerTypesSettingsCard />

          <!-- Custom Categories -->
          <CategoriesSettingsCard />

          <!-- Custom Brands -->
          <BrandsSettingsCard />
        </div>
      </div>
    </div>
  </AuthenticatedLayout>
</template>

