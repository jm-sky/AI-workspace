import { computed, onUnmounted, ref, type Ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { IAgentStreamStepEvent } from '@/modules/workspace/types/agent'

const ROTATION_MS = 2500

const ROTATION_KEYS = [
  'workspace.chat.thinking',
  'workspace.chat.analyzing',
  'workspace.chat.preparing',
] as const

export function useThinkingStatus(
  steps: Ref<IAgentStreamStepEvent[]>,
  isActive: Ref<boolean>,
) {
  const { t } = useI18n()
  const rotationIndex = ref(0)
  let timer: ReturnType<typeof setInterval> | null = null

  const clearTimer = () => {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  watch(
    isActive,
    (active) => {
      clearTimer()
      if (!active) return
      rotationIndex.value = 0
      timer = setInterval(() => {
        rotationIndex.value = (rotationIndex.value + 1) % ROTATION_KEYS.length
      }, ROTATION_MS)
    },
    { immediate: true },
  )

  onUnmounted(clearTimer)

  const statusLabel = computed(() => {
    const last = steps.value[steps.value.length - 1]
    if (last?.type === 'tool_call') {
      return t('workspace.chat.callingTool', { tool: last.tool ?? 'tool' })
    }
    if (last?.type === 'tool_result') {
      return t('workspace.chat.processingResult')
    }
    return t(ROTATION_KEYS[rotationIndex.value]!)
  })

  return { statusLabel }
}
