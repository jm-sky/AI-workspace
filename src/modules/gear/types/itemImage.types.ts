import type { TUUID } from '@/shared/types/base.type'

export type TStorageType = 'local' | 's3' | 'external'

export interface IItemImage {
  id: TUUID
  itemId: TUUID
  userId: TUUID
  storageType: TStorageType
  url: string
  fileName: string
  fileSize: number
  mimeType: string
  width: number | null
  height: number | null
  isPrimary: boolean
  order: number
  createdAt: string
  updatedAt: string
}

export interface IImageOrderUpdate {
  id: TUUID
  order: number
}
