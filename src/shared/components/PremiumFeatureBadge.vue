<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import Badge from '@/components/ui/badge/Badge.vue'
import { BillingRoutePaths } from '@/modules/billing/routes'

const { t } = useI18n()
</script>

<template>
  <RouterLink v-slot="{ navigate, href }" :to="BillingRoutePaths.billing" custom>
    <Badge
      variant="premium"
      as="a"
      :href="href"
      @click.stop="navigate"
    >
      <slot>
        {{ t('premium.premiumFeature') }}
      </slot>
    </Badge>
  </RouterLink>
</template>
