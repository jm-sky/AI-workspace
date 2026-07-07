<script setup lang="ts">
import { CreditCard, SettingsIcon, ShieldIcon, UserIcon } from 'lucide-vue-next'
import { type Component, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import UserNav from '@/components/layout/UserNav.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import LogoText from '@/components/ui/LogoText.vue'
import { SidebarTrigger } from '@/components/ui/sidebar'
import { AdminRoutePaths } from '@/modules/admin/routes'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { AuthRouteNames } from '@/modules/auth/config/routes'
import { BillingRoutePaths } from '@/modules/billing/routes'
import { SettingsRoutePaths } from '@/modules/settings/routes'
import { useUser } from '@/modules/user/composables/useUser'
import { UserRoutePaths } from '@/modules/user/routes'
import { WorkspaceRoutePath } from '@/modules/workspace/routes'
import DarkModeToggle from '@/shared/components/DarkModeToggle.vue'
import { usePermissions } from '@/shared/composables/usePermissions'
import LocaleToggle from '@/shared/i18n/components/LocaleToggle.vue'

const { t } = useI18n()
const router = useRouter()
const { profile } = useUser()
const { canAccessAdminPanel } = usePermissions()
const { logout, user: authUser } = useAuth()

const user = computed(() => authUser.value ?? profile.value)

interface Link {
  to: string
  label: string
  icon?: Component
  hidden?: boolean
}

const coreLinks = computed<Link[]>(() => [
  {
    to: UserRoutePaths.profile,
    label: t('user.profile.title', 'Profile'),
    icon: UserIcon,
  },
  {
    to: SettingsRoutePaths.settings,
    label: t('settings.page.title', 'Settings'),
    icon: SettingsIcon,
  },
  {
    to: BillingRoutePaths.billing,
    label: t('billing.title', 'Billing & Subscription'),
    icon: CreditCard,
  },
  {
    to: AdminRoutePaths.dashboard,
    label: t('admin.dashboard.title', 'Admin Dashboard'),
    icon: ShieldIcon,
    hidden: !canAccessAdminPanel.value,
  },
])

const handleLogout = async () => {
  try {
    await logout()
    toast.success(t('auth.logout_success', 'Logged out successfully'))
    await router.push({ name: AuthRouteNames.login })
  } catch (error) {
    console.error('Logout error:', error)
    toast.error(t('auth.logout_error', 'Failed to logout'))
  }
}
</script>

<template>
  <header class="fixed left-0 top-0 z-50 w-full border-b bg-background/75 backdrop-blur-sm">
    <div class="mx-auto flex h-(--header-height) items-center">
      <div class="flex w-(--sidebar-width) items-center justify-start gap-6">
        <SidebarTrigger class="ml-2.5 opacity-80" />
        <RouterLink
          :to="WorkspaceRoutePath.Chat"
          class="flex items-center gap-2 transition-all duration-300 ease-in-out hover:scale-103 hover:brightness-80"
        >
          <AppIcon class="size-7 shrink-0" />
          <LogoText />
        </RouterLink>
      </div>

      <div class="mr-6 flex flex-1 items-center justify-end space-x-2">
        <nav class="flex items-center space-x-2">
          <LocaleToggle />
          <DarkModeToggle />
          <UserNav
            :core-links
            :user-name="user?.name ?? t('user.guest')"
            :user-email="user?.email"
            :user-avatar="user?.avatarUrl"
            @logout="handleLogout"
          >
            <template #menu-items>
              <!-- Add menu items here if needed -->
            </template>
          </UserNav>
        </nav>
      </div>
    </div>
  </header>
</template>
