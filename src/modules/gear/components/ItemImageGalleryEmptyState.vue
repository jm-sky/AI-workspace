<script setup lang="ts">
import { ImageIcon } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="w-full md:w-[calc(25%-1rem)] flex flex-col gap-2 items-center justify-center border-2 border-border rounded-lg p-4">
    <ImageIcon class="size-10 text-muted-foreground/50" />
    <div class="text-sm text-center text-muted-foreground">
      {{ t('gear.fileUpload.imageGallery.noImages') }}
    </div>
  </div>
</template>

