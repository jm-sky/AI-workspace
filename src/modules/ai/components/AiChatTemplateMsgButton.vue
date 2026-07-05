<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

export type TemplateMsgVariant = 'whatsUnnecessary' | 'whatsNeeded' | 'addRandomItem'

const { variant } = defineProps<{
  variant: TemplateMsgVariant
}>()

const emit = defineEmits<{
  prompt: [prompt: string]
}>()

const { t } = useI18n()

const label = computed(() => {
  return t(`ai.chat.templateMessages.${variant}.label`)
})

const makePrompt = () => {
  emit('prompt', t(`ai.chat.templateMessages.${variant}.prompt`))
}
</script>

<template>
  <button type="button" class="cursor-pointer text-primary hover:opacity-50" @click="makePrompt">
    {{ label }}
  </button>
</template>
