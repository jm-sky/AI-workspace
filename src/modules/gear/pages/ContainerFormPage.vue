<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { useDebounceFn } from '@vueuse/core'
import { useForm } from 'vee-validate'
import { watch, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useSettings } from '@/modules/settings/composables/useSettings'
import { useHandleError } from '@/shared/composables/useHandleError'
import { usePageTitle } from '@/shared/composables/usePageTitle'
import type { TContainerColor } from '../types/gear.types'
import type { ICreateGearItemV2Dto, IUpdateGearItemV2Dto } from '../types/gear.types.v2'
import ContainerFormFields from '../components/ContainerFormFields.vue'
import { useContainerOperationsV2 } from '../composables/internal/v2/useContainerOperationsV2'
import { useContainerV2 } from '../composables/useContainerV2'
import { useGearSettings } from '../composables/useGearSettings'
import { GearRoutePath } from '../routes'
import { CONTAINER_COLORS } from '../utils/containerColors'
import { recognizeContainerType } from '../utils/containerTypeRecognition'
import { createNavigationQuery, getFrom } from '../utils/navigationParams'
import { recognizeParameters } from '../utils/parameterRecognition'
import { type ContainerFormData, containerSchema } from '../utils/validation'
import { toBasicWeightUnit } from '../utils/weightUnits'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const { createContainer, updateContainer } = useContainerOperationsV2()
const { customBrands } = useGearSettings()
const { settings } = useSettings()
const { handleError } = useHandleError()
const { setTitle } = usePageTitle()

const containerId = route.params.id as string | undefined
const isEditMode: boolean = !!containerId

const { container } = useContainerV2(containerId)

// Set dynamic page title
watchEffect(() => {
  if (isEditMode && container.value?.name) {
    setTitle('gear.container.edit.title', { name: container.value.name })
  }
})

const getInitialValues = (): ContainerFormData => {
  if (container.value) {
    return {
      name: container.value.name,
      description: container.value.description ?? '',
      type: container.value.containerType ?? 'other',
      color: (container.value.color ?? 'default') as TContainerColor,
      hideWhenNested: container.value.hideWhenNested ?? false,
      isPublic: container.value.isPublic ?? false,
      brand: container.value.brand ?? '',
      price: container.value.price ?? undefined,
      weight: container.value.weight ?? undefined,
      weightUnit: toBasicWeightUnit(container.value.weightUnit) ?? 'kg',
      maxWeight: container.value.maxWeight ?? undefined,
      maxWeightUnit: toBasicWeightUnit(container.value.maxWeightUnit) ?? 'kg',
      url: container.value.url ?? '',
      showItemImages: container.value.showItemImages ?? false,
    }
  }
  // For new containers, use default from settings (will be updated via watch)
  return {
    name: '',
    description: '',
    type: 'other' as const,
    color: 'default' as const,
    hideWhenNested: false,
    isPublic: false, // Will be updated via watch when settings load
    brand: '',
    price: undefined,
    weight: undefined,
    weightUnit: 'kg' as const,
    maxWeight: undefined,
    maxWeightUnit: 'kg' as const,
    url: '',
    showItemImages: false,
  }
}

const { handleSubmit, isSubmitting, setFieldValue, values, setErrors } = useForm({
  validationSchema: toTypedSchema(containerSchema),
  initialValues: getInitialValues(),
})

// Watch for settings changes and update isPublic field for new containers
watch(() => settings.value?.defaultContainersPublic, (newValue) => {
  if (!isEditMode && newValue !== undefined) {
    // Update isPublic when settings load (only if still at initial false value)
    // This allows user to change it manually without it being overwritten
    const currentValue = values.isPublic
    if (currentValue === false && newValue === true) {
      setFieldValue('isPublic', newValue)
    } else if (currentValue === false && newValue === false) {
      // Keep it false if settings also say false
      setFieldValue('isPublic', false)
    }
  }
}, { immediate: true })

// Map item colors to container colors
const mapItemColorToContainerColor = (itemColor: string): TContainerColor | null => {
  const normalized = itemColor.toLowerCase().trim()

  // Map item colors to available container colors
  const colorMap: Record<string, TContainerColor> = {
    // Direct matches (colors that exist in TContainerColor)
    'orange': 'orange',
    'olive': 'olive',
    'tan': 'tan',
    'brown': 'brown',
    'black': 'black',
    'navy': 'navy',
    'jeans': 'jeans',
    'gray': 'gray',
    'grey': 'gray',
    'coyote': 'coyote',
    'khaki': 'khaki',
    'forestgreen': 'forestGreen',
    'forest-green': 'forestGreen',
    // Mappings from old colors to new colors
    'green': 'forestGreen',
    'blue': 'jeans',
    'red': 'orange',
    'yellow': 'tan',
    'purple': 'navy',
    'pink': 'orange',
    'teal': 'jeans',
    'indigo': 'navy',
    // Default fallback
    'default': 'default',
  }

  // Check direct match
  if (colorMap[normalized]) {
    return colorMap[normalized]
  }

  // Check if container color exists
  if (CONTAINER_COLORS.includes(normalized as TContainerColor)) {
    return normalized as TContainerColor
  }

  return null
}

// Auto-recognize type, color, and brand from name during typing (only for new containers, not when editing)
const autoRecognizeFromName = useDebounceFn(() => {
  if (isEditMode || !values.name || values.name.trim().length === 0) {
    return
  }

  // Recognize container type (only if type is 'other' or not set)
  if (values.type === 'other' || !values.type) {
    const detectedType = recognizeContainerType(values.name)
    if (detectedType) {
      setFieldValue('type', detectedType)
    }
  }

  // Recognize brand and color
  const params = recognizeParameters(
    values.name,
    customBrands.value
  )

  if (params.brand && !values.brand) {
    setFieldValue('brand', params.brand)
  }

  // Map item color to container color
  if (params.color && (!values.color || values.color === 'default')) {
    const containerColor = mapItemColorToContainerColor(params.color)
    if (containerColor) {
      setFieldValue('color', containerColor)
    }
  }
}, 500)

// Watch for name changes and auto-recognize
watch(() => values.name, () => {
  autoRecognizeFromName()
})

// Auto-detect container type from name on blur (only for new containers, not when editing)
const handleNameBlur = () => {
  if (!isEditMode && values.name && values.type === 'other') {
    const detectedType = recognizeContainerType(values.name)
    if (detectedType) {
      setFieldValue('type', detectedType)
    }
  }
}

// Convert form data to V2 DTO format
const convertToV2Dto = (data: ContainerFormData): Omit<ICreateGearItemV2Dto, 'itemType'> => ({
  name: data.name,
  description: data.description || null,
  containerType: data.type, // V1 'type' → V2 'containerType'
  color: data.color || null,
  parentItemId: data.parentContainerId || null, // V1 'parentContainerId' → V2 'parentItemId'
  hideWhenNested: data.hideWhenNested || false,
  isPublic: data.isPublic || false,
  favorite: data.favorite || false,
  brand: data.brand || null,
  price: data.price || null,
  currency: data.currency || null,
  weight: data.weight || null,
  weightUnit: data.weightUnit || null,
  maxWeight: data.maxWeight || null,
  maxWeightUnit: data.maxWeightUnit || null,
  url: data.url || null,
  showItemImages: data.showItemImages || false,
})

// Submit handler
const onSubmit = handleSubmit(async (data: ContainerFormData) => {
  try {
    const v2Data = convertToV2Dto(data)

    if (isEditMode && containerId) {
      await updateContainer(containerId, v2Data as IUpdateGearItemV2Dto)
      toast.success(t('common.success'))
      // Preserve 'from' parameter when navigating back to ContainerDetails
      // This ensures the back button in ContainerHeader works correctly
      const from = getFrom(route)
      router.push({
        path: GearRoutePath.ContainerDetailById(containerId),
        query: createNavigationQuery(undefined, from),
      })
    } else {
      const newContainer = await createContainer(v2Data)
      toast.success(t('common.success'))
      router.push(GearRoutePath.ContainerDetailById(newContainer.id))
    }
  } catch (error) {
    console.error(error)
    handleError(error, { setErrors })
  }
})

// Cancel handler
const handleCancel = () => {
  if (isEditMode && containerId) {
    router.push(GearRoutePath.ContainerDetailById(containerId))
  } else {
    router.push(GearRoutePath.Containers)
  }
}

// Recognize parameters handler
const handleRecognizeParameters = () => {
  if (!values.name) {
    toast.error(t('gear.container.name'))
    return
  }

  try {
    const params = recognizeParameters(
      values.name,
      customBrands.value
    )

    if (!params.brand && !params.color) {
      toast.info(t('gear.actions.noParametersFound'))
      return
    }

    if (params.brand && !values.brand) {
      setFieldValue('brand', params.brand)
    }

    // Map item color to container color
    if (params.color && (!values.color || values.color === 'default')) {
      const containerColor = mapItemColorToContainerColor(params.color)
      if (containerColor) {
        setFieldValue('color', containerColor)
      }
    }

    toast.success(t('gear.actions.parametersRecognized'))
  } catch (error) {
    toast.error(t('common.error'))
    console.error('Error recognizing parameters:', error)
  }
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 class="text-3xl font-bold">
          {{ isEditMode ? t('gear.container.edit.title') : t('gear.container.create.title') }}
        </h1>
        <p class="text-muted-foreground mt-1">
          {{ isEditMode ? t('gear.container.edit.description') : t('gear.container.create.description') }}
        </p>
      </div>

      <div class="bg-card rounded-lg border p-6">
        <form @submit="onSubmit">
          <ContainerFormFields
            :container="container"
            :loading="isSubmitting"
            @submit="handleSubmit"
            @cancel="handleCancel"
            @name-blur="handleNameBlur"
            @recognize-parameters="handleRecognizeParameters"
          />
        </form>
      </div>
    </div>
  </AuthenticatedLayout>
</template>

