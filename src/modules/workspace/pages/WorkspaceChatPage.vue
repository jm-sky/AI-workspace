<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import ChatLayout from '@/layouts/ChatLayout.vue'
import AgentMarkdown from '@/modules/workspace/components/AgentMarkdown.vue'
import AgentRichBlocks from '@/modules/workspace/components/AgentRichBlocks.vue'
import AgentRunAudit from '@/modules/workspace/components/AgentRunAudit.vue'
import ChatComposer from '@/modules/workspace/components/ChatComposer.vue'
import { useAgentChat } from '@/modules/workspace/composables/useAgentChat'
import { useChatSessionNav } from '@/modules/workspace/composables/useChatSessionNav'

const { t } = useI18n()
const input = ref('')

const {
  messages,
  steps,
  isLoading,
  activeRunId,
  sendMessage,
  loadRun,
  copyActiveRun,
  clearChat,
} = useAgentChat()

const { runsError, refreshRuns, setRunQuery } = useChatSessionNav({
  activeRunId,
  loadRun,
  clearChat,
})

const handleSubmit = async () => {
  const text = input.value.trim()
  if (!text) return
  input.value = ''
  const runId = await sendMessage(text)
  await refreshRuns()
  if (runId) {
    await setRunQuery(runId)
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
        <p class="shrink-0 text-sm text-muted-foreground">
          {{ t('workspace.chat.subtitle') }}
        </p>

        <p
          v-if="runsError"
          class="shrink-0 text-sm text-destructive"
        >
          {{ runsError }}
        </p>

        <AgentRunAudit
          :steps="steps"
          :run-id="activeRunId"
          @copy-run="handleCopyRun"
        />

        <div class="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto rounded-lg border bg-background p-4">
          <p
            v-if="messages.length === 0"
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

          <div
            v-if="isLoading"
            class="animate-pulse text-sm text-muted-foreground"
          >
            {{ t('workspace.chat.thinking') }}
          </div>
        </div>
      </div>

      <ChatComposer
        v-model="input"
        :is-loading="isLoading"
        @submit="handleSubmit"
      />
    </div>
  </ChatLayout>
</template>
