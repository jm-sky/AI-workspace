<script setup lang="ts">
import { useFocus } from '@vueuse/core'
import { nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import WeightInputWithUnitPicker from '@/components/ui/weight-input/WeightInputWithUnitPicker.vue'
import BrandAutocomplete from '@/modules/gear/components/inputs/BrandAutocomplete.vue'
import CategorySelect from '@/modules/gear/components/inputs/CategorySelect.vue'
import ColorAutocomplete from '@/modules/gear/components/inputs/ColorAutocomplete.vue'
import CurrencySelect from '@/modules/gear/components/inputs/CurrencySelect.vue'
import QualitySelect from '@/modules/gear/components/inputs/QualitySelect.vue'
import TextareaWithMarkdownPreview from '@/modules/gear/components/TextareaWithMarkdownPreview.vue'
import { usePriceTierLabel } from '@/modules/gear/composables/usePriceTierLabel'
import type { IGlobalCatalogueItem, TCataloguePriceTier } from '@/modules/gear/types/catalogue.types'

defineProps<{
  item?: IGlobalCatalogueItem | null
  loading?: boolean
  isEditMode: boolean
}>()

const emit = defineEmits<{
  cancel: []
}>()

const { t } = useI18n()
const { getPriceTierLabel } = usePriceTierLabel()

const priceTiers: TCataloguePriceTier[] = ['low', 'medium', 'high']

const nameInputRef = ref<HTMLInputElement | undefined>(undefined)
nextTick(() => {
  useFocus(nameInputRef)
})
</script>

<template>
  <div class="space-y-6">
    <FormField v-slot="{ componentField }" name="name">
      <FormItem>
        <FormLabel :label="t('gear.item.name')" required />
        <Input
          ref="nameInputRef"
          v-bind="componentField"
          :placeholder="t('gear.item.name')"
        />
        <FormMessage />
      </FormItem>
    </FormField>

    <FormField v-slot="{ value, handleChange }" name="category">
      <FormItem>
        <FormLabel :label="t('gear.item.category')" required />
        <CategorySelect :model-value="value" @update:model-value="handleChange" />
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

    <FormField v-slot="{ componentField }" name="description">
      <FormItem>
        <FormLabel :label="t('gear.catalogue.description')" />
        <TextareaWithMarkdownPreview
          v-bind="componentField"
          :placeholder="t('gear.catalogue.description')"
          :rows="4"
        />
        <FormMessage />
      </FormItem>
    </FormField>

    <div class="border-t pt-6 space-y-6">
      <h3 class="text-lg font-semibold text-muted-foreground">
        {{ t('gear.item.extendedFields') }}
      </h3>

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

      <FormField v-slot="{ componentField }" name="model">
        <FormItem>
          <FormLabel :label="t('gear.catalogue.model')" />
          <Input
            v-bind="componentField"
            :placeholder="t('gear.catalogue.model')"
          />
          <FormMessage />
        </FormItem>
      </FormField>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FormField v-slot="{ value, handleChange }" name="priceTier">
          <FormItem>
            <FormLabel :label="t('gear.catalogue.priceTier')" />
            <Select :model-value="value ?? null" @update:model-value="handleChange">
              <SelectTrigger>
                <SelectValue :placeholder="t('gear.filters.all')" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem :value="null">
                  {{ t('gear.filters.all') }}
                </SelectItem>
                <SelectItem v-for="tier in priceTiers" :key="tier" :value="tier">
                  {{ getPriceTierLabel(tier) }}
                </SelectItem>
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ value, handleChange }" name="quality">
          <FormItem>
            <FormLabel :label="t('gear.catalogue.quality')" />
            <QualitySelect :model-value="value ?? null" @update:model-value="handleChange" />
            <FormMessage />
          </FormItem>
        </FormField>
      </div>

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
            <CurrencySelect :model-value="value || undefined" @update:model-value="handleChange" />
            <FormMessage />
          </FormItem>
        </FormField>
      </div>

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

      <FormField v-slot="{ componentField, handleChange }" name="isActive">
        <FormItem v-slot="{ id }" class="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
          <div class="flex-1 space-y-1">
            <FormLabel :label="t('gear.catalogue.isActive')" class="cursor-pointer" />
            <p class="text-sm text-muted-foreground">
              {{ t('gear.catalogue.isActive') }}
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

    <div class="border-t my-4" />

    <div class="flex flex-col sm:flex-row justify-end gap-3">
      <Button
        type="button"
        variant="outline"
        class="flex-1 sm:flex-none"
        @click="emit('cancel')"
      >
        {{ t('gear.actions.cancel') }}
      </Button>
      <Button type="submit" class="flex-1 sm:flex-none" :loading>
        {{ isEditMode ? t('gear.actions.save') : t('gear.catalogue.create.title') }}
      </Button>
    </div>
  </div>
</template>

