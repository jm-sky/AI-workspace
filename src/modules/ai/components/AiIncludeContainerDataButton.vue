<script setup lang="ts">
import { CogIcon } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import OnOffButton from '@/components/ui/button/OnOffButton.vue'

const { t } = useI18n()

const includeContainerData = defineModel<boolean>('includeContainerData', { required: true })

const emit = defineEmits<{
  toggleContextConfig: []
}>()
</script>

<template>
  <OnOffButton
    v-model:on="includeContainerData"
    :label="t('ai.chat.includeContainerData.label')"
  >
    <template #after>
      <button type="button" class="cursor-pointer hover:text-primary hover:bg-background rounded-full p-0.5 -mr-0.5" @click.stop.capture="emit('toggleContextConfig')">
        <CogIcon class="size-4" />
      </button>
    </template>
  </OnOffButton>
</template>
