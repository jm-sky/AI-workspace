import { apiClient } from '@/shared/services/apiClient'
import type { IChatAttachment } from '@/modules/workspace/types/attachments'

export async function uploadChatAttachment(
  file: File,
  sessionId?: string | null,
): Promise<IChatAttachment> {
  const form = new FormData()
  form.append('file', file)
  if (sessionId) {
    form.append('sessionId', sessionId)
  }
  const response = await apiClient.post<IChatAttachment>(
    '/agent/attachments',
    form,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
    },
  )
  return response.data
}

export async function deleteChatAttachment(attachmentId: string): Promise<void> {
  await apiClient.delete(`/agent/attachments/${attachmentId}`)
}
