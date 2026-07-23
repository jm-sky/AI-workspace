export type AttachmentKind = 'image' | 'text' | 'pdf'

export interface IChatAttachment {
  id: string
  kind: AttachmentKind
  originalFilename: string
  mimeType: string
  sizeBytes: number
  width?: number | null
  height?: number | null
  thumbnailUrl?: string | null
  url?: string | null
  createdAt: string
  /** Local blob URL for immediate preview (composer only). */
  previewUrl?: string
}
