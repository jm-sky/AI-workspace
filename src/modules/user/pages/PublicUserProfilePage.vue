<script setup lang="ts">
import { HttpStatusCode, isAxiosError } from 'axios'
import { Package, User } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import Avatar from '@/components/ui/avatar/Avatar.vue'
import AvatarFallback from '@/components/ui/avatar/AvatarFallback.vue'
import AvatarImage from '@/components/ui/avatar/AvatarImage.vue'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import UserRoleBadge from '@/components/ui/UserRoleBadge.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import ContainerTypeBadge from '@/modules/gear/components/badges/ContainerTypeBadge.vue'
import ColorDot from '@/modules/gear/components/ColorDot.vue'
import MarkdownRenderer from '@/modules/gear/components/MarkdownRenderer.vue'
import { convertV1ContainerToV2 } from '@/modules/gear/utils/typeConverters'
import { apiClient } from '@/shared/services/apiClient'
import { getInitials } from '@/shared/utils/getInitials'
import type { IUser } from '../types/user.types'
import { UserRoutePaths } from '../routes'
import { userApiService } from '../services/userApiService'
import type { IGearContainer } from '@/modules/gear/types/gear.types'
import type { IGearItemV2 } from '@/modules/gear/types/gear.types.v2'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const { user: currentUser } = useAuth()

const userId = route.params.userId as string
const user = ref<IUser | null>(null)
const containers = ref<IGearItemV2[]>([])
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
    // Fetch public user profile using service
    user.value = await userApiService.getPublicUser(userId)

    // Fetch public containers for this user
    const containersResponse = await apiClient.get<IGearContainer[]>(`/gear/public/containers?authorId=${userId}`)
    containers.value = containersResponse.data.map(c => convertV1ContainerToV2(c))
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

const handleContainerClick = (containerId: string) => {
  router.push(`/gear/public/${containerId}`)
}
</script>

<template>
  <AuthenticatedLayout>
    <div v-if="isLoading" class="space-y-6">
      <div class="h-32 bg-muted rounded animate-pulse" />
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="i in 6" :key="i" class="h-48 bg-muted rounded-lg animate-pulse" />
      </div>
    </div>

    <div v-else-if="error" class="space-y-6">
      <div class="bg-destructive/10 border border-destructive/20 text-destructive rounded-lg p-6 text-center">
        <User class="size-12 mx-auto mb-4 text-destructive/50" />
        <h2 class="text-xl font-semibold mb-2">
          {{ t('user.publicProfile.error_title') }}
        </h2>
        <p>{{ error }}</p>
      </div>
    </div>

    <div v-else-if="user" class="space-y-6 w-full max-w-full">
      <!-- User Profile Header -->
      <Card>
        <CardContent>
          <div class="flex flex-col sm:flex-row items-center sm:items-stretch gap-4 sm:gap-6">
            <Avatar class="size-20 sm:size-24 ring-1 ring-border shrink-0">
              <AvatarImage :src="user.avatarUrl ?? ''" :alt="user.name" />
              <AvatarFallback class="bg-muted text-muted-foreground text-xl sm:text-2xl font-semibold">
                {{ initials }}
              </AvatarFallback>
            </Avatar>
            <div class="flex flex-col items-start text-center sm:text-left flex-1">
              <div class="flex items-center gap-2 flex-wrap justify-center sm:justify-start">
                <h1 class="text-2xl sm:text-3xl font-bold">
                  {{ user.name }}
                </h1>
                <UserRoleBadge
                  :is-admin="user.isAdmin"
                  :is-owner="user.isOwner"
                  :is-premium="user.isPremium"
                />
              </div>
              <p v-if="user.emailPublic && user.email" class="flex items-center justify-center sm:justify-start w-full text-muted-foreground text-sm sm:text-base break-all mt-2">
                {{ user.email }}
              </p>
            </div>
            <div v-if="isCurrentUser">
              <ButtonLink :to="UserRoutePaths.profileEdit">
                {{ t('common.edit') }}
              </ButtonLink>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Public Containers -->
      <div>
        <h2 class="text-xl sm:text-2xl font-bold mb-4">
          {{ t('user.publicProfile.public_containers') }}
        </h2>

        <div v-if="containers.length === 0" class="flex flex-col items-center justify-center py-12 text-center">
          <div class="rounded-full bg-muted p-6 mb-4">
            <Package class="size-12 text-muted-foreground" />
          </div>
          <h3 class="text-lg font-semibold mb-2">
            {{ t('user.publicProfile.no_containers') }}
          </h3>
          <p class="text-muted-foreground max-w-md">
            {{ t('user.publicProfile.no_containers_description') }}
          </p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card
            v-for="container in containers"
            :key="container.id"
            class="gap-1 hover:shadow-lg hover:bg-current/5 hover:scale-102 hover:-translate-y-1 transition-all duration-300 cursor-pointer"
            @click="handleContainerClick(container.id)"
          >
            <CardHeader class="text-card-foreground">
              <div class="flex items-center gap-2">
                <ColorDot :color="(container.color as any) ?? undefined" />
                <Package class="size-5" />
                <CardTitle>{{ container.name }}</CardTitle>
              </div>
              <CardDescription v-if="container.description">
                <MarkdownRenderer
                  :content="container.description"
                  class="text-sm"
                />
              </CardDescription>
            </CardHeader>

            <CardContent class="flex flex-col gap-3 px-6 pb-4 text-card-foreground">
              <div class="flex items-center gap-2 flex-wrap">
                <ContainerTypeBadge :container="container" />
              </div>
              <div class="text-sm text-muted-foreground">
                {{ t('gear.container.itemsCount', { count: container.children?.length ?? 0 }) }}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  </AuthenticatedLayout>
</template>
