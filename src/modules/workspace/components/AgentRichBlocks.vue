<script setup lang="ts">
import AgentMarkdown from '@/modules/workspace/components/AgentMarkdown.vue'
import type { IRichBlock } from '@/modules/workspace/types/agent'

const { blocks } = defineProps<{
  blocks: IRichBlock[]
}>()

const isTableBlock = (block: IRichBlock): boolean => block.type === 'table'
const isCardBlock = (block: IRichBlock): boolean => block.type === 'card'
const isMarkdownBlock = (block: IRichBlock): boolean => block.type === 'markdown'

const tableRows = (block: IRichBlock): Record<string, unknown>[] => {
  const rows = block.data.rows
  return Array.isArray(rows) ? rows as Record<string, unknown>[] : []
}
</script>

<template>
  <div class="flex flex-col gap-4 mt-3">
    <template v-for="(block, index) in blocks" :key="index">
      <div
        v-if="isCardBlock(block)"
        class="rounded-lg border bg-card p-4 shadow-sm"
      >
        <h3 v-if="block.title" class="font-semibold mb-2">
          {{ block.title }}
        </h3>
        <dl class="grid gap-1 text-sm">
          <template v-for="(value, key) in block.data" :key="key">
            <div v-if="value != null && value !== ''" class="flex gap-2">
              <dt class="text-muted-foreground capitalize">
                {{ key }}:
              </dt>
              <dd>
                <a
                  v-if="key === 'url' && typeof value === 'string'"
                  :href="value"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-primary underline"
                >
                  {{ value }}
                </a>
                <span v-else>{{ value }}</span>
              </dd>
            </div>
          </template>
        </dl>
      </div>

      <div
        v-else-if="isTableBlock(block)"
        class="rounded-lg border overflow-x-auto"
      >
        <h3 v-if="block.title" class="font-semibold p-3 border-b bg-muted/50">
          {{ block.title }}
        </h3>
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b bg-muted/30">
              <th
                v-for="col in (block.data.columns as string[] | undefined) ?? []"
                :key="col"
                class="text-left p-2 font-medium"
              >
                {{ col }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, rowIndex) in tableRows(block)"
              :key="rowIndex"
              class="border-b last:border-0"
            >
              <td
                v-for="col in (block.data.columns as string[] | undefined) ?? []"
                :key="col"
                class="p-2"
              >
                <a
                  v-if="col === 'url' && typeof row[col] === 'string'"
                  :href="row[col] as string"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-primary underline"
                >
                  link
                </a>
                <span v-else>{{ row[col] }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <AgentMarkdown
        v-else-if="isMarkdownBlock(block) && typeof block.data.content === 'string'"
        :content="block.data.content"
      />
    </template>
  </div>
</template>
