/**
 * AI Chat Composable
 * Handles chat interactions with AI
 */

import { computed, ref } from 'vue'
import type { IAiChatHistoryMessage, IAiChatMessage, IAiChatRequest, IAiChatResponse, IAiStructuredOutput } from '../types'
import type { IAiHistoryItem } from '../types/history'
import { aiApiService } from '../services/aiApiService'
import { useAiStore } from '../store/useAiStore'

export function useAiChat() {
  const aiStore = useAiStore()
  const messages = ref<IAiChatMessage[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const lastPrompt = ref<string | null>(null)
  const lastStructuredOutput = ref<IAiStructuredOutput | null>(null)

  const sendMessage = async (
    message: string,
    context?: Record<string, unknown>,
  ): Promise<IAiChatResponse | null> => {
    if (!message.trim()) return null

    isLoading.value = true
    error.value = null

    // Add user message
    const userMessage: IAiChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: message,
      created_at: new Date().toISOString(),
    }
    messages.value.push(userMessage)

    try {
      // Build history from current messages (exclude the just-added user message)
      const history: IAiChatHistoryMessage[] = messages.value.slice(0, -1).map(msg => ({
        role: msg.role,
        content: msg.content,
      }))

      const request: IAiChatRequest = {
        message,
        history,
        context,
        model: aiStore.settings?.selectedModel,
      }

      const response = await aiApiService.chat(request)

      // Save prompt and structured output for debug
      lastPrompt.value = response.prompt ?? null
      lastStructuredOutput.value = response.structured_output ?? null

      // Add assistant message
      const assistantMessage: IAiChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.message,
        tokens: {
          input: response.tokens.prompt,
          output: response.tokens.completion,
          total: response.tokens.total,
        },
        cost: response.cost !== null
          ? {
              input: 0,
              output: 0,
              total: response.cost,
            }
          : undefined,
        created_at: new Date().toISOString(),
      }
      messages.value.push(assistantMessage)

      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message'
      error.value = errorMessage

      // Add error message
      const errorMsg: IAiChatMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `Error: ${errorMessage}`,
        created_at: new Date().toISOString(),
      }
      messages.value.push(errorMsg)

      return null
    } finally {
      isLoading.value = false
    }
  }

  const clearMessages = (): void => {
    messages.value = []
    error.value = null
    lastPrompt.value = null
    lastStructuredOutput.value = null
  }

  const hasMessages = computed<boolean>(() => messages.value.length > 0)

  const restoreFromHistory = async (historyItem: IAiHistoryItem): Promise<void> => {
    try {
      // Clear current messages
      clearMessages()

      // Try to get full history detail to get complete data
      let detail: import('../types/history').IAiHistoryDetail | null = null
      try {
        detail = await aiApiService.getHistoryDetail(historyItem.id)
      } catch (error) {
        // If detail fetch fails, continue with basic restoration
        console.warn('Failed to fetch history detail:', error)
      }

      // Reconstruct messages from history
      const restoredMessages: IAiChatMessage[] = []

      // Extract user message from finalPrompt or inputData.message
      const userMessageContent = historyItem.finalPrompt
        || (detail?.inputData && typeof detail.inputData.message === 'string' ? detail.inputData.message : '')

      if (userMessageContent) {
        restoredMessages.push({
          id: `user-restored-${historyItem.id}`,
          role: 'user',
          content: userMessageContent,
          created_at: historyItem.createdAt,
        })
      }

      // Add assistant response
      const assistantContent = (detail?.outputData && typeof detail.outputData.message === 'string'
        ? detail.outputData.message
        : null)
        || (historyItem.responseData && typeof historyItem.responseData.message === 'string'
          ? historyItem.responseData.message
          : JSON.stringify(historyItem.responseData || {}))

      if (assistantContent) {
        restoredMessages.push({
          id: `assistant-restored-${historyItem.id}`,
          role: 'assistant',
          content: assistantContent,
          tokens: historyItem.tokens,
          cost: historyItem.cost,
          created_at: historyItem.createdAt,
        })
      }

      // Set messages
      messages.value = restoredMessages
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to restore conversation'
      error.value = errorMessage
      throw err
    }
  }

  return {
    messages,
    isLoading,
    error,
    lastPrompt,
    lastStructuredOutput,
    sendMessage,
    clearMessages,
    restoreFromHistory,
    hasMessages,
  }
}

