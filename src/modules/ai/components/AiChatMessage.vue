<!--
  AI Chat Message Component
  Displays a single chat message with markdown support
-->
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { secureMarkdownHtml } from '@/shared/utils/markdownPostProcess'
import type { IAiChatMessage, IAiStructuredOutput } from '../types'
import AiChatMessageDebugPrompt from './AiChatMessageDebugPrompt.vue'
import AiChatMessageDebugStructuredOutput from './AiChatMessageDebugStructuredOutput.vue'
import AiChatMessageFooter from './AiChatMessageFooter.vue'

const { message, debugPrompt, debugStructuredOutput } = defineProps<{
  message: IAiChatMessage
  debugPrompt?: string | null
  debugStructuredOutput?: IAiStructuredOutput | null
}>()

const mdInstance = ref<InstanceType<typeof import('markdown-it').default> | null>(null)
const isLoadingMd = ref(true)

/**
 * Lazy loads and initializes markdown-it parser
 * Creates a configured instance with security-focused settings
 */
async function initializeMarkdownIt(): Promise<void> {
  try {
    const MarkdownItModule = await import('markdown-it')
    const MarkdownIt = MarkdownItModule.default
    mdInstance.value = new MarkdownIt({
      html: false, // Disable HTML tags for security
      linkify: true, // Auto-convert URLs to links
      typographer: true, // Enable smart quotes and other typographic replacements
      breaks: true, // Convert line breaks to <br>
    })
  } catch (error) {
    console.error('Failed to load markdown-it:', error)
  } finally {
    isLoadingMd.value = false
  }
}

// Lazy load markdown-it only when component is mounted
onMounted(() => {
  initializeMarkdownIt()
})

const debugPromptMessage = ref(false)
const debugStructuredOutputMessage = ref(false)

const renderedContent = computed<string>(() => {
  if (!mdInstance.value) {
    // Fallback: return plain text if markdown-it is not loaded yet
    return message.content
  }
  const rawHtml = mdInstance.value.render(message.content)
  // Post-process HTML to secure links
  return secureMarkdownHtml(rawHtml)
})

const messageClasses = computed<string>(() => {
  return message.role === 'user'
    ? 'bg-primary text-primary-foreground ml-auto max-w-[80%]'
    : 'bg-muted max-w-[80%]'
})
</script>

<template>
  <div :class="['p-3 rounded-lg', messageClasses]">
    <!-- eslint-disable-next-line vue/no-v-html -->
    <div class="prose prose-sm dark:prose-invert max-w-none" v-html="renderedContent" />

    <AiChatMessageDebugPrompt
      v-model:show="debugPromptMessage"
      :message="message"
      :debug-prompt="debugPrompt"
    />

    <AiChatMessageDebugStructuredOutput
      v-model:show="debugStructuredOutputMessage"
      :message="message"
      :debug-structured-output="debugStructuredOutput"
    />

    <AiChatMessageFooter
      :message="message"
      :debug-prompt="debugPrompt"
      :debug-structured-output="debugStructuredOutput"
    />
  </div>
</template>

<style scoped>
/* Override prose styles for better integration with our theme */
.prose :deep(p) {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

.prose :deep(p:first-child) {
  margin-top: 0;
}

.prose :deep(p:last-child) {
  margin-bottom: 0;
}

.prose :deep(ul),
.prose :deep(ol) {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

.prose :deep(code) {
  background-color: hsl(var(--muted));
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-size: 0.875em;
}

.prose :deep(pre) {
  background-color: hsl(var(--muted));
  padding: 0.75rem;
  border-radius: 0.375rem;
  overflow-x: auto;
}

.prose :deep(pre code) {
  background-color: transparent;
  padding: 0;
}

.prose :deep(a) {
  color: hsl(var(--primary));
  text-decoration: underline;
}

.prose :deep(a:hover) {
  opacity: 0.8;
}

.prose :deep(blockquote) {
  border-left: 3px solid hsl(var(--primary));
  padding-left: 1rem;
  font-style: italic;
  opacity: 0.9;
}

.prose :deep(h1),
.prose :deep(h2),
.prose :deep(h3),
.prose :deep(h4),
.prose :deep(h5),
.prose :deep(h6) {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.prose :deep(h1:first-child),
.prose :deep(h2:first-child),
.prose :deep(h3:first-child),
.prose :deep(h4:first-child),
.prose :deep(h5:first-child),
.prose :deep(h6:first-child) {
  margin-top: 0;
}

.prose :deep(ul) {
  list-style-type: disc;
  margin-left: 1rem;
}

.prose :deep(ol) {
  list-style-type: decimal;
  margin-left: 1rem;
}

.prose :deep(li) {
  margin-bottom: 0.25rem;
}

/* Disabled links styling */
.prose :deep(a.link-disabled) {
  color: hsl(var(--muted-foreground));
  text-decoration: line-through;
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
