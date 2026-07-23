import { computed, ref } from 'vue'
import {
  deleteChatAttachment,
  uploadChatAttachment,
} from '@/modules/workspace/services/attachmentApiService'
import { getApiErrorMessage } from '@/shared/utils/apiError'
import type { IChatAttachment } from '@/modules/workspace/types/attachments'

const IMAGE_ACCEPT = 'image/jpeg,image/png,image/webp,image/gif'
const MAX_PER_MESSAGE = 5
const MAX_FILE_BYTES = 10 * 1024 * 1024

export function useChatAttachments() {
  const attachments = ref<IChatAttachment[]>([])
  const isUploading = ref(false)
  const error = ref<string | null>(null)
  const previewAttachment = ref<IChatAttachment | null>(null)

  const attachmentIds = computed(() => attachments.value.map((a) => a.id))
  const canAddMore = computed(() => attachments.value.length < MAX_PER_MESSAGE)

  const revokePreview = (item: IChatAttachment) => {
    if (item.previewUrl?.startsWith('blob:')) {
      URL.revokeObjectURL(item.previewUrl)
    }
  }

  const clearAttachments = (revoke = true) => {
    if (revoke) {
      for (const item of attachments.value) {
        revokePreview(item)
      }
    }
    attachments.value = []
    error.value = null
  }

  const takeAttachments = (): IChatAttachment[] => {
    const pending = [...attachments.value]
    attachments.value = []
    error.value = null
    return pending
  }

  const validateFile = (file: File): string | null => {
    if (!IMAGE_ACCEPT.split(',').includes(file.type)) {
      return 'unsupportedType'
    }
    if (file.size > MAX_FILE_BYTES) {
      return 'tooLarge'
    }
    if (!canAddMore.value) {
      return 'tooMany'
    }
    return null
  }

  const addFiles = async (
    files: FileList | File[],
    sessionId?: string | null,
  ) => {
    const list = Array.from(files)
    if (list.length === 0) return

    isUploading.value = true
    error.value = null
    try {
      for (const file of list) {
        const code = validateFile(file)
        if (code) {
          error.value = code
          continue
        }
        const uploaded = await uploadChatAttachment(file, sessionId)
        attachments.value.push({
          ...uploaded,
          previewUrl: URL.createObjectURL(file),
        })
      }
    } catch (err) {
      error.value = getApiErrorMessage(err, 'uploadFailed')
    } finally {
      isUploading.value = false
    }
  }

  const removeAttachment = async (attachmentId: string) => {
    const item = attachments.value.find((a) => a.id === attachmentId)
    try {
      await deleteChatAttachment(attachmentId)
    } catch (err) {
      // Still remove from UI if already gone on server
      error.value = getApiErrorMessage(err, 'deleteFailed')
    }
    if (item) {
      revokePreview(item)
    }
    attachments.value = attachments.value.filter((a) => a.id !== attachmentId)
  }

  const takeAttachmentIds = (): string[] => {
    const ids = [...attachmentIds.value]
    // Keep local previews until send completes; caller clears after send
    return ids
  }

  return {
    attachments,
    attachmentIds,
    isUploading,
    error,
    previewAttachment,
    canAddMore,
    addFiles,
    removeAttachment,
    clearAttachments,
    takeAttachments,
    takeAttachmentIds,
    IMAGE_ACCEPT,
    MAX_PER_MESSAGE,
    MAX_FILE_BYTES,
  }
}
