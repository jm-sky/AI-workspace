import type { TDateTime, TUUID } from '@/shared/types/base.type'

// Report reason enum
export type ReportReason = 'spam_fraud' | 'violence' | 'sexual_content' | 'profanity' | 'other'

// Report status enum
export type ReportStatus = 'pending' | 'reviewed' | 'dismissed' | 'action_taken'

// Content report interface
export interface IContentReport {
  id: TUUID
  containerId: TUUID
  containerName?: string | null
  reporterUserId: TUUID
  reporterName?: string | null
  reason: ReportReason
  additionalInfo?: string | null
  status: ReportStatus
  createdAt: TDateTime
  reviewedAt?: TDateTime | null
  reviewedBy?: TUUID | null
}

// Create report request
export interface ICreateReportRequest {
  reason: ReportReason
  additionalInfo?: string | null
}

// Update report request
export interface IUpdateReportRequest {
  status: ReportStatus
}

// Reports list response with pagination
export interface IContentReportListResponse {
  reports: IContentReport[]
  total: number
  limit: number
  offset: number
}

