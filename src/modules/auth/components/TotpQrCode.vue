<script setup lang="ts">
import { useClipboard } from '@vueuse/core'
import { Check, Copy } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const props = defineProps<{
  qrCode?: string // Data URL for QR code image (preferred)
  qrCodeUri?: string // QR code URI (otpauth://...) - will be converted to data URL
  secret: string // Base32 encoded secret
}>()

const qrCodeDataUrl = ref<string>('')
const isLoading = ref(true)

onMounted(async () => {
  try {
    // If qrCode is provided, use it directly (preferred - already generated)
    if (props.qrCode) {
      qrCodeDataUrl.value = props.qrCode
      isLoading.value = false
      return
    }
    
    // If qrCodeUri is provided, generate QR code from URI
    if (props.qrCodeUri) {
      const QRCode = await import('qrcode')
      qrCodeDataUrl.value = await QRCode.default.toDataURL(props.qrCodeUri)
      isLoading.value = false
      return
    }
    
    // No QR code data provided
    isLoading.value = false
  } catch (error) {
    console.error('Error generating QR code:', error)
    toast.error('Failed to generate QR code')
    isLoading.value = false
  }
})

const { t } = useI18n()
const { copy, copied } = useClipboard()

const handleCopySecret = async () => {
  await copy(props.secret)
  toast.success(t('auth.two_factor.totp.secret_copied'))
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>{{ t('auth.two_factor.totp.scan_qr_code') }}</CardTitle>
      <CardDescription>{{ t('auth.two_factor.totp.scan_qr_code_description') }}</CardDescription>
    </CardHeader>
    <CardContent class="space-y-4">
      <!-- QR Code -->
      <div class="flex justify-center">
        <img
          v-if="!isLoading && qrCodeDataUrl"
          :src="qrCodeDataUrl"
          alt="TOTP QR Code"
          class="max-w-[256px] w-full h-auto"
        />
        <div
          v-else-if="isLoading"
          class="flex items-center justify-center w-64 h-64 bg-muted rounded"
        >
          <p class="text-sm text-muted-foreground">
            Loading QR code...
          </p>
        </div>
        <div
          v-else
          class="flex items-center justify-center w-64 h-64 bg-muted rounded"
        >
          <p class="text-sm text-muted-foreground text-red-500">
            Failed to load QR code
          </p>
        </div>
      </div>

      <!-- Secret Key -->
      <div class="space-y-2">
        <p class="text-sm font-medium">
          {{ t('auth.two_factor.totp.manual_entry') }}
        </p>
        <div class="flex items-center gap-2">
          <code class="flex-1 bg-muted p-2 rounded text-sm break-all">
            {{ secret }}
          </code>
          <Button
            type="button"
            variant="outline"
            size="icon"
            :aria-label="t('auth.two_factor.totp.copy_secret')"
            @click="handleCopySecret"
          >
            <Check v-if="copied" :size="16" />
            <Copy v-else :size="16" />
          </Button>
        </div>
      </div>

      <!-- Instructions -->
      <div class="text-sm text-muted-foreground space-y-1">
        <p>{{ t('auth.two_factor.totp.scan_instructions') }}</p>
      </div>
    </CardContent>
  </Card>
</template>
