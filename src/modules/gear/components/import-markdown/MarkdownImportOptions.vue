<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'

const { t } = useI18n()

defineProps<{
  recognizeFromName: boolean
  importMode: 'create' | 'update'
  hasUuids: boolean
  showPreview: boolean
}>()

const recognizeFromNameModel = defineModel<boolean>('recognizeFromName', { required: true })
const importModeModel = defineModel<'create' | 'update'>('importMode', { required: true })
</script>

<template>
  <div class="space-y-4">
    <!-- Recognition Options -->
    <div class="flex items-center space-x-2">
      <Checkbox id="recognize-from-name" v-model="recognizeFromNameModel" />
      <Label for="recognize-from-name" class="text-sm font-normal cursor-pointer">
        {{ t('gear.import.recognizeFromName') }}
        <span class="text-xs text-muted-foreground block">
          {{ t('gear.import.recognizeFromNameDesc') }}
        </span>
      </Label>
    </div>

    <!-- Import Mode Selection (shown only when UUIDs detected and preview is shown) -->
    <div v-if="hasUuids && showPreview" class="border rounded-lg p-4 space-y-3">
      <Label class="text-sm font-medium">{{ t('gear.import.mode') }}</Label>
      <RadioGroup v-model="importModeModel" class="gap-3">
        <div class="flex items-center space-x-2">
          <RadioGroupItem id="mode-update" value="update" />
          <Label for="mode-update" class="font-normal cursor-pointer">
            {{ t('gear.import.modeUpdate') }}
            <span class="text-xs text-muted-foreground block">
              {{ t('gear.import.modeUpdateDesc') }}
            </span>
          </Label>
        </div>
        <div class="flex items-center space-x-2">
          <RadioGroupItem id="mode-create" value="create" />
          <Label for="mode-create" class="font-normal cursor-pointer">
            {{ t('gear.import.modeCreate') }}
            <span class="text-xs text-muted-foreground block">
              {{ t('gear.import.modeCreateDesc') }}
            </span>
          </Label>
        </div>
      </RadioGroup>
    </div>
  </div>
</template>
