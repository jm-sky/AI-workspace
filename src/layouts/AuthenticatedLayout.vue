<script setup lang="ts">
import AppFooter from '@/components/layout/AppFooter.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar'
import { cn } from '@/lib/utils'
import type { HTMLAttributes } from 'vue'

defineProps<{
  cardClass?: HTMLAttributes['class']
}>()
</script>

<template>
  <SidebarProvider>
    <AppSidebar class="mt-(--header-height) shadow-[0_0_.6rem_#0002]" />
    <SidebarInset class="pt-14 bg-surface">
      <div class="flex min-h-screen flex-col bg-muted bg-radial from-card to-slate-300 dark:to-slate-800 w-full max-w-full overflow-x-hidden">
        <!-- Top Bar -->
        <AppHeader />

        <!-- Main Content -->
        <main class="w-full max-w-7xl mx-auto flex-1 py-6 px-2 sm:px-6 lg:px-8">
          <div :class="cn('border border-border rounded-xl bg-card p-4 sm:p-6 shadow-lg w-full max-w-full', cardClass)">
            <slot />
          </div>
        </main>

        <!-- Footer -->
        <AppFooter />
      </div>
    </SidebarInset>
  </SidebarProvider>
</template>
