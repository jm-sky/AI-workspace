<script setup lang="ts">
import { CheckCircle } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { GearRoutePath } from '@/modules/gear/routes'
import { useSubscription } from '../composables/useSubscription'
import { BillingRoutePaths } from '../routes'

const { t } = useI18n()
const router = useRouter()
const { refetchSubscription } = useSubscription()

const isAnimated = ref(false)

onMounted(async () => {
  await refetchSubscription()
  // Trigger animation after a short delay
  setTimeout(() => {
    isAnimated.value = true
  }, 100)
})

const handleGoToApp = () => {
  router.push(GearRoutePath.Containers)
}

const handleManageBilling = () => {
  router.push(BillingRoutePaths.billing)
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="flex min-h-[60vh] items-center justify-center px-4">
      <Card
        class="w-full max-w-full transition-all duration-500 border-none shadow-none"
        :class="{
          'opacity-100 translate-y-0': isAnimated,
          'opacity-0 translate-y-4': !isAnimated,
        }"
      >
        <CardHeader class="text-center space-y-4">
          <div
            class="mx-auto mb-2 flex size-20 items-center justify-center rounded-full bg-green-100 transition-all duration-500"
            :class="{
              'scale-100 opacity-100': isAnimated,
              'scale-0 opacity-0': !isAnimated,
            }"
          >
            <CheckCircle
              class="size-12 text-green-600 transition-all duration-500 delay-200"
              :class="{
                'scale-100 opacity-100': isAnimated,
                'scale-0 opacity-0': !isAnimated,
              }"
            />
          </div>
          <CardTitle class="text-3xl font-bold">
            {{ t('billing.success.title') }}
          </CardTitle>
          <CardDescription class="text-base">
            {{ t('billing.success.description') }}
          </CardDescription>
        </CardHeader>

        <CardContent class="text-center space-y-4">
          <p class="text-base text-muted-foreground">
            {{ t('billing.success.message') }}
          </p>
        </CardContent>

        <CardFooter class="flex flex-col sm:flex-row gap-3 justify-center pt-2">
          <Button class="w-full sm:w-auto" @click="handleGoToApp">
            {{ t('billing.success.goToApp') }}
          </Button>
          <Button variant="outline" class="w-full sm:w-auto" @click="handleManageBilling">
            {{ t('billing.success.manageBilling') }}
          </Button>
        </CardFooter>
      </Card>
    </div>
  </AuthenticatedLayout>
</template>
