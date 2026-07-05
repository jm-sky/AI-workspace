<script setup lang="ts">
import { defineAsyncComponent } from 'vue'
import PwaUpdatePrompt from '@/components/PwaUpdatePrompt.vue'
import { Toaster } from '@/components/ui/sonner'
import 'vue-sonner/style.css'
import LoginModal from './shared/components/LoginModal.vue'
import { useAppInitialization } from './shared/composables/useAppInitialization'

// Lazy load DataMigrationDialog to fix mixed import warning and reduce initial bundle size
// This component is only shown conditionally after login
const DataMigrationDialog = defineAsyncComponent(
  () => import('@/modules/gear/components/DataMigrationDialog.vue')
)

const { isInitialized } = useAppInitialization()
</script>

<template>
  <RouterView :is-initialized />
  <LoginModal />
  <DataMigrationDialog />
  <PwaUpdatePrompt />
  <Toaster rich-colors />
</template>

<style scoped></style>
