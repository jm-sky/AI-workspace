<!--
  Textarea with Markdown Preview Component
  Provides a textarea for editing Markdown with a preview mode toggle
-->
<script setup lang="ts">
import { useVModel } from '@vueuse/core'
import { computed, ref, useAttrs } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import Textarea from '@/components/ui/textarea/Textarea.vue'
import { cn } from '@/lib/utils'
import MarkdownRenderer from './MarkdownRenderer.vue'
import type { HTMLAttributes } from 'vue'

type Mode = 'edit' | 'preview'

const props = defineProps<{
  class?: HTMLAttributes['class']
  defaultValue?: string | number
  modelValue?: string | number
  placeholder?: string
  rows?: number
  disabled?: boolean
}>()

const emits = defineEmits<{
  (e: 'update:modelValue', payload: string | number): void
}>()

const { t } = useI18n()
const attrs = useAttrs()

const modelValue = useVModel(props, 'modelValue', emits, {
  passive: true,
  defaultValue: props.defaultValue,
})

const mode = ref<Mode>('edit')

const isPreview = computed<boolean>(() => mode.value === 'preview')
</script>

<template>
  <div class="border border-border rounded-lg">
    <!-- Mode toggle buttons -->
    <div class="flex gap-2 border-b px-1 py-0.5">
      <Button
        v-if="isPreview"
        variant="ghost"
        size="xs"
        class="text-sm"
        @click="mode = 'edit'"
      >
        {{ t('common.edit', 'Edit') }}
      </Button>
      <Button
        v-if="!isPreview"
        variant="ghost"
        size="xs"
        class="text-sm"
        @click="mode = 'preview'"
      >
        {{ t('common.preview', 'Preview') }}
      </Button>
    </div>

    <!-- Edit mode -->
    <div v-if="mode === 'edit'">
      <Textarea
        v-model="modelValue"
        v-bind="attrs"
        :placeholder="placeholder"
        :rows="rows ?? 3"
        :disabled="disabled"
        :class="cn('border-none rounded-none', props.class)"
      />
    </div>

    <!-- Preview mode -->
    <div v-else :class="cn('min-h-[80px] w-full px-3 py-2', props.class)">
      <MarkdownRenderer
        :content="String(modelValue ?? '')"
      />
    </div>

    <div v-if="isPreview" class="text-xs text-muted-foreground border-t p-2">
      {{ t('markdown.showingPreview', 'Showing preview') }}
    </div>
    <div v-if="!isPreview" class="text-xs text-muted-foreground border-t p-2">
      {{ t('markdown.supported', 'Markdown is supported') }}
    </div>
  </div>
</template>
