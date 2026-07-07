<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Send, Sparkles } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import AgentMarkdown from '@/modules/workspace/components/AgentMarkdown.vue'
import AgentRichBlocks from '@/modules/workspace/components/AgentRichBlocks.vue'
import AgentRunAudit from '@/modules/workspace/components/AgentRunAudit.vue'
import { useAgentChat } from '@/modules/workspace/composables/useAgentChat'
import { toast } from 'vue-sonner'

const { t } = useI18n()
const input = ref('')

const {
  messages,
  steps,
  isLoading,
  activeRunId,
  sendMessage,
  copyActiveRun,
} = useAgentChat()

const handleSubmit = async () => {
  const text = input.value.trim()
  if (!text) return
  input.value = ''
  await sendMessage(text)
}

const handleCopyRun = async () => {
  try {
    await copyActiveRun()
    toast.success(t('workspace.audit.copied', 'Run copied to clipboard'))
  } catch {
    toast.error(t('workspace.audit.copyFailed', 'Failed to copy run'))
  }
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="container max-w-4xl py-6 flex flex-col gap-4 min-h-[calc(100vh-8rem)]">
      <header class="flex flex-col gap-1">
        <div class="flex items-center gap-2">
          <Sparkles class="size-6 text-primary" />
          <h1 class="text-2xl font-semibold">
            {{ t('workspace.chat.title', 'AI Workspace') }}
          </h1>
        </div>
        <p class="text-muted-foreground text-sm">
          {{ t('workspace.chat.subtitle', 'Jira 360° — enter an issue key (e.g. IT-123)') }}
        </p>
      </header>

      <AgentRunAudit
        :steps="steps"
        :run-id="activeRunId"
        @copy-run="handleCopyRun"
      />

      <div class="flex-1 flex flex-col gap-3 overflow-y-auto rounded-lg border p-4 bg-background min-h-[320px]">
        <p
          v-if="messages.length === 0"
          class="text-muted-foreground text-sm m-auto text-center"
        >
          {{ t('workspace.chat.empty', 'Ask about a Jira issue to build a 360° view.') }}
        </p>

        <div
          v-for="msg in messages"
          :key="msg.id"
          :class="[
            'rounded-lg p-3 max-w-[95%]',
            msg.role === 'user' ? 'bg-primary text-primary-foreground ml-auto' : 'bg-muted mr-auto w-full',
          ]"
        >
          <AgentMarkdown :content="msg.content" />
          <AgentRichBlocks
            v-if="msg.blocks?.length"
            :blocks="msg.blocks"
          />
        </div>

        <div v-if="isLoading" class="text-sm text-muted-foreground animate-pulse">
          {{ t('workspace.chat.thinking', 'Agent is working…') }}
        </div>
      </div>

      <form class="flex gap-2 items-end" @submit.prevent="handleSubmit">
        <Textarea
          v-model="input"
          :placeholder="t('workspace.chat.placeholder', 'IT-123 or describe your request')"
          :disabled="isLoading"
          rows="2"
          class="resize-none"
          @keydown.enter.exact.prevent="handleSubmit"
        />
        <Button type="submit" :disabled="isLoading || !input.trim()">
          <Send class="size-4" />
          {{ t('workspace.chat.send', 'Send') }}
        </Button>
      </form>
    </div>
  </AuthenticatedLayout>
</template>
