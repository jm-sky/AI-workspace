<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { secureMarkdownHtml } from '@/shared/utils/markdownPostProcess'

const { content } = defineProps<{
  content: string
}>()

const mdInstance = ref<InstanceType<typeof import('markdown-it').default> | null>(null)

onMounted(async () => {
  const MarkdownItModule = await import('markdown-it')
  mdInstance.value = new MarkdownItModule.default({
    html: false,
    linkify: true,
    typographer: true,
    breaks: true,
  })
})

const rendered = computed(() => {
  if (!mdInstance.value) return content
  return secureMarkdownHtml(mdInstance.value.render(content))
})
</script>

<template>
  <!-- eslint-disable-next-line vue/no-v-html -->
  <div class="prose prose-sm dark:prose-invert max-w-none" v-html="rendered" />
</template>
