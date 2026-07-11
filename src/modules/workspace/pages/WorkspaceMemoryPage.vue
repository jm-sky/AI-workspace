<script setup lang="ts">
import { Brain, Search, Trash2 } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import ChatLayout from '@/layouts/ChatLayout.vue'
import { useMemoryBrowser } from '@/modules/workspace/composables/useMemoryBrowser'
import type { MemoryScope } from '@/modules/workspace/types/memory'

const { t } = useI18n()

const newContent = ref('')
const newScope = ref<MemoryScope>('user')

const {
  total,
  isLoading,
  isSaving,
  error,
  searchQuery,
  scopeFilter,
  displayedEntries,
  isSemanticSearch,
  loadEntries,
  runSemanticSearch,
  addMemory,
  removeMemory,
} = useMemoryBrowser()

onMounted(() => {
  void loadEntries()
})

const handleSearch = async () => {
  await runSemanticSearch()
}

const handleAdd = async () => {
  const content = newContent.value.trim()
  if (!content) return
  try {
    await addMemory(content, newScope.value)
    newContent.value = ''
    toast.success(t('workspace.memory.saved'))
  } catch {
    toast.error(t('workspace.memory.saveFailed'))
  }
}

const handleDelete = async (entryId: string) => {
  try {
    await removeMemory(entryId)
    toast.success(t('workspace.memory.deleted'))
  } catch {
    toast.error(t('workspace.memory.deleteFailed'))
  }
}

const scopeLabel = (scope: string) => t(`workspace.memory.scopes.${scope}`, scope)

const formatDate = (iso: string) => new Date(iso).toLocaleString()
</script>

<template>
  <ChatLayout>
    <div class="flex min-h-0 flex-1 flex-col gap-4 overflow-hidden px-4 py-3 sm:px-6">
      <div class="flex shrink-0 items-center gap-2">
        <Brain class="size-5 text-muted-foreground" />
        <div>
          <h1 class="text-lg font-semibold">
            {{ t('workspace.memory.title') }}
          </h1>
          <p class="text-sm text-muted-foreground">
            {{ t('workspace.memory.subtitle') }}
          </p>
        </div>
      </div>

      <div class="grid shrink-0 gap-3 rounded-xl border border-hairline bg-surface-raised p-4 md:grid-cols-2">
        <div class="space-y-2">
          <Label for="memory-search">{{ t('workspace.memory.search') }}</Label>
          <div class="flex gap-2">
            <Input
              id="memory-search"
              v-model="searchQuery"
              :placeholder="t('workspace.memory.searchPlaceholder')"
              @keydown.enter="handleSearch"
            />
            <Button variant="outline" :disabled="isLoading" @click="handleSearch">
              <Search class="size-4" />
              {{ t('workspace.memory.searchAction') }}
            </Button>
          </div>
          <p v-if="isSemanticSearch" class="text-xs text-muted-foreground">
            {{ t('workspace.memory.semanticHint') }}
          </p>
        </div>

        <div class="space-y-2">
          <Label for="memory-scope-filter">{{ t('workspace.memory.filterScope') }}</Label>
          <Select v-model="scopeFilter" @update:model-value="loadEntries">
            <SelectTrigger id="memory-scope-filter">
              <SelectValue :placeholder="t('workspace.memory.filterScope')" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">
                {{ t('workspace.memory.scopes.all') }}
              </SelectItem>
              <SelectItem value="user">
                {{ t('workspace.memory.scopes.user') }}
              </SelectItem>
              <SelectItem value="agent">
                {{ t('workspace.memory.scopes.agent') }}
              </SelectItem>
              <SelectItem value="session">
                {{ t('workspace.memory.scopes.session') }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div class="shrink-0 space-y-2 rounded-xl border border-hairline bg-surface-raised p-4">
        <Label for="memory-new">{{ t('workspace.memory.add') }}</Label>
        <Textarea
          id="memory-new"
          v-model="newContent"
          :placeholder="t('workspace.memory.addPlaceholder')"
          rows="2"
        />
        <div class="flex flex-wrap items-center gap-2">
          <Select v-model="newScope">
            <SelectTrigger class="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="user">
                {{ t('workspace.memory.scopes.user') }}
              </SelectItem>
              <SelectItem value="agent">
                {{ t('workspace.memory.scopes.agent') }}
              </SelectItem>
              <SelectItem value="session">
                {{ t('workspace.memory.scopes.session') }}
              </SelectItem>
            </SelectContent>
          </Select>
          <Button :disabled="isSaving || !newContent.trim()" @click="handleAdd">
            {{ t('workspace.memory.addAction') }}
          </Button>
        </div>
      </div>

      <p v-if="error" class="shrink-0 text-sm text-destructive">
        {{ error }}
      </p>

      <div class="min-h-0 flex-1 overflow-y-auto rounded-xl border border-hairline bg-surface-canvas">
        <p
          v-if="isLoading"
          class="p-4 text-sm text-muted-foreground"
        >
          {{ t('workspace.memory.loading') }}
        </p>
        <p
          v-else-if="displayedEntries.length === 0"
          class="p-4 text-sm text-muted-foreground"
        >
          {{ t('workspace.memory.empty') }}
        </p>
        <ul v-else class="divide-y divide-hairline">
          <li
            v-for="entry in displayedEntries"
            :key="entry.id"
            class="flex items-start justify-between gap-3 p-4"
          >
            <div class="min-w-0 flex-1 space-y-1">
              <p class="text-sm whitespace-pre-wrap">
                {{ entry.content }}
              </p>
              <div class="flex flex-wrap gap-2 text-xs text-muted-foreground">
                <span class="rounded bg-muted px-1.5 py-0.5">
                  {{ scopeLabel(entry.scope) }}
                </span>
                <span>{{ entry.source }}</span>
                <span v-if="entry.similarity != null">
                  {{ t('workspace.memory.similarity', { value: entry.similarity.toFixed(2) }) }}
                </span>
                <span>{{ formatDate(entry.createdAt) }}</span>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              :aria-label="t('workspace.memory.delete')"
              @click="handleDelete(entry.id)"
            >
              <Trash2 class="size-4 text-destructive" />
            </Button>
          </li>
        </ul>
      </div>

      <p class="shrink-0 text-xs text-muted-foreground">
        {{ t('workspace.memory.total', { count: total }) }}
      </p>
    </div>
  </ChatLayout>
</template>
