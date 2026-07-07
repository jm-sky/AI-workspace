<script setup lang="ts">
import { History, Send, Sparkles } from 'lucide-vue-next'
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Textarea } from '@/components/ui/textarea'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import AgentMarkdown from '@/modules/workspace/components/AgentMarkdown.vue'
import AgentRichBlocks from '@/modules/workspace/components/AgentRichBlocks.vue'
import AgentRunAudit from '@/modules/workspace/components/AgentRunAudit.vue'
import SessionHistorySidebar from '@/modules/workspace/components/SessionHistorySidebar.vue'
import { useAgentChat } from '@/modules/workspace/composables/useAgentChat'
import { useAgentRuns } from '@/modules/workspace/composables/useAgentRuns'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const input = ref('')
const showMobileSessions = ref(false)

const {
  isLoading: runsLoading,
  error: runsError,
  searchQuery,
  filteredRuns,
  loadRuns,
} = useAgentRuns()

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

const loadRunFromRoute = async (runId: string) => {
  try {
    await loadRun(runId)
  } catch {
    toast.error(t('workspace.sessions.loadError'))
  }
}

onMounted(async () => {
  await loadRuns()
  const runId = typeof route.query.run === 'string' ? route.query.run : null
  if (runId) {
    await loadRunFromRoute(runId)
  }
})

watch(
  () => route.query.run,
  async (runId) => {
    if (typeof runId === 'string' && runId !== activeRunId.value) {
      await loadRunFromRoute(runId)
    }
  },
)

const setActiveRunQuery = async (runId?: string) => {
  await router.replace({
    path: route.path,
    query: runId ? { run: runId } : {},
  })
}

const handleSubmit = async () => {
  const text = input.value.trim()
  if (!text) return
  input.value = ''
  const runId = await sendMessage(text)
  await loadRuns()
  if (runId) {
    await setActiveRunQuery(runId)
  }
}

const handleSelectRun = async (runId: string) => {
  showMobileSessions.value = false
  await loadRunFromRoute(runId)
  await setActiveRunQuery(runId)
}

const handleNewChat = async () => {
  showMobileSessions.value = false
  clearChat()
  await setActiveRunQuery()
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
  <AuthenticatedLayout flush>
    <div class="flex min-h-[calc(100vh-var(--header-height))] w-full">
      <SessionHistorySidebar
        class="hidden lg:flex"
        :runs="filteredRuns"
        :active-run-id="activeRunId"
        :is-loading="runsLoading"
        :search-query="searchQuery"
        @update:search-query="searchQuery = $event"
        @select="handleSelectRun"
        @new-chat="handleNewChat"
      />

      <div class="flex min-w-0 flex-1 flex-col">
        <header class="flex items-start justify-between gap-3 border-b px-4 py-4 sm:px-6">
          <div class="flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <Sparkles class="size-6 text-primary" />
              <h1 class="text-2xl font-semibold">
                {{ t('workspace.chat.title') }}
              </h1>
            </div>
            <p class="text-muted-foreground text-sm">
              {{ t('workspace.chat.subtitle') }}
            </p>
            <p
              v-if="runsError"
              class="text-destructive text-sm"
            >
              {{ runsError }}
            </p>
          </div>

          <div class="flex items-center gap-2 lg:hidden">
            <Sheet v-model:open="showMobileSessions">
              <SheetTrigger as-child>
                <Button variant="outline" size="sm">
                  <History class="size-4" />
                  {{ t('workspace.chat.showSessions') }}
                </Button>
              </SheetTrigger>
              <SheetContent side="left" class="w-80 p-0">
                <SessionHistorySidebar
                  :runs="filteredRuns"
                  :active-run-id="activeRunId"
                  :is-loading="runsLoading"
                  :search-query="searchQuery"
                  @update:search-query="searchQuery = $event"
                  @select="handleSelectRun"
                  @new-chat="handleNewChat"
                />
              </SheetContent>
            </Sheet>
          </div>
        </header>

        <div class="flex flex-1 flex-col gap-4 overflow-hidden px-4 py-4 sm:px-6">
          <AgentRunAudit
            :steps="steps"
            :run-id="activeRunId"
            @copy-run="handleCopyRun"
          />

          <div class="flex min-h-[320px] flex-1 flex-col gap-3 overflow-y-auto rounded-lg border bg-background p-4">
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

          <form class="flex items-end gap-2" @submit.prevent="handleSubmit">
            <Textarea
              v-model="input"
              :placeholder="t('workspace.chat.placeholder')"
              :disabled="isLoading"
              rows="2"
              class="resize-none"
              @keydown.enter.exact.prevent="handleSubmit"
            />
            <Button type="submit" :disabled="isLoading || !input.trim()">
              <Send class="size-4" />
              {{ t('workspace.chat.send') }}
            </Button>
          </form>
        </div>
      </div>
    </div>
  </AuthenticatedLayout>
</template>
