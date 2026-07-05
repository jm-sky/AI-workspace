<script setup lang="ts">
import { Copy } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { smallDateTime } from '@/shared/utils/smallDateTime'
import { useContainerV2 } from '../composables/useContainerV2'
import { GearRoutePath } from '../routes'
import { type IShareToken, sharedContainersService } from '../services/sharedContainersService'
import { getActionIcon } from '../utils/actionIcons'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const { container } = useContainerV2()

const containerId = route.params.id as string
const tokens = ref<IShareToken[]>([])
const isLoading = ref(true)
const isCreateDialogOpen = ref(false)
const isRevokingToken = ref<string | null>(null)
const expiryDate = ref<string>('')

const CreateIcon = getActionIcon('create')
const DeleteIcon = getActionIcon('delete')

const loadTokens = async () => {
  try {
    isLoading.value = true
    tokens.value = await sharedContainersService.getShareTokens(containerId)
  } catch (error) {
    console.error('Failed to load share tokens:', error)
    toast.error(t('gear.shareTokens.errorLoading'))
  } finally {
    isLoading.value = false
  }
}

const handleCreateToken = async () => {
  try {
    const newToken = await sharedContainersService.createShareToken(containerId)
    tokens.value = await sharedContainersService.getShareTokens(containerId)
    isCreateDialogOpen.value = false
    toast.success(t('gear.shareTokens.createdSuccess'))
    // Copy share URL to clipboard
    await copyToClipboard(newToken.shareUrl)
  } catch (error) {
    console.error('Failed to create share token:', error)
    toast.error(t('gear.shareTokens.errorCreating'))
  }
}

const handleRevokeToken = async (token: string) => {
  if (!confirm(t('gear.shareTokens.confirmRevoke'))) {
    return
  }

  try {
    isRevokingToken.value = token
    await sharedContainersService.revokeShareToken(containerId, token)
    tokens.value = await sharedContainersService.getShareTokens(containerId)
    toast.success(t('gear.shareTokens.revoked'))
  } catch (error) {
    console.error('Failed to revoke share token:', error)
    toast.error(t('gear.shareTokens.errorRevoking'))
  } finally {
    isRevokingToken.value = null
  }
}

const copyToClipboard = async (text: string) => {
  try {
    const fullUrl = `${window.location.origin}${text}`
    await navigator.clipboard.writeText(fullUrl)
    toast.success(t('gear.shareTokens.copied'))
  } catch (error) {
    console.error('Failed to copy to clipboard:', error)
    toast.error(t('gear.shareTokens.errorCopying'))
  }
}

const isExpired = (token: IShareToken): boolean => {
  if (!token.expiresAt) return false
  return new Date(token.expiresAt) < new Date()
}

const formatExpiry = (expiresAt: string | null): string => {
  if (!expiresAt) return t('gear.shareTokens.noExpiry')
  return smallDateTime(expiresAt)
}

onMounted(async () => {
  await loadTokens()
})

const handleBack = () => {
  router.push(GearRoutePath.ContainerDetailById(containerId))
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 class="text-2xl sm:text-3xl font-bold">
            {{ t('gear.shareTokens.title') }}
          </h1>
          <p v-if="container" class="text-muted-foreground mt-1">
            {{ container.name }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <Button variant="outline" class="flex-1 sm:flex-initial" @click="handleBack">
            {{ t('common.back') }}
          </Button>
          <Button class="flex-1 sm:flex-initial" @click="isCreateDialogOpen = true">
            <CreateIcon class="size-4" />
            {{ t('gear.shareTokens.create') }}
          </Button>
        </div>
      </div>

      <!-- Tokens Table -->
      <div v-if="isLoading" class="space-y-4">
        <div class="h-12 bg-muted rounded animate-pulse" />
        <div class="h-64 bg-muted rounded animate-pulse" />
      </div>

      <div v-else-if="tokens.length === 0" class="text-center py-12 px-4">
        <p class="text-muted-foreground mb-4 text-sm sm:text-base">
          {{ t('gear.shareTokens.empty') }}
        </p>
        <Button class="w-full sm:w-auto" @click="isCreateDialogOpen = true">
          <CreateIcon class="size-4" />
          {{ t('gear.shareTokens.createFirst') }}
        </Button>
      </div>

      <div v-else class="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{{ t('gear.shareTokens.shareUrl') }}</TableHead>
              <TableHead>{{ t('gear.shareTokens.created') }}</TableHead>
              <TableHead>{{ t('gear.shareTokens.expires') }}</TableHead>
              <TableHead class="text-right">
                {{ t('common.actions') }}
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="token in tokens" :key="token.token">
              <TableCell>
                <div class="flex items-center gap-2">
                  <code class="text-sm bg-muted px-2 py-1 rounded break-all">
                    {{ token.shareUrl }}
                  </code>
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="copyToClipboard(token.shareUrl)"
                  >
                    <Copy class="size-4" />
                  </Button>
                </div>
              </TableCell>
              <TableCell>
                {{ smallDateTime(token.createdAt) }}
              </TableCell>
              <TableCell>
                <span :class="{ 'text-destructive': isExpired(token) }">
                  {{ formatExpiry(token.expiresAt) }}
                </span>
              </TableCell>
              <TableCell class="text-right">
                <Button
                  variant="ghost"
                  size="sm"
                  :disabled="isRevokingToken === token.token"
                  @click="handleRevokeToken(token.token)"
                >
                  <DeleteIcon class="size-4" />
                </Button>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>

      <!-- Create Token Dialog -->
      <Dialog v-model:open="isCreateDialogOpen">
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{{ t('gear.shareTokens.create') }}</DialogTitle>
            <DialogDescription>
              {{ t('gear.shareTokens.createDescription') }}
            </DialogDescription>
          </DialogHeader>
          <div class="space-y-4 py-4">
            <div class="space-y-2">
              <Label>{{ t('gear.shareTokens.expiryDate') }}</Label>
              <Input
                v-model="expiryDate"
                type="datetime-local"
                :placeholder="t('gear.shareTokens.expiryPlaceholder')"
              />
              <p class="text-sm text-muted-foreground">
                {{ t('gear.shareTokens.expiryHint') }}
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" @click="isCreateDialogOpen = false">
              {{ t('common.cancel') }}
            </Button>
            <Button @click="handleCreateToken">
              {{ t('gear.shareTokens.create') }}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  </AuthenticatedLayout>
</template>
