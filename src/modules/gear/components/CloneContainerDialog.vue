<script setup lang="ts">
import { useQueryClient } from '@tanstack/vue-query'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { useGearV2 } from '../composables/useGearV2'
import { GearRoutePath } from '../routes'
import { cloneContainerV2 } from '../utils/cloneContainerV2'
import { gearQueryKeys } from '../utils/queryKeys'

const props = defineProps<{
  open: boolean
  container: IGearItemV2 | null
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const { t } = useI18n()
const router = useRouter()
const queryClient = useQueryClient()
const { getItemById, getChildren, createItem } = useGearV2()
const { handleError } = useHandleError()

const newName = ref('')
const includeNestedContainers = ref(false)
const includePrices = ref(true)
const isCloning = ref(false)

// Reset form when dialog opens/closes or container changes
watch(
  () => [props.open, props.container],
  () => {
    if (props.open && props.container) {
      newName.value = `[${t('gear.container.copy')}] ${props.container.name}`
      includeNestedContainers.value = false
      includePrices.value = true
    }
  },
  { immediate: true },
)

const canClone = computed<boolean>(() => {
  return newName.value.trim().length > 0 && !isCloning.value
})

const handleClone = async () => {
  if (!props.container || !canClone.value) return

  try {
    isCloning.value = true
    const clonedContainer = await cloneContainerV2(
      props.container.id,
      {
        newName: newName.value.trim(),
        includeNestedContainers: includeNestedContainers.value,
        includePrices: includePrices.value,
      },
      { getItemById, getChildren, createItem },
    )
    await queryClient.invalidateQueries({ queryKey: gearQueryKeys.all })

    toast.success(t('gear.container.cloneSuccess'))
    handleOpenChange(false)
    
    // Navigate to the cloned container
    router.push(GearRoutePath.ContainerDetailById(clonedContainer.id))
  } catch (error) {
    console.error('Error cloning container:', error)
    handleError(error)
  } finally {
    isCloning.value = false
  }
}

const handleOpenChange = (value: boolean) => {
  emit('update:open', value)
}
</script>

<template>
  <Dialog :open="open" @update:open="handleOpenChange">
    <DialogContent class="sm:max-w-md">
      <DialogHeader>
        <DialogTitle>
          {{ t('gear.container.clone') }}
        </DialogTitle>
        <DialogDescription>
          {{ t('gear.container.cloneDescription') }}
        </DialogDescription>
      </DialogHeader>

      <div class="space-y-6 py-4">
        <!-- New Name -->
        <div class="space-y-2">
          <Label for="newName">
            {{ t('gear.container.name') }}
          </Label>
          <Input
            id="newName"
            v-model="newName"
            :placeholder="t('gear.container.name')"
            :disabled="isCloning"
            @keyup.enter="handleClone"
          />
        </div>

        <!-- Options -->
        <div class="space-y-4">
          <div class="text-sm font-medium">
            {{ t('gear.container.cloneOptions') }}
          </div>

          <!-- Include Nested Containers -->
          <div class="flex items-start space-x-3 space-y-0 rounded-md border p-4">
            <Checkbox
              id="includeNestedContainers"
              v-model="includeNestedContainers"
              :disabled="isCloning"
            />
            <div class="flex-1 space-y-1">
              <Label for="includeNestedContainers" class="cursor-pointer text-sm font-normal">
                {{ t('gear.container.includeNestedContainers') }}
              </Label>
              <p class="text-sm text-muted-foreground">
                {{ t('gear.container.includeNestedContainersDescription') }}
              </p>
            </div>
          </div>

          <!-- Include Prices -->
          <div class="flex items-start space-x-3 space-y-0 rounded-md border p-4">
            <Checkbox
              id="includePrices"
              v-model="includePrices"
              :disabled="isCloning"
            />
            <div class="flex-1 space-y-1">
              <Label for="includePrices" class="cursor-pointer text-sm font-normal">
                {{ t('gear.container.includePrices') }}
              </Label>
              <p class="text-sm text-muted-foreground">
                {{ t('gear.container.includePricesDescription') }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" :disabled="isCloning" @click="handleOpenChange(false)">
          {{ t('common.cancel') }}
        </Button>
        <Button :disabled="!canClone" @click="handleClone">
          {{ isCloning ? t('common.loading') : t('gear.container.cloneButton') }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

