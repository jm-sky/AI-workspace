<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { refAutoReset } from '@vueuse/core'
import { CheckCircleIcon, Settings } from 'lucide-vue-next'
import { useForm } from 'vee-validate'
import { watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import Separator from '@/components/ui/separator/Separator.vue'
import { useGearSettings } from '@/modules/gear/composables/useGearSettings'
import { preferredWeightUnitEnum } from '@/modules/gear/utils/weightUnits'
import { useSettings } from '@/modules/settings/composables/useSettings'
import { config } from '@/shared/config/config'
import CurrencySelect from './inputs/CurrencySelect.vue'
import WeightUnitSelect from './inputs/WeightUnitSelect.vue'
import type { TGearWeightUnit } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()

const didSucceed = refAutoReset(false, 3000)

const settingsSchema = z.object({
  preferredWeightUnit: preferredWeightUnitEnum,
  defaultCurrency: z.string().optional(),
  defaultContainersPublic: z.boolean().optional(),
})

const { settings, updateSettings, defaultCurrency } = useGearSettings()
const { settings: appSettings, updateSettings: updateAppSettings } = useSettings()

const { handleSubmit, setValues, isSubmitting } = useForm({
  validationSchema: toTypedSchema(settingsSchema),
  initialValues: {
    preferredWeightUnit: config.defaults.preferredWeightUnit,
    defaultCurrency: defaultCurrency.value,
    defaultContainersPublic: appSettings.value?.defaultContainersPublic ?? false,
  },
})

watch(() => settings.value, (val) => {
  if (val) {
    setValues({
      preferredWeightUnit: val.preferredWeightUnit ?? config.defaults.preferredWeightUnit,
      defaultCurrency: defaultCurrency.value,
      defaultContainersPublic: appSettings.value?.defaultContainersPublic ?? false,
    })
  }
}, { immediate: true })

watch(() => appSettings.value, (val) => {
  if (val) {
    setValues({
      defaultContainersPublic: val.defaultContainersPublic ?? false,
    })
  }
}, { immediate: true })

const onSubmit = handleSubmit(async (values) => {
  // Update gear settings
  updateSettings({
    preferredWeightUnit: values.preferredWeightUnit as TGearWeightUnit,
    defaultCurrency: values.defaultCurrency,
  })

  // Update app settings (defaultContainersPublic)
  await updateAppSettings({
    defaultContainersPublic: values.defaultContainersPublic,
  })

  didSucceed.value = true
})
</script>

<template>
  <Card>
    <CardHeader>
      <div class="flex items-center gap-2">
        <Settings :size="20" />
        <CardTitle>{{ t('settings.preferences.title') }}</CardTitle>
      </div>
      <CardDescription>
        {{ t('settings.preferences.description') }}
      </CardDescription>
    </CardHeader>
    <CardContent>
      <form class="flex flex-col gap-6" :class="{ 'opacity-50': isSubmitting }" @submit="onSubmit">
        <div class="grid gap-6 md:grid-cols-2">
          <!-- Preferred Weight Unit -->
          <div class="space-y-3">
            <FormField v-slot="{ componentField }" name="preferredWeightUnit">
              <FormItem>
                <FormLabel required>
                  {{ t('settings.preferences.preferredWeightUnit.label') }}
                </FormLabel>
                <p class="text-sm text-muted-foreground">
                  {{ t('settings.preferences.preferredWeightUnit.subtitle') }}
                </p>
                <FormControl>
                  <WeightUnitSelect v-bind="componentField" />
                </FormControl>
                <FormMessage />
              </FormItem>
            </FormField>
          </div>

          <!-- Default Currency -->
          <div class="space-y-3">
            <FormField v-slot="{ componentField }" name="defaultCurrency">
              <FormItem>
                <FormLabel>
                  {{ t('settings.preferences.defaultCurrency.label') }}
                </FormLabel>
                <p class="text-sm text-muted-foreground">
                  {{ t('settings.preferences.defaultCurrency.subtitle') }}
                </p>
                <FormControl>
                  <CurrencySelect v-bind="componentField" />
                </FormControl>
                <FormMessage />
              </FormItem>
            </FormField>
          </div>
        </div>

        <Separator />

        <!-- Default Containers Public -->
        <FormField v-slot="{ componentField, handleChange }" name="defaultContainersPublic">
          <FormItem v-slot="{ id }" class="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
            <Checkbox
              :id="id"
              :model-value="componentField.modelValue"
              @update:model-value="handleChange"
            />
            <div class="flex-1 space-y-1">
              <FormLabel :label="$t('settings.page.sections.defaultContainersPublic.label')" class="cursor-pointer" />
              <p class="text-sm text-muted-foreground">
                {{ $t('settings.page.sections.defaultContainersPublic.subtitle') }}
              </p>
            </div>
            <FormMessage />
          </FormItem>
        </FormField>


        <div class="flex justify-end gap-4">
          <Transition
            enter-from-class="opacity-0 -translate-y-2"
            enter-to-class="opacity-100 translate-y-0"
            enter-active-class="transition-all duration-300"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 translate-y-2"
            leave-active-class="transition-all duration-300"
          >
            <div v-if="didSucceed" class="flex items-center gap-2 text-success">
              <CheckCircleIcon class="size-4" />
              {{ t('settings.preferences.saved') }}
            </div>
          </Transition>
          <Button type="submit" :loading="isSubmitting">
            {{ t('settings.preferences.save') }}
          </Button>
        </div>
      </form>
    </CardContent>
  </Card>
</template>

