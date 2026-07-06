# AI Workspace / AI Operating System

> **Status:** Bootstrap complete (gear-stack mirror) — Faza 0 (fundament) next

## Idea

AI Workspace is an AI-native platform for organizations that combines knowledge, memory, agents, tools, workflows and execution environments into a single system.

The chat interface is only the entry point. The real product is an orchestration layer that enables AI agents to reason, access organizational knowledge, collaborate, execute tasks and automate business processes.

The long-term vision is to build an **AI Operating System** for organizations.

---

# Goals

- Centralize organizational knowledge.
- Make AI an active member of the team rather than just a chatbot.
- Provide a unified platform for AI agents, workflows and automation.
- Enable secure access to company systems and data.
- Keep every AI action observable, auditable and reproducible.

---

# Core Ideas

## Multi-tenancy

The platform is designed as a SaaS application.

Hierarchy:

- Organization (Tenant)
- Teams
- Users
- Projects
- Agents

Each level may have its own knowledge, memory, permissions and configuration.

Self-hosted deployment should also be possible in the future.

---

## Chat-first UX

Chat is the main user interface.

Users interact naturally with the system while the platform automatically:

- selects models,
- selects agents,
- chooses tools,
- retrieves knowledge,
- builds context,
- executes workflows.

---

## Chat UI Extensions

Chat responses are not limited to Markdown.

The platform should support rich interactive outputs through plugins/tools, including:

- interactive tables
- charts
- dashboards
- Mermaid diagrams
- flowcharts
- sequence diagrams
- architecture diagrams
- timelines
- mind maps
- Kanban boards
- spreadsheets
- maps
- image galleries
- code viewers
- PDF/document preview
- file diff viewers

The LLM should automatically choose the most appropriate visualization for the generated content.

Markdown remains the default output format, while rich visualizations complement the conversation whenever they improve understanding.

---

## Memory

Different memory scopes:

- Session Memory
- User Memory
- Team Memory
- Organization Memory
- Project Memory
- Agent Memory

Memory should be automatically injected into prompts depending on context.

---

## Knowledge Layer

The platform should expose organizational knowledge through a unified abstraction.

Potential sources:

- documents
- files
- SQL databases
- APIs
- GraphQL
- MCP tools
- Confluence
- SharePoint
- Wikis
- Email
- Calendars

Knowledge retrieval is automatic.

The agent decides which sources should be queried.

---

## Integrations

The preferred integration standard is **Model Context Protocol (MCP)**.

Goal:

Plug-and-play integrations.

Typical flow:

1. Connect provider.
2. Authenticate.
3. Grant permissions.
4. AI agents can immediately use available tools.

Native integrations may still exist where necessary.

### Initial Integrations

The first version should focus on the most commonly used productivity and development platforms.

- GitHub
- Jira
- Gmail
- Google Calendar
- Google Drive
- Microsoft Teams
- Microsoft Outlook
- Microsoft OneDrive
- Slack
- Confluence

Future integrations may include ERP, CRM, databases, cloud providers and custom enterprise systems.

---

## Agents

Examples:

- Developer
- Accountant
- HR
- Support
- DevOps
- Researcher

Agents should:

- plan work,
- collaborate,
- use tools,
- execute tasks,
- review results.

---

## Agent Teams

Multiple agents working together.

Possible roles:

- Planner
- Researcher
- Executor
- Reviewer

---

## Tasks

Prompt → Task.

Tasks become first-class objects.

Each task should have:

- state
- history
- assigned agents
- artifacts
- replay
- continuation

---

## Workflow Engine

Support for:

- scheduled jobs
- event-driven automations
- AI pipelines
- multi-agent workflows

---

## Execution Environment

Agents should execute code in isolated environments.

Possible runtimes:

- Python
- Node.js
- Bash
- SQL
- Docker

Typical use cases:

- data analysis
- report generation
- automation
- file processing

---

## Audit

Everything should be observable.

Examples:

- prompts
- model calls
- tool calls
- retrieved knowledge
- execution history
- costs
- timing
- replay

---

## Security

- RBAC
- agent permissions
- tool permissions
- knowledge permissions
- sandboxed execution

---

# AI Techniques (Research)

The exact architecture is still under investigation.

Topics to research include:

- RAG
- Memory Injection
- RAPTOR
- Graph RAG
- Agentic RAG
- Hybrid Search
- Query Routing
- Context Engineering
- Prompt Engineering
- Long-term Memory
- Model Routing
- Prompt Routing
- Tool Routing
- Context Compression
- Context Caching
- Overlapping batches
- Semantic search
- Knowledge graphs

This list will evolve during research.

---

# Administration Ideas

Potential admin features:

- Model routing
- Prompt routing
- Agent routing
- Tool routing
- Cost limits
- Model policies
- Permission management
- Organization configuration

---

# Development Plan

This repository starts as a research and architecture project.

Initial goals:

- define product vision;
- research state-of-the-art AI techniques;
- compare existing frameworks;
- compare commercial AI platforms;
- document architectural decisions;
- define MVP;
- identify reusable components;
- implement incrementally.

Claude Code will be used as the primary development and research assistant.

Research tasks include:

- summarizing AI papers;
- reviewing RAG techniques;
- reviewing prompt engineering practices;
- evaluating AI frameworks;
- evaluating enterprise AI products;
- documenting findings inside this repository;
- proposing architecture improvements.

The repository will gradually become the project's knowledge base and design documentation.

---

# Existing Foundation

A significant part of the platform may reuse the core from **gear-stack.ovh**.

Potential reusable components:

- FastAPI backend
- authentication
- users
- OAuth
- 2FA
- RBAC
- multi-tenancy
- API foundation
- infrastructure

The final scope of reused components is yet to be determined.

---

# Current Status

This project is currently in the **vision and architecture phase**.

The first milestone is not writing production code.

The first milestone is:

- validating the idea;
- researching existing solutions;
- designing the architecture;
- identifying the MVP;
- building a solid foundation for long-term development.

---

# Documentation

Planning and research live under [`docs/`](docs/) — start with the index:

- **[docs/README.md](docs/README.md)** — documentation index.
- **[docs/MVP.md](docs/MVP.md)** — MVP plan: architectural decisions, agent schema, build sequence, open points.
- **[docs/research/](docs/research/)** — research workstream; indeks w [research/README.md](docs/research/README.md), synteza w [implications](docs/research/2026-07-04--000--implications.md).
