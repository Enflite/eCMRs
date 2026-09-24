# Enflite Brand Style Guide — PPTX & DOCX

A shared reference for building PowerPoint decks and Word documents that look like they
belong to Enflite, not a generic template. Covers color, type, and component conventions;
apply it whenever a new slide/deck/doc is built or an existing one is reformatted.

**Direction: modern, minimal, premium** — think Tesla / Bodor, not a stock corporate
template. That means: fewer boxed/bordered "cards," no drop shadows, a tighter Black/White/
Red palette (grays are for body text only, not decoration), generous whitespace, and a mixed
type hierarchy — light/thin weight for most large display text, bold reserved for the one
word or number that should land hardest. Flat rules (thin 1px lines) replace bordered card
containers as the way to separate sections. This is a deliberate shift from a busier, more
"boxed-card-on-every-slide" first pass — if you're updating something built before this
direction landed, strip the card borders/shadows out rather than just swapping colors.

**Provenance**: `Enflite Red` is sampled directly from the real logo file the user provided
(`docs/branding/assets/enflite-logo-original.jpg`) — exact, not an estimate. Everything else
below was sampled from pixels on a screenshot of [enflite.com](https://enflite.com/), since
this environment's network egress is blocked from reaching enflite.com directly (the live
site/CSS couldn't be fetched programmatically). Those remaining colors are close
approximations, not exact brand-book values — replace them if an actual Enflite brand book or
exact hex palette becomes available.

## Colors

| Role | Hex | Usage |
|---|---|---|
| **Enflite Red** (primary) | `#CF0C2C` | Buttons, links, accent headings, section labels, icon strokes, key stats — exact, from the real logo file |
| **Charcoal** (dark) | `#252525` | Dark section backgrounds, footer, dark hero overlays |
| **Ink** (body/heading text on light bg) | `#1A1A1A` | Primary text color on white/light backgrounds |
| **Body Gray** | `#4A4A4A` | Secondary/body copy on light backgrounds (estimated — verify against real brand assets) |
| **Divider Gray** | `#E5E5E5` | Hairline borders, table dividers, card outlines |
| **Light Section Gray** | `#F7F7F7` | Alternate light section background (vs. pure white) |
| **Red Tint** (light) | `#FAE7EA` | Icon/badge backgrounds, subtle highlight fills on light backgrounds |
| **White** | `#FFFFFF` | Text on dark/red backgrounds, light section background |

Do not substitute a brighter/pinker red (e.g. `#E31E24`, `#FF0000`) or a blue/green accent —
the real brand red is a deep crimson, not a bright red.

**Palette discipline**: treat this as Black, White, and Red, in that order of usage — Ink/
Charcoal and White carry almost everything (backgrounds, text, imagery overlays), Red is the
one accent, used sparingly enough that it still reads as deliberate on a slide/page, not as
"the color everything happens to be." Body Gray, Divider Gray, Light Section Gray, and Red
Tint are utility colors for readability and separation, not decoration — don't reach for them
to fill space, add a card background, or add visual "interest." A slide with more than one or
two red accents is probably overusing it.

## Typography

No serif anywhere — that part is unchanged. What's new is weight contrast: don't set every
heading in the same bold weight. Use a light/regular weight for most large display text, and
save bold for the single word, number, or phrase that should carry the emphasis. That
contrast (thin type next to one bold hit) is most of what makes Tesla/Bodor-style type feel
premium instead of corporate-template bold-everywhere.

- **Large display text** (slide titles, hero headlines): light or regular weight sans-serif,
  large size, generous letter-spacing at big sizes — `Segoe UI Light`/`Segoe UI` regular in
  Office documents, or `Montserrat`/`Poppins` Light if importing a web font is an option.
  Bold only the one word/number inside it that matters.
- **Section labels / eyebrows**: small, bold, Enflite Red, uppercase, wide letter-spacing —
  sits above a light-weight heading, not instead of one.
- **Body**: `Calibri` or `Segoe UI`, regular weight, in Body Gray or Ink.
- **Stat numbers**: very large, light/thin weight numerals in Ink or White, with a small bold
  Red label underneath (e.g. a huge thin "40%" over a small bold red "IN-HOUSE ENGINEERING").
- **Buttons/labels**: uppercase, tracked slightly wider than body text, but not necessarily
  bold — a thin-weight uppercase label reads more premium than a heavy bold one.

## Components

- **No cards.** Don't box content in a bordered/shadowed rectangle to separate it from the
  rest of the slide/page. Separate sections with whitespace and, where a hard edge is truly
  needed, one thin (0.5–0.75pt) Divider Gray rule — never a filled card with a border and a
  drop shadow.
- **Buttons/CTAs**: minimal — a thin 1px border (Ink or White, matching the surface) with
  no fill, or solid Ink/White with no fill color at all. Reserve a solid Red button for the
  single most important action on a page/deck; if every button is red, none of them are.
- **Section labels**: short, bold, Enflite Red, uppercase, sitting above a light-weight Ink/
  White heading (e.g. "THE CORE CATALOG" in red above a light-weight "Products By Enflite").
- **Icon badges**: solid Enflite Red rounded-square, white icon glyph centered on top —
  confirmed in the actual plan deck (`eCMRs_plan.pptx`), not the outlined/no-badge look this
  section used to recommend (that direction was tried and superseded live). Corner rounding
  is modest, not a pill/circle — PowerPoint's roundRect `adj` around `8000` (out of 50000),
  i.e. roughly 16% of the shorter side. Icon and badge are the same square aspect ratio, icon
  inset with a comfortable margin inside the badge (not edge-to-edge).
- **Dark sections**: Charcoal or full-bleed photography with a dark overlay, white light-
  weight heading text, Enflite Red reserved for the one number/word that should pop.
- **Dividers**: thin, Divider Gray, never colored, never doubling as a card border.

## Layout & Composition

- **Whitespace is the layout tool.** Wider margins than feel natural at first, more room
  between sections than a dense corporate deck would use. If a slide/page feels empty, that's
  usually correct — resist filling it with another card, icon, or rule.
- **No drop shadows, no gradients-as-decoration, no rounded-rectangle-everything.** Flat
  surfaces, sharp or barely-rounded corners, hard edges between color blocks.
- **Full-bleed photography** for hero/section-break moments, with a dark (Charcoal, ~40–60%
  opacity) overlay under white text — not a photo inset into a bordered box.
- **Alignment over decoration**: a strong left-aligned grid (or a single centered axis) does
  more visual work than a colored accent shape. Use accent shapes (a thin rule, a single bold
  numeral) sparingly, not on every slide.

## Logo

The real logo (the "Enflite" wordmark, bold italic red on white) is checked in:

- `docs/branding/assets/enflite-logo-original.jpg` — the file as provided, flat white
  background, no transparency.
- `docs/branding/assets/enflite-logo.png` — the same mark with the white background keyed
  out to alpha, generated from the original (near-white pixels → transparent, edges kept
  partially transparent for a smooth cutout instead of jagged edges). Use this version
  whenever the logo sits on anything other than a plain white background (e.g. the Charcoal
  title slide) — the original JPG only looks right on white.

Use the real file everywhere a logo is needed; there's no reason to redraw a placeholder
wordmark now that the real asset exists.

## Applying this to a PPTX

- Slide background: white for most content slides; Charcoal (or full-bleed photo + dark
  overlay) for title/divider slides, with light-weight white text and one Red accent.
- No bordered/shadowed content boxes. Group related content with whitespace and, at most,
  one thin Divider Gray rule between sections — don't wrap a table or a block of bullets in a
  filled, outlined card.
- Titles/headlines: light or regular weight, large; bold only the one word or number that
  needs the emphasis. Section labels (eyebrows): small, bold, Red, uppercase.
- Section header banners (a full-width colored band, e.g. "QUALITY:"): keep these only where
  they're already load-bearing navigation within a long document-style deck — Charcoal or
  Ink background, white text, not filled Red (a whole banner in Red is the "everything is the
  accent color" problem the palette-discipline note above warns about).
- Icon treatment: line-weight icons in Ink or Red, no filled tint badge behind them, unless
  it's a numbered step indicator (then a thin outlined circle, not a filled one).
- Stats/big numbers: large light-weight numerals, small bold Red label beneath.

## Applying this to a DOCX

- Heading 1/2/3 styles: light/regular weight sans-serif (Segoe UI), Ink for body headings;
  Enflite Red only for a Heading 1 eyebrow/label line, not the whole heading.
- Body style: Calibri/Segoe UI, Body Gray or Ink, single-spaced.
- Table header rows: Ink or Charcoal fill, white text, regular (not bold) weight; body rows
  plain white with thin Divider Gray rules between rows — no banded fill colors.
- Pull quotes / callouts: no filled Red Tint box — a thin Red left-border rule, white/Light
  Section Gray background, Ink text is enough.
