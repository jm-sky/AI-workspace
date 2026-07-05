import { computed, type Reactive, type Ref, toValue } from 'vue'
import { isExpired as isExpiredUtils } from '../utils/isExpired'
import { isExpiringSoon as isExpiringSoonUtils } from '../utils/isExpiringSoon'
import type { TDateTime } from '@/shared/types/base.type'

interface IExpirable {
  expirationDate?: TDateTime | null // ISO date string
}

export const useExpiration = (expirable: Ref<IExpirable | null> | Reactive<IExpirable | null>) => {
  const isExpired = computed(() => isExpiredUtils(toValue(expirable)))
  const isExpiringSoon = computed(() => isExpiringSoonUtils(toValue(expirable)))

  return {
    isExpired,
    isExpiringSoon,
  }
}
