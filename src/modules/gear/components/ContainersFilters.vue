<script setup lang="ts">
import { RefreshCcw } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'
import { Checkbox } from '@/components/ui/checkbox'
import SearchInput from '@/components/ui/input/SearchInput.vue'
import { Label } from '@/components/ui/label'

const { t } = useI18n()

defineProps<{
  loading?: boolean
  rootContainersFilter?: boolean
}>()

// Define models using defineModel
const searchQuery = defineModel<string>('searchQuery', { default: '' })
const showOnlyRootContainers = defineModel<boolean>('showOnlyRootContainers', { default: false })

const emit = defineEmits<{
  refresh: []
}>()
</script>

<template>
  <div class="flex flex-col gap-3">
    <div class="flex flex-row items-center gap-2">
      <SearchInput
        id="container-search"
        v-model="searchQuery"
        name="container-search"
        :placeholder="$t('gear.filters.searchContainers')"
      />
      <Button
        variant="ghost"
        size="sm"
        class="w-9"
        :loading
        :aria-label="t('gear.filters.refresh', 'Refresh containers')"
        @click="emit('refresh')"
      >
        <RefreshCcw v-if="!loading" class="size-4" />
      </Button>
    </div>
    <div v-if="rootContainersFilter" class="flex items-center gap-2">
      <Checkbox
        id="root-containers-filter"
        v-model="showOnlyRootContainers"
      />
      <Label
        for="root-containers-filter"
        class="text-sm text-muted-foreground cursor-pointer"
      >
        {{ t('gear.container.showOnlyRootContainers') }}
      </Label>
    </div>
  </div>
</template>

