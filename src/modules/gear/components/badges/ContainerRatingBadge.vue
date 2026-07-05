<script setup lang="ts">
import { StarIcon } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import { useBackend } from '@/shared/composables/useBackend'
import type { IGearItemV2 } from '../../types/gear.types.v2'

const { t } = useI18n()
const { shouldUseAPI } = useBackend()

defineProps<{
  container: IGearItemV2
}>()
</script>

<template>
  <Badge
    v-if="container && shouldUseAPI"
    v-tooltip.bottom="t('gear.container.ratings')"
    variant="secondary"
  >
    <StarIcon class="size-4" />
    {{ container.averageUserRating ?? 0 }} / 5
  </Badge>
</template>
