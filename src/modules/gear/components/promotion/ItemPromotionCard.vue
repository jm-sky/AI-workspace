<script setup lang="ts">
  import { CheckCircle2, Sparkles, ThumbsUp } from 'lucide-vue-next'
  import { computed } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { Badge } from '@/components/ui/badge'
  import { Button } from '@/components/ui/button'
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
  import { usePermissions } from '@/shared/composables/usePermissions'
  import { useItemPromotion } from '../../composables/promotion/useItemPromotion'
  import type { TUUID } from '@/shared/types/base.type'

  const props = defineProps<{
    itemId: TUUID
  }>()

  const { t } = useI18n()
  const { isAdmin } = usePermissions()
  const { promotionStatus, isStatusLoading, canPromote, userPromoted, inCatalogue, promoteItem, isPromoting, addToCatalogue, isAddingToCatalogue } = useItemPromotion(computed(() => props.itemId))

  const handlePromote = () => {
    promoteItem()
  }

  const handleAddToCatalogue = () => {
    addToCatalogue()
  }
  </script>

<template>
  <Card v-if="promotionStatus && !isStatusLoading" class="w-full">
    <CardHeader>
      <CardTitle class="flex items-center justify-between gap-2">
        <div class="flex flex-row items-center gap-2">
          <ThumbsUp class="size-4" />
          {{ t('gear.promotion.title') }}
          <Badge v-if="inCatalogue" variant="default" class="ml-auto">
            {{ t('gear.promotion.inCatalogue') }}
          </Badge>
        </div>
        <Button
          v-if="isAdmin && !inCatalogue"
          :disabled="isAddingToCatalogue"
          variant="outline"
          size="xs"
          class="px-3!"
          @click="handleAddToCatalogue"
        >
          <Sparkles class="size-4" />
          {{ t('gear.promotion.addToCatalogueAdmin') }}
        </Button>
      </CardTitle>
    </CardHeader>
    <CardContent>
      <div class="flex flex-col md:flex-row gap-4 md:gap-10 items-center">
        <!-- Progress bar -->
        <div class="space-y-2 flex-1">
          <div class="flex justify-between text-sm">
            <span>{{ t('gear.promotion.promotions') }}</span>
            <span>{{ promotionStatus.promoteCount }} / {{ promotionStatus.threshold }}</span>
          </div>
          <div class="w-full bg-muted rounded-full h-2">
            <div
              :class="[
                'h-2 rounded-full transition-all',
                promotionStatus.percentage >= 100 ? 'bg-green-600' : promotionStatus.percentage >= 50 ? 'bg-yellow-600' : 'bg-blue-600',
              ]"
              :style="{ width: `${Math.min(100, promotionStatus.percentage)}%` }"
            />
          </div>
          <p v-if="promotionStatus.remaining > 0" class="text-xs text-muted-foreground">
            {{ t('gear.promotion.remaining', { count: promotionStatus.remaining }) }}
          </p>
          <p v-else-if="!inCatalogue" class="text-xs text-green-600 font-medium">
            {{ t('gear.promotion.thresholdReached') }}
          </p>
        </div>

        <!-- User: Promote button -->
        <Button
          v-if="!userPromoted && !inCatalogue && canPromote"
          :disabled="isPromoting"
          variant="outline"
          @click="handlePromote"
        >
          <ThumbsUp class="size-4" />
          {{ t('gear.promotion.promoteButton') }}
        </Button>
      </div>

      <div class="flex flex-col gap-2 mt-4">
        <!-- Already promoted -->
        <div v-if="userPromoted && !inCatalogue" class="flex items-center gap-2 text-sm text-muted-foreground">
          <CheckCircle2 class="size-4" />
          {{ t('gear.promotion.alreadyPromoted') }}
        </div>

        <!-- In catalogue -->
        <div v-if="inCatalogue" class="flex items-center gap-2 text-sm text-green-600 font-medium">
          <CheckCircle2 class="size-4" />
          {{ t('gear.promotion.addedToCatalogue') }}
        </div>

        <!-- Cannot promote (requirements not met) -->
        <div v-if="!canPromote && !userPromoted && !inCatalogue" class="text-xs text-muted-foreground">
          {{ t('gear.promotion.requirements') }}
        </div>
      </div>
    </CardContent>
  </Card>
</template>

