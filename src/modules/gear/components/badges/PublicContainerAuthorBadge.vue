<script setup lang="ts">
import { User } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import { UserRoutePaths } from '@/modules/user/routes'
import type { TUUID } from '@/shared/types/base.type'

const { t } = useI18n()

defineProps<{
  authorName: string
  authorId?: TUUID | null
  asLink?: boolean
}>()
</script>

<template>
  <template v-if="asLink && authorId">
    <RouterLink
      v-slot="{ navigate, href }"
      :to="UserRoutePaths.publicUserProfileById(authorId)"
      custom
    >
      <Badge
        v-tooltip.bottom="t('gear.publicContainers.author')"
        as="a"
        variant="secondary"
        class="cursor-pointer hover:bg-secondary/80"
        :aria-label="t('gear.publicContainers.author')"
        :href
        @click.stop.capture.prevent="navigate"
      >
        <User class="size-3" />
        {{ authorName }}
      </Badge>
    </RouterLink>
  </template>
  <template v-else>
    <Badge
      v-tooltip.bottom="t('gear.publicContainers.author')"
      variant="secondary"
      :aria-label="t('gear.publicContainers.author')"
    >
      <User class="size-3" />
      {{ authorName }}
    </Badge>
  </template>
</template>
