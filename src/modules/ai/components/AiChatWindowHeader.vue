<script setup lang="ts">
import { History, MoreVertical, Settings, Trash2, X } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import DialogTitle from '@/components/ui/dialog/DialogTitle.vue'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useAiChat } from '../composables/useAiChat'
import AiModelSelector from './AiModelSelector.vue'

const { t } = useI18n()
const { clearMessages } = useAiChat()

const showContextConfig = defineModel<boolean>('showContextConfig', { required: true })
const showHistorySidebar = defineModel<boolean>('showHistorySidebar', { required: true })

const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <DialogTitle class="flex items-center justify-between gap-2 border-b p-4">
    <h2 class="text-lg font-semibold">
      {{ t('ai.chat.title') }}
    </h2>
    <div class="flex flex-row items-center gap-2 -my-1">
      <!-- Desktop actions -->
      <div class="hidden md:flex flex-row items-center gap-2">
        <AiModelSelector />
        <Button
          v-tooltip.bottom="t('ai.chat.showContextConfig')"
          :variant="showContextConfig ? 'default' : 'outline'"
          size="sm"
          @click="showContextConfig = !showContextConfig"
        >
          <Settings class="size-4" />
          {{ t('ai.chat.context') }}
        </Button>
        <Button
          v-tooltip.bottom="t('ai.chat.clearMessages')"
          variant="ghost"
          size="sm"
          @click="clearMessages"
        >
          <Trash2 class="size-4" />
        </Button>
        <Button
          v-tooltip.bottom="t('ai.chat.history.openHistory')"
          variant="ghost"
          size="sm"
          @click="showHistorySidebar = true"
        >
          <History class="size-4" />
        </Button>
      </div>

      <!-- Mobile menu -->
      <div class="flex md:hidden flex-row items-center gap-2">
        <div class="hidden sm:block">
          <AiModelSelector />
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button
              variant="ghost"
              size="sm"
            >
              <MoreVertical class="size-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem @click="showContextConfig = !showContextConfig">
              <Settings class="size-4 mr-2" />
              {{ t('ai.chat.context') }}
            </DropdownMenuItem>
            <DropdownMenuItem @click="clearMessages">
              <Trash2 class="size-4 mr-2" />
              {{ t('ai.chat.clearMessages') }}
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem @click="showHistorySidebar = true">
              <History class="size-4 mr-2" />
              {{ t('ai.chat.history.openHistory') }}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <!-- Close button -->
      <Button
        v-tooltip.bottom="t('common.close')"
        variant="ghost"
        size="sm"
        @click="emit('close')"
      >
        <X class="size-4" />
      </Button>
    </div>
  </DialogTitle>
</template>
