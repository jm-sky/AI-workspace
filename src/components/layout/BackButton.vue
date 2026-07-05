<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'
import { getActionIcon } from '@/modules/gear/utils/actionIcons'

const { t } = useI18n()
const BackIcon = getActionIcon('back')

defineProps<{
  noLabel?: boolean
}>()
</script>

<template>
  <Button
    variant="ghost"
    size="sm"
  >
    <BackIcon class="size-4" />
    {{ !noLabel ? t('common.back') : null }}
  </Button>
</template>
