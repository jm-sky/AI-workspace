<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import type { TGearItemStatus } from '../types/gear.types'
import { getStatusVariant } from '../utils/badgeVariants'

const { t } = useI18n()

const props = defineProps<{
  status: TGearItemStatus
  class?: string
}>()
</script>

<template>
  <Badge :variant="getStatusVariant(props.status)" :class="props.class">
    {{ t(`gear.item.statuses.${props.status}`) }}
  </Badge>
</template>

