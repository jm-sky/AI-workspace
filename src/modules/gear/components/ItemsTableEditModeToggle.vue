<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Label from '@/components/ui/label/Label.vue'
import Switch from '@/components/ui/switch/Switch.vue'
import { config } from '@/shared/config/config'
import { useItemsTableEditMode } from '../composables/useItemsTableEditMode'

const { t } = useI18n()
const { editMode } = useItemsTableEditMode()

</script>

<template>
  <div v-if="config.features.inlineEditing.enabled" class="flex items-center space-x-2 px-1">
    <Label for="airplane-mode">
      {{ editMode ? t('gear.actions.disableInlineEditing') : t('gear.actions.enableInlineEditing') }}
    </Label>
    <Switch id="airplane-mode" v-model="editMode" />
  </div>
</template>

