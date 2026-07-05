<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { Edit, InfoIcon, Plus, Trash2 } from 'lucide-vue-next'
import { useForm } from 'vee-validate'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { FormField, FormItem, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { useGearSettings } from '@/modules/gear/composables/useGearSettings'
import type { IUserContainerType } from '@/modules/gear/types/gearSettings.types'

const { t } = useI18n()
const { customContainerTypes, addContainerType, updateContainerType, removeContainerType } = useGearSettings()

const editingId = ref<string | null>(null)

const containerTypeSchema = z.object({
  value: z.string().min(1, t('settings.containerTypes.valueRequired')),
})

const { handleSubmit, setValues, resetForm, values } = useForm({
  validationSchema: toTypedSchema(containerTypeSchema),
  initialValues: {
    value: '',
  },
})

const onSubmit = handleSubmit(async (formValues) => {
  if (editingId.value) {
    // Edit mode
    const containerType = customContainerTypes.value.find(t => t.id === editingId.value)
    if (!containerType) return

    const updated: IUserContainerType = {
      ...containerType,
      value: formValues.value.trim(),
      updatedAt: new Date().toISOString(),
    }

    await updateContainerType(updated)
    editingId.value = null
  } else {
    // Add mode
    const now = new Date().toISOString()
    const containerType: IUserContainerType = {
      id: crypto.randomUUID(),
      value: formValues.value.trim(),
      createdAt: now,
      updatedAt: now,
    }

    await addContainerType(containerType)
  }

  resetForm()
})

const handleEdit = (containerType: IUserContainerType) => {
  editingId.value = containerType.id
  setValues({ value: containerType.value })
}

const handleCancel = () => {
  editingId.value = null
  resetForm()
}

const handleDelete = async (id: string) => {
  if (confirm(t('settings.containerTypes.deleteConfirm'))) {
    await removeContainerType(id)
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>{{ t('settings.containerTypes.title') }}</CardTitle>
      <CardDescription>
        {{ t('settings.containerTypes.description') }}
      </CardDescription>
    </CardHeader>
    <CardContent class="space-y-4">
      <!-- Add New Container Type Form -->
      <form @submit="onSubmit">
        <div class="border rounded-lg p-4 space-y-3">
          <h4 class="font-medium text-sm">
            {{ editingId ? t('settings.containerTypes.edit') : t('settings.containerTypes.add') }}
          </h4>
          <div class="flex gap-2">
            <FormField v-slot="{ componentField }" name="value">
              <FormItem class="flex-1">
                <Input
                  v-bind="componentField"
                  :placeholder="t('settings.containerTypes.valuePlaceholder')"
                />
                <FormMessage />
              </FormItem>
            </FormField>
            <Button
              type="submit"
              :disabled="!values.value?.trim()"
            >
              <Plus v-if="!editingId" class="size-4" />
              <Edit v-else class="size-4" />
              {{ editingId ? t('settings.common.save') : t('settings.common.add') }}
            </Button>
            <Button
              v-if="editingId"
              type="button"
              variant="outline"
              @click="handleCancel"
            >
              {{ t('settings.containerTypes.cancel') }}
            </Button>
          </div>
        </div>
      </form>

      <!-- Container Types List -->
      <div v-if="customContainerTypes.length > 0" class="space-y-2">
        <div
          v-for="containerType in customContainerTypes"
          :key="containerType.id"
          class="flex flex-col sm:flex-row sm:items-center justify-between p-3 border rounded-lg gap-3"
        >
          <div class="flex-1">
            <div class="text-sm">
              {{ containerType.value }}
            </div>
          </div>
          <div class="flex gap-2 sm:shrink-0">
            <Button
              size="sm"
              variant="outline"
              @click="handleEdit(containerType)"
            >
              <Edit class="size-4" />
            </Button>
            <Button
              size="sm"
              variant="destructive"
              @click="handleDelete(containerType.id)"
            >
              <Trash2 class="size-4" />
            </Button>
          </div>
        </div>
      </div>
      <div v-else class="flex items-center justify-center gap-2 text-sm py-6 text-muted-foreground">
        <InfoIcon class="size-4 inline" />
        {{ t('settings.containerTypes.empty') }}
      </div>
    </CardContent>
  </Card>
</template>

