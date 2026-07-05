import { GearRoutePath } from '../routes'
import type { LocationQueryRaw, RouteLocationNormalizedLoadedGeneric, RouteLocationRaw } from 'vue-router'

export type ReturnToValue = 'detail' | 'shopping' | 'container'
export type FromValue = 'all-items' | 'container'

export const RETURN_TO_VALUES: readonly ReturnToValue[] = [
  'detail',
  'shopping',
  'container',
] as const

export const FROM_VALUES: readonly FromValue[] = [
  'all-items',
  'container',
] as const

export function isValidReturnTo(value: unknown): value is ReturnToValue {
  return typeof value === 'string' && RETURN_TO_VALUES.includes(value as ReturnToValue)
}

export function isValidFrom(value: unknown): value is FromValue {
  return typeof value === 'string' && FROM_VALUES.includes(value as FromValue)
}

export interface NavigationQuery {
  returnTo?: ReturnToValue
  from?: FromValue
}

export function createNavigationQuery(
  returnTo?: ReturnToValue,
  from?: FromValue,
): LocationQueryRaw {
  return {
    ...(returnTo && { returnTo }),
    ...(from && { from }),
  }
}

export function getReturnTo(route: RouteLocationNormalizedLoadedGeneric): ReturnToValue | undefined {
  const value = route.query.returnTo
  return isValidReturnTo(value) ? value : undefined
}

export function getFrom(route: RouteLocationNormalizedLoadedGeneric): FromValue | undefined {
  const value = route.query.from
  return isValidFrom(value) ? value : undefined
}

export function createItemEditPath(
  containerId: string,
  itemId: string,
  returnTo?: ReturnToValue,
  from?: FromValue,
): RouteLocationRaw {
  return {
    path: GearRoutePath.ItemEditById(containerId, itemId),
    query: createNavigationQuery(returnTo, from),
  }
}

