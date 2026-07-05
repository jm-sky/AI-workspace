<script setup lang="ts">
import { Globe } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { Badge } from '@/components/ui/badge'

const { t } = useI18n()
</script>

<template>
  <Badge
    v-tooltip.bottom="t('gear.container.isPublicStatus')"
    variant="outline"
    class="text-xs"
  >
    <Globe class="size-4" />
    {{ t('gear.container.isPublic') }}
  </Badge>
</template>
