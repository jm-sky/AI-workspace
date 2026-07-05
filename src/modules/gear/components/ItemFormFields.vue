<script setup lang="ts">
import { useFocus } from '@vueuse/core'
import { nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import ShelfLifeInput from '@/components/ui/shelf-life-input/ShelfLifeInput.vue'
import WeightInputWithUnitPicker from '@/components/ui/weight-input/WeightInputWithUnitPicker.vue'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { useGearSettings } from '../composables/useGearSettings'
import BrandAutocomplete from './inputs/BrandAutocomplete.vue'
import CategorySelect from './inputs/CategorySelect.vue'
import ColorAutocomplete from './inputs/ColorAutocomplete.vue'
import CurrencySelect from './inputs/CurrencySelect.vue'
import PrioritySelect from './inputs/PrioritySelect.vue'
import QualitySelect from './inputs/QualitySelect.vue'
import StatusSelect from './inputs/StatusSelect.vue'
import TextareaWithMarkdownPreview from './TextareaWithMarkdownPreview.vue'

defineProps<{
  item?: IGearItemV2
  loading?: boolean
  hideName?: boolean
}>()

const emit = defineEmits<{
  cancel: []
  nameBlur: []
  recognizeParameters: []
  setExpirationDate: []
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
    <FormField
      v-if="!hideName"
      v-slot="{ componentField }"
      name="name"
    >
      <FormItem>
        <FormLabel :label="t('gear.item.name')" required />
        <Input
          ref="nameInputRef"
          v-bind="componentField"
          :placeholder="t('gear.item.name')"
          @blur="emit('nameBlur')"
        />
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Category -->
    <FormField v-slot="{ value, handleChange }" name="category">
      <FormItem>
        <FormLabel :label="t('gear.item.category')" required />
        <CategorySelect :model-value="value" @update:model-value="handleChange" />
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Quantity and Weight -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <FormField v-slot="{ componentField }" name="quantity">
        <FormItem>
          <FormLabel :label="t('gear.item.quantity')" required />
          <Input
            v-bind="componentField"
            type="number"
            :placeholder="t('gear.item.quantity')"
            min="1"
          />
          <FormMessage />
        </FormItem>
      </FormField>

      <FormField v-slot="{ value: weightValue, handleChange: handleWeightChange }" name="weight">
        <FormField v-slot="{ value: unitValue, handleChange: handleUnitChange }" name="weightUnit">
          <FormItem>
            <FormLabel :label="t('gear.item.weight')" required />
            <WeightInputWithUnitPicker
              :model-value="weightValue"
              :unit="unitValue"
              :placeholder="t('gear.item.weight')"
              :required="true"
              @update:model-value="handleWeightChange"
              @update:unit="handleUnitChange"
            />
            <FormMessage />
          </FormItem>
        </FormField>
      </FormField>
    </div>

    <!-- Priority and Status -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <FormField v-slot="{ value, handleChange }" name="priority">
        <FormItem>
          <FormLabel :label="t('gear.item.priority')" required />
          <PrioritySelect :model-value="value" @update:model-value="handleChange" />
          <FormMessage />
        </FormItem>
      </FormField>

      <FormField v-slot="{ value, handleChange }" name="status">
        <FormItem>
          <FormLabel :label="t('gear.item.status')" required />
          <StatusSelect :model-value="value" @update:model-value="handleChange" />
          <FormMessage />
        </FormItem>
      </FormField>
    </div>

    <!-- Expiration Date and Shelf Life -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <!-- Expiration Date -->
      <FormField v-slot="{ componentField }" name="expirationDate">
        <FormItem>
          <FormLabel :label="t('gear.item.expirationDate')" />
          <Input
            v-bind="componentField"
            type="date"
            :placeholder="t('gear.item.expirationDate')"
          />
          <FormMessage />
        </FormItem>
      </FormField>

      <!-- Shelf Life -->
      <FormField v-slot="{ value: shelfLifeValue, handleChange: handleShelfLifeValueChange }" name="shelfLifeValue">
        <FormField v-slot="{ value: shelfLifeUnit, handleChange: handleShelfLifeUnitChange }" name="shelfLifeUnit">
          <FormItem>
            <FormLabel :label="t('gear.item.shelfLife')" />
            <ShelfLifeInput
              :model-value="shelfLifeValue"
              :unit="shelfLifeUnit"
              :placeholder="t('gear.item.shelfLifePlaceholder')"
              @update:model-value="handleShelfLifeValueChange"
              @update:unit="handleShelfLifeUnitChange"
            />
            <FormMessage />
          </FormItem>
        </FormField>
      </FormField>
    </div>

    <!-- Set Expiration Date Button -->
    <FormField v-slot="{ value: shelfLifeValue }" name="shelfLifeValue">
      <FormField v-slot="{ value: shelfLifeUnit }" name="shelfLifeUnit">
        <div v-if="shelfLifeValue && shelfLifeUnit">
          <Button
            type="button"
            variant="outline"
            size="sm"
            @click="$emit('setExpirationDate')"
          >
            {{ t('gear.actions.setExpirationDate') }}
          </Button>
          <p class="text-sm text-muted-foreground mt-2">
            {{ t('gear.item.shelfLifeDescription') }}
          </p>
        </div>
      </FormField>
    </FormField>

    <!-- Notes -->
    <FormField v-slot="{ componentField }" name="notes">
      <FormItem>
        <FormLabel :label="t('gear.item.notes')" />
        <TextareaWithMarkdownPreview
          v-bind="componentField"
          :placeholder="t('gear.item.notes')"
          :rows="3"
        />
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Extended Fields Section -->
    <div class="border-t pt-6 space-y-6">
      <h3 class="text-lg font-semibold text-muted-foreground">
        {{ t('gear.item.extendedFields') }}
      </h3>

      <!-- Price and Currency -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FormField v-slot="{ componentField }" name="price">
          <FormItem>
            <FormLabel :label="t('gear.item.price')" />
            <Input
              v-bind="componentField"
              type="number"
              :placeholder="t('gear.item.price')"
              min="0"
              step="0.01"
            />
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ value, handleChange }" name="currency">
          <FormItem>
            <FormLabel :label="t('gear.item.currency')" />
            <CurrencySelect :model-value="value || defaultCurrency" @update:model-value="handleChange" />
            <FormMessage />
          </FormItem>
        </FormField>
      </div>

      <!-- Brand -->
      <FormField v-slot="{ value, handleChange }" name="brand">
        <FormItem>
          <FormLabel :label="t('gear.item.brand')" />
          <BrandAutocomplete
            :value="value"
            @update:value="handleChange"
          />
          <FormMessage />
        </FormItem>
      </FormField>

      <!-- URL -->
      <FormField v-slot="{ componentField }" name="url">
        <FormItem>
          <FormLabel :label="t('gear.item.url')" />
          <Input
            v-bind="componentField"
            type="url"
            :placeholder="t('gear.item.url')"
          />
          <FormMessage />
        </FormItem>
      </FormField>

      <!-- Color and Quality -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FormField v-slot="{ value, handleChange }" name="color">
          <FormItem>
            <FormLabel :label="t('gear.item.color')" />
            <ColorAutocomplete
              :value="value"
              class="w-full"
              @update:value="handleChange"
            />
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ value, handleChange }" name="quality">
          <FormItem>
            <FormLabel :label="t('gear.item.quality')" />
            <QualitySelect :model-value="value" @update:model-value="handleChange" />
            <FormMessage />
          </FormItem>
        </FormField>
      </div>

      <!-- Wearable and Consumable -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FormField v-slot="{ componentField, handleChange }" name="wearable">
          <FormItem v-slot="{ id }" class="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
            <div class="flex-1 space-y-1">
              <FormLabel :label="t('gear.item.wearable')" class="cursor-pointer" />
              <p class="text-sm text-muted-foreground">
                {{ t('gear.item.wearableDescription') }}
              </p>
            </div>
            <Checkbox
              :id="id"
              :model-value="componentField.modelValue"
              @update:model-value="handleChange"
            />
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ componentField, handleChange }" name="consumable">
          <FormItem v-slot="{ id }" class="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
            <div class="flex-1 space-y-1">
              <FormLabel :label="t('gear.item.consumable')" class="cursor-pointer" />
              <p class="text-sm text-muted-foreground">
                {{ t('gear.item.consumableDescription') }}
              </p>
            </div>
            <Checkbox
              :id
              :model-value="componentField.modelValue"
              @update:model-value="handleChange"
            />
            <FormMessage />
          </FormItem>
        </FormField>
      </div>

      <!-- Show on Container (Implementation postponed - use container.showItemImages instead) -->
      <FormField v-slot="{ componentField, handleChange }" name="showOnContainer">
        <FormItem v-slot="{ id }" class="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4 opacity-50">
          <div class="flex-1 space-y-1">
            <FormLabel :label="t('gear.item.showOnContainer')" class="cursor-not-allowed" />
            <p class="text-sm text-muted-foreground">
              {{ t('gear.item.showOnContainerDescription') }}
              <span class="text-xs italic"> (Implementation postponed)</span>
            </p>
          </div>
          <Checkbox
            :id
            :model-value="componentField.modelValue"
            :disabled="true"
            @update:model-value="handleChange"
          />
          <FormMessage />
        </FormItem>
      </FormField>
    </div>

    <div class="border-t my-4" />

    <!-- Actions -->
    <div class="flex flex-col sm:flex-row justify-between gap-3">
      <Button
        type="button"
        variant="outline"
        @click="$emit('recognizeParameters')"
      >
        {{ t('gear.actions.recognizeParameters') }}
      </Button>
      <div class="flex gap-3">
        <Button
          type="button"
          variant="outline"
          class="flex-1"
          @click="handleCancel"
        >
          {{ t('gear.actions.cancel') }}
        </Button>
        <Button type="submit" class="flex-1" :loading>
          {{ t('gear.actions.save') }}
        </Button>
      </div>
    </div>
  </div>
</template>

