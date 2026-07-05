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
import type { IUserCategory } from '@/modules/gear/types/gearSettings.types'

const { t } = useI18n()
const { customCategories, addCategory, updateCategory, removeCategory } = useGearSettings()

const editingId = ref<string | null>(null)

const categorySchema = z.object({
  value: z.string().min(1, t('settings.categories.valueRequired')),
})

const { handleSubmit, setValues, resetForm, values } = useForm({
  validationSchema: toTypedSchema(categorySchema),
  initialValues: {
    value: '',
  },
})

const onSubmit = handleSubmit(async (formValues) => {
  if (editingId.value) {
    // Edit mode
    const category = customCategories.value.find(c => c.id === editingId.value)
    if (!category) return

    const updated: IUserCategory = {
      ...category,
      value: formValues.value.trim(),
      updatedAt: new Date().toISOString(),
    }

    await updateCategory(updated)
    editingId.value = null
  } else {
    // Add mode
    const now = new Date().toISOString()
    const category: IUserCategory = {
      id: crypto.randomUUID(),
      value: formValues.value.trim(),
      createdAt: now,
      updatedAt: now,
    }

    await addCategory(category)
  }

  resetForm()
})

const handleEdit = (category: IUserCategory) => {
  editingId.value = category.id
  setValues({ value: category.value })
}

const handleCancel = () => {
  editingId.value = null
  resetForm()
}

const handleDelete = async (id: string) => {
  if (confirm(t('settings.categories.deleteConfirm'))) {
    await removeCategory(id)
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>{{ t('settings.categories.title') }}</CardTitle>
      <CardDescription>
        {{ t('settings.categories.description') }}
      </CardDescription>
    </CardHeader>
    <CardContent class="space-y-4">
      <!-- Add New Category Form -->
      <form @submit="onSubmit">
        <div class="border rounded-lg p-4 space-y-3">
          <h4 class="font-medium text-sm">
            {{ editingId ? t('settings.categories.edit') : t('settings.categories.add') }}
          </h4>
          <div class="flex gap-2">
            <FormField v-slot="{ componentField }" name="value">
              <FormItem class="flex-1">
                <Input
                  v-bind="componentField"
                  :placeholder="t('settings.categories.valuePlaceholder')"
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
              {{ t('settings.categories.cancel') }}
            </Button>
          </div>
        </div>
      </form>

      <!-- Categories List -->
      <div v-if="customCategories.length > 0" class="space-y-2">
        <div
          v-for="category in customCategories"
          :key="category.id"
          class="flex flex-col sm:flex-row sm:items-center justify-between p-3 border rounded-lg gap-3"
        >
          <div class="flex-1">
            <div class="text-sm">
              {{ category.value }}
            </div>
          </div>
          <div class="flex gap-2 sm:shrink-0">
            <Button
              size="sm"
              variant="outline"
              @click="handleEdit(category)"
            >
              <Edit class="size-4" />
            </Button>
            <Button
              size="sm"
              variant="destructive"
              @click="handleDelete(category.id)"
            >
              <Trash2 class="size-4" />
            </Button>
          </div>
        </div>
      </div>
      <div v-else class="flex items-center justify-center gap-2 text-sm py-6 text-muted-foreground">
        <InfoIcon class="size-4 inline" />
        {{ t('settings.categories.empty') }}
      </div>
    </CardContent>
  </Card>
</template>

