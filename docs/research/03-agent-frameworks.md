# Research 03 — Frameworki agentowe

> Ścieżka 3 workstreamu research. Cel: walidacja decyzji 2 (SDK Anthropic teraz, LangGraph przy multi-agent) i ustalenie kryteriów przełączenia.
> Data: 2026-07.

## Skrót wniosków (TL;DR)

- **Nasz wybór jest zgodny z rekomendacją rynku:** „proste pętle narzędziowe → minimalny SDK dostawcy; wielokrokowe stanowe workflow w Pythonie → LangGraph". ✅ SDK Anthropic (tool runner) na MVP, LangGraph na multi-agent.
- **MCP jest przenośne między frameworkami** (PydanticAI, OpenAI SDK, Google ADK, mcp-agent działają natywnie z MCP) — nasza warstwa narzędzi MCP (dec. 5) nie zwiąże nas z żadnym frameworkiem.
- **LangGraph = graf stanów + checkpointing (time-travel/replay)** — to nie tylko orkiestracja multi-agent, ale też mechanizm **replay/audytu**, którego chcemy (dec. 13). Naturalny wybór na fazę multi-agent.
- **A2A (agent-to-agent)** rośnie jako standard interop (Google ADK natywnie; też ServiceNow/Copilot z comparables) — do obserwacji na fazę multi-agent, obok MCP.
- **Anthropic Managed Agents** (hosted) to alternatywa dla self-hosted tool runnera; ich koncepcje **vaults** (per-user credentials) i **agent-config jako obiekt** walidują nasze decyzje 3 (magazyn tokenów) i 10 (edytor agentów).

## Style orkiestracji (mapa rynku)

| Styl | Przykłady | Kiedy |
|---|---|---|
| **Graph-based** | LangGraph, MS Agent Framework | wielokrokowe stanowe workflow, rozgałęzienia, checkpoint/replay |
| **Handoff-based** | OpenAI Agents SDK | proste przekazania między agentami, minimalne API |
| **Role-based** | CrewAI, Agno | szybki prototyp „zespół ról" (researcher/writer/reviewer) |
| **Hierarchical** | Google ADK | hierarchia agentów, natywne A2A (interop między frameworkami) |
| **Minimal SDK loop** | **Claude/Anthropic SDK**, OpenAI SDK | pojedynczy agent w pętli narzędzi, pełna kontrola/audyt |

## Nasze warianty — porównanie

| Kryterium | SDK Anthropic (tool runner) — **nasz rdzeń** | LangGraph — **faza multi-agent** | Managed Agents (Anthropic, hosted) |
|---|---|---|---|
| Model pętli | tool runner prowadzi pętlę; my logujemy każdy krok | graf węzłów/krawędzi, wspólny typowany stan | serwer prowadzi pętlę; my sterujemy zdarzeniami |
| Multi-agent | ręcznie / później | natywne (równoległe sub-agenty, warunki) | wbudowane (coordinator + threads) |
| Stan / replay | sami trzymamy (trace, dec. 13) | **checkpointing + time-travel** (PostgresSaver) | server-side sesje/trace |
| MCP | natywne (helpery MCP) | przez adaptery | natywne (mcp_toolset) |
| Audyt/kontrola | **pełna** (rdzeń cienki) | dobra (graf + checkpoints) | zależna od platformy |
| Hosting | self-hosted (reuse gear-stack) | self-hosted | hosted przez Anthropic |
| Per-user OAuth | my wstrzykujemy token | my wstrzykujemy token | **vaults** (auto-refresh) |

**Dlaczego nie hosted (Managed Agents) na MVP:** chcemy pełnej kontroli nad audytem, self-hostingu i reuse rdzenia gear-stack (dec. 4) + własnych serwerów MCP (dec. 5). Ale ich **vaults** to dobry wzorzec dla naszego magazynu tokenów per-user, a **agent jako wersjonowany obiekt** — dla edytora agentów.

## Kryteria przełączenia SDK Anthropic → LangGraph

Przechodzimy na LangGraph (jako orkiestrator ponad tymi samymi narzędziami MCP), gdy pojawi się **którekolwiek**:
- realny **drugi agent** i potrzeba jawnej koordynacji (Planner/Executor/Reviewer),
- **równoległe sub-agenty** / rozgałęzienia warunkowe w jednym zadaniu,
- **human-in-the-loop** z pauzą/wznowieniem w środku grafu,
- potrzeba **checkpoint/replay na poziomie kroków** ponad to, co daje nasz trace,
- długie, wznawialne joby w tle (workflow engine z wizji).

Dopóki to jeden agent w pętli (Faza 1–4) — tool runner wygrywa prostotą i kontrolą.

## Do obserwacji
- **A2A** — jeśli pojawi się potrzeba interop z agentami z innych frameworków (Google ADK, ServiceNow).
- **PydanticAI** — type-safe, tani, budowany przez zespół Pydantic (który stoi też za SDK Anthropic); nasz backend to Python/Pydantic (gear-stack) — potencjalny komplement, gdyby tool runner uwierał.
- **LangGraph v1.x** — stabilne API checkpointera (PostgresSaver) pasuje do naszej bazy Postgres.

## Źródła
- LangGraph: https://www.langchain.com/langgraph , https://github.com/langchain-ai/langgraph , https://sparkco.ai/blog/mastering-langgraph-checkpointing-best-practices-for-2025
- Porównania frameworków: https://www.speakeasy.com/blog/ai-agent-framework-comparison/ , https://langfuse.com/blog/2025-03-19-ai-agent-comparison , https://dev.to/hani__8725b7a/agentic-ai-frameworks-comparison-2025-mcp-agent-langgraph-ag2-pydanticai-crewai-h40
