<script setup lang="ts">
import { useFocus } from '@vueuse/core'
import { nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import WeightInputWithUnitPicker from '@/components/ui/weight-input/WeightInputWithUnitPicker.vue'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { useGearSettings } from '../composables/useGearSettings'
import BrandAutocomplete from './inputs/BrandAutocomplete.vue'
import ContainerColorPicker from './inputs/ContainerColorPicker.vue'
import ContainerTypeSelect from './inputs/ContainerTypeSelect.vue'
import CurrencySelect from './inputs/CurrencySelect.vue'
import TextareaWithMarkdownPreview from './TextareaWithMarkdownPreview.vue'

const _props = defineProps<{
  container?: IGearItemV2
  loading?: boolean
}>()

const emit = defineEmits<{
  cancel: []
  nameBlur: []
  recognizeParameters: []
}>()

const { t } = useI18n()
const { defaultCurrency } = useGearSettings()

// Auto-focus na pierwszym polu
const nameInputRef = ref<HTMLInputElement | undefined>(undefined)
nextTick(() => {
  useFocus(nameInputRef)
})

// Cancel handler
const handleCancel = () => {
  emit('cancel')
}
</script>

<template>
  <div class="space-y-6">
    <!-- Name -->
    <FormField v-slot="{ componentField }" name="name">
      <FormItem>
        <FormLabel :label="t('gear.container.name')" required />
        <Input
          ref="nameInputRef"
          v-bind="componentField"
          :placeholder="t('gear.container.name')"
          @blur="emit('nameBlur')"
        />
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Description -->
    <FormField v-slot="{ componentField }" name="description">
      <FormItem>
        <FormLabel :label="t('gear.container.description')" />
        <TextareaWithMarkdownPreview
          v-bind="componentField"
          :placeholder="t('gear.container.description')"
          :rows="3"
        />
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Type -->
    <FormField v-slot="{ value, handleChange }" name="type">
      <FormItem>
        <FormLabel :label="t('gear.container.type')" required />
        <ContainerTypeSelect :model-value="value" @update:model-value="handleChange" />
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Color -->
    <FormField v-slot="{ value, handleChange }" name="color">
      <FormItem>
        <FormLabel :label="t('gear.container.color')" />
        <ContainerColorPicker
          :value="value"
          @update:value="handleChange"
        />
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Is Public -->
    <FormField v-slot="{ componentField, handleChange }" name="isPublic">
      <FormItem v-slot="{ id }" class="flex flex-row items-start space-x-3 space-y-0 rounded-md border border-blue-200 bg-blue-50 dark:bg-blue-950/20 dark:border-blue-800 p-4">
        <Checkbox
          :id="id"
          :model-value="componentField.modelValue"
          @update:model-value="handleChange"
        />
        <div class="flex-1 space-y-1">
          <FormLabel :label="t('gear.container.isPublic')" class="cursor-pointer" />
          <p class="text-sm text-muted-foreground">
            {{ t('gear.container.isPublicDescription') }}
          </p>
        </div>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Show Item Images -->
    <FormField v-slot="{ componentField, handleChange }" name="showItemImages">
      <FormItem v-slot="{ id }" class="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
        <Checkbox
          :id
          :model-value="componentField.modelValue"
          @update:model-value="handleChange"
        />
        <div class="flex-1 space-y-1">
          <FormLabel :label="t('gear.container.showItemImages')" class="cursor-pointer" />
          <p class="text-sm text-muted-foreground">
            {{ t('gear.container.showItemImagesDescription') }}
          </p>
        </div>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Hide When Nested -->
    <FormField v-slot="{ componentField, handleChange }" name="hideWhenNested">
      <FormItem v-slot="{ id }" class="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
        <Checkbox
          :id="id"
          :model-value="componentField.modelValue"
          @update:model-value="handleChange"
        />
        <div class="flex-1 space-y-1">
          <FormLabel :label="t('gear.container.hideWhenNested')" class="cursor-pointer" />
          <p class="text-sm text-muted-foreground">
            {{ t('gear.container.hideWhenNestedDescription') }}
          </p>
        </div>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Extended Fields Section -->
    <div class="border-t pt-6 space-y-6">
      <h3 class="text-lg font-semibold text-muted-foreground">
        {{ t('gear.container.extendedFields') }}
      </h3>

      <!-- Brand -->
      <FormField v-slot="{ value, handleChange }" name="brand">
        <FormItem>
          <FormLabel :label="t('gear.container.brand')" />
          <BrandAutocomplete
            :value="value"
            :placeholder="t('gear.container.brand')"
            @update:value="handleChange"
          />
          <FormMessage />
        </FormItem>
      </FormField>

      <!-- Price and Currency -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FormField v-slot="{ componentField }" name="price">
          <FormItem>
            <FormLabel :label="t('gear.container.price')" />
            <Input
              v-bind="componentField"
              type="number"
              :placeholder="t('gear.container.price')"
              min="0"
              step="0.01"
            />
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ value, handleChange }" name="currency">
          <FormItem>
            <FormLabel :label="t('gear.container.currency')" />
            <CurrencySelect :model-value="value || defaultCurrency" @update:model-value="handleChange" />
            <FormMessage />
          </FormItem>
        </FormField>
      </div>

      <!-- Weight and Weight Unit -->
      <FormField v-slot="{ value: weightValue, handleChange: handleWeightChange }" name="weight">
        <FormField v-slot="{ value: unitValue, handleChange: handleUnitChange }" name="weightUnit">
          <FormItem>
            <FormLabel :label="t('gear.container.weight')" />
            <WeightInputWithUnitPicker
              :model-value="weightValue"
              :unit="unitValue"
              :placeholder="t('gear.container.weight')"
              @update:model-value="handleWeightChange"
              @update:unit="handleUnitChange"
            />
            <FormMessage />
          </FormItem>
        </FormField>
      </FormField>

      <!-- Max Weight and Max Weight Unit -->
      <FormField v-slot="{ value: maxWeightValue, handleChange: handleMaxWeightChange }" name="maxWeight">
        <FormField v-slot="{ value: maxUnitValue, handleChange: handleMaxUnitChange }" name="maxWeightUnit">
          <FormItem>
            <FormLabel :label="t('gear.container.maxWeight')" />
            <WeightInputWithUnitPicker
              :model-value="maxWeightValue"
              :unit="maxUnitValue || 'g'"
              :placeholder="t('gear.container.maxWeight')"
              @update:model-value="handleMaxWeightChange"
              @update:unit="handleMaxUnitChange"
            />
            <FormMessage />
          </FormItem>
        </FormField>
      </FormField>

      <!-- URL -->
      <FormField v-slot="{ componentField }" name="url">
        <FormItem>
          <FormLabel :label="t('gear.container.url')" />
          <Input
            v-bind="componentField"
            type="url"
            :placeholder="t('gear.container.url')"
          />
          <FormMessage />
        </FormItem>
      </FormField>
    </div>

    <!-- Actions -->
    <Button
      type="button"
      variant="outline"
      @click="$emit('recognizeParameters')"
    >
      {{ t('gear.actions.recognizeParameters') }}
    </Button>
    <div class="flex flex-col sm:flex-row justify-end gap-3">
      <Button type="button" variant="outline" @click="handleCancel">
        {{ t('gear.actions.cancel') }}
      </Button>
      <Button type="submit" :loading>
        {{ t('gear.actions.save') }}
      </Button>
    </div>
  </div>
</template>

