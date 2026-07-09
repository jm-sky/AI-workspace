<script setup lang="ts">
import { Loader2 } from 'lucide-vue-next'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import ChatLayout from '@/layouts/ChatLayout.vue'
import AgentAuditSheet from '@/modules/workspace/components/AgentAuditSheet.vue'
import AgentMarkdown from '@/modules/workspace/components/AgentMarkdown.vue'
import AgentRichBlocks from '@/modules/workspace/components/AgentRichBlocks.vue'
import ChatComposer from '@/modules/workspace/components/ChatComposer.vue'
import ChatThinkingIndicator from '@/modules/workspace/components/ChatThinkingIndicator.vue'
import ChatToolbar from '@/modules/workspace/components/ChatToolbar.vue'
import { useAgentChat } from '@/modules/workspace/composables/useAgentChat'
import { useChatSessionNav } from '@/modules/workspace/composables/useChatSessionNav'
import { useWorkspaceModels } from '@/modules/workspace/composables/useWorkspaceModels'

const { t } = useI18n()
const input = ref('')
const auditOpen = ref(false)

const { getSelectedModelId, hasValidModel } = useWorkspaceModels()

const {
  messages,
  steps,
  isLoading,
  isStreaming,
  isLoadingRun,
  activeRunId,
  activeRun,
  activeSessionId,
  error,
  sendMessage,
  loadSession,
  copyActiveRun,
  clearChat,
} = useAgentChat(getSelectedModelId)

const { sessionsError, refreshSessions, setSessionQuery } = useChatSessionNav({
  activeSessionId,
  loadSession,
  clearChat,
})

const handleSubmit = async () => {
  const text = input.value.trim()
  if (!text || !hasValidModel.value) return
  input.value = ''
  await sendMessage(text)
  await refreshSessions()
  if (activeSessionId.value) {
    await setSessionQuery(activeSessionId.value)
  }
}

const handleCopyRun = async () => {
  try {
    await copyActiveRun()
    toast.success(t('workspace.audit.copied'))
  } catch {
    toast.error(t('workspace.audit.copyFailed'))
  }
}
</script>

<template>
  <ChatLayout>
    <div class="flex min-h-0 flex-1 flex-col">
      <div class="flex min-h-0 flex-1 flex-col gap-4 overflow-hidden px-4 py-3 sm:px-6">
        <ChatToolbar
          :active-run="activeRun"
          :step-count="steps.length"
          :audit-open="auditOpen"
          @open-audit="auditOpen = true"
        />

        <p
          v-if="sessionsError"
          class="shrink-0 text-sm text-destructive"
        >
          {{ sessionsError }}
        </p>

        <p
          v-if="error"
          class="shrink-0 text-sm text-destructive"
        >
          {{ error }}
        </p>

        <div
          v-if="isLoadingRun"
          class="flex items-center gap-2 text-sm text-muted-foreground"
        >
          <Loader2 class="size-4 animate-spin" />
          {{ t('workspace.chat.loadingSession') }}
        </div>

        <div class="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto rounded-lg border bg-background p-4">
          <p
            v-if="messages.length === 0 && !isLoadingRun"
            class="m-auto text-center text-sm text-muted-foreground"
          >
            {{ t('workspace.chat.empty') }}
          </p>

          <div
            v-for="msg in messages"
            :key="msg.id"
            :class="[
              'max-w-[95%] rounded-lg p-3',
              msg.role === 'user' ? 'ml-auto bg-primary text-primary-foreground' : 'mr-auto w-full bg-muted',
            ]"
          >
            <AgentMarkdown :content="msg.content" />
            <AgentRichBlocks
              v-if="msg.blocks?.length"
              :blocks="msg.blocks"
            />
          </div>

          <ChatThinkingIndicator
            v-if="isStreaming"
            :steps="steps"
          />
        </div>
      </div>

      <ChatComposer
        v-model="input"
        :is-loading="isLoading"
        :is-streaming="isStreaming"
        :can-submit="hasValidModel && !isLoading"
        @submit="handleSubmit"
      />

      <AgentAuditSheet
        v-model:open="auditOpen"
        :steps="steps"
        :run-id="activeRunId"
        :active-run="activeRun"
        :is-streaming="isStreaming"
        @copy-run="handleCopyRun"
      />
    </div>
  </ChatLayout>
</template>
