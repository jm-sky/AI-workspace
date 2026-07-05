<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import type { TGearItemPriority } from '../../types/gear.types.v2'
import { getPriorityVariant } from '../../utils/badgeVariants'

const { t } = useI18n()

const props = defineProps<{
  priority: TGearItemPriority
  class?: string
}>()
</script>

<template>
  <Badge :variant="getPriorityVariant(props.priority)" :class="props.class">
    {{ t(`gear.item.priorities.${props.priority}`) }}
  </Badge>
</template>

