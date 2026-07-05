<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { Key, Trash2 } from 'lucide-vue-next'
import { useForm } from 'vee-validate'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import z from 'zod'
import { Button } from '@/components/ui/button'
import { FormControl, FormField, FormItem, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAiStore } from '@/modules/ai/store/useAiStore'
import { useHandleError } from '@/shared/composables/useHandleError'
import RemoveTokenConfirmDialog from './RemoveTokenConfirmDialog.vue'

const { isAuthenticated = true } = defineProps<{
  isAuthenticated?: boolean
}>()

const { t } = useI18n()
const { handleError } = useHandleError()
const aiStore = useAiStore()

const isRemovingToken = ref(false)
const isRemoveDialogOpen = ref(false)

const hasOwnToken = computed<boolean>(() => aiStore.hasOwnToken)

const { handleSubmit, resetForm, isSubmitting } = useForm({
  initialValues: {
    apiToken: '',
  },
  validationSchema: toTypedSchema(z.object({
    apiToken: z.string().min(32, t('gear.settings.ai.tokenRequired')),
  })),
})

const handleSaveToken = handleSubmit(async (values) => {
  try {
    await aiStore.setApiToken(values.apiToken)
    resetForm()
    toast.success(t('gear.settings.ai.tokenSaved'))
  } catch (error: unknown) {
    handleError(error, { fallbackMessage: t('gear.settings.ai.tokenSaveError') })
  }
})

const handleRemoveToken = () => {
  isRemoveDialogOpen.value = true
}

const handleRemoveConfirm = async () => {
  isRemovingToken.value = true
  isRemoveDialogOpen.value = false
  try {
    await aiStore.removeApiToken()
    toast.success(t('gear.settings.ai.tokenRemoved'))
  } catch (error: unknown) {
    handleError(error, { fallbackMessage: t('gear.settings.ai.tokenRemoveError') })
  } finally {
    isRemovingToken.value = false
  }
}
</script>

<template>
  <div class="space-y-3 relative">
    <div class="flex items-center gap-2">
      <Key :size="16" />
      <Label for="ai-api-token">
        {{ t('gear.settings.ai.apiToken.label') }}
      </Label>
    </div>

    <p class="text-sm text-muted-foreground">
      {{ t('gear.settings.ai.apiToken.subtitle') }}
    </p>

    <Transition
      enter-from-class="opacity-50 -translate-y-2"
      enter-active-class="transition-all duration-300 ease-out z-10"
      enter-to-class="opacity-100 -translate-y-0"
      leave-from-class="opacity-100 translate-y-0"
      leave-active-class="absolute transition-all duration-300 ease-in -z-10"
      leave-to-class="opacity-0 translate-y-2"
    >
      <div v-if="hasOwnToken" class="space-y-3">
        <div class="rounded-md border bg-muted/50 p-3">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium">
                {{ t('gear.settings.ai.apiToken.configured') }}
              </p>
              <p class="text-xs text-muted-foreground">
                {{ t('gear.settings.ai.apiToken.encrypted') }}
              </p>
            </div>
            <Button
              variant="destructive"
              size="sm"
              :loading="isRemovingToken"
              :disabled="!isAuthenticated"
              @click="handleRemoveToken"
            >
              <Trash2 class="size-4" />
              {{ t('gear.settings.ai.apiToken.remove') }}
            </Button>
          </div>
        </div>
      </div>

      <form v-else class="space-y-3" @submit.prevent="handleSaveToken">
        <FormField v-slot="{ componentField }" name="apiToken">
          <FormItem>
            <FormControl>
              <Input
                id="ai-api-token"
                v-bind="componentField"
                :placeholder="t('gear.settings.ai.apiToken.placeholder')"
                :disabled="!isAuthenticated || isSubmitting"
                class="font-mono text-sm"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <Button
          type="submit"
          :loading="isSubmitting"
          :disabled="!isAuthenticated"
        >
          {{ t('gear.settings.ai.apiToken.save') }}
        </Button>
      </form>
    </Transition>

    <!-- Remove Token Confirmation Dialog -->
    <RemoveTokenConfirmDialog
      v-model:open="isRemoveDialogOpen"
      :loading="isRemovingToken"
      @confirm="handleRemoveConfirm"
    />
  </div>
</template>
