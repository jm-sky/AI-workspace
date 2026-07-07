import { ref } from 'vue'
import { copyRunToClipboard, streamAgentChat } from '@/modules/workspace/services/agentApiService'
import type {
  IAgentChatMessage,
  IAgentStreamStepEvent,
  IRichBlock,
} from '@/modules/workspace/types/agent'

export function useAgentChat() {
  const messages = ref<IAgentChatMessage[]>([])
  const steps = ref<IAgentStreamStepEvent[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const activeRunId = ref<string | null>(null)

  const sendMessage = async (message: string) => {
    if (!message.trim() || isLoading.value) return

    isLoading.value = true
    error.value = null
    steps.value = []

    const userMessage: IAgentChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: message.trim(),
    }
    messages.value.push(userMessage)

    let assistantContent = ''
    let blocks: IRichBlock[] = []
    let runId: string | undefined

    try {
      await streamAgentChat(
        { message: message.trim(), agentKey: 'jira-360' },
        {
          onStep: (event) => {
            steps.value.push(event)
            if (event.runId) {
              runId = event.runId
              activeRunId.value = event.runId
            }
          },
          onComplete: (event) => {
            assistantContent = event.message
            blocks = event.blocks ?? []
            runId = event.runId
            activeRunId.value = event.runId
          },
          onError: (msg) => {
            error.value = msg
          },
        },
      )

      if (assistantContent) {
        messages.value.push({
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: assistantContent,
          runId,
          blocks,
        })
      } else if (error.value) {
        messages.value.push({
          id: `assistant-error-${Date.now()}`,
          role: 'assistant',
          content: `**Error:** ${error.value}`,
        })
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
    } finally {
      isLoading.value = false
    }
  }

  const copyActiveRun = async () => {
    if (!activeRunId.value) return
    await copyRunToClipboard(activeRunId.value)
  }

  const clearChat = () => {
    messages.value = []
    steps.value = []
    error.value = null
    activeRunId.value = null
  }

  return {
    messages,
    steps,
    isLoading,
    error,
    activeRunId,
    sendMessage,
    copyActiveRun,
    clearChat,
  }
}
