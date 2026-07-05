<script setup lang="ts">
import { Edit2, Save, Shield, X } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import Badge from '@/components/ui/badge/Badge.vue'
import Button from '@/components/ui/button/Button.vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { IFeatureLimit, IFeatureLimitUpdate } from '../types/limits.types'
import { limitsApiService } from '../services/limitsApiService'

const { t } = useI18n()
const { handleError } = useHandleError()

const limits = ref<IFeatureLimit[]>([])
const loading = ref(false)
const editingRole = ref<string | null>(null)
const editForm = ref<Record<string, IFeatureLimitUpdate>>({})

const roleLabels: Record<string, string> = {
  user: t('admin.limits.roles.user', 'User'),
  premium: t('admin.limits.roles.premium', 'Premium'),
  admin: t('admin.limits.roles.admin', 'Admin'),
  owner: t('admin.limits.roles.owner', 'Owner'),
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
}

async function loadLimits() {
  loading.value = true
  try {
    limits.value = await limitsApiService.getLimits()
  } catch (error) {
    handleError(error, { fallbackMessage: t('admin.limits.loadError', 'Failed to load limits') })
  } finally {
    loading.value = false
  }
}

function startEdit(limit: IFeatureLimit) {
  editingRole.value = limit.role
  editForm.value[limit.role] = {
    aiLimit: limit.aiLimit,
    storageLimitBytes: limit.storageLimitBytes,
    description: limit.description,
  }
}

function cancelEdit(role: string) {
  editingRole.value = null
  delete editForm.value[role]
}

async function saveLimit(role: string) {
  const formData = editForm.value[role]
  if (!formData) return

  try {
    await limitsApiService.updateLimit(role, formData)
    toast.success(t('admin.limits.updateSuccess', 'Limit updated successfully'))
    editingRole.value = null
    delete editForm.value[role]
    await loadLimits()
  } catch (error) {
    handleError(error, { fallbackMessage: t('admin.limits.updateError', 'Failed to update limit') })
  }
}

onMounted(() => {
  loadLimits()
})
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6 w-full max-w-full">
      <!-- Header -->
      <div>
        <h1 class="text-3xl font-bold tracking-tight flex items-center gap-3">
          <Shield class="size-8 text-primary" />
          {{ t('admin.limits.title', 'Feature Limits') }}
        </h1>
        <p class="text-muted-foreground mt-2">
          {{ t('admin.limits.subtitle', 'Configure AI and storage limits per user role') }}
        </p>
      </div>

      <!-- Limits List -->
      <div v-if="loading" class="space-y-4">
        <div v-for="i in 4" :key="i" class="h-32 bg-muted rounded animate-pulse" />
      </div>

      <div v-else class="grid gap-4 md:grid-cols-2">
        <Card v-for="limit in limits" :key="limit.id">
          <CardHeader>
            <div class="flex items-center justify-between">
              <div>
                <CardTitle>{{ roleLabels[limit.role] ?? limit.role }}</CardTitle>
                <CardDescription v-if="limit.description">
                  {{ limit.description }}
                </CardDescription>
              </div>
              <Badge :variant="limit.role === 'owner' ? 'default' : 'secondary'">
                {{ limit.role }}
              </Badge>
            </div>
          </CardHeader>
          <CardContent class="space-y-4">
            <!-- AI Limit -->
            <div class="space-y-2">
              <Label>{{ t('admin.limits.aiLimit', 'AI Limit (USD)') }}</Label>
              <div v-if="editingRole === limit.role" class="space-y-2">
                <Input
                  :model-value="editForm[limit.role]?.aiLimit?.toString() ?? ''"
                  type="number"
                  step="0.01"
                  min="0"
                  :placeholder="t('admin.limits.unlimitedPlaceholder', 'Unlimited (leave empty)')"
                  @update:model-value="(val) => {
                    const form = editForm[limit.role]
                    if (form) {
                      form.aiLimit = val === '' || val === null ? null : parseFloat(val as string)
                    }
                  }"
                />
                <p class="text-xs text-muted-foreground">
                  {{ t('admin.limits.aiLimitHint', 'Leave empty for unlimited, 0 for no access') }}
                </p>
              </div>
              <div v-else class="text-sm">
                <span v-if="limit.aiLimit === null" class="font-medium text-green-600">
                  {{ t('admin.limits.unlimited', 'Unlimited') }}
                </span>
                <span v-else-if="limit.aiLimit === 0" class="font-medium text-red-600">
                  {{ t('admin.limits.noAccess', 'No Access') }}
                </span>
                <span v-else class="font-medium">
                  ${{ limit.aiLimit.toFixed(2) }}
                </span>
              </div>
            </div>

            <!-- Storage Limit -->
            <div class="space-y-2">
              <Label>{{ t('admin.limits.storageLimit', 'Storage Limit') }}</Label>
              <div v-if="editingRole === limit.role" class="space-y-2">
                <Input
                  :model-value="editForm[limit.role]?.storageLimitBytes?.toString() ?? ''"
                  type="number"
                  min="0"
                  step="1048576"
                  @update:model-value="(val) => {
                    const form = editForm[limit.role]
                    if (form && val) {
                      form.storageLimitBytes = parseInt(val as string, 10)
                    }
                  }"
                />
                <p class="text-xs text-muted-foreground">
                  {{ formatBytes(editForm[limit.role]?.storageLimitBytes ?? 0) }}
                </p>
              </div>
              <div v-else class="text-sm font-medium">
                {{ formatBytes(limit.storageLimitBytes) }}
              </div>
            </div>

            <!-- Actions -->
            <div v-if="editingRole === limit.role" class="flex gap-2">
              <Button size="sm" @click="saveLimit(limit.role)">
                <Save class="size-4" />
                {{ t('admin.limits.save', 'Save') }}
              </Button>
              <Button size="sm" variant="ghost" @click="cancelEdit(limit.role)">
                <X class="size-4" />
                {{ t('admin.limits.cancel', 'Cancel') }}
              </Button>
            </div>
            <Button
              v-else
              size="sm"
              variant="outline"
              :disabled="limit.role === 'owner'"
              @click="startEdit(limit)"
            >
              <Edit2 class="size-4" />
              {{ t('admin.limits.edit', 'Edit') }}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  </AuthenticatedLayout>
</template>

