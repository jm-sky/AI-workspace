<script setup lang="ts">
import { MessageSquarePlus, Search } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import type { IAgentSessionSummary } from '@/modules/workspace/types/agent'

const props = defineProps<{
  sessions: IAgentSessionSummary[]
  activeSessionId?: string | null
  isLoading?: boolean
  searchQuery: string
}>()

const emit = defineEmits<{
  'update:searchQuery': [value: string]
  select: [sessionId: string]
  newChat: []
}>()

const { t } = useI18n()

const searchModel = computed({
  get: () => props.searchQuery,
  set: (value: string) => emit('update:searchQuery', value),
})

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

const title = (session: IAgentSessionSummary): string => {
  const value = session.title?.trim()
  if (value) return value
  return t('workspace.sessions.untitled', 'Untitled chat')
}
</script>

<template>
  <div class="flex min-h-0 flex-1 flex-col">
    <div class="flex shrink-0 flex-col gap-2 border-b border-hairline p-3">
      <Button
        variant="ghost"
        class="hover-veil w-full justify-start rounded-lg border border-hairline bg-surface-canvas font-medium shadow-soft"
        @click="emit('newChat')"
      >
        <MessageSquarePlus class="size-4" />
        {{ t('workspace.chat.newChat') }}
      </Button>

      <div class="relative">
        <Search class="absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          v-model="searchModel"
          :placeholder="t('workspace.sessions.search')"
          class="border-hairline bg-surface-canvas pl-8 shadow-none"
        />
      </div>
    </div>

    <div class="min-h-0 flex-1 overflow-y-auto p-2">
      <div
        v-if="isLoading"
        class="flex items-center justify-center py-12 text-sm text-muted-foreground"
      >
        {{ t('common.loading') }}
      </div>

      <div
        v-else-if="sessions.length === 0"
        class="px-2 py-12 text-center text-sm text-muted-foreground"
      >
        {{ searchQuery ? t('workspace.sessions.noResults') : t('workspace.sessions.empty') }}
      </div>

      <div v-else class="space-y-0.5">
        <button
          v-for="session in sessions"
          :key="session.id"
          type="button"
          :class="cn(
            'hover-veil w-full rounded-lg px-3 py-2.5 text-left transition-colors',
            activeSessionId === session.id && 'bg-hover-veil font-medium',
          )"
          @click="emit('select', session.id)"
        >
          <div class="mb-0.5 line-clamp-2 text-sm text-foreground">
            {{ title(session) }}
          </div>
          <div class="text-xs text-muted-foreground">
            {{ formatDate(session.lastMessageAt) }}
          </div>
        </button>
      </div>
    </div>
  </div>
</template>
