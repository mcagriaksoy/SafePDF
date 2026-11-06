# SafePDF Agent Guide

## Project Context

SafePDF is an open-source, privacy-first desktop PDF toolkit. The website is a static site published from `docs/`, while the application code lives under `SafePDF/`.

The central product promise is:

> Process PDF files locally. Files never leave the user's device.

Keep this promise visible in product copy and UI without making every section sound like a marketing slogan.

## Repository Map

- `docs/`: static website, SEO pages, localized pages, shared CSS and JavaScript
- `docs/index.html`: English homepage
- `docs/de/index.html`: German homepage
- `docs/tr/index.html`: Turkish homepage
- `docs/style.css`: shared website stylesheet
- `docs/nav.js`: shared navigation and language switching
- `docs/head.js`: shared metadata, structured data and analytics setup
- `docs/*-to-*.html`: converter landing pages
- `docs/downloads.html`: application downloads
- `SafePDF/`: Python desktop application
- `SafePDF/ops/`: PDF operation implementations
- `SafePDF/ctrl/`: application controllers and language management
- `SafePDF/test/`: application tests

## Website Design Direction

The website should feel like a serious desktop utility, not a generic AI-generated SaaS landing page.

Use the visual direction called **privacy workstation**:

- Prefer product screenshots, operation lists and visible workflows over decorative cards.
- Use a restrained palette: graphite, off-white/light gray, and SafePDF red as an accent.
- Use dark product-led hero areas when they help the application screenshot stand out.
- Avoid excessive gradients, pills, floating blobs, oversized claims and repeated card grids.
- Prefer quiet directory rows, ruled sections, compact metadata and clear text links for converter lists.
- Keep layouts information-dense but calm, similar in spirit to established desktop software websites such as Scooter Software / Beyond Compare.
- Preserve responsive behavior. Converter lists should become a single readable column on small screens.
- Use real screenshots and existing assets. Do not invent fake testimonials, download counts or product capabilities.

## Current Website Decisions

- The homepage hero uses a dark product-led treatment and gives the application screenshot visual priority.
- The homepage converter section uses two-column directory rows rather than raised marketing cards.
- The live download count in the dark hero is intentionally white for contrast.
- `docs/style.css` has accumulated older and newer rule blocks. Add narrowly scoped overrides or consolidate carefully; do not rewrite the entire stylesheet without a visual reason.
- `docs/style.css` uses shared CSS variables. Keep `--muted` defined because older sections still reference it.

## Localization Rules

- English lives at `/`.
- German lives at `/de/`.
- Turkish lives at `/tr/`.
- Keep static localized pages and `hreflang` tags. They are important for search engines.
- Do not replace localized HTML with client-side machine translation.
- `docs/nav.js` detects a German browser language on a first visit to the English homepage and sends the visitor to `/de/`.
- Explicit language selections are stored in `localStorage` under `safepdf-language-choice` and must not be overridden by automatic detection.
- Do not add IP-based redirects in static frontend code. They are fragile, privacy-sensitive and can hurt SEO.
- When adding a localized page, update its `lang` attribute, title, description, canonical URL, Open Graph locale, JSON-LD language, navigation labels and `docs/sitemap.xml`.

## SEO and Growth Rules

- Each converter page should target a clear task intent, for example offline PDF-to-Word or PDF compression.
- Use natural English or German search language, not keyword stuffing.
- Keep title, description, H1, canonical and `hreflang` consistent.
- Add structured data only when it describes visible, truthful content.
- Keep download claims factual and generated from a public source when possible.
- Preserve accessibility: meaningful image alt text, keyboard-accessible links, visible focus states and adequate contrast.

## Editing Workflow

Before editing:

1. Read the owning HTML/CSS/JS surface and one nearby related implementation.
2. State a local hypothesis about the behavior or visual problem.
3. Make the smallest change that tests that hypothesis.
4. Check for unrelated user changes and do not revert them.

After editing:

1. Validate the touched JavaScript with `node --check docs/nav.js` when applicable.
2. Use VS Code diagnostics or a focused browser check for CSS/HTML changes.
3. For Python changes, run the narrowest relevant test first, then broaden only if needed.
4. For visual changes, inspect desktop and mobile layouts before declaring completion.
5. Do not commit, reset, checkout, or create branches unless explicitly requested.

## Validation Commands

```powershell
node --check docs/nav.js
```

For Python changes, use the repository's configured environment and run the focused tests under `SafePDF/test/` before the full suite.

## Safe Change Boundaries

- Do not modify generated build output under `SafePDF/build/` unless the task explicitly concerns packaging.
- Do not commit secrets, credentials, API keys or personal analytics data.
- Do not remove existing localized pages or SEO metadata during a visual redesign.
- Do not claim that a file is processed offline unless the application path actually guarantees local processing.
- Keep unrelated refactors out of a focused website or PDF operation change.

## Suggested Next Website Work

1. Inspect the homepage in a real browser at desktop and mobile widths.
2. Consolidate duplicated homepage CSS blocks only after confirming the visual result.
3. Replace remaining generic homepage card groups with product/workflow sections where appropriate.
4. Improve German converter copy for native search intent rather than literal translation.
5. Add truthful download checksum/version information to the downloads page.
6. Verify all localized links and sitemap entries after any page addition.
