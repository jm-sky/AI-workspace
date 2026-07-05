<script setup lang="ts">
import { AlertCircle } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import type { markdownImportService } from '../../services/markdownImportService'

const { t } = useI18n()

defineProps<{
  previewResult: ReturnType<typeof markdownImportService.parseMarkdown> | null
}>()
</script>

<template>
  <div v-if="previewResult" class="space-y-4">
    <!-- Errors -->
    <Alert v-if="previewResult.errors.length > 0" variant="destructive">
      <AlertCircle class="size-4" />
      <AlertTitle>{{ t('gear.import.errors') }}</AlertTitle>
      <AlertDescription>
        <ul class="list-disc list-inside text-xs">
          <li v-for="(error, idx) in previewResult.errors" :key="idx">
            {{ error }}
          </li>
        </ul>
      </AlertDescription>
    </Alert>

    <!-- Preview Summary -->
    <div v-if="previewResult.containers.length > 0" class="border rounded-lg p-4 space-y-3">
      <h3 class="font-semibold">
        {{ t('gear.import.previewTitle') }}
      </h3>

      <div class="space-y-2 text-sm">
        <div v-for="(container, idx) in previewResult.containers" :key="idx" class="border-l-2 pl-3">
          <div class="font-medium">
            {{ container.name }} ({{ container.items.length }} {{ t('gear.import.items') }})
          </div>
          <ul class="text-xs text-muted-foreground mt-1 space-y-0.5">
            <li v-for="(item, itemIdx) in container.items.slice(0, 5)" :key="itemIdx">
              {{ item.name }}
              <span v-if="item.brand" class="text-primary">{{ item.brand }}</span>
              <span v-if="item.quantity > 1">x{{ item.quantity }}</span>
            </li>
            <li v-if="container.items.length > 5" class="italic">
              {{ t('gear.import.andMore', { count: container.items.length - 5 }) }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
