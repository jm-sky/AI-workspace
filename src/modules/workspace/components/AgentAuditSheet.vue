<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import AgentRunAudit from '@/modules/workspace/components/AgentRunAudit.vue'
import type { IAgentRun, IAgentStreamStepEvent } from '@/modules/workspace/types/agent'

const open = defineModel<boolean>('open', { default: false })

const { steps, runId, activeRun, isStreaming } = defineProps<{
  steps: IAgentStreamStepEvent[]
  runId?: string | null
  activeRun?: IAgentRun | null
  isStreaming?: boolean
}>()

const emit = defineEmits<{
  copyRun: []
}>()

const { t } = useI18n()

const hasAuditData = computed(() => steps.length > 0 || !!runId)

const formatCost = (cost?: number | null): string => {
  if (cost == null) return '—'
  return `$${cost.toFixed(4)}`
}
</script>

<template>
  <Sheet v-model:open="open">
    <SheetContent class="flex w-full flex-col gap-0 overflow-hidden sm:max-w-lg">
      <SheetHeader class="shrink-0">
        <SheetTitle>{{ t('workspace.audit.title') }}</SheetTitle>
        <SheetDescription>
          {{ t('workspace.audit.description') }}
        </SheetDescription>
      </SheetHeader>

      <div v-if="!hasAuditData" class="px-4 py-8 text-center text-sm text-muted-foreground">
        {{ t('workspace.audit.noRun') }}
      </div>

      <Tabs v-else default-value="trace" class="flex min-h-0 flex-1 flex-col">
        <TabsList class="mx-4 shrink-0">
          <TabsTrigger value="trace">
            {{ t('workspace.audit.trace') }}
          </TabsTrigger>
          <TabsTrigger value="systemPrompt">
            {{ t('workspace.audit.systemPrompt') }}
          </TabsTrigger>
          <TabsTrigger value="session">
            {{ t('workspace.audit.session') }}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="trace" class="min-h-0 flex-1 overflow-y-auto px-4 pb-4 pt-4">
          <AgentRunAudit
            :steps="steps"
            :run-id="runId"
            :is-streaming="isStreaming"
            expanded
            @copy-run="emit('copyRun')"
          />
        </TabsContent>

        <TabsContent value="systemPrompt" class="min-h-0 flex-1 overflow-y-auto px-4 pb-4 pt-4">
          <pre
            v-if="activeRun?.systemPrompt"
            class="max-h-[60vh] overflow-auto whitespace-pre-wrap break-words rounded-lg border bg-muted/40 p-3 text-xs"
          >{{ activeRun.systemPrompt }}</pre>
          <p v-else class="text-sm text-muted-foreground">
            {{ t('workspace.audit.noSystemPrompt') }}
          </p>
        </TabsContent>

        <TabsContent value="session" class="min-h-0 flex-1 overflow-y-auto px-4 pb-4 pt-4">
          <dl v-if="activeRun" class="space-y-3 text-sm">
            <div>
              <dt class="text-muted-foreground">
                {{ t('workspace.audit.runId') }}
              </dt>
              <dd class="font-mono text-xs break-all">
                {{ activeRun.id }}
              </dd>
            </div>
            <div>
              <dt class="text-muted-foreground">
                {{ t('workspace.audit.status') }}
              </dt>
              <dd>
                <Badge variant="outline">
                  {{ activeRun.status }}
                </Badge>
              </dd>
            </div>
            <div>
              <dt class="text-muted-foreground">
                {{ t('workspace.model.currentLabel') }}
              </dt>
              <dd>{{ activeRun.model }}</dd>
            </div>
            <div>
              <dt class="text-muted-foreground">
                {{ t('workspace.audit.tokens') }}
              </dt>
              <dd>
                {{
                  t('workspace.audit.tokensSummary', {
                    prompt: activeRun.promptTokens,
                    completion: activeRun.completionTokens,
                    total: activeRun.totalTokens,
                  })
                }}
              </dd>
            </div>
            <div>
              <dt class="text-muted-foreground">
                {{ t('workspace.audit.cost') }}
              </dt>
              <dd>{{ formatCost(activeRun.costUsd) }}</dd>
            </div>
          </dl>
          <p v-else class="text-sm text-muted-foreground">
            {{ t('workspace.audit.noRun') }}
          </p>
          <Button
            v-if="runId"
            variant="outline"
            size="sm"
            class="mt-4"
            @click="emit('copyRun')"
          >
            {{ t('workspace.audit.copyRun') }}
          </Button>
        </TabsContent>
      </Tabs>
    </SheetContent>
  </Sheet>
</template>
