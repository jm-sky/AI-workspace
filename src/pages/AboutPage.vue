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
  return `# AI Workspace - AI Context

## Overview
AI Workspace is an AI-native platform for organizations that combines knowledge, memory, agents, tools, workflows, and execution environments into a single system. Chat is the entry point; the product is an orchestration layer for AI agents.

## Key Capabilities
- **Multi-Tenant Platform** - Secure accounts with authentication, RBAC, and tenant isolation
- **Chat-First UX** - Natural interaction with automatic model, agent, and tool selection
- **Agent Orchestration** - OpenRouter + tool-calling loop with MCP integrations and SSE streaming
- **Cascade Configuration** - App → Tenant → Team → User settings with ceilings and allow-lists
- **Observable AI** - Task/Run trace with auditable steps, token usage, and cost tracking

## Core Features

### Chat & Agents
- Chat-first interface with streaming SSE responses
- Agent routing (explicit selection, hybrid routing planned)
- Rich output blocks: Markdown, cards, tables, charts
- Audit trail accessible from chat with copyable run/step traces

### Integrations (MCP)
- Thin MCP servers per provider (Jira, GitLab, Gmail, Teams planned)
- Per-user OAuth token injection into tool calls
- Jira 360° scenario: issue → client → fan-out to GitLab and other sources

### Configuration
- Cascade resolver: models, token limits, RAG on/off, tools on/off
- Effective config = intersection of ceilings + overrides
- Multi-tenant from day one (user ↔ tenant M:N)

## Business Features

### User Management & Security
- Email/password authentication with secure password hashing
- OAuth social login (Google, Microsoft, GitHub)
- Email verification, 2FA (TOTP + WebAuthn)
- JWT tokens with automatic refresh
- GDPR-compliant account deletion

### Multi-Language Support
- English and Polish fully supported
- Automatic locale detection and manual switching

### Theming
- Dark mode with system preference detection
- Sky/blue primary brand color

## Technical Stack

### Frontend
- Vue 3.5+ with TypeScript & Composition API
- Pinia, Vue Router, TailwindCSS v4 + shadcn-vue
- TanStack Query, vue-i18n

### Backend
- FastAPI (Python) with async/await
- PostgreSQL + pgvector (planned)
- SQLAlchemy ORM, modular architecture

## Architecture
- **Monorepo** - Vue frontend in repo root + FastAPI backend
- **OpenRouter** - OpenAI-compatible API with own tool-calling loop
- **MCP Tools** - Converted to OpenAI tool format for the agent loop
- **SSE Streaming** - Real-time agent steps and responses`
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
          {{ t('about.title', 'About AI Workspace') }}
        </h1>
        <p class="text-muted-foreground">
          {{ t('about.subtitle', 'AI-native workspace for organizations — chat-first agent platform with MCP integrations') }}
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
          {{ t('about.overview.description', 'AI Workspace is a full-stack platform that combines knowledge, memory, agents, tools, and workflows into a single system. Chat is the entry point; the product is an orchestration layer where AI agents reason, access organizational knowledge, and execute tasks with full auditability.') }}
        </p>
      </section>

      <!-- Key Capabilities -->
      <section id="capabilities" class="space-y-4 scroll-mt-18">
        <h2 class="text-2xl font-semibold">
          {{ t('about.capabilities.title', 'Key Capabilities') }}
        </h2>
        <ul class="list-disc list-inside space-y-2 text-muted-foreground">
          <li>{{ t('about.capabilities.multiUser', 'Multi-tenant platform with authentication, RBAC, and tenant isolation') }}</li>
          <li>{{ t('about.capabilities.chat', 'Chat-first UX with SSE streaming and auditable agent runs') }}</li>
          <li>{{ t('about.capabilities.agents', 'Agent orchestration via OpenRouter and MCP tool integrations') }}</li>
          <li>{{ t('about.capabilities.config', 'Cascade configuration from app to user with ceilings and allow-lists') }}</li>
          <li>{{ t('about.capabilities.integrations', 'Per-user OAuth for Jira, GitLab, and other enterprise systems') }}</li>
        </ul>
      </section>

      <!-- Core Features -->
      <section id="core-features" class="space-y-4 scroll-mt-18">
        <h2 class="text-2xl font-semibold">
          {{ t('about.coreFeatures.title', 'Core Features') }}
        </h2>
        <div class="space-y-6">
          <div id="chat-agents" class="space-y-2 scroll-mt-18">
            <h3 class="text-xl font-semibold">
              {{ t('about.coreFeatures.chat.title', 'Chat & Agents') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.coreFeatures.chat.streaming', 'Streaming SSE responses with Markdown and rich blocks') }}</li>
              <li>{{ t('about.coreFeatures.chat.sessions', 'Session history with search and run trace audit') }}</li>
              <li>{{ t('about.coreFeatures.chat.routing', 'Explicit agent selection with hybrid routing planned') }}</li>
            </ul>
          </div>

          <div id="integrations" class="space-y-2 scroll-mt-18">
            <h3 class="text-xl font-semibold">
              {{ t('about.coreFeatures.integrations.title', 'MCP Integrations') }}
            </h3>
            <ul class="list-disc list-inside space-y-1 text-muted-foreground ml-4">
              <li>{{ t('about.coreFeatures.integrations.oauth', 'Per-user OAuth token injection into tool calls') }}</li>
              <li>{{ t('about.coreFeatures.integrations.jira', 'Jira 360° scenario: issue → client → fan-out to GitLab and more') }}</li>
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
          {{ t('aiContext.subtitle', 'Short description of AI Workspace in Markdown format for AI assistants like ChatGPT') }}
        </p>

        <Card>
          <CardHeader>
            <div class="flex items-center justify-between">
              <div>
                <CardTitle>
                  {{ t('aiContext.card.title', 'Copy Context to Clipboard') }}
                </CardTitle>
                <CardDescription>
                  {{ t('aiContext.card.description', 'Click the button below to copy the context description. You can then paste it into ChatGPT or other AI assistants to provide context about AI Workspace.') }}
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

