export type AgentRunStatus = 'running' | 'completed' | 'failed'

export type AgentStepType = 'model' | 'tool_call' | 'tool_result' | 'step'

export interface IAgentChatRequest {
  message: string
  agentKey?: string
  model?: string
}

export interface IRichBlock {
  type: 'card' | 'table' | 'markdown'
  title?: string | null
  data: Record<string, unknown>
}

export interface IAgentRunStep {
  id: string
  stepIndex: number
  stepType: string
  name?: string | null
  inputData?: Record<string, unknown> | null
  outputData?: Record<string, unknown> | null
  createdAt: string
}

export interface IAgentRunSummary {
  id: string
  agentKey: string
  status: AgentRunStatus
  inputMessage: string
  outputMessage?: string | null
  createdAt: string
  completedAt?: string | null
}

export interface IAgentRunsListResponse {
  runs: IAgentRunSummary[]
  total: number
}

export interface IAgentRun extends IAgentRunSummary {
  systemPrompt: string
  model: string
  promptTokens: number
  completionTokens: number
  totalTokens: number
  costUsd?: number | null
  blocks: IRichBlock[]
  steps: IAgentRunStep[]
}

export interface IAgentChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  runId?: string
  blocks?: IRichBlock[]
}

export interface IAgentStreamStepEvent {
  type: AgentStepType
  stepIndex?: number
  tool?: string
  arguments?: Record<string, unknown>
  result?: Record<string, unknown>
  finishReason?: string
  runId?: string
}

export interface IAgentStreamCompleteEvent {
  runId: string
  message: string
  blocks?: IRichBlock[]
  promptTokens?: number
  completionTokens?: number
  totalTokens?: number
  costUsd?: number | null
}
