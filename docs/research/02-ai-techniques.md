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

## Runda 2 — pogłębienie

### Graph RAG / RAPTOR w praktyce — uwaga na koszt indeksacji
- Pełny GraphRAG bywa **prohibicyjnie drogi** (dużo wywołań LLM + summaryzacja). Historycznie indeksacja jednego zbioru potrafiła kosztować dziesiątki tys. USD; **Microsoft LazyGraphRAG** zbił koszt indeksacji do poziomu **vector RAG (~0,1% pełnego GraphRAG)** przy zachowaniu jakości.
- **RAPTOR** jest drogi w budowie (rekurencyjna summaryzacja → miliony tokenów). **EraRAG** (aktualizacje przyrostowe) redukuje ~**57% tokenów** vs RAPTOR i ~**77% czasu** przebudowy grafu.
- **Wniosek dla nas:** jeśli w ogóle graf, to **lazy/incremental** (LazyGraphRAG + przyrostowe update jak EraRAG), nigdy „pełny GraphRAG od zera przy każdej zmianie". Dla widoku 360° graf dokładamy dopiero, gdy hybrid+reranker przestanie wystarczać na pytania cross-document.

### Ewaluacja RAG — mierzyć od Fazy 4
- **RAGAS** — metryki: **faithfulness** (spójność odpowiedzi z kontekstem = anty-halucynacja), **context precision/recall**, **answer relevancy**, groundedness, hallucination detection. Praktyczne minimum: **faithfulness + recall + relevance**.
- Benchmarki cross-document: **MultiHop-RAG** (dowody rozłożone na 2–4 dokumenty), **CRAG**.
- **Wniosek dla nas:** od Fazy 4 utrzymywać **złoty zbiór pytań** (per typ agenta) i liczyć te 3 metryki w CI — inaczej „ulepszenia" RAG są nie do zmierzenia.

### Pamięć jako zarządzany lifecycle (domyka otwarty punkt „decay")
- Nowoczesne systemy (Mem0, Zep) traktują pamięć jako **zarządzany cykl życia, nie pasywny append**: extract → update z operacjami **ADD / UPDATE / DELETE / NOOP**; Zep utrzymuje temporalny knowledge graph.
- **Decay/forgetting:** Ebbinghaus-inspired (MemoryBank), okresowa **konsolidacja przez refleksję** (Generative Agents).
- **Wniosek dla nas (dec. 12 + otwarty punkt decay):** nasza pamięć powinna mieć **operacje** (dodaj/aktualizuj/usuń/scal), nie tylko dopisywanie, oraz **politykę decay/konsolidacji** (np. okresowa refleksja + wygaszanie starych, nietrafianych wpisów). To realistyczny, oszczędny wybór na później; w MVP wystarczy ADD + retrieval, ale zaprojektować interfejs pod pełny lifecycle.

## Do pogłębienia
- **Reranker i embeddingi** — konkretny wybór technologii (wspólny z otwartym punktem „magazyn wektorowy + embeddingi").
- **LazyGraphRAG / EraRAG** — proof-of-concept, gdy dojdziemy do cross-document 360°.
- **Harness eval RAG w CI** — narzędzie (RAGAS/Langfuse) + złote zbiory.

## Źródła
- RAG strategie 2025: https://synthimind.net/blog/rag-optimization-strategies-2025/ , https://blog.starmorph.com/blog/rag-techniques-compared-best-practices-guide
- Systematic review RAG: https://arxiv.org/pdf/2507.18910
- Context engineering / pamięć: https://mem0.ai/blog/context-engineering-ai-agents-guide , https://arxiv.org/pdf/2510.12635 (Memory as Action) , https://arxiv.org/pdf/2507.21428 (MemTool)
- Routing: https://github.com/vllm-project/semantic-router , https://arxiv.org/pdf/2510.08731 (When to Reason) , https://arxiv.org/html/2602.02823v1 (R2-Router)
- Graph RAG koszt/incremental: https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/ , https://arxiv.org/pdf/2506.20963 (EraRAG) , https://arxiv.org/html/2502.11371v3 (RAG vs GraphRAG)
- Eval RAG: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/ , https://www.confident-ai.com/blog/rag-evaluation-metrics-answer-relevancy-faithfulness-and-more
- Pamięć / decay: https://arxiv.org/html/2601.01885v1 (Agentic Memory) , https://arxiv.org/pdf/2505.00675 (Rethinking Memory) , https://github.com/Shichun-Liu/Agent-Memory-Paper-List
