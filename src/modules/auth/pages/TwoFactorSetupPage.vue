<script setup lang="ts">
import { CheckCircle2, Shield } from 'lucide-vue-next'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import PageCard from '@/components/layout/PageCard.vue'
import { Button } from '@/components/ui/button'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import PasskeyList from '@/modules/auth/components/PasskeyList.vue'
import TotpSetupForm from '@/modules/auth/components/TotpSetupForm.vue'
import WebAuthnRegisterForm from '@/modules/auth/components/WebAuthnRegisterForm.vue'
import { useTotpStatus, useTwoFactorStatus, useWebAuthnStatus } from '@/modules/auth/composables/useTwoFactor'
import { SettingsRoutePaths } from '@/modules/settings/routes'
import DisableTotpDialog from '../components/DisableTotpDialog.vue'
import type { ITwoFactorService } from '@/modules/auth/types/twoFactor.type'

const props = defineProps<{
  service?: ITwoFactorService
}>()

const { t } = useI18n()

const isDisableTotpDialogOpen = ref(false)

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const { data: twoFactorStatus } = useTwoFactorStatus(props.service)
const { data: totpStatus, refetch: refetchTotpStatus } = useTotpStatus(props.service)
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const { data: webauthnStatus, refetch: refetchWebAuthnStatus } = useWebAuthnStatus(props.service)

const showTotpSetup = ref(false)
const showPasskeyRegister = ref(false)

const handleTotpSetupSuccess = async () => {
  showTotpSetup.value = false
  await refetchTotpStatus()
}

const handlePasskeyRegisterSuccess = async () => {
  showPasskeyRegister.value = false
  await refetchWebAuthnStatus()
}

const handleDisableTotpSuccess = async () => {
  isDisableTotpDialogOpen.value = false
  await refetchTotpStatus()
}
</script>

<template>
  <AuthenticatedLayout>
    <PageCard>
      <div class="space-y-6">
        <!-- Header -->
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <Shield :size="24" />
            <h1 class="text-3xl font-bold">
              {{ t('auth.two_factor.title') }}
            </h1>
          </div>
          <p class="text-muted-foreground">
            {{ t('auth.two_factor.subtitle') }}
          </p>
        </div>

        <div class="space-y-6 max-w-2xl mx-auto">
          <!-- Tabs for TOTP and WebAuthn -->
          <Tabs default-value="totp" class="w-full">
            <TabsList class="grid w-full grid-cols-2">
              <TabsTrigger value="totp">
                {{ t('auth.two_factor.totp.title') }}
              </TabsTrigger>
              <TabsTrigger value="webauthn">
                {{ t('auth.two_factor.webauthn.title') }}
              </TabsTrigger>
            </TabsList>

            <!-- TOTP Tab -->
            <TabsContent value="totp" class="space-y-4">
              <!-- TOTP Status Card -->
              <Card v-if="totpStatus?.enabled">
                <CardHeader>
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2">
                      <CheckCircle2 :size="20" class="text-success" />
                      <CardTitle>{{ t('auth.two_factor.totp.enabled') }}</CardTitle>
                    </div>
                    <Button
                      v-if="!isDisableTotpDialogOpen"
                      variant="destructive"
                      size="sm"
                      @click="isDisableTotpDialogOpen = true"
                    >
                      {{ t('auth.two_factor.totp.disable') }}
                    </Button>
                    <Button
                      v-else
                      variant="outline"
                      size="sm"
                      @click="isDisableTotpDialogOpen = false"
                    >
                      {{ t('auth.two_factor.totp.cancel') }}
                    </Button>
                  </div>
                  <CardDescription>{{ t('auth.two_factor.totp.enabled_description') }}</CardDescription>
                  <DisableTotpDialog
                    v-if="isDisableTotpDialogOpen"
                    :service
                    class="mt-3"
                    @success="handleDisableTotpSuccess"
                    @cancel="isDisableTotpDialogOpen = false"
                  />
                </CardHeader>
              </Card>

              <!-- TOTP Setup -->
              <div v-if="!totpStatus?.enabled">
                <TotpSetupForm v-if="showTotpSetup" :service @success="handleTotpSetupSuccess" />
                <Card v-else>
                  <CardHeader>
                    <CardTitle>{{ t('auth.two_factor.totp.title') }}</CardTitle>
                    <CardDescription>{{ t('auth.two_factor.totp.description') }}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Button @click="showTotpSetup = true">
                      {{ t('auth.two_factor.totp.setup') }}
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <!-- WebAuthn Tab -->
            <TabsContent value="webauthn" class="space-y-4">
              <!-- Passkeys List -->
              <PasskeyList :service />

              <!-- Add Passkey -->
              <div v-if="showPasskeyRegister">
                <WebAuthnRegisterForm :service @success="handlePasskeyRegisterSuccess" />
              </div>
              <Button v-else class="w-full" @click="showPasskeyRegister = true">
                {{ t('auth.two_factor.webauthn.add_passkey') }}
              </Button>
            </TabsContent>
          </Tabs>

          <!-- Back Button -->
          <div class="flex justify-start">
            <ButtonLink variant="outline" :to="SettingsRoutePaths.settings">
              {{ t('common.back') }}
            </ButtonLink>
          </div>
        </div>
      </div>
    </PageCard>
  </AuthenticatedLayout>
</template>
