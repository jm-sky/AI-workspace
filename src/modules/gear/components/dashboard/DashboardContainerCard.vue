<script setup lang="ts">
import { GearRoutePath } from '@/modules/gear/routes'
import type { Component } from 'vue'

defineProps<{
  to: string
  count: number | string
  label: string
  icon?: Component
}>()
</script>

<template>
  <RouterLink
    :to="GearRoutePath.Containers"
    class="cursor-pointer bg-card rounded-lg border p-6 text-center hover:scale-102 hover:-translate-y-1 hover:shadow-md transition-all duration-300"
  >
    <div class="text-3xl font-bold text-primary mb-2">
      {{ count }}
    </div>
    <div class="text-muted-foreground flex items-center justify-center gap-1">
      <component :is="icon" class="size-4" />
      {{ label }}
    </div>
  </RouterLink>
</template>
