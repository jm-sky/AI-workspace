<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import { nextTick, onMounted, ref, watch, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Label } from '@/components/ui/label'
import Tabs from '@/components/ui/tabs/Tabs.vue'
import TabsContent from '@/components/ui/tabs/TabsContent.vue'
import TabsList from '@/components/ui/tabs/TabsList.vue'
import TabsTrigger from '@/components/ui/tabs/TabsTrigger.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useHandleError } from '@/shared/composables/useHandleError'
import { usePageTitle } from '@/shared/composables/usePageTitle'
import { config } from '@/shared/config/config'
import type { ICreateGearItemV2Dto, IGearItemV2, IUpdateGearItemV2Dto } from '../types/gear.types.v2'
import type { IItemWithContainer } from '../utils/allItemsColumns'
import ItemCatalogSelector from '../components/ItemCatalogSelector.vue'
import ItemFormFields from '../components/ItemFormFields.vue'
import { useContainerV2 } from '../composables/useContainerV2'
import { useGearV2 } from '../composables/useGearV2'
import { useNavigationReturn } from '../composables/useNavigationReturn'
import { GearRoutePath } from '../routes'
import { recognizeCategory } from '../utils/categoryRecognition'
import {
  DEFAULT_ITEM_CATEGORY,
  DEFAULT_ITEM_PRIORITY,
  DEFAULT_ITEM_QUANTITY,
  DEFAULT_ITEM_STATUS,
  DEFAULT_ITEM_WEIGHT,
} from '../utils/constants'
import { getDefaultItemValues } from '../utils/defaultValues'
import { recognizeParameters } from '../utils/parameterRecognition'
import { calculateExpirationDate } from '../utils/shelfLife'
import { type ItemFormData, itemSchema } from '../utils/validation'
import { toBasicWeightUnit } from '../utils/weightUnits'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const { createItem, updateItem, getItemById } = useGearV2()
const { handleError } = useHandleError()
const { setTitle } = usePageTitle()

const containerId = route.params.containerId as string
const itemId = route.params.itemId as string | undefined
const isEditMode: boolean = !!itemId

const { container } = useContainerV2(containerId)
const { navigateBackAndClean } = useNavigationReturn(containerId, itemId)

// Local state for item (loaded explicitly, not from computed)
const item = ref<IGearItemV2 | null>(null)

// Set dynamic page title
watchEffect(() => {
  if (isEditMode && item.value?.name) {
    setTitle('gear.item.edit', { name: item.value.name })
  } else if (!isEditMode && container.value?.name) {
    setTitle('gear.item.create', { name: container.value.name })
  }
})
const isLoading = ref(isEditMode) // Only show loading when editing

// Redirect if container not found
if (!container.value) {
  router.push(GearRoutePath.Containers)
}

// Tabs mode - only show tabs when creating new item (not editing)
const tabMode = ref<'new' | 'catalog'>('new')
const selectedCatalogItemId = ref<string>('')

const getInitialValues = (): ItemFormData => {
  if (item.value) {
    return {
      name: item.value.name,
      category: item.value.category ?? DEFAULT_ITEM_CATEGORY,
      quantity: item.value.quantity ?? DEFAULT_ITEM_QUANTITY,
      weight: item.value.weight ?? DEFAULT_ITEM_WEIGHT,
      weightUnit: toBasicWeightUnit(item.value.weightUnit) ?? config.defaults.preferredWeightUnit,
      notes: item.value.notes ?? '',
      expirationDate: item.value.expirationDate ?? '',
      shelfLifeValue: item.value.shelfLife?.value ?? undefined,
      shelfLifeUnit: item.value.shelfLife?.unit ?? 'years',
      priority: item.value.priority ?? DEFAULT_ITEM_PRIORITY,
      status: item.value.status ?? DEFAULT_ITEM_STATUS,
      price: item.value.price ?? undefined,
      currency: item.value.currency ?? undefined,
      url: item.value.url ?? '',
      brand: item.value.brand ?? '',
      color: item.value.color ?? '',
      quality: item.value.quality ?? undefined,
      wearable: item.value.wearable ?? false,
      consumable: item.value.consumable ?? false,
      showOnContainer: item.value.showOnContainer ?? false,
    }
  }
  return {
    ...getDefaultItemValues(),
  } as ItemFormData
}

const form = useForm({
  validationSchema: toTypedSchema(itemSchema),
  initialValues: getInitialValues(),
})

const { handleSubmit, isSubmitting, setFieldValue, setValues, values, resetForm, setErrors } = form

// Load item data for edit mode
const loadItem = async () => {
  if (!isEditMode || !itemId) {
    isLoading.value = false
    return
  }

  try {
    const foundItem = await getItemById(itemId)

    if (!foundItem) {
      toast.error(t('common.error'))
      router.push(GearRoutePath.ContainerDetailById(containerId))
      return
    }

    item.value = foundItem
  } catch (error) {
    console.error('Failed to load item:', error)
    toast.error(t('common.error'))
    router.push(GearRoutePath.ContainerDetailById(containerId))
  } finally {
    // First: show the form
    isLoading.value = false

    // Then: wait for Vue to render the form fields, then set values
    if (item.value) {
      await nextTick()

      const loadedItem = item.value
      setValues({
        name: loadedItem.name,
        category: loadedItem.category ?? DEFAULT_ITEM_CATEGORY,
        quantity: loadedItem.quantity ?? DEFAULT_ITEM_QUANTITY,
        weight: loadedItem.weight ?? DEFAULT_ITEM_WEIGHT,
        weightUnit: toBasicWeightUnit(loadedItem.weightUnit) ?? 'g',
        notes: loadedItem.notes ?? '',
        expirationDate: loadedItem.expirationDate ?? '',
        shelfLifeValue: loadedItem.shelfLife?.value ?? undefined,
        shelfLifeUnit: loadedItem.shelfLife?.unit ?? 'years',
        priority: loadedItem.priority ?? DEFAULT_ITEM_PRIORITY,
        status: loadedItem.status ?? DEFAULT_ITEM_STATUS,
        price: loadedItem.price ?? undefined,
        currency: loadedItem.currency ?? undefined,
        url: loadedItem.url ?? '',
        brand: loadedItem.brand ?? '',
        color: loadedItem.color ?? '',
        quality: loadedItem.quality ?? undefined,
        wearable: loadedItem.wearable ?? false,
        consumable: loadedItem.consumable ?? false,
      })
    }
  }
}

onMounted(async () => {
  await loadItem()
})

// Reset form when switching tabs
watch(tabMode, () => {
  resetForm({
    values: getDefaultItemValues() as ItemFormData,
  })
  selectedCatalogItemId.value = ''
})

// Auto-detect category from name on blur (only for new items, not when editing)
const handleNameBlur = () => {
  if (!isEditMode && values.name && values.category === 'other') {
    const detectedCategory = recognizeCategory(values.name)
    if (detectedCategory) {
      setFieldValue('category', detectedCategory)
    }
  }
}

// Auto-set consumable/wearable based on category (only for new items, not when editing)
watch(
  () => values.category,
  (newCategory) => {
    if (!isEditMode && newCategory) {
      if (newCategory === 'food') {
        setFieldValue('consumable', true)
      } else if (newCategory === 'clothing') {
        setFieldValue('wearable', true)
      }
    }
  },
)

// Handle catalog item selection
const handleCatalogItemSelect = (selectedItem: IItemWithContainer) => {
  // Pre-fill form with selected item data
  setFieldValue('name', selectedItem.name)
  setFieldValue('category', selectedItem.category)
  setFieldValue('quantity', selectedItem.quantity)
  setFieldValue('weight', selectedItem.weight)
      setFieldValue('weightUnit', toBasicWeightUnit(selectedItem.weightUnit))
  setFieldValue('notes', selectedItem.expirationDate ? '' : '') // Reset notes for linked items
  setFieldValue('expirationDate', selectedItem.expirationDate ?? '')
  setFieldValue('priority', selectedItem.priority)
  setFieldValue('status', selectedItem.status)
  setFieldValue('brand', selectedItem.brand ?? '')
  setFieldValue('color', selectedItem.color ?? '')
  // Note: We don't copy price, url, quality, wearable, consumable as these may differ per container
}

// Handle set expiration date from shelf life
const handleSetExpirationDate = () => {
  const shelfLifeValue = values.shelfLifeValue
  const shelfLifeUnit = values.shelfLifeUnit

  if (!shelfLifeValue || !shelfLifeUnit) {
    toast.error(t('gear.item.shelfLife'))
    return
  }

  const expirationDate = calculateExpirationDate({
    value: shelfLifeValue,
    unit: shelfLifeUnit,
  })

  setFieldValue('expirationDate', expirationDate)
  toast.success(t('common.success'))
}

// Submit handler
const onSubmit = handleSubmit(async (data: ItemFormData) => {
  try {
    // Convert form data to DTO
    const dtoData: ICreateGearItemV2Dto | IUpdateGearItemV2Dto = {
      ...data,
      shelfLife: data.shelfLifeValue && data.shelfLifeUnit
        ? {
            value: data.shelfLifeValue,
            unit: data.shelfLifeUnit,
          }
        : null,
    }

    // Remove form-specific fields
    delete (dtoData as Record<string, unknown>).shelfLifeValue
    delete (dtoData as Record<string, unknown>).shelfLifeUnit

    if (isEditMode && itemId) {
      await updateItem(itemId, dtoData as IUpdateGearItemV2Dto)
      toast.success(t('common.success'))
      await navigateBackAndClean()
    } else {
      // Add parentItemId and linkedItemId if selecting from catalog
      const createData: ICreateGearItemV2Dto = {
        ...dtoData as ICreateGearItemV2Dto,
        itemType: 'item',
        parentItemId: containerId,
        linkedItemId: tabMode.value === 'catalog' && selectedCatalogItemId.value ? selectedCatalogItemId.value : undefined,
      }
      await createItem(createData)
      toast.success(t('common.success'))
      await navigateBackAndClean()
    }
  } catch (error) {
    console.error(error)
    handleError(error, { setErrors })
  }
})

// Cancel handler
const handleCancel = async () => {
  await navigateBackAndClean()
}

// Recognize parameters handler
const handleRecognizeParameters = () => {
  if (!values.name) {
    toast.error(t('gear.item.name'))
    return
  }

  try {
    const params = recognizeParameters(values.name)

    if (!params.brand && !params.color) {
      toast.info(t('gear.actions.noParametersFound'))
      return
    }

    if (params.brand && !values.brand) {
      setFieldValue('brand', params.brand)
    }
    if (params.color && !values.color) {
      setFieldValue('color', params.color)
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
    <div v-if="container" class="max-w-2xl mx-auto space-y-6">
      <!-- Header - always visible -->
      <div>
        <h1 class="text-3xl font-bold">
          {{ isEditMode ? t('gear.item.edit') : t('gear.item.create') }}
        </h1>
        <p class="text-muted-foreground mt-1">
          <RouterLink
            :to="GearRoutePath.ContainerDetailById(container.id)"
            class="hover:text-primary hover:underline transition-colors"
          >
            {{ container.name }}
          </RouterLink>
        </p>
      </div>

      <!-- Loading state for form -->
      <div v-if="isLoading" class="h-96 animate-pulse rounded-lg bg-muted" />

      <div v-else class="bg-card rounded-lg border p-6">
        <!-- Tabs - only show when creating new item (not editing) -->
        <Tabs v-if="!isEditMode" v-model="tabMode">
          <TabsList class="mb-6">
            <TabsTrigger value="new">
              {{ t('gear.item.catalog.tabNew') }}
            </TabsTrigger>
            <TabsTrigger value="catalog">
              {{ t('gear.item.catalog.tabExisting') }}
            </TabsTrigger>
          </TabsList>

          <form @submit="onSubmit">
            <!-- Catalog mode - show selector first -->
            <TabsContent
              value="catalog"
              class="mt-0 mb-6"
            >
              <div class="space-y-2">
                <Label required>
                  {{ t('gear.item.catalog.selectItem') }}
                </Label>
                <ItemCatalogSelector
                  :container-id="containerId"
                  :model-value="selectedCatalogItemId"
                  @update:model-value="selectedCatalogItemId = $event"
                  @select="handleCatalogItemSelect"
                />
              </div>
            </TabsContent>

            <TabsContent value="new" class="mt-0">
              <div />
            </TabsContent>

            <ItemFormFields
              :item="item ?? undefined"
              :loading="isSubmitting"
              :hide-name="!isEditMode && tabMode === 'catalog' && !selectedCatalogItemId"
              @cancel="handleCancel"
              @name-blur="handleNameBlur"
              @recognize-parameters="handleRecognizeParameters"
              @set-expiration-date="handleSetExpirationDate"
            />
          </form>
        </Tabs>

        <!-- No tabs when editing -->
        <form v-else @submit="onSubmit">
          <ItemFormFields
            :item="item ?? undefined"
            :loading="isSubmitting"
            @cancel="handleCancel"
            @name-blur="handleNameBlur"
            @recognize-parameters="handleRecognizeParameters"
            @set-expiration-date="handleSetExpirationDate"
          />
        </form>
      </div>
    </div>
  </AuthenticatedLayout>
</template>
