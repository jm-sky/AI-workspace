# Plan 002 — Załączniki w czacie (attachments picker)

**Status:** `in progress`  
**Data:** 2026-07-09 (aktualizacja 2026-07-23: etapy 1–3 obrazów)  
**Obszar:** backend (`agent`, `core/storage`) + frontend (`workspace`)

## Cel

Możliwość dołączenia plików do wiadomości w czacie workspace:

- **obrazy** — miniatura w composerze i w wątku, duży podgląd po kliknięciu,
- **formaty tekstowe** (`txt`, `md`, `json`, `csv`, `yaml`) — treść trafia do modelu,
- **PDF** — ekstrakcja tekstu (etap 3),
- **bezpieczeństwo** — walidacja typu po zawartości, limity, skalowanie dużych obrazów.

## Stan obecny (co już jest — reuse, nie pisać od zera)

| Element | Gdzie | Uwaga |
|---------|-------|-------|
| Adapter storage (local + S3) | `backend/app/core/storage/` | `upload/download/delete/exists/get_url` |
| Skalowanie / kompresja obrazów | `core/storage/image_processor.py` | `ImageProcessor(max_width, max_height, jpeg_quality, convert_to_webp)`, async przez `asyncio.to_thread` |
| Wzorzec uploadu z walidacją | `modules/gear/catalogue_item_image_upload_service.py` | `python-magic` (sniff MIME), `MIME_TO_EXTENSION`, `IMAGE_PROCESSING_MODES` |
| Konfiguracja | `core/config.py:477` `StorageSettings` | `STORAGE_TYPE`, `STORAGE_LOCAL_PATH`, `STORAGE_BASE_URL`, S3 |
| Zależności | `backend/requirements.txt:28-29` | `Pillow`, `python-magic` już są |
| Composer | `src/modules/workspace/components/ChatComposer.vue` | dziś tylko `Textarea` + `Send` |
| Wiadomość → model | `agent/services/agent_loop.py:111` | `{"role": "user", "content": user_message}` — **string**, do zamiany na content parts |
| Request czatu | `agent/schemas.py:12` | `message: str` (max 8000) |

**Brakuje:** flagi `supports_vision` w katalogu modeli (`ai/utils/models_config.py` — wpisy
nie mają tego pola), biblioteki do PDF, tabeli załączników.

Następna migracja: **`062`**.

## Architektura

### Przepływ

Upload jest **oddzielony** od wysłania wiadomości (jak w ChatGPT) — użytkownik widzi
miniaturę i błędy walidacji zanim wyśle prompt.

```
1. POST /agent/attachments        (multipart, 1 plik)  -> { id, kind, thumbnailUrl, ... }
2. POST /agent/chat/stream        { message, attachmentIds: [...] }
3. agent_loop buduje content parts -> OpenRouter
```

Załącznik po uploadzie jest „osierocony” (`run_id = NULL`) i dowiązywany do run-a przy
wysłaniu wiadomości. Osierocone rekordy starsze niż 24 h — do sprzątnięcia (cron/CLI).

### Migracja `062_chat_attachments.py`

Tabela `chat_attachments`:

| Kolumna | Typ | Uwaga |
|---------|-----|-------|
| `id` | `String(36)` PK | `generate_id()` |
| `owner_user_id` | FK `users.id` CASCADE | authz |
| `tenant_id` | FK `tenants.id` CASCADE | izolacja tenantów |
| `session_id` | FK `chat_sessions.id` CASCADE, nullable | |
| `run_id` | FK `agent_runs.id` SET NULL, nullable | dowiązanie przy wysłaniu |
| `kind` | `String(20)` | `image` \| `text` \| `pdf` |
| `original_filename` | `Text` | tylko do wyświetlenia, **nigdy** jako ścieżka |
| `mime_type` | `String(100)` | wykryty z zawartości |
| `size_bytes` | `Integer` | po przetworzeniu |
| `storage_path` | `Text` | ścieżka w adapterze |
| `thumbnail_path` | `Text` nullable | tylko `kind=image` |
| `width` / `height` | `Integer` nullable | po skalowaniu |
| `extracted_text` | `Text` nullable | `kind` ∈ {`text`,`pdf`} |
| `extracted_chars` | `Integer` nullable | przed obcięciem (do UI: „obcięto”) |
| `created_at` | `DateTime(tz)` | |

Indeks na `(owner_user_id, created_at)` i `(run_id)`.

### Bezpieczeństwo (wymóg — nie pomijać)

1. **MIME z zawartości, nie z nagłówka.** `python-magic` na pierwszych bajtach.
   `Content-Type` i rozszerzenie od klienta są *tylko* wskazówką — odrzucamy przy
   niezgodności z sniffem.
2. **Allow-list**, nie deny-list:
   - obrazy: `image/jpeg`, `image/png`, `image/webp`, `image/gif`
   - tekst: `text/plain`, `text/markdown`, `text/csv`, `application/json`, `application/yaml`
   - dokumenty: `application/pdf`
   - **`image/svg+xml` — odrzucone** (XSS / XXE; SVG to dokument, nie bitmapa).
3. **Limity** (nowa sekcja `AttachmentSettings` w `core/config.py`):
   - `ATTACHMENT_MAX_FILE_BYTES` (domyślnie 10 MB)
   - `ATTACHMENT_MAX_PER_MESSAGE` (domyślnie 5)
   - `ATTACHMENT_MAX_TOTAL_BYTES` (na wiadomość, domyślnie 25 MB)
   - `ATTACHMENT_MAX_TEXT_CHARS` (domyślnie 100 000 — potem obcięcie z adnotacją)
   - `ATTACHMENT_PDF_MAX_PAGES` (domyślnie 50)
   - Limit egzekwować **strumieniowo** przy czytaniu `UploadFile`, nie po `await file.read()`
     (inaczej 2 GB pliku ląduje w RAM zanim sprawdzimy rozmiar).
4. **Decompression bomb** — `PIL.Image.MAX_IMAGE_PIXELS` (świadomy limit, nie `None`),
   `Image.verify()` przed właściwym otwarciem; łapać `Image.DecompressionBombError`.
5. **Nazwa pliku** — nigdy nie używać `original_filename` do budowy ścieżki.
   Ścieżka = `attachments/{tenant_id}/{attachment_id}{ext}`, `ext` z **naszej** mapy MIME.
   Chroni przed path traversal (`../../etc/passwd`) i nullbyte.
6. **EXIF** — re-encode przez `ImageProcessor` usuwa metadane (geolokalizacja!).
   GIF: nie przepuszczać animacji przez resize bezmyślnie — albo pierwsza klatka, albo skip.
7. **Serwowanie** — endpoint `GET /agent/attachments/{id}` i `/thumbnail` sprawdza
   `owner_user_id` **oraz** `tenant_id` z `CurrentTenantContext`. Odpowiedź z
   `Content-Disposition: inline; filename="..."` (nazwa escapowana) i **naszym** `Content-Type`
   z allow-listy — nigdy `text/html` (stored XSS przez podgląd pliku).
8. **PDF** — tylko ekstrakcja tekstu; żadnego renderowania, wykonywania JS, follow
   external refs. Cap stron. Zaszyfrowane/uszkodzone PDF → czytelny błąd.
9. **Rate limit** na endpoint uploadu (jest `RateLimitSettings`).

### Obrazy — skalowanie

`ImageProcessor` już to robi; potrzebne dwa przebiegi:

- **do modelu**: `max_width/height = 1536`, `jpeg_quality=85` — powyżej tego modele i tak
  downsamplują, a koszt tokenów rośnie liniowo z liczbą kafelków.
- **miniatura**: `max_width/height = 320`, `webp`.

Oryginał: **nie** przechowywać domyślnie (RODO + koszt) — zapisujemy wersję przetworzoną.
Jeśli kiedyś potrzebny oryginał, to osobna decyzja.

### Przekazanie do modelu (`agent_loop.py`)

`user_message: str` → lista content parts:

```python
content = [{"type": "text", "text": user_message}]
for att in attachments:
    if att.kind == "image":
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{att.mime_type};base64,{b64}"},
        })
    else:
        content.append({
            "type": "text",
            "text": f"<attachment name=\"{att.original_filename}\">\n{att.extracted_text}\n</attachment>",
        })
```

- Data URL (nie publiczny URL) — storage jest prywatny, a presigned URL wyciekałby do providera.
- Gdy brak załączników: zostawić `content` jako **string** (zgodność wstecz, mniej niespodzianek
  u providerów, które nie lubią jednoelementowej listy).
- Tekst wstrzykiwać w tagach, żeby model odróżnił treść pliku od promptu (prompt injection
  z pliku pozostaje realnym ryzykiem — udokumentować, że treść załącznika to **dane, nie polecenia**;
  wzmocnić system prompt).

### Gating po modelu

Dodać `"supports_vision": bool` do wpisów w `ai/utils/models_config.py`
(GPT-4o, GPT-4o-mini, Claude, Gemini → `True`; modele tekstowe → `False`).

- Backend: obraz + model bez vision → `400` z jasnym komunikatem.
- Frontend: przycisk załącznika obrazu wyszarzony + tooltip, gdy wybrany model nie ma vision.
- Załączniki tekstowe/PDF działają na **każdym** modelu (to zwykły tekst).

## Frontend

### Komponenty

| Plik | Rola |
|------|------|
| `components/ChatAttachmentPicker.vue` | przycisk spinacza + `<input type="file" multiple hidden>` |
| `components/ChatAttachmentChip.vue` | miniatura/ikona + nazwa + rozmiar + `X` (usuń) |
| `components/ChatAttachmentPreview.vue` | lightbox — duży podgląd obrazu (Dialog) |
| `composables/useChatAttachments.ts` | stan, upload, progres, błędy, limity |

- `ChatComposer.vue` — pod `Textarea` rząd chipów; `ChatAttachmentPicker` obok `Send`.
- Drag & drop na obszar composera + **paste ze schowka** (`paste` → `event.clipboardData.files`)
  — to jest realnie najczęstsza ścieżka dla zrzutów ekranu.
- Kliknięcie miniatury (w composerze i w wątku) → `ChatAttachmentPreview` (Dialog + `Esc`).
- Walidacja po stronie klienta = **UX, nie bezpieczeństwo** (rozmiar, liczba, typ) — backend
  waliduje ponownie i jest źródłem prawdy.
- i18n: `workspace.attachments.*` (`pl`, `en`).

### Wątek

`WorkspaceChatPage.vue` — nad treścią bąbelka użytkownika siatka miniatur;
pliki nie-obrazy jako chip z ikoną + nazwą. Historia sesji musi je odtwarzać
(`GET /agent/sessions/{id}` zwraca załączniki per run).

## Etapy

| Etap | Zakres | Efekt |
|------|--------|-------|
| **1** | Migracja 062, `AttachmentSettings`, `attachments` service (sniff, limity, storage), `POST/GET/DELETE /agent/attachments`, testy bezpieczeństwa | Upload obrazu działa przez API | ✅ |
| **2** | `supports_vision`, content parts w `agent_loop`, `attachmentIds` w `AgentChatRequest`, dowiązanie do run-a | Model „widzi” obraz | ✅ |
| **3** | Composer: picker, chipy, miniatury, lightbox, paste/DnD, i18n | Pełny UX obrazów | ✅ |
| **4** | Ekstrakcja tekstu: `txt/md/json/csv/yaml` (decode + limit znaków) | Pliki tekstowe do modelu | ✅ |
| **5** | PDF: `pypdf` (dodać do `requirements.txt`), cap stron, błędy szyfrowanych | PDF do modelu | ✅ |
| **6** | Sprzątanie osieroconych załączników (CLI/cron), `StorageUsageCard` uwzględnia załączniki | Higiena | |

Etapy 1–3 to minimum użyteczne (obrazy). 4–5 dokładają formaty.

## Testy

- **Bezpieczeństwo:** plik `.png` z zawartością PDF (sniff wygrywa); SVG odrzucony;
  `../../etc/passwd` jako `filename`; decompression bomb (mały plik, ogromne wymiary);
  przekroczony rozmiar strumieniowo; dostęp do cudzego załącznika → `404`/`403`;
  załącznik z innego tenanta → `404`.
- **Skalowanie:** obraz 6000×4000 → ≤1536 px dłuższy bok, EXIF usunięty.
- **Model:** obraz + model bez vision → `400`; brak załączników → `content` pozostaje stringiem.
- **Ekstrakcja:** JSON/CSV/utf-8 z BOM; plik binarny udający `text/plain`; obcięcie po
  `ATTACHMENT_MAX_TEXT_CHARS` z adnotacją.
- Frontend: `pnpm test:run` — `useChatAttachments` (limity, usuwanie, błędy).

## Otwarte punkty

1. Czy przechowywać oryginał obrazu obok wersji przetworzonej? (koszt + RODO) — **domyślnie nie**.
2. Czy załączniki liczyć do `StorageUsageCard` / limitów planu (`feature_limits`)? Prawdopodobnie tak.
3. Audio/wideo — poza zakresem tego planu.
4. Prompt injection z treści plików — czy dokładamy guard w `agent/guards/`?
5. Czy `extracted_text` trzymać w DB (prosto, ale puchnie), czy w storage obok pliku?
