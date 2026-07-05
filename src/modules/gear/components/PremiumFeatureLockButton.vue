<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import { BillingRoutePaths } from '@/modules/billing/routes'
import { getActionIcon } from '../utils/actionIcons'
import type { Component } from 'vue'

interface Props {
  /**
   * Whether the user has access to this premium feature
   */
  hasAccess: boolean
  /**
   * Icon to display when user has access (defaults to AI Sparkles icon)
   */
  icon?: Component | string
  /**
   * Tooltip text when user has access (optional, will use default if not provided)
   */
  tooltip?: string
  /**
   * Aria label when user has access (optional, will use tooltip if not provided)
   */
  ariaLabel?: string
}

const props = withDefaults(defineProps<Props>(), {
  icon: undefined,
  tooltip: undefined,
  ariaLabel: undefined,
})

const { t } = useI18n()

const emit = defineEmits<{
  click: []
}>()

// Get icon component - use provided icon or default to AI icon
const AccessIcon = computed<Component>(() => {
  if (props.icon) {
    return typeof props.icon === 'string' ? getActionIcon(props.icon) : props.icon
  }
  return getActionIcon('ai')
})

const PremiumLockIcon = getActionIcon('aiPremium')

const handleClick = () => {
  emit('click')
}

const tooltipText = computed(() => {
  if (props.hasAccess && props.tooltip) {
    return props.tooltip
  }
  if (!props.hasAccess) {
    return t('premium.unlockPremiumFeatures')
  }
  return props.tooltip || ''
})

const ariaLabelText = computed(() => {
  if (props.hasAccess && props.ariaLabel) {
    return props.ariaLabel
  }
  return tooltipText.value
})
</script>

<template>
  <Button
    v-if="hasAccess"
    v-tooltip.bottom="tooltipText"
    variant="ghost"
    size="sm"
    class="shrink-0"
    :aria-label="ariaLabelText"
    @click="handleClick"
  >
    <component :is="AccessIcon" class="size-4" />
  </Button>
  <ButtonLink
    v-else
    v-tooltip.bottom="tooltipText"
    variant="ghost"
    size="sm"
    class="shrink-0"
    :to="BillingRoutePaths.billing"
    :aria-label="ariaLabelText"
  >
    <PremiumLockIcon class="size-4 text-violet-500" />
  </ButtonLink>
</template>

