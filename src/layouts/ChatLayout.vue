<script setup lang="ts">
import ChatHeader from '@/components/layout/ChatHeader.vue'
import ChatSidebar from '@/components/layout/ChatSidebar.vue'
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar'
</script>

<template>
  <SidebarProvider>
    <ChatSidebar class="mt-(--header-height) shadow-[0_0_.6rem_#0002]" />
    <SidebarInset class="flex h-dvh flex-col overflow-hidden bg-surface pt-14">
      <ChatHeader />
      <main class="flex min-h-0 flex-1 flex-col overflow-hidden">
        <slot />
      </main>
    </SidebarInset>
  </SidebarProvider>
</template>
