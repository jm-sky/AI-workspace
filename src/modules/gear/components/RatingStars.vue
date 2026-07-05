<script setup lang="ts">
import { Star } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { TRatingValue } from '../types/gear.types'

const { t } = useI18n()

interface Props {
  rating?: TRatingValue | number | null
  maxRating?: number
  size?: 'sm' | 'md' | 'lg'
  interactive?: boolean
  showNumber?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  maxRating: 5,
  size: 'md',
  interactive: false,
  showNumber: false,
  disabled: false
})

const emit = defineEmits<{
  'update:rating': [value: TRatingValue | null]
  'change': [value: TRatingValue | null]
}>()

const hoveredRating = ref<number | null>(null)

const displayRating = computed(() => {
  if (hoveredRating.value !== null) {
    return hoveredRating.value
  }
  if (props.rating == null) return null
  return Math.round(props.rating)
})

const starSize = computed(() => {
  switch (props.size) {
    case 'lg': return 'size-6'
    case 'md': return 'size-5'
    case 'sm': return 'size-4'
    default: return 'size-5'
  }
})

function handleStarClick(rating: number) {
  if (props.disabled || !props.interactive) return

  const newRating = rating === props.rating ? null : (rating as TRatingValue)
  emit('update:rating', newRating)
  emit('change', newRating)
}

function handleStarHover(rating: number) {
  if (props.disabled || !props.interactive) return
  hoveredRating.value = rating
}

function handleStarLeave() {
  if (props.disabled || !props.interactive) return
  hoveredRating.value = null
}
</script>

<template>
  <div class="flex items-center gap-1">
    <div class="flex items-center gap-0.5">
      <button
        v-for="star in maxRating"
        :key="star"
        type="button"
        :class="[
          'flex items-center justify-center transition-colors',
          starSize,
          interactive && !disabled ? 'cursor-pointer hover:scale-110' : 'cursor-default',
          disabled ? 'opacity-50' : ''
        ]"
        :aria-label="interactive ? t('gear.actions.rateStar', { count: star }) : undefined"
        :disabled="disabled || !interactive"
        @click="handleStarClick(star)"
        @mouseenter="handleStarHover(star)"
        @mouseleave="handleStarLeave"
      >
        <Star
          :class="[
            'transition-colors',
            star <= (displayRating ?? 0)
              ? 'fill-yellow-400 text-yellow-400'
              : 'fill-gray-200 text-gray-300'
          ]"
        />
      </button>
    </div>
    <span
      v-if="showNumber && rating != null"
      class="text-sm font-medium text-gray-700 dark:text-gray-300 ml-1"
    >
      {{ rating.toFixed(1) }}
    </span>
  </div>
</template>

