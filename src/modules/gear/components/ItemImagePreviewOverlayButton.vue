<script setup lang="ts">
import { Button } from '@/components/ui/button'
</script>

<template>
  <Button
    size="icon"
    variant="ghost"
    v-bind="$attrs"
    class="absolute top-1/2 -translate-y-1/2 aspect-square rounded-full bg-black text-white opacity-50 hover:scale-105 hover:opacity-90 hover:text-white hover:bg-black transition-all duration-300"
  >
    <slot />
  </Button>
</template>
