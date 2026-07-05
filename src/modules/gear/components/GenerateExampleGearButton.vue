<script setup lang="ts">
import { useQueryClient } from '@tanstack/vue-query'
import { BookCopyIcon, ChevronDown } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useGearV2 } from '@/modules/gear/composables/useGearV2'
import { GearRouteName } from '@/modules/gear/routes'
import { generateSampleSet } from '@/modules/gear/services/sampleSetGenerator'
import { gearQueryKeys } from '@/modules/gear/utils/queryKeys'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { ButtonProps } from '@/components/ui/button'

export type SampleSetVariant = 'firePouch' | 'bugOutBag' | 'edc' | 'budgetEdc' | 'mediumEdc'

const props = withDefaults(defineProps<{
  size?: ButtonProps['size']
  variant?: ButtonProps['variant']
  class?: string
  redirect?: boolean
}>(), {
  size: 'lg',
  variant: 'outline',
  redirect: true,
})

const router = useRouter()
const { t } = useI18n()
const { handleError } = useHandleError()
const { createItem } = useGearV2()
const queryClient = useQueryClient()

const handleGenerate = async (variant: SampleSetVariant) => {
  try {
    await generateSampleSet(t, variant, createItem)
    await queryClient.invalidateQueries({ queryKey: gearQueryKeys.all })
    toast.success(t('gear.sampleSet.success'))
    if (props.redirect) {
      router.push({ name: GearRouteName.Containers })
    }
  } catch (error) {
    console.error('Error generating sample set:', error)
    handleError(error)
  }
}
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button
        :size="size"
        :variant="variant"
        :class="props.class"
      >
        <BookCopyIcon class="size-4" />
        {{ t('gear.sampleSet.generateButton', 'Generate Sample Set') }}
        <ChevronDown class="size-4" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end" class="min-w-48">
      <DropdownMenuItem @click="handleGenerate('firePouch')">
        {{ t('gear.sampleSet.variants.firePouch.name', 'Fire Pouch') }}
      </DropdownMenuItem>
      <DropdownMenuItem @click="handleGenerate('bugOutBag')">
        {{ t('gear.sampleSet.variants.bugOutBag.name', 'Bug Out Bag') }}
      </DropdownMenuItem>
      <DropdownMenuItem @click="handleGenerate('edc')">
        {{ t('gear.sampleSet.variants.edc.name', 'EDC (Every Day Carry)') }}
      </DropdownMenuItem>
      <DropdownMenuItem @click="handleGenerate('budgetEdc')">
        {{ t('gear.sampleSet.variants.budgetEdc.name', 'Budget EDC Survival Kit') }}
      </DropdownMenuItem>
      <DropdownMenuItem @click="handleGenerate('mediumEdc')">
        {{ t('gear.sampleSet.variants.mediumEdc.name', 'Medium EDC / Urban Survival Kit') }}
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>

