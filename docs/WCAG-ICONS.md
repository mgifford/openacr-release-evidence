# WCAG 2.2 pictograms

**Status: implemented on 2026-11-13.**

The release reports and the ACR narrative use the supplied WCAG 2.2 pictogram
sprite beside success criterion numbers. The pictograms are decorative: the
adjacent number and title remain the accessible name.

## Supplied assets

| File | Purpose |
| --- | --- |
| `config/wcag22-icons.json` | 86 active success criteria and 13 guideline mappings, with title, level, principle, URL and icon description |
| `src/acr_evidence/static/wcag22_icons.svg` | 99 reusable `<symbol>` drawings, keyed by criterion (for example `#sc-1-4-3`) |

The mapping records:

- version `1.0`;
- source version `2024-12-12`;
- 86 success criteria and 13 guidelines;
- 4.1.1 Parsing explicitly excluded because it is obsolete in WCAG 2.2.

Every success criterion in the mapping has a corresponding symbol. The build
validates that the sprite contains no scripts, event-handler attributes,
external references, DOCTYPE/entity declarations, or duplicate symbol ids.

## How the icons are used

- **Criterion index** on `criteria.html`: a small icon before the criterion
  number.
- **Criterion sections**: the same icon before the heading.
- **ACR narrative HTML** (`acr.html`): a decorative icon in the first column of
  each criterion table.
- **ACR Markdown** (`acr.md`): no icons; the text remains portable.

The icon is always beside visible criterion text:

```html
<a href="#sc-1-4-3">
  <svg class="wcag-icon" viewBox="0 0 100 100" aria-hidden="true" focusable="false">
    <use href="./wcag22_icons.svg#sc-1-4-3"></use>
  </svg>
  1.4.3
</a>
```

`aria-hidden="true"` and `focusable="false"` keep the decorative SVG out of the
accessibility tree and tab order. There is no `<title>` on the rendered
instance, so it does not duplicate the criterion name. The shared symbol may
contain its own title/description for direct use; the rendered icon does not
expose it.

## Delivery and fallback

Each target directory contains a copy of `wcag22_icons.svg`, and the Pages
allowlist publishes it. Pages reference it with a same-directory relative URL.
If a browser does not render the external `<use>` reference, the criterion
number and title remain visible and usable. Icons are not required to
understand a criterion.

The build copies the sprite from `src/acr_evidence/static/`. Do not hand-edit
the copies in `reports/`.

## Security

The sprite is an author-controlled asset, but SVG is active XML. `icons.py`
validates it before copying:

- no `<script>`;
- no `on*` event-handler attributes;
- no external `href`/`src` (same-document fragments only);
- no DOCTYPE or entity declarations;
- unique symbol ids.

`tests/test_icons.py` covers the mapping, the icon markup and the sprite
validation.

## Validation

On 2026-11-13:

- the icon sprite rendered over a same-origin HTTP server (the GitHub Pages
  condition) in Chrome 157;
- each rendered icon measured about 17 × 17 CSS px beside the criterion number;
- the outer SVG remained `aria-hidden="true"` and did not add duplicate names;
- axe-core reported 0 violations on all six beta2 pages at 1280 px and 320 px;
- the page still had no level horizontal scrolling at 320 px;
- `acr.md` contained no SVG markup.

The external `<use>` reference means a browser that blocks cross-document
sprite references falls back to the visible criterion text. That fallback has
not been tested in Safari.

## Limits

- Icons are not conformance results, severity indicators or evidence.
- The mapping is WCAG 2.2 only. Older criteria such as 4.1.1 have no icon.
- A tag such as `wcag327` produces a criterion number the mapping does not
  contain; the report keeps the text and omits the icon rather than inventing
  a symbol.
- The icons have not been manually reviewed with a screen reader. Because they
  are hidden from AT and adjacent text is always present, the risk is low, but
  a real AT session remains part of Phase 6 validation.
- The sprite is served as a separate file. A browser that blocks external
  `<use>` references gets the text-only version.

## Updated files

- `config/wcag22-icons.json`
- `src/acr_evidence/static/wcag22_icons.svg`
- `src/acr_evidence/icons.py`
- `src/acr_evidence/report.py`
- `src/acr_evidence/acr_narrative.py`
- `src/acr_evidence/static/report.css`
- `.github/workflows/pages.yml`
- `tests/test_icons.py`
- `tests/test_report.py`
- `tests/test_pages.py`
