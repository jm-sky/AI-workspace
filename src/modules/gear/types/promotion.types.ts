/**
 * Types for item promotion to catalogue feature
 */

export interface IItemPromotionStatus {
  promoteCount: number
  threshold: number
  remaining: number
  percentage: number
  inCatalogue: boolean
  userPromoted: boolean
  canPromote: boolean
}

export interface IPromoteItemResponse {
  success: boolean
  promoteCount: number
  message: string
}

