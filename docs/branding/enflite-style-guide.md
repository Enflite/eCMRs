# Enflite Brand Style Guide — PPTX & DOCX

A shared reference for building PowerPoint decks and Word documents that look like they
belong to Enflite, not a generic template. Covers color, type, and component conventions;
apply it whenever a new slide/deck/doc is built or an existing one is reformatted.

**Provenance**: colors below were sampled directly from pixels on a screenshot of
[enflite.com](https://enflite.com/) (this environment's network egress is blocked from
reaching enflite.com directly, so the live site/CSS/logo file couldn't be fetched
programmatically). They're close approximations, not exact brand-book values. If an actual
Enflite brand book, logo file (SVG/AI/EPS), or exact hex palette becomes available, replace
the values below and remove this caveat.

## Colors

| Role | Hex | Usage |
|---|---|---|
| **Enflite Red** (primary) | `#B41832` | Buttons, links, accent headings, section labels, icon strokes, key stats |
| **Charcoal** (dark) | `#252525` | Dark section backgrounds, footer, dark hero overlays |
| **Ink** (body/heading text on light bg) | `#1A1A1A` | Primary text color on white/light backgrounds |
| **Body Gray** | `#4A4A4A` | Secondary/body copy on light backgrounds (estimated — verify against real brand assets) |
| **Divider Gray** | `#E5E5E5` | Hairline borders, table dividers, card outlines |
| **Light Section Gray** | `#F7F7F7` | Alternate light section background (vs. pure white) |
| **Red Tint** (light) | `#F8E8EA` | Icon/badge backgrounds, subtle highlight fills on light backgrounds |
| **White** | `#FFFFFF` | Text on dark/red backgrounds, light section background |

Do not substitute a brighter/pinker red (e.g. `#E31E24`, `#FF0000`) or a blue/green accent —
the sampled brand red is a deep crimson, not a bright red.

## Typography

Enflite's site headings are a clean, bold, geometric sans-serif with no serif characteristics
anywhere on the page — no Cambria/Georgia/Times-style display font.

- **Headings**: a bold sans-serif — `Segoe UI Semibold`/`Bold` in Office documents (ships with
  Office, safe cross-platform), or `Montserrat`/`Poppins` Bold if importing a web font is an
  option. Never a serif font for headings.
- **Body**: `Calibri` or `Segoe UI`, regular weight, in Body Gray or Ink.
- **Buttons/labels**: uppercase, bold, tracked slightly wider than body text — matches the
  site's pill-shaped uppercase red CTAs ("VIEW INTERIOR SOLUTIONS", "LEARN MORE").

## Components

- **Buttons/CTAs**: fully-rounded (pill) shape, solid Enflite Red fill, white uppercase bold
  text, no border.
- **Section labels**: short, bold, Enflite Red, all-caps or title-case, sitting above a plain
  black/Ink heading (e.g. "THE CORE CATALOG" in red above "Products By Enflite" in black).
- **Icon badges**: circular or rounded-square, Red Tint fill, Enflite Red icon/stroke —
  replaces any green/blue icon treatment.
- **Dark sections**: Charcoal background, white heading text, Enflite Red for stat numbers/
  emphasis (e.g. "40% In-House Engineering Workforce").
- **Dividers**: thin, Divider Gray, never colored.

## Logo

No logo file could be pulled into this repo yet (network egress to enflite.com is blocked in
this environment). Until the real asset is supplied:

- **Placeholder wordmark**: "Enflite" set in bold, slightly italic sans-serif, Enflite Red.
  This is a *stand-in*, not a recreation of Enflite's real mark — don't treat it as final.
- **To finish this properly**: get the real logo file (SVG/PNG/EPS) into the repo — e.g.
  `docs/branding/assets/enflite-logo.svg` — and swap the placeholder wordmark for it
  everywhere it appears (title slides, footers, letterhead).

## Applying this to a PPTX

- Slide background: white or Light Section Gray for content slides; Charcoal for a title/
  divider slide, with white text and a Red accent line or shape.
- Replace any green/blue/teal accent color 1:1 with Enflite Red; replace its light-tint
  companion (icon backgrounds, subtle fills) with Red Tint.
- Section header banners: Enflite Red background, white bold text (or Charcoal background,
  Red text — pick one and use it consistently within a deck).
- Body/heading fonts per Typography above.

## Applying this to a DOCX

- Heading 1/2/3 styles: bold sans-serif (Segoe UI Semibold), Ink or Enflite Red for Heading 1.
- Body style: Calibri/Segoe UI, Body Gray or Ink, single-spaced.
- Table header rows: Enflite Red or Charcoal fill, white bold text; body rows white/Light
  Section Gray banding, Divider Gray borders.
- Pull quotes / callouts: Red Tint background, Enflite Red left border accent, Ink text.
