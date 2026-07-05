<script setup lang="ts">
import { Copy, Edit, Eye, MoreVertical, Trash2 } from 'lucide-vue-next'
import { defineAsyncComponent, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { GearRoutePath } from '../routes'

// Lazy load dialog to reduce initial bundle size
const CloneContainerDialog = defineAsyncComponent(() => import('./CloneContainerDialog.vue'))

const props = defineProps<{
  container: IGearItemV2
}>()

const emit = defineEmits<{
  delete: [id: string]
}>()

const router = useRouter()
const { t } = useI18n()
const isCloneDialogOpen = ref(false)

// Actions
const handleShow = () => {
  router.push(GearRoutePath.ContainerDetailById(props.container.id))
}

const handleEdit = () => {
  router.push(GearRoutePath.ContainerEditById(props.container.id))
}

const handleClone = () => {
  isCloneDialogOpen.value = true
}

const handleDelete = () => {
  emit('delete', props.container.id)
}
</script>

<template>
  <div>
    <DropdownMenu>
      <DropdownMenuTrigger as-child>
        <Button
          v-tooltip.bottom="t('gear.actions.moreActions')"
          variant="ghost"
          size="sm"
          class="size-8 p-0"
          :aria-label="t('gear.actions.moreActions')"
          @click.stop
        >
          <MoreVertical class="size-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem @click.stop="handleShow">
          <Eye class="size-4 mr-2" />
          {{ t('gear.actions.show') }}
        </DropdownMenuItem>
        <DropdownMenuItem @click.stop="handleEdit">
          <Edit class="size-4 mr-2" />
          {{ t('gear.actions.edit') }}
        </DropdownMenuItem>
        <DropdownMenuItem @click.stop="handleClone">
          <Copy class="size-4 mr-2" />
          {{ t('gear.container.clone') }}
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          class="text-destructive hover:text-destructive! hover:bg-destructive/4!"
          @click.stop="handleDelete"
        >
          <Trash2 class="size-4 mr-2" />
          {{ t('gear.actions.delete') }}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>

    <!-- Clone Dialog -->
    <CloneContainerDialog
      v-model:open="isCloneDialogOpen"
      :container="container"
    />
  </div>
</template>
