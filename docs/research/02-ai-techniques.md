# Research 02 — Techniki pracy z AI

> Ścieżka 2 workstreamu research. Cel: przegląd technik (RAG, routing, pamięć, context engineering) i rekomendacje dla AI Workspace, zmapowane na decyzje i fazy z `docs/MVP.md`.
> Data: 2026-07. Runda 1 (RAG family, routing, context engineering/memory). Do pogłębienia: RAPTOR w praktyce, Graph RAG budowa grafu, eval RAG.

## Skrót wniosków (TL;DR)

- **RAG: zacznij od hybrid search + reranker** (foundation), nie od najbardziej złożonego. Graph RAG i RAPTOR dokładaj tylko dla trudnych, wielo-hopowych / cross-document pytań.
- **Agentic RAG pasuje wprost do naszego rdzenia** — agent (tool runner) sam decyduje, czy i kiedy pobrać wiedzę. To dokładnie nasza decyzja 12 (pamięć: auto-injection po progu **+** narzędzie do szukania na żądanie).
- **„Context rot"** — długi kontekst *pogarsza* wyniki. ⇒ selektywne wstrzykiwanie i kompresja są ważniejsze niż „wrzuć wszystko".
- **Routing to kilka osobnych problemów** (model / agent / tool / „kiedy myśleć") — nasza abstrakcja routera (dec. 9) powinna to rozróżniać.
- **SDK Anthropic ma gotowe cegły** pod te techniki: prompt caching, tool search tool (`tool_search_tool_regex/bm25` + `defer_loading`), context editing/compaction, adaptive thinking + `effort`.

## 1. Rodzina RAG — kiedy co

| Technika | Co robi | Kiedy używać |
|---|---|---|
| **Naive RAG** (dense) | chunk → embedding → top-k | baseline; szybko, ale słabe na precyzję/lexical |
| **Hybrid search + reranker** | sparse+dense (RRF) + reranker | **foundation** — pierwszy krok, gdy naive nie wystarcza; najlepszy stosunek koszt/jakość |
| **Graph RAG** | encje+relacje → graf → traversal | pytania „cross-document"/globalne, wielo-hop; do +35% na multi-hop vs vector |
| **RAPTOR** | rekurencyjne podsumowania → drzewo | retrieval wielopoziomowy (szczegół ↔ ogół) |
| **Agentic RAG** | agent w pętli: plan → retrieve → oceń → doszukaj | złożone pytania wymagające rozumowania; **marnotrawstwo dla prostych faktów** |

**Rekomendacja dla nas:**
- **Faza 4** startuje od **hybrid + reranker**. To baza pamięci i RAG (wspólna infra wektorowa, dec. 12).
- **Agentic RAG** dostajemy „za darmo" z tool runnera — agent woła narzędzie retrieval, gdy uzna za potrzebne (nasze narzędzie do przeszukiwania pamięci na żądanie). Nie budujemy osobnego pipeline'u.
- **Graph RAG / RAPTOR** — później, dla scenariuszy syntezy cross-document (widok 360° z wielu źródeł to naturalny kandydat). Zgodne z wnioskiem z comparables (Writer/Glean: KG-grounded RAG jako kotwica faktów).
- **Permissions-aware retrieval** (wniosek z comparables, Glean): przy per-user OAuth każdy retrieval musi filtrować po uprawnieniach użytkownika **przed** rankingiem — projektujemy to w warstwie retrieval od początku.

## 2. Routing — to nie jeden problem

- **Model routing** — dobór LLM z puli wg koszt/jakość/latencja/prywatność (np. vLLM Semantic Router, R2-Router). U nas: start jednodostawcowy (SDK Anthropic), ale **warstwa modelu zaprojektowana pod pulę** (spójne z „dostępne modele/domyślny" w konfiguracji i wnioskiem z comparables o hubie wielu LLM).
- **Agent routing** (nasza dec. 9) — semantyczne dopasowanie zapytania do agenta po **embeddingu opisu agenta** (nasze „opis używany przez auto-router"). Start: jawny wybór; auto-router jako druga strategia.
- **Tool routing / tool search** — gdy narzędzi jest dużo, nie ładować wszystkich schematów; dynamiczne wyszukiwanie (nasza flaga tool search; w SDK Anthropic `tool_search_tool_*` + `defer_loading`). Kierunek MemTool: dynamiczne zarządzanie zestawem narzędzi w rozmowie.
- **„Kiedy myśleć"** (Semantic Router / „When to Reason") — dobór głębi rozumowania per zapytanie. U nas: **adaptive thinking + `effort`** per agent (konfigurowalne w schemacie agenta).

## 3. Context engineering & pamięć

- **Context rot** — wraz ze wzrostem tokenów model **gorzej** korzysta z informacji rozproszonej w długim kontekście. ⇒ nasza pamięć **selektywna** (próg podobieństwa) i **kompresja** są słuszne; unikać „wrzuć całą historię".
- **Zarządzanie temporalne pamięci** — short vs long-term, session vs cross-session, **polityki zapominania/decay**. ⇒ mapuje na nasze zakresy (sesja/użytkownik/agent); **decay/forgetting to otwarty punkt do zaprojektowania**.
- **Assembly i kolejność kontekstu** — hierarchia instrukcji, umiejscowienie wyników narzędzi, kolejność pamięci (świeże vs fundamentalne). ⇒ praktyczne wytyczne do składania promptu agenta; warto ustandaryzować „szablon kontekstu".
- **Kompresja / caching** — RAG-style memory (retrieve on demand) vs token-level (podsumowania, bufory). W SDK Anthropic: **prompt caching** (tani, gdy stały prefix — nasz system prompt/definicja agenta), **context editing** (czyszczenie starych tool-results/thinking), **compaction** (podsumowanie historii). ⇒ używać od Fazy 1 dla kosztów i stabilności.

## Mapowanie na decyzje i fazy

| Technika | Nasza decyzja / faza | Uwaga |
|---|---|---|
| Hybrid + reranker (foundation) | Faza 4 (Pamięć + RAG) | pierwszy krok RAG |
| Agentic RAG | dec. 2 (tool runner) + dec. 12 (memory tool) | „za darmo" z rdzenia |
| Graph RAG / RAPTOR | później (cross-doc synteza) | kandydat: widok 360° |
| Permissions-aware retrieval | dec. 3 (per-user OAuth) | filtr przed rankingiem |
| Model routing | „dostępne modele" (dec. 8) | warstwa modelu pod pulę |
| Agent routing (embedding opisu) | dec. 9 | start jawny, auto później |
| Tool search / defer_loading | schemat agenta (dec. 11) | SDK Anthropic ma gotowe |
| Adaptive thinking + effort | dec. 2, schemat agenta | per agent |
| Prompt caching / compaction / context editing | dec. 2, Faza 1 | koszt + stabilność |
| Selektywna pamięć + decay | dec. 12 | decay = otwarty punkt |

## Do pogłębienia
- **RAPTOR i Graph RAG** — jak budować (koszt indeksacji, aktualizacja grafu, utrzymanie).
- **Eval RAG** — jak mierzyć jakość retrievalu/odpowiedzi (multi-hop, deep search benchmarks).
- **Polityki decay/forgetting** dla pamięci per zakres.
- **Reranker i embeddingi** — konkretny wybór technologii (wspólny z otwartym punktem „magazyn wektorowy + embeddingi").

## Źródła
- RAG strategie 2025: https://synthimind.net/blog/rag-optimization-strategies-2025/ , https://blog.starmorph.com/blog/rag-techniques-compared-best-practices-guide
- Systematic review RAG: https://arxiv.org/pdf/2507.18910
- Context engineering / pamięć: https://mem0.ai/blog/context-engineering-ai-agents-guide , https://arxiv.org/pdf/2510.12635 (Memory as Action) , https://arxiv.org/pdf/2507.21428 (MemTool)
- Routing: https://github.com/vllm-project/semantic-router , https://arxiv.org/pdf/2510.08731 (When to Reason) , https://arxiv.org/html/2602.02823v1 (R2-Router)
