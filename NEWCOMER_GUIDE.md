# SafePDF Newcomer Guide

## What this project is
SafePDF is a desktop-first, privacy-focused PDF toolkit built in Python with Tkinter. The key design promise is that all PDF processing happens locally (offline), without sending documents to external services.

## High-level structure

### 1) Entry points and app bootstrapping
- `run_safe_pdf.py` is a convenience launcher for running from repo root.
- `SafePDF/safe_pdf_app.py` wires together the Tk root window, controller, and UI.

### 2) MVC-ish runtime architecture
- `SafePDF/ctrl/` contains state + workflow orchestration (`SafePDFController`) and localization loading (`LanguageManager`).
- `SafePDF/ui/` contains the Tkinter UI and delegated UI modules (tabs, settings, help, update screens).
- `SafePDF/ops/` contains the operation backend and specialized operation classes (compress/split/merge/rotate/convert).

A useful mental model: **UI triggers intent -> Controller validates and chooses operation -> Ops executes and reports progress/results back to UI**.

### 3) Operation layer
`SafePDF/ops/pdf_operations.py` is the facade that composes operation-specific helpers (`PDFCompressor`, `PDFSplitter`, `PDFMerger`, `PDFRotator`, converters), exposes a unified API, and provides shared concerns like:
- cancellation signaling,
- PDF validation,
- atomic file writes via temp files + `os.replace`.

### 4) Localization and content
`SafePDF/text/<lang>/` stores language-specific UI strings and text content files. `LanguageManager` resolves these at runtime and supports fallback behavior.

### 5) Logging and diagnostics
`SafePDF/logger/logging_config.py` configures a rotating file log (default under `~/.safepdf/safepdf.log`), enabling troubleshooting without cluttering console output.

### 6) Web/docs and packaging-adjacent files
- `docs/` contains static website pages and assets.
- `setup.py`, `requirements.txt`, `MANIFEST.in`, and `SafePDF/pyproject.toml` support packaging/distribution.
- `SafePDF/installer/` and `create_executable.bat` are focused on Windows distribution workflows.

## Important things to know before editing

1. **State lives primarily in `SafePDFController`**
   - selected files, selected operation, operation settings, output paths, pro activation state.

2. **Controller/UI contract is callback-driven**
   - Controller exposes callbacks for UI updates and completion events.
   - Long-running operations are executed in a worker thread to keep the UI responsive.

3. **Operations are mostly delegated, not monolithic**
   - Keep new operation logic in the `ops/` modules; avoid bloating controller or UI.

4. **Localization is first-class**
   - New user-facing text should go through localization files and `LanguageManager` lookups.

5. **Desktop + Windows considerations are deliberate**
   - There is platform-aware behavior (icons, file opening, installer, taskbar identity), so test on target OS where possible.

## Good “learn next” path for a new contributor

1. Read `README.md` for product goals and feature map.
2. Trace startup path:
   - `run_safe_pdf.py` -> `SafePDF/safe_pdf_app.py` -> `SafePDF/ui/safe_pdf_ui.py`.
3. Read `SafePDF/ctrl/safe_pdf_controller.py` end-to-end to understand state and operation dispatch.
4. Dive into `SafePDF/ops/pdf_operations.py`, then one concrete operation module (e.g., split or merge).
5. Review localization assets in `SafePDF/text/en/ui.json` and one additional language folder.
6. Check logging setup (`SafePDF/logger/logging_config.py`) and run locally to inspect log output.
7. Explore tests/scripts under `SafePDF/test/` to understand current validation coverage and gaps.

## Contribution tips
- Keep UI flow changes aligned with tab gating rules and callback flow.
- Keep file writes safe/atomic where practical.
- Prefer adding operation-specific tests when touching `ops/` behavior.
- If adding new strings, update all supported languages or define a clean fallback.
