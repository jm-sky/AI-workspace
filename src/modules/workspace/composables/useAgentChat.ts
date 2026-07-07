import { ref } from 'vue'
import {
  copyRunToClipboard,
  getAgentRun,
  streamAgentChat,
} from '@/modules/workspace/services/agentApiService'
import type {
  AgentStepType,
  IAgentChatMessage,
  IAgentRun,
  IAgentRunStep,
  IAgentStreamStepEvent,
  IRichBlock,
} from '@/modules/workspace/types/agent'

function mapPersistedStep(step: IAgentRunStep): IAgentStreamStepEvent {
  return {
    type: step.stepType as AgentStepType,
    stepIndex: step.stepIndex,
    tool: step.name ?? undefined,
    arguments: step.inputData ?? undefined,
    result: step.outputData ?? undefined,
    runId: undefined,
  }
}

function runToMessages(run: IAgentRun): IAgentChatMessage[] {
  const messages: IAgentChatMessage[] = [
    {
      id: `user-${run.id}`,
      role: 'user',
      content: run.inputMessage,
      runId: run.id,
    },
  ]

  if (run.outputMessage) {
    messages.push({
      id: `assistant-${run.id}`,
      role: 'assistant',
      content: run.outputMessage,
      runId: run.id,
      blocks: run.blocks,
    })
  }

  return messages
}

export function useAgentChat() {
  const messages = ref<IAgentChatMessage[]>([])
  const steps = ref<IAgentStreamStepEvent[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const activeRunId = ref<string | null>(null)

  const sendMessage = async (message: string): Promise<string | undefined> => {
    if (!message.trim() || isLoading.value) return undefined

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
        { message: message.trim(), agentKey: 'github-workspace' },
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

    return runId
  }

  const loadRun = async (runId: string) => {
    isLoading.value = true
    error.value = null
    try {
      const run = await getAgentRun(runId)
      messages.value = runToMessages(run)
      steps.value = run.steps.map(mapPersistedStep)
      activeRunId.value = run.id
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load session'
      throw err
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
    loadRun,
    copyActiveRun,
    clearChat,
  }
}
