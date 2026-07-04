# Research 01 — Platformy AI klasy enterprise (comparables)

> Ścieżka 1 workstreamu research. Cel: jak robią to gotowe produkty enterprise i jakie wnioski dla AI Workspace.
> Data: 2026-07. Runda 1 (Glean, Google Agentspace, Dust, Microsoft Copilot Studio). Kolejne do dołożenia: Writer, Salesforce Agentforce, ServiceNow, Cohere North.

## Skrót wniosków (TL;DR)

- **MCP stał się de facto standardem integracji** w platformach enterprise (Dust i Copilot Studio są MCP-native; MCP GA w Copilot Studio). ✅ potwierdza naszą decyzję „narzędzia jako MCP".
- **Retrieval musi być permissions-aware** — filtrowanie po uprawnieniach użytkownika *przed* rankingiem, nie tylko ukrywanie w UI (Glean). ⇒ istotne dla naszego per-user OAuth + RAG.
- **No-code edytor agentów to standard** (Agentspace Agent Designer, Copilot Studio, Dust). ✅ potwierdza nasz „edytor agentów dla adminów".
- **Wszyscy idą w multi-agent orchestration** (Glean Agentic Engine 2 — adaptive planning + równoległe sub-agenty; Copilot Studio — A2A, multi-agent GA). ✅ potwierdza nasze „LangGraph/multi-agent później".
- **Model-agnostyczność / hub wielu LLM + BYO-key** to trend (Glean 15+ LLM, Dust: OpenAI/Anthropic/Google/Mistral). ⚠️ my startujemy na SDK Anthropic — świadomie; warto zaprojektować warstwę modelu tak, by dało się dołożyć innych dostawców (spójne z „dostępne modele" w konfiguracji).
- **Governance/audyt jako filar** (Copilot Studio: audyt aktywności, inventory tenant-wide, CMK). ✅ potwierdza nasz nacisk na audyt + kaskadę konfiguracji z sufitami.

## Platformy

### Glean — „Work AI" na bazie enterprise knowledge graph
- Indeksuje 100+ aplikacji SaaS do **permissions-aware knowledge graph**; serwuje przez Assistant, Agents i no-code Apps.
- **Retrieval:** RAG ponad knowledge graph; **query-time filtering** rozwiązuje bieżące uprawnienia użytkownika *przed* rankingiem — wyniki, do których user nie ma prawa, wypadają z kandydatów. Odpowiedzi z odnośnikami do źródeł.
- **Agenty:** Agentic Engine 2 — adaptive planning + równoległa orkiestracja sub-agentów; wieloetapowe procesy, follow-upy, fine-grained permissioning.
- **Modele:** hub 15+ LLM, BYO model keys.
- **Wniosek dla nas:** wzorzec „permissions-aware retrieval" to must dla RAG w multi-tenant z per-user OAuth. Odnośniki do źródeł = nasz blok „odnośniki do źródeł" w widoku 360°.

### Google Agentspace (Gemini Enterprise) — search-agent + no-code agenty
- Centralny, multimodalny **search agent** jako „single source of truth"; gotowe konektory (Confluence, Slack, Drive, **Jira**, SharePoint, ServiceNow).
- **Agent Designer** — no-code tworzenie agentów podpiętych do źródeł danych.
- **Deep Research agent** — syntezuje wiedzę z wielu źródeł w raport (bliskie naszemu „widok 360°").
- **Wniosek dla nas:** potwierdza wartość scenariusza „zbierz i zsyntetyzuj z wielu źródeł"; no-code Agent Designer = nasz edytor agentów.

### Dust — „AI operating system for work" (najbliższy naszej wizji)
- Zespoły agentów ze **współdzielonym kontekstem**; 100+ konektorów; model-agnostyczny (OpenAI/Anthropic/Google/Mistral).
- **MCP jako klient i serwer** — agenci łączą się z zewnętrznymi serwerami MCP, można podpiąć własne (custom MCP servers), z zarządzaniem auth i dostępem. Narzędzia działają na **credentials osobistych lub workspace** (dokładnie nasz motyw per-user vs współdzielone).
- Wiele powierzchni: UI konwersacyjne, Slack, rozszerzenie Chrome, CLI, REST API, webhooki, OAuth2.
- **Wniosek dla nas:** to najbliższy „AI OS for work" — potwierdza cały nasz kierunek (MCP-native, per-user credentials, wiele frontów na jednym silniku). Ich „synthetic filesystem" mapujący źródła to ciekawy pomysł na przyszłość (jednolita nawigacja po danych).

### Microsoft Copilot Studio — agent builder + governance w ekosystemie MS
- **MCP GA** z rosnącym wsparciem konektorów; multi-agent orchestration (Fabric, Agents SDK, **A2A** — agent-to-agent) w GA.
- **Wiedza:** kolekcje plików jako jedno źródło; odwołania do **Outlook** i **Teams** (czaty, kanały, spotkania) — pokrywa się z naszymi integracjami Gmail/Teams.
- **Governance:** audyt aktywności (Purview/Sentinel), tenant-wide inventory, customer-managed keys, podgląd postawy bezpieczeństwa agenta w kreatorze.
- **Wniosek dla nas:** wzorzec governance (audyt + inventory + polityki na poziomie tenantа) potwierdza naszą kaskadę konfiguracji z sufitami i nacisk na audyt dostępny/„inspekcjonowalny".

## Przekrojowe wzorce → mapowanie na nasze decyzje

| Wzorzec z rynku | Nasza decyzja | Status |
|---|---|---|
| MCP jako standard integracji (Dust, Copilot Studio) | Własne cienkie serwery MCP (dec. 5) | ✅ zgodne |
| Permissions-aware retrieval przed rankingiem (Glean) | per-user OAuth (dec. 3) + RAG (dec. 12) | ⇒ wymóg do zaprojektowania w RAG/pamięci |
| No-code edytor agentów (Agentspace, Copilot Studio, Dust) | Edytor agentów dla adminów (dec. 10–11) | ✅ zgodne |
| Multi-agent orchestration (Glean, Copilot Studio) | Multi-agent/LangGraph później (dec. 2) | ✅ zgodne (odłożone świadomie) |
| Hub wielu LLM + BYO key (Glean, Dust) | Start SDK Anthropic; „dostępne modele" w konfiguracji | ⚠️ zaprojektować warstwę modelu pod wielu dostawców |
| Governance/audyt na poziomie tenantа (Copilot Studio) | Kaskada konfiguracji (dec. 8) + audyt (dec. 13) | ✅ zgodne |
| Per-user vs workspace credentials (Dust) | per-user OAuth, dane tenant-scoped (dec. 3, 15) | ✅ zgodne |

## Do pogłębienia w kolejnych rundach
- Writer, Salesforce Agentforce, ServiceNow AI, Cohere North.
- Jak dokładnie robią **permissions-aware RAG** przy per-user OAuth (indeksacja z ACL vs filtrowanie query-time).
- Warstwa modelu: jak abstrahować wielu dostawców LLM, skoro rdzeń oparliśmy na SDK Anthropic (tool runner).

## Źródła
- Glean: https://www.glean.com/press/glean-introduces-third-generation-ai-assistant-new-enterprise-graph-to-enable-the-superintelligent-enterprise , https://www.glean.com/perspectives/security-permissions-aware-ai , https://futurumgroup.com/insights/glean-doubles-arr-to-200m-can-its-knowledge-graph-beat-copilot/
- Google Agentspace: https://cloud.google.com/blog/products/ai-machine-learning/google-agentspace-enables-the-agent-driven-enterprise , https://blog.google/feed/google-agentspace/
- Dust: https://blog.dust.tt/mcp-and-enterprise-agents-building-the-ai-operating-system-for-work/ , https://blog.dust.tt/give-dust-agents-access-to-your-internal-systems-with-custom-mcp-servers/ , https://dust.tt/blog/2025-dust-product-update-recap
- Microsoft Copilot Studio: https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/multi-agent-orchestration-maker-controls-and-more-microsoft-copilot-studio-announcements-at-microsoft-build-2025/ , https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
