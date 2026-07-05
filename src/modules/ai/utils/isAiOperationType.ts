import type { AiOperationType } from '../types'
import { AI_OPERATION_TYPES } from '../config/constants'

export const isAiOperationType = (value: unknown): value is AiOperationType => {
  return typeof value === 'string' && AI_OPERATION_TYPES.includes(value as AiOperationType)
}
