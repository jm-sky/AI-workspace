<script setup lang="ts">
import { BookIcon } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import Badge from '@/components/ui/badge/Badge.vue'
import { GearRoutePath } from '../../routes'

const { t } = useI18n()

defineProps<{
  catalogueItemId: string
}>()
</script>

<template>
  <RouterLink
    v-slot="{ navigate, href }"
    :to="GearRoutePath.CatalogueItemDetailById(catalogueItemId)"
    custom
  >
    <Badge
      variant="secondary"
      class="text-xs flex items-center gap-1 cursor-pointer hover:bg-secondary/80 hover:border-primary/80 transition-all duration-300"
      as="a"
      :href
      @click.stop="navigate"
    >
      {{ t('gear.catalogue.fromCatalogue') }}
      <BookIcon class="size-3" />
    </Badge>
  </RouterLink>
</template>
