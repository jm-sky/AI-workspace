# Issue 024 — Załączniki w czacie + vision

**Data:** 2026-07-20  
**Status:** `planned`  
**Priorytet:** P1  
**Plan bazowy:** [2026-07-09--002--chat-attachments.md](../plans/2026-07-09--002--chat-attachments.md)  
**Powiązane:** [#020](./2026-07-09--020--chat-attachments-plan.md) (sam plan — zrobiony)  
**Wzorzec Kancelarii:** [#012](../../../ai-kancelaria/docs/alfa/issues/2026-012-chat-attachments.md) — Etap A+B+D ✅, Etap C vision 🟡 (działa e2e na Ollama `llama3.2-vision`)

## Cel

Dołączanie plików do wiadomości + ścieżka **vision** dla obrazów przez modele multimodal OpenRouter.

Zakres funkcjonalny (z planu 002 + vision):
- **Obrazy** — upload, miniatura, podgląd, skalowanie dużych plików, content parts → model vision.
- **Tekst** (`txt`, `md`, `json`, `csv`, `yaml`) — ekstrakcja → treść w kontekście.
- **PDF** — ekstrakcja tekstu (etap późniejszy w planie).
- **Bezpieczeństwo** — sniff MIME, limity rozmiaru, brak zaufania do rozszerzenia.
- **Katalog modeli** — flaga `supports_vision` / filtrowanie modeli multimodal.

## Stan obecny (Workspace)

- Plan 002 gotowy; reuse storage + `ImageProcessor`.
- Composer bez pickera; wiadomość = string (bez content parts).
- Brak tabeli załączników / endpointu uploadu pod czat.

## Stan Kancelarii (po pullu 2026-07)

- ✅ UI załączników + ekstrakcja tekst/PDF.
- ✅ Vision path w `llm.py` / `agent.py` (osobny system prompt; w ich iteracji vision **bez** pętli MCP).
- 🟡 Retest jakości vision.

## Zakres implementacji

- [ ] Backend: upload + metadane załącznika powiązane z sesją/runem
- [ ] Content parts w `agent_loop` (tekst + `image_url` data URL / URL storage)
- [ ] Wybór / walidacja modelu vision (OpenRouter)
- [ ] FE: picker, miniatury, podgląd, błędy walidacji przed send
- [ ] (Opcjonalnie) PDF text extract jak w planie 002 etap 3

## Uwagi produktowe

U Kancelarii vision wyłącza tool-calling w tej samej turze. U nas do ustalenia przy implementacji: czy tura z obrazem może jednocześnie wołać tooli (zależy od modelu OpenRouter), czy osobna ścieżka „vision-only”.
