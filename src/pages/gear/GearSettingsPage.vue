<script setup lang="ts">
import AiSettingsCard from '@/modules/ai/components/AiSettingsCard.vue'
import GearSettingsPageCore from '@/modules/gear/pages/GearSettingsPage.vue'
</script>

<template>
  <GearSettingsPageCore>
    <template #after-preferences>
      <AiSettingsCard />
    </template>
  </GearSettingsPageCore>
</template>
