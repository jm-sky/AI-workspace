<script setup lang="ts">
import { Check, Copy } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'

const { t } = useI18n()
const copied = ref(false)

const aiContextMarkdown = computed(() => {
  return `# Gear Stack - AI Context

## Overview
Gear Stack is a full-stack web application for managing survival gear, bug-out bags, and outdoor equipment. It's designed for outdoor enthusiasts, preppers, and survival gear collectors.

## Key Capabilities
- **Multi-User Platform** - Secure user accounts with authentication and authorization
- **Hybrid Architecture** - Works offline with localStorage, syncs with cloud when online
- **Advanced Organization** - Hierarchical container system with nested items and weight tracking
- **Rich Metadata** - Track weight, expiration dates, priorities, brands, and custom categories
- **Data Portability** - Import/export functionality with AI-ready markdown format

## Core Features

### Container System
- Multiple container types (Bug-out bags, EDC kits, get-home bags, medical kits, camping gear, custom)
- Hierarchical organization - containers can contain other containers (nested packs, pouches in bags)
- Visual distinction - assign colors to containers (10+ colors)
- Container metadata - type, description, base weight, color coding
- Cycle detection - prevents circular references

### Item Management
- Rich item data: name, quantity, weight (g, kg, oz, lb), category, priority, status (owned/missing/to buy), brand, notes, expiration date
- Smart categorization - automatic category recognition (water, fire, food, shelter, first aid, tools, navigation, communication, clothing, hygiene, light, other)
- Status tracking - owned, missing, or to buy
- Priority levels - low, medium, high, critical
- Expiration tracking for consumables

### Analytics & Insights
- Weight calculations - total pack weight with recursive calculation for nested containers
- Category-based weight distribution
- Base weight vs. consumables tracking
- Readiness indicators - kit completeness percentage
- Donut charts - visual breakdown by category
- Item statistics by status, category, or priority

### Search & Filtering
- Smart search - find items by name, brand, or notes across all containers
- Multi-criteria filtering - by category, status, priority, or container
- Sorting options - by name, weight, expiration date, or priority
- Highlight expired items - visual warnings

### Import/Export
- JSON export/import - full data backup and restore
- AI-ready markdown export - structured format with metadata, nested container support, calculated weights
- CSV export - for spreadsheet applications
- Cross-device transfer

## Business Features

### User Management & Security
- Email/password authentication with secure password hashing
- OAuth social login (Google, GitHub planned)
- Email verification
- Two-factor authentication (2FA) - TOTP and WebAuthn (passkeys)
- Password management - reset and change
- reCAPTCHA v3 protection
- JWT tokens with automatic refresh
- GDPR-compliant account deletion

### User Profile
- Profile management - name, email, preferences
- Avatar support from OAuth providers
- Preferred settings - weight units, language, theme
- Security settings - manage 2FA methods

### Multi-Language Support
- English and Polish fully supported
- Automatic locale detection
- Manual language switching
- All UI text, validation messages, and emails localized

### Theming
- Dark mode with system preference detection
- Theme persistence per user account

## Technical Stack

### Frontend
- Vue 3.5+ with TypeScript & Composition API
- Pinia for state management
- Vue Router for navigation
- TailwindCSS v4 + shadcn-vue components
- VeeValidate + Zod for form validation
- TanStack Query for server state management
- vue-i18n for internationalization

### Backend
- FastAPI (Python) with async/await
- PostgreSQL database
- SQLAlchemy ORM with async support
- JWT authentication with refresh tokens
- Rate limiting and reCAPTCHA protection
- Modular architecture (auth, two-factor, email)

## Architecture
- **Hybrid Persistence**: Client-side localStorage for offline-first, server-side PostgreSQL for multi-device sync
- **Automatic Synchronization** - Changes sync to cloud when online
- **Conflict Resolution** - Smart merging of offline changes
- **Module-Based Frontend** - Each feature is self-contained in modules
- **Backend Modules** - FastAPI modular pattern with routers, services, repositories`
})

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(aiContextMarkdown.value)
    copied.value = true
    toast.success(t('aiContext.copied', 'Context copied to clipboard'))
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (error) {
    toast.error(t('common.error'))
    console.error('Error copying to clipboard:', error)
  }
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-8">
      <div class="space-y-2">
        <h1 class="text-3xl font-bold tracking-tight">
          {{ t('about.title', 'About Gear Stack') }}
        </h1>
        <p class="text-muted-foreground">
          {{ t('about.subtitle', 'A comprehensive web application for managing survival gear, bug-out bags, and outdoor equipment') }}
        </p>
      </div>

      <!-- Table of Contents -->
      <nav class="flex flex-row flex-wrap items-center gap-2 text-sm text-muted-foreground">
        <a href="#overview" class="text-primary hover:underline">
          {{ t('about.overview.title', 'Overview') }}
        </a>
        <span>|</span>
        <a href="#capabilities" class="text-primary hover:underline">
          {{ t('about.capabilities.title', 'Key Capabilities') }}
        </a>
        <span>|</span>
        <a href="#core-features" class="text-primary hover:underline">
          {{ t('about.coreFeatures.title', 'Core Features') }}
        </a>
        <span>|</span>
        <a href="#business-features" class="text-primary hover:underline">
          {{ t('about.businessFeatures.title', 'Business Features') }}
        </a>
        <span>|</span>
        <a href="#technical-stack" class="text-primary hover:underline">
          {{ t('about.technical.title', 'Technical Stack') }}
        </a>
        <span>|</span>
        <a href="#ai-context" class="text-primary hover:underline">
          {{ t('aiContext.title', 'AI Context') }}
        </a>
      </nav>

      <!-- Overview -->
      <section id="overview" class="space-y-4 scroll-mt-18">
        <h2 class="text-2xl font-semibold">
          {{ t('about.overview.title', 'Overview') }}
        </h2>
        <p class="text-muted-foreground">
          {{ t('about.overview.description', 'Gear Stack is a full-stack application designed for outdoor enthusiasts, preppers, and survival gear collectors. It combines an intuitive front-end interface with a robust backend to provide secure multi-user gear management with cloud synchronization across devices.') }}
        </p>
      </section>

      <!-- Key Capabilities -->
      <section id="capabilities" class="space-y-4 scroll-mt-18">
        <h2 class="text-2xl font-semibold">
          {{ t('about.capabilities.title', 'Key Capabilities') }}
        </h2>
        <ul class="list-disc list-inside space-y-2 text-muted-foreground">
          <li>{{ t('about.capabilities.multiUser', 'Multi-User Platform - Secure user accounts with authentication and authorization') }}</li>
          <li>{{ t('about.capabilities.hybrid', 'Hybrid Architecture - Works offline with localStorage, syncs with cloud when online') }}</li>
          <li>{{ t('about.capabilities.organization', 'Advanced Organization - Hierarchical container system with nested items and weight tracking') }}</li>
          <li>{{ t('about.capabilities.metadata', 'Rich Metadata - Track weight, expiration dates, priorities, brands, and custom categories') }}</li>
          <li>{{ t('about.capabilities.portability', 'Data Portability - Import/export functionality with AI-ready markdown format') }}</li>
        </ul>
      </section>

      <!-- Core Features -->
      <section id="core-features" class="space-y-4 scroll-mt-18">
        <h2 class="text-2xl font-semibold">
          {{ t('about.coreFeatures.title', 'Core Features') }}
        </h2>
        <div class="space-y-6">
          <div id="container-system" class="space-y-2 scroll-mt-18">
            <h3 class="text-xl font-semibold">
              {{ t('about.coreFeatures.containers.title', 'Container System') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.coreFeatures.containers.multiple', 'Multiple container types (Bug-out bags, EDC kits, get-home bags, medical kits, camping gear, and custom types)') }}</li>
              <li>{{ t('about.coreFeatures.containers.hierarchical', 'Hierarchical organization - containers can contain other containers (nested packs, pouches in bags)') }}</li>
              <li>{{ t('about.coreFeatures.containers.colors', 'Visual distinction - assign colors to containers for quick identification (10+ colors)') }}</li>
              <li>{{ t('about.coreFeatures.containers.metadata', 'Container metadata - type, description, base weight, color coding') }}</li>
              <li>{{ t('about.coreFeatures.containers.cycle', 'Cycle detection - prevents circular references in nested containers') }}</li>
            </ul>
          </div>

          <div id="item-management" class="space-y-2 scroll-mt-18">
            <h3 class="text-xl font-semibold">
              {{ t('about.coreFeatures.items.title', 'Item Management') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.coreFeatures.items.rich', 'Rich item data: name, quantity, weight (with unit selection: g, kg, oz, lb), category, priority, status (owned/missing/to buy), brand, notes, expiration date') }}</li>
              <li>{{ t('about.coreFeatures.items.categorization', 'Smart categorization - automatic category recognition based on item name (water, fire, food, shelter, first aid, tools, navigation, communication, clothing, hygiene, light, other)') }}</li>
              <li>{{ t('about.coreFeatures.items.status', 'Status tracking - mark items as owned, missing, or to buy') }}</li>
              <li>{{ t('about.coreFeatures.items.priority', 'Priority levels - low, medium, high, critical') }}</li>
              <li>{{ t('about.coreFeatures.items.expiration', 'Expiration tracking - monitor consumables and replace before they expire') }}</li>
            </ul>
          </div>

          <div id="analytics-insights" class="space-y-2 scroll-mt-18">
            <h3 class="text-xl font-semibold">
              {{ t('about.coreFeatures.analytics.title', 'Analytics & Insights') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.coreFeatures.analytics.weight', 'Weight calculations - total pack weight with recursive calculation for nested containers, category-based weight distribution, base weight vs. consumables tracking') }}</li>
              <li>{{ t('about.coreFeatures.analytics.readiness', 'Readiness indicators - kit completeness percentage based on owned vs. missing items') }}</li>
              <li>{{ t('about.coreFeatures.analytics.charts', 'Donut charts - visual breakdown of weight or quantity by category') }}</li>
              <li>{{ t('about.coreFeatures.analytics.statistics', 'Item statistics - count items by status, category, or priority') }}</li>
            </ul>
          </div>

          <div id="search-filtering" class="space-y-2 scroll-mt-18">
            <h3 class="text-xl font-semibold">
              {{ t('about.coreFeatures.search.title', 'Search & Filtering') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.coreFeatures.search.smart', 'Smart search - find items by name, brand, or notes across all containers') }}</li>
              <li>{{ t('about.coreFeatures.search.filtering', 'Multi-criteria filtering - filter by category, status, priority, or container') }}</li>
              <li>{{ t('about.coreFeatures.search.sorting', 'Sorting options - sort by name, weight, expiration date, or priority') }}</li>
              <li>{{ t('about.coreFeatures.search.expired', 'Highlight expired items - visual warnings for expired or soon-to-expire items') }}</li>
            </ul>
          </div>

          <div id="import-export" class="space-y-2 scroll-mt-18">
            <h3 class="text-xl font-semibold">
              {{ t('about.coreFeatures.importExport.title', 'Import/Export') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.coreFeatures.importExport.json', 'JSON export/import - full data backup and restore') }}</li>
              <li>{{ t('about.coreFeatures.importExport.markdown', 'AI-ready markdown export - export containers to markdown format for AI processing with structured format, nested container support, and calculated weights') }}</li>
              <li>{{ t('about.coreFeatures.importExport.csv', 'CSV export - export data in CSV format for spreadsheet applications') }}</li>
              <li>{{ t('about.coreFeatures.importExport.crossDevice', 'Cross-device transfer - export from one device, import on another') }}</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- Business Features -->
      <section id="business-features" class="space-y-4 scroll-mt-18">
        <h2 class="text-2xl font-semibold">
          {{ t('about.businessFeatures.title', 'Business Features') }}
        </h2>
        <div class="space-y-6">
          <div id="user-management-security" class="space-y-2 scroll-mt-18">
            <h3 class="text-xl font-semibold">
              {{ t('about.businessFeatures.security.title', 'User Management & Security') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.businessFeatures.security.auth', 'User registration & login - email/password authentication with secure password hashing') }}</li>
              <li>{{ t('about.businessFeatures.security.oauth', 'OAuth social login - sign in with Google (GitHub support planned)') }}</li>
              <li>{{ t('about.businessFeatures.security.email', 'Email verification - confirm email addresses for account security') }}</li>
              <li>{{ t('about.businessFeatures.security.2fa', 'Two-factor authentication (2FA) - TOTP (authenticator apps) and WebAuthn (passkeys/security keys)') }}</li>
              <li>{{ t('about.businessFeatures.security.password', 'Password management - reset forgotten passwords, change password for authenticated users') }}</li>
              <li>{{ t('about.businessFeatures.security.recaptcha', 'reCAPTCHA v3 protection - invisible bot protection on login, registration, and password reset') }}</li>
              <li>{{ t('about.businessFeatures.security.session', 'Session management - JWT tokens with automatic refresh, secure logout') }}</li>
              <li>{{ t('about.businessFeatures.security.deletion', 'Account deletion - GDPR-compliant soft delete with confirmation') }}</li>
            </ul>
          </div>

          <div id="user-profile" class="space-y-2 scroll-mt-18">
            <h3 class="text-xl font-semibold">
              {{ t('about.businessFeatures.profile.title', 'User Profile') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.businessFeatures.profile.management', 'Profile management - update name, email, and preferences') }}</li>
              <li>{{ t('about.businessFeatures.profile.avatar', 'Avatar support - OAuth providers automatically provide profile pictures') }}</li>
              <li>{{ t('about.businessFeatures.profile.settings', 'Preferred settings - weight units, language, theme preferences') }}</li>
              <li>{{ t('about.businessFeatures.profile.security', 'Security settings - manage 2FA methods, view security status') }}</li>
            </ul>
          </div>

          <div id="multi-language-support" class="space-y-2 scroll-mt-18">
            <h3 class="text-xl font-semibold">
              {{ t('about.businessFeatures.i18n.title', 'Multi-Language Support') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.businessFeatures.i18n.languages', 'English and Polish fully supported') }}</li>
              <li>{{ t('about.businessFeatures.i18n.detection', 'Automatic locale detection from browser') }}</li>
              <li>{{ t('about.businessFeatures.i18n.switching', 'Manual language switching in settings') }}</li>
              <li>{{ t('about.businessFeatures.i18n.localized', 'All UI text, validation messages, and emails localized') }}</li>
            </ul>
          </div>

          <div id="theming" class="space-y-2 scroll-mt-18">
            <h3 class="text-xl font-semibold">
              {{ t('about.businessFeatures.theming.title', 'Theming') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.businessFeatures.theming.dark', 'Dark mode - full dark theme support with system preference detection') }}</li>
              <li>{{ t('about.businessFeatures.theming.persistence', 'Theme persistence - settings saved per user account') }}</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- Technical Stack -->
      <section id="technical-stack" class="space-y-4 scroll-mt-18">
        <h2 class="text-2xl font-semibold">
          {{ t('about.technical.title', 'Technical Stack') }}
        </h2>
        <div class="space-y-4">
          <div id="frontend" class="space-y-2 scroll-mt-18">
            <h3 class="text-xl font-semibold">
              {{ t('about.technical.frontend.title', 'Frontend') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>Vue 3.5+ with TypeScript & Composition API</li>
              <li>Pinia for state management</li>
              <li>Vue Router for navigation</li>
              <li>TailwindCSS v4 + shadcn-vue components</li>
              <li>VeeValidate + Zod for form validation</li>
              <li>TanStack Query for server state management</li>
              <li>vue-i18n for internationalization</li>
            </ul>
          </div>

          <div id="backend" class="space-y-2 scroll-mt-18">
            <h3 class="text-xl font-semibold">
              {{ t('about.technical.backend.title', 'Backend') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>FastAPI (Python) with async/await</li>
              <li>PostgreSQL database</li>
              <li>SQLAlchemy ORM with async support</li>
              <li>JWT authentication with refresh tokens</li>
              <li>Rate limiting and reCAPTCHA protection</li>
              <li>Modular architecture (auth, two-factor, email)</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- AI Context -->
      <section id="ai-context" class="space-y-4 scroll-mt-18">
        <h2 class="text-2xl font-semibold">
          {{ t('aiContext.title', 'AI Context') }}
        </h2>
        <p class="text-muted-foreground">
          {{ t('aiContext.subtitle', 'Short description of Gear Stack in Markdown format for AI assistants like ChatGPT') }}
        </p>

        <Card>
          <CardHeader>
            <div class="flex items-center justify-between">
              <div>
                <CardTitle>
                  {{ t('aiContext.card.title', 'Copy Context to Clipboard') }}
                </CardTitle>
                <CardDescription>
                  {{ t('aiContext.card.description', 'Click the button below to copy the context description. You can then paste it into ChatGPT or other AI assistants to provide context about Gear Stack.') }}
                </CardDescription>
              </div>
              <Button @click="handleCopy">
                <Copy v-if="!copied" class="size-4" />
                <Check v-else class="size-4" />
                {{ copied ? t('common.copyToClipboard.copied') : t('common.copyToClipboard.copy') }}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <pre class="whitespace-pre-wrap text-sm font-mono bg-muted p-4 rounded-md border overflow-x-auto max-h-[600px] overflow-y-auto">{{ aiContextMarkdown }}</pre>
          </CardContent>
        </Card>
      </section>
    </div>
  </AuthenticatedLayout>
</template>

