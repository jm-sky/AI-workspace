<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import { computed, nextTick, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import CatalogueItemFormFields from '@/modules/gear/components/catalogue/CatalogueItemFormFields.vue'
import CatalogueItemImageGallery from '@/modules/gear/components/catalogue/CatalogueItemImageGallery.vue'
import { useCatalogue } from '@/modules/gear/composables/catalogue/useCatalogue'
import { GearRoutePath } from '@/modules/gear/routes'
import { type CatalogueItemFormData, catalogueItemSchema } from '@/modules/gear/utils/catalogueValidation'
import { toBasicWeightUnit } from '@/modules/gear/utils/weightUnits'
import { useHandleError } from '@/shared/composables/useHandleError'
import { usePageTitle } from '@/shared/composables/usePageTitle'
import type { IGlobalCatalogueItemCreate, IGlobalCatalogueItemUpdate } from '@/modules/gear/types/catalogue.types'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const { setTitle } = usePageTitle()
const { handleError } = useHandleError()

const catalogueItemId = route.params.id as string | undefined
const isEditMode = computed<boolean>(() => !!catalogueItemId)

const {
  createCatalogueItem,
  getCatalogueItem,
  isCreating,
  isUpdating,
  updateCatalogueItem,
} = useCatalogue()

const itemQuery = computed(() => {
  if (!catalogueItemId) return null
  return getCatalogueItem(catalogueItemId)
})

const item = computed(() => itemQuery.value?.data.value ?? null)
const isLoading = computed(() => itemQuery.value?.isLoading.value ?? false)

watchEffect(() => {
  if (isEditMode.value && item.value?.name) {
    setTitle('gear.catalogue.edit.title', { name: item.value.name })
  } else {
    setTitle('gear.catalogue.create.title')
  }
})

const getInitialValues = (): CatalogueItemFormData => {
  if (item.value) {
    return {
      name: item.value.name,
      category: item.value.category,
      weight: item.value.weight,
      weightUnit: toBasicWeightUnit(item.value.weightUnit),
      description: item.value.description ?? '',
      brand: item.value.brand ?? '',
      model: item.value.model ?? '',
      priceTier: item.value.priceTier ?? undefined,
      price: item.value.price ?? undefined,
      currency: item.value.currency ?? undefined,
      quality: item.value.quality ?? undefined,
      url: item.value.url ?? '',
      color: item.value.color ?? '',
      isActive: item.value.isActive ?? true,
    }
  }

  return {
    name: '',
    category: 'other',
    weight: 0,
    weightUnit: 'g',
    description: '',
    brand: '',
    model: '',
    priceTier: undefined,
    price: undefined,
    currency: undefined,
    quality: undefined,
    url: '',
    color: '',
    isActive: true,
  }
}

const form = useForm({
  validationSchema: toTypedSchema(catalogueItemSchema),
  initialValues: getInitialValues(),
})

const { handleSubmit, isSubmitting, setErrors, setValues } = form

watchEffect(async () => {
  if (!isEditMode.value) return
  if (!item.value) return

  await nextTick()
  setValues(getInitialValues())
})

const normalize = (value: string | undefined): string | null => {
  const trimmed = (value ?? '').trim()
  return trimmed.length ? trimmed : null
}

const onSubmit = handleSubmit(async (data: CatalogueItemFormData) => {
  try {
    const payloadBase = {
      name: data.name.trim(),
      category: data.category,
      weight: data.weight,
      weightUnit: data.weightUnit,
      description: normalize(data.description) ?? null,
      brand: normalize(data.brand) ?? null,
      model: normalize(data.model) ?? null,
      priceTier: data.priceTier ?? null,
      price: data.price ?? null,
      currency: data.currency ?? null,
      quality: data.quality ?? null,
      url: normalize(data.url) ?? null,
      color: normalize(data.color) ?? null,
      isActive: data.isActive ?? true,
    }

    if (isEditMode.value && catalogueItemId) {
      const updatePayload: IGlobalCatalogueItemUpdate = payloadBase
      await updateCatalogueItem(catalogueItemId, updatePayload)
      toast.success(t('common.success'))
      router.push(GearRoutePath.CatalogueItemDetailById(catalogueItemId))
    } else {
      const createPayload: IGlobalCatalogueItemCreate = payloadBase
      const created = await createCatalogueItem(createPayload)
      toast.success(t('common.success'))
      router.push(GearRoutePath.CatalogueItemEditById(created.id))
    }
  } catch (error) {
    console.error(error)
    handleError(error, { setErrors })
  }
})

const handleCancel = () => {
  if (isEditMode.value && catalogueItemId) {
    router.push(GearRoutePath.CatalogueItemDetailById(catalogueItemId))
  } else {
    router.push(GearRoutePath.CatalogueManage)
  }
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 class="text-3xl font-bold">
          {{ isEditMode ? t('gear.catalogue.edit.title') : t('gear.catalogue.create.title') }}
        </h1>
        <p class="text-muted-foreground mt-1">
          {{ isEditMode ? t('gear.catalogue.edit.description') : t('gear.catalogue.create.description') }}
        </p>
      </div>

      <div v-if="isEditMode && isLoading" class="h-96 animate-pulse rounded-lg bg-muted" />

      <div v-else class="bg-card rounded-lg border p-6 space-y-6">
        <form @submit="onSubmit">
          <CatalogueItemFormFields
            :item
            :loading="isSubmitting || isCreating || isUpdating"
            :is-edit-mode="isEditMode"
            @cancel="handleCancel"
          />
        </form>

        <div v-if="isEditMode && catalogueItemId" class="border-t pt-6">
          <CatalogueItemImageGallery
            :catalogue-item-id="catalogueItemId"
            :editable="true"
          />
        </div>
      </div>
    </div>
  </AuthenticatedLayout>
</template>

