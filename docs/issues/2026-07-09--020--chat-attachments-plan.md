# Issue 020 — Plan załączników w czacie (attachments picker)

**Data:** 2026-07-09  
**Status:** `planned`  
**Commit (dokumentacja):** `9ff6641`  
**Plan:** [2026-07-09--002--chat-attachments.md](../plans/2026-07-09--002--chat-attachments.md)  
**Z tego samego promptu:** [#007](./2026-07-09--007--audit-sheet-no-padding.md), [#008](./2026-07-09--008--memory-page-no-canvas-background.md)

## Prompt (Claude Code)

> Another, bigger: Add attachments picker. You need to plan this one in docs  
> Images should show thumbnail preview, with big preview on click.  
> Should implement safety, maybe scale down mechanism for xtra large imaged.  
> Text extraction from simple formats … Maybe text extractor for PDF.  
> **First create issues/plans, commit. Next: implement.**

*(sesja `615d85ac`)*

## Decyzja

Załączniki to osobna, większa funkcja — **najpierw plan**, potem implementacja w osobnych commitach. Reuse: `core/storage`, `ImageProcessor`, wzorzec z `catalogue_item_image_upload_service`.

Implementacja **nie** wchodzi w zakres tego issue — tylko ślad decyzji i plan.

## Implementacja (na dziś)

- `9ff6641` — `docs: issues 007/008 (design) + plan 002 (chat attachments)`
- Plan 002 opisuje etapy: obrazy → tekst → PDF

## Następne kroki

- Nowe issue po rozpoczęciu implementacji (composer picker, backend content parts)
