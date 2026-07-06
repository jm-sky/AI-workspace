# Research 05 — Wybór domyślnego modelu (OpenRouter)

> Cel: dobrać **domyślny model** na OpenRouter — tani, ale niezawodny w tool-callingu (cała pętla stoi na wywołaniach narzędzi) i sensowny w syntezie widoku 360°.
> Data: 2026-07. ⚠️ Ceny i ID modeli na OpenRouter zmieniają się co tydzień — **zweryfikować w chwili implementacji** na https://openrouter.ai/models.

## Kryteria

1. **Niezawodny tool-calling multi-turn** — nasza pętla jest wieloturowa; wg benchmarków multi-turn spada o 5–10 pkt vs single-turn dla *każdego* modelu, więc to najważniejsze kryterium.
2. **Niski koszt** (priorytet użytkownika — Claude drogi).
3. **Przyzwoita synteza/rozumowanie** — złożenie danych z wielu systemów w spójny widok.
4. **Dostępny na OpenRouter** z obsługą function calling.

## Sygnał z benchmarków (BFCL / tool-calling, lipiec 2026)

Czołówka tool-callingu jest wyrównana, a **Gemini Flash siedzi tuż przy szczycie mimo niskiej ceny**: Llama 3.1 405B (41.1), **Gemini 3.5 Flash (41.0)**, Claude Opus 4.8 (40.8). To nietypowe — zwykle „tanie" = „słabsze", a tu tani Flash rywalizuje z flagowcami w function-callingu.

## Shortlista kandydatów

| Model (rodzina) | Profil | Uwagi |
|---|---|---|
| ⭐ **Gemini Flash** (2.5/3.x Flash) | **najlepszy stosunek tool-calling/cena** | blisko czołówki BFCL, tani, szybki, duży kontekst — **główny kandydat na default** |
| **GPT-5 mini / GPT-4.1-mini** (OpenAI) | solidny, przewidywalny function calling + structured output | droższy od Flasha, ale bardzo stabilny — dobry do allow-listy jako „mocniejszy fallback" |
| **DeepSeek V3.x** | **skrajnie tani**, dobre rozumowanie | multi-turn tool-calling nieco słabszy; open-weights (opcja self-host później) — opcja „rock-bottom cost" |
| **Qwen3** | mocny open-model, tanie/darmowe tiery | dobry tool-use; kandydat do testów |
| **Claude Haiku** | tani Claude, spójny z rodziną | droższy niż Flash/DeepSeek; sensowny, jeśli chcemy zostać w Claude |

## Rekomendacja

- **Default: Gemini Flash (najnowszy Flash na OpenRouter).** Najlepszy profil tanio+niezawodny tool-calling; cała pętla na tym zyskuje.
- **Allow-lista (konfiguracja, dec. 8):** Gemini Flash (default) + jeden **mocniejszy** do trudnej syntezy (np. Claude Sonnet / GPT-5) jako per-agent override + jeden **skrajnie tani** (DeepSeek V3.x). To wprost realizuje „dostępne modele + domyślny" z kaskady konfiguracji.
- **Per-agent override:** agent „Jira 360°" może dostać mocniejszy model, jeśli Flash nie domyka syntezy — bez zmiany defaultu platformy.
- **Nie zamykać na sztywno — zwalidować A/B** na realnym zadaniu 360° (harness eval z `02-ai-techniques.md`): niezawodność tool-callingu i jakość syntezy vs koszt. Dopiero wynik A/B „zabetonuje" default.

## Do zrobienia przy implementacji
- Sprawdzić **aktualne ID modeli i ceny** na OpenRouter (zmienne co tydzień).
- Potwierdzić, że wybrany Flash wspiera **parallel/multi tool calls** w formacie OpenAI (nasza pętla może wołać kilka narzędzi naraz w fan-oucie 360°).
- Zmierzyć realny koszt jednego „widoku 360°" (tokeny wejścia z issue+wyników narzędzi) na 2–3 kandydatach.

## Źródła
- Function Calling / BFCL leaderboards: https://llm-stats.com/leaderboards/best-ai-for-tool-calling , https://benchlm.ai/llm-agent-benchmarks , https://www.spheron.network/blog/tool-calling-benchmarks-bfcl-tau-bench-latency-optimization/
- OpenRouter modele/ceny: https://openrouter.ai/models , https://openrouter.ai/pricing
- MCP-Bench (tool-using agents via MCP): https://arxiv.org/pdf/2508.20453
