<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { HttpStatusCode, isAxiosError } from 'axios'
import { AlertTriangle, CheckCircle2 } from 'lucide-vue-next'
import { useForm } from 'vee-validate'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { ReportReason } from '../types/reports.types'
import { gearContainerApiService } from '../services/gearContainerApiService'

const { t } = useI18n()
const { handleError } = useHandleError()

const open = defineModel<boolean>('open', { required: true })

const props = defineProps<{
  containerId: string
  hasReported?: boolean
}>()

const emit = defineEmits<{
  withdrawn: []
  reported: []
}>()

const isWithdrawing = ref<boolean>(false)

// Zod schema for validation
const reportSchema = z.object({
  reason: z.enum(['spam_fraud', 'violence', 'sexual_content', 'profanity', 'other'], {
    required_error: t('gear.report.reasonRequired'),
  }),
  additionalInfo: z.string().max(1000).optional().nullable(),
})

type ReportFormData = z.infer<typeof reportSchema>

const { handleSubmit, resetForm, isSubmitting, setErrors } = useForm<ReportFormData>({
  validationSchema: toTypedSchema(reportSchema),
  initialValues: {
    reason: undefined,
    additionalInfo: '',
  },
})

// Reactive reason options for i18n support
const reasonOptions = computed<{ value: ReportReason; label: string }[]>(() => [
  { value: 'spam_fraud', label: t('gear.report.reasons.spam_fraud') },
  { value: 'violence', label: t('gear.report.reasons.violence') },
  { value: 'sexual_content', label: t('gear.report.reasons.sexual_content') },
  { value: 'profanity', label: t('gear.report.reasons.profanity') },
  { value: 'other', label: t('gear.report.reasons.other') },
])

const onSubmit = handleSubmit(async (values) => {
  try {
    await gearContainerApiService.reportPublicContainer(props.containerId, {
      reason: values.reason,
      additionalInfo: values.additionalInfo || null,
    })

    toast.success(t('gear.report.success'))
    emit('reported')
    open.value = false
  } catch (error) {
    // Handle 409 Conflict (already reported) with translated message
    if (isAxiosError(error) && error.response?.status === HttpStatusCode.Conflict) {
      toast.error(t('gear.report.alreadyReported'))
      return
    }
    handleError(error, { setErrors, fallbackMessage: t('gear.report.error') })
  }
})

const handleWithdraw = async () => {
  isWithdrawing.value = true
  try {
    await gearContainerApiService.withdrawReport(props.containerId)
    toast.success(t('gear.report.withdrawSuccess'))
    emit('withdrawn')
    open.value = false
  } catch (error) {
    handleError(error, { fallbackMessage: t('gear.report.withdrawError') })
  } finally {
    isWithdrawing.value = false
  }
}

// Reset form when dialog closes
watch(open, (isOpen) => {
  if (!isOpen) {
    resetForm()
  }
})
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-md">
      <DialogHeader>
        <div class="flex items-start gap-3">
          <div
            class="rounded-full p-2"
            :class="hasReported ? 'bg-primary/10' : 'bg-destructive/10'"
          >
            <CheckCircle2 v-if="hasReported" class="size-5 text-primary" />
            <AlertTriangle v-else class="size-5 text-destructive" />
          </div>
          <div class="flex-1">
            <DialogTitle>
              {{ hasReported ? t('gear.report.alreadyReportedInfo') : t('gear.report.title') }}
            </DialogTitle>
            <DialogDescription>
              {{ hasReported ? t('gear.report.withdrawConfirm') : t('gear.report.description') }}
            </DialogDescription>
          </div>
        </div>
      </DialogHeader>

      <!-- Withdraw mode -->
      <template v-if="hasReported">
        <DialogFooter>
          <Button type="button" variant="outline" @click="open = false">
            {{ t('gear.report.cancel') }}
          </Button>
          <Button
            type="button"
            variant="destructive"
            :disabled="isWithdrawing"
            :loading="isWithdrawing"
            @click="handleWithdraw"
          >
            {{ t('gear.report.withdraw') }}
          </Button>
        </DialogFooter>
      </template>

      <!-- Report mode -->
      <template v-else>
        <form class="space-y-4" :class="{ 'pointer-events-none opacity-50': isSubmitting }" @submit="onSubmit">
          <FormField v-slot="{ componentField }" name="reason">
            <FormItem>
              <FormLabel required>
                {{ t('gear.report.reason') }}
              </FormLabel>
              <Select v-bind="componentField">
                <FormControl>
                  <SelectTrigger>
                    <SelectValue :placeholder="t('gear.report.reasonPlaceholder')" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem
                    v-for="option in reasonOptions"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          </FormField>

          <FormField v-slot="{ componentField }" name="additionalInfo">
            <FormItem>
              <FormLabel>
                {{ t('gear.report.additionalInfo') }}
              </FormLabel>
              <FormControl>
                <Textarea
                  v-bind="componentField"
                  :placeholder="t('gear.report.additionalInfoPlaceholder')"
                  :rows="4"
                  class="resize-none"
                />
              </FormControl>
              <p class="text-xs text-muted-foreground">
                {{ t('gear.report.additionalInfoHint') }}
              </p>
              <FormMessage />
            </FormItem>
          </FormField>

          <DialogFooter>
            <Button type="button" variant="outline" @click="open = false">
              {{ t('gear.report.cancel') }}
            </Button>
            <Button type="submit" :disabled="isSubmitting" :loading="isSubmitting">
              {{ t('gear.report.submit') }}
            </Button>
          </DialogFooter>
        </form>
      </template>
    </DialogContent>
  </Dialog>
</template>
