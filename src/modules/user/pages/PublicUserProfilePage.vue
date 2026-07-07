<script setup lang="ts">
import { HttpStatusCode, isAxiosError } from 'axios'
import { User } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import Avatar from '@/components/ui/avatar/Avatar.vue'
import AvatarFallback from '@/components/ui/avatar/AvatarFallback.vue'
import AvatarImage from '@/components/ui/avatar/AvatarImage.vue'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import UserRoleBadge from '@/components/ui/UserRoleBadge.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { getInitials } from '@/shared/utils/getInitials'
import type { IUser } from '../types/user.types'
import { UserRoutePaths } from '../routes'
import { userApiService } from '../services/userApiService'

const route = useRoute()
const { t } = useI18n()
const { user: currentUser } = useAuth()

const userId = route.params.userId as string
const user = ref<IUser | null>(null)
const isLoading = ref(true)
const error = ref<string | null>(null)

const isCurrentUser = computed(() => user.value?.id === currentUser.value?.id)

const initials = computed(() => {
  if (user.value?.name) {
    return getInitials(user.value.name)
  }
  if (user.value?.email) {
    return user.value.email.substring(0, 2).toUpperCase()
  }
  return 'U'
})

onMounted(async () => {
  try {
    user.value = await userApiService.getPublicUser(userId)
  } catch (err: unknown) {
    console.error('Failed to load public user profile:', err)
    if (isAxiosError(err) && err.response?.status === HttpStatusCode.NotFound) {
      error.value = t('user.publicProfile.not_found')
    } else if (isAxiosError(err) && err.response?.status === HttpStatusCode.Forbidden) {
      error.value = t('user.publicProfile.not_public')
    } else {
      error.value = t('user.publicProfile.error')
    }
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <AuthenticatedLayout>
    <div v-if="isLoading" class="space-y-6">
      <div class="h-32 bg-muted rounded animate-pulse" />
      <div class="h-64 bg-muted rounded animate-pulse" />
    </div>

    <div v-else-if="error" class="text-center py-12">
      <p class="text-muted-foreground">
        {{ error }}
      </p>
    </div>

    <div v-else-if="user" class="max-w-2xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <div class="flex items-center gap-4">
            <Avatar class="size-16">
              <AvatarImage v-if="user.avatarUrl" :src="user.avatarUrl" :alt="user.name" />
              <AvatarFallback>{{ initials }}</AvatarFallback>
            </Avatar>
            <div class="space-y-1">
              <CardTitle class="flex items-center gap-2">
                <User class="size-5" />
                {{ user.name }}
              </CardTitle>
              <CardDescription>{{ user.email }}</CardDescription>
              <UserRoleBadge
                :is-admin="user.isAdmin"
                :is-owner="user.isOwner"
                :is-premium="user.isPremium"
              />
            </div>
          </div>
        </CardHeader>
      </Card>

      <div v-if="isCurrentUser" class="flex justify-center">
        <ButtonLink :to="UserRoutePaths.profileEdit">
          {{ t('user.edit.title', 'Edit Profile') }}
        </ButtonLink>
      </div>
    </div>
  </AuthenticatedLayout>
</template>
