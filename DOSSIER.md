# DOSSIER — news-image-20261118 v4

## What this is

Entry for the make.fun bounty **news-image-20261118** — "Sum up
18 November's world news in one image". A program (`main.py`)
that writes one 1024×1024 PNG to `/output/entry.png`. The poster
is a premium illustrated newspaper front page summing up
Wednesday 18 November 2026 in **37 stories across 6 continents**:
3 illustrated hero stories, 10 illustrated mid stories, 24
briefs, and a numbered world map.

## v4 — generated raster illustrations, larger art areas

Ivan's feedback on v3.1 (19 Nov ~06:01 WIB): the poster was sharp
now, but its illustrations still looked worse than rank 1 — the
PIL code-drawn scenes (rectangles, polygons, ellipses) were
schematic and empty next to rank 1's rich raster art (its footer
credits "Illustrations: ChatGPT"). v4 replaces the code-drawn art
with generated raster illustrations, one per card:

- **Contact sheets** (4 `media.generate_image` calls, in
  `v4-illustrations/`): heroes triptych (Gulf / Kerch / APEC),
  mids-a 2x2 (COP31 / Gaza / Russia drones / Bangladesh),
  mids-b 2x2 (GTA VI / ECDC / Australia / Haiti), mids-c 2 panels
  (Ethiopia–Eritrea / Voyager 1). Style per sheet: detailed flat
  editorial newspaper illustration, rich layered scene, saturated
  colors, strong silhouettes, no text of any kind in the images
  (all text is added later by PIL — generated text would be
  garbled).
- **Crops** (`v4-crop.py`): each panel is cut to the card art
  aspect as a horizontal band (heroes 308x128, mids 176x84),
  with a small inset so the white sheet gaps do not leak in, and
  saved at 2x render size in `v4-illustrations/crops/`. Every
  crop was inspected on a contact sheet before use.
- **Per-card art** (12 generated, 1 fallback):
  1 Gulf — generated (burning tanker, drones, explosions);
  2 Kerch — generated (collapsing arch, smoke, boats);
  3 APEC — generated panel's **skyline-only window** (Shenzhen
  towers, no people). The full panel shows Xi shaking hands
  with Trump — but the Trump–Xi meeting is Thursday 19 Nov,
  not Wednesday (see facts.md), so using it would contradict
  the poster. The v3.1 PIL `scene_apec` remains in the code as
  a fallback and is no longer used;
  4 COP31 — generated (globe + smokestacks + negotiation table);
  5 Gaza — generated (negotiation table + tent camp);
  6 Russia drones — generated (night sky, drones, explosions);
  7 Bangladesh — generated (garment floor + protest);
  8 GTA VI — generated (game shop at midnight + queue);
  9 ECDC — generated (lab bench, microscope, vials, petri dishes);
  10 Australia — generated (courthouse + sealed document);
  11 Haiti — generated (helicopter + smoking mansion + palms);
  12 Ethiopia–Eritrea — generated (truck convoy, arid mountains);
  13 Voyager 1 — generated (probe + big dish in deep space).
  No panel was regenerated (4-call budget spent); no panel
  needed a PIL fallback except hero 3's window treatment above.
- **Layout rebalance**: mid cards grew from 184x152 to 184x172
  so the art is 176x84 — 49% of the card instead of 38% (the
  small art was part of why v3 looked weak). To make room, the
  masthead moved up (kicker y12, date y30, deck y114, rules
  y134/139), heroes start y142, mids at y406/y584, the map
  shrank to 536x156 (y784–940), and briefs were cut from 31 to
  24 (the 7 weakest dropped: S.F. data-centre ban, leukaemia
  jab — both single-source — IPL lists, Nigeria 0–0 Tanzania,
  S. Africa summons envoy, Fed minutes, Mariana quake). Total:
  **37 stories**. Headlines/sublines/numbers/facts are
  unchanged from v3 — only the pictures and the layout changed.
  Map dots were re-checked after the shrink: the Hungary brief
  dot was nudged (-10, -8) so it no longer touches dot 4
  (Antalya).
- New poster: 1,036,223 bytes, sha256
  `45d0ccb1fc9c05f6ff75187f98c00bfd2cd0a7fde80e7a7e96e447ff3a054246`
  (1024×1024 RGB, ≤1 MiB; v3.1 was 614,478 bytes, sha256
  `80278fcdda43120cd0f00713eb633e8a9917199e3c55ac441b0f21262fd6af5d`).
- QA (3 iterations, override §10): (1) full composition — all
  13 cards carry rich scenes, no overflow; hero 3's PIL scene
  looked flat next to the generated heroes, so it was replaced
  with the skyline window; (2) re-render — hero 3 now matches,
  mid grid inspected card by card (all scenes recognizable
  without reading the headline); (3) 300 px + quadrants — date
  and hero headlines readable at 300 px, map dots/legend/footer
  legible at 100%. **PASS.**
- Determinism: `main.py` run twice, byte-identical, same sha256
  as `entry-1024.png`.

## v3.1 — sharp RGB render, no palette quantize

Ivan's feedback on v3 (19 Nov ~05:49 WIB): the poster looked blurry
next to the rank 1 entry. Diagnosis: after the 2048→1024 LANCZOS
downsample, `build_image.py` converted the image to a 256-colour
adaptive palette (`convert("P", palette=Image.ADAPTIVE, colors=256)`).
That merged near-identical pastel tones, softened every thin line
and washed out pale fills — exactly the blur Ivan saw. The rank 1
poster is plain RGB. A straight RGB re-render is 614,478 bytes
(~610 KB), far under the 1 MiB cap, so quantizing buys nothing.

Changes (rendering only — no story, headline, number, fact or
layout changed):
- `out1024` stays RGB and is saved with `optimize=True`; the
  `convert("P", …)` line is deleted. Assert ≤1 MiB kept.
- Outlines thickened ~1.5–2× (in 1024 units) and fills given more
  contrast, because thin lines and low-contrast fills suffered
  most: card borders 1→2 px, double rule 1/2→2/3 px, footer rule
  2→3 px; `dashed`/`starburst` defaults 2→3; Gulf land darkened
  (228,210,175 → 214,190,148) with 2 px island/tanker outlines and
  3 px drone dashes; Kerch ripples and drone rotors 2→3 px; APEC
  towers got INK outlines and the table an INK outline; COP31
  globe/ground 1→2 px, smokestacks outlined; Gaza table/document/
  flag 1→2 px, legs 2→3 px, tents darkened; drone paths 1→2 px;
  Bangladesh sign 1→2 px, table legs 2→3 px; GTA door/clock
  1→2 px; ECDC vials/petri 1→2 px, bench legs 2→3 px; Australia
  columns/document 1→2 px, pediment darkened; Voyager trajectory
  1→2 px, dish 1→2 px, booms 2→3 px; Haiti mansion/columns 1→2 px,
  rotor/palm 2→3 px; Horn trucks outlined, flag poles 1→2 px; map
  leader lines 1→2 px, numbered-dot outlines 1→2 (render px),
  Voyager inset frame 1→2 px.
- New poster: 614,478 bytes, sha256
  `80278fcdda43120cd0f00713eb633e8a9917199e3c55ac441b0f21262fd6af5d`
  (v3 palette version: 197,284 bytes, sha256
  `a6a1116e426e585bc38049128b8af981e79046015134ff8b8c75048db60fafa2`,
  kept at `qa/v3-palette.png` for before/after comparison).
- QA: full image, hero crop, mid-grid crop and 300 px version
  inspected — edges crisp, no wash-out, text readable. Determinism:
  `main.py` run twice, byte-identical, same sha256 as
  `entry-1024.png`.

## v3 — what changed vs v2 (submitted 18 Nov ~21:40 WIB)

v2 looked like a financial dashboard: its ten mid cards were
giant-number tiles (big "$115.8B", "141", "72%", "3.6%") with a
navy masthead block and an all-caps white date. The visual
redesign override (from Ivan, with the rank 1 poster as
reference) required a rebuild as an illustrated newspaper:

- **Paper**: warm ivory #F5F0E4, near-black ink, muted brick red
  + antique gold accents. No navy masthead block, no all-caps
  white date. The date is now title-case
  "Wednesday 18 November 2026" in a large editorial serif, one
  line, with a thin double rule below it.
- **Every hero and mid card now has its own story-specific
  flat-vector illustration on top** (50–58% of the hero card,
  40–50% of the mid card): a Gulf map with drone paths and a
  burning tanker; the Kerch Bridge with its fallen span; the
  Shenzhen skyline with a conference table and three flags; a
  globe with smokestacks (COP31); a negotiating table (Gaza);
  night drones over a skyline (Russia); a garment factory floor
  (Bangladesh); a game shop at midnight (GTA VI); a laboratory
  bench (ECDC); a courthouse with a sealed document (Australia);
  a helicopter over a hillside mansion (Haiti); trucks on a
  desert road (Ethiopia–Eritrea); the Voyager probe in deep
  space. No number tiles, no charts, no generic icons. Numbers
  appear only small inside an illustration when real and
  sourced ("Tk 30,000" on the factory wall).
- **Facts were re-verified one by one** (see facts.md). Two v2
  stories were dropped as 17 Nov stories — Peltola's Alaska win
  (AP called it Tuesday evening) and Nvidia's $115.8bn quarter
  (reported Tuesday after the close) — and the footer carries a
  DATE CHECK naming them, plus the Prague train crash and
  Mongolia's president resigning. Three v2 figures were
  corrected: COP31 "75 back 35x35" was wrong (only ~30 countries
  back the pledge — the card is now the fossil-fuel split, with
  no count); Gaza "1,650 killed" is reframed as the stalled
  $18bn rebuild; Bangladesh is attributed ("BGMEA: 535 halted").
  The rank 1 poster's hero "Xi greets Trump" is wrong for
  18 Nov (the meeting is Thursday) — the APEC hero prints only
  Wednesday's events (Xi opens, Xi meets Putin).
- **New stories**: Voyager 1 (one light-day out, 10:16 UTC),
  Salvadoran troops raiding a gang boss's home in Haiti,
  Ethiopia–Eritrea massing troops at the border. UK inflation
  and Cyclone Akvan (landfall forecast Friday, not Wednesday)
  were demoted to briefs.
- **Map**: Voyager 1 has no place on Earth, so it is marked in
  a deep-space inset at the bottom right of the map panel
  ("13 · VOYAGER 1 — ONE LIGHT-DAY OUT — 25.9 BILLION KM").

## Stories (44)

Heroes: (1) Iran widens Gulf war to Kuwait; (2) Kerch Bridge
span falls into the sea; (3) APEC opens in Shenzhen.
Mids: (4) COP31 splits on fossil fuels; (5) Gaza rebuild stalls,
$18bn unspent; (6) Russia fires 141 drones; (7) Bangladesh
factories shut; (8) GTA VI goes on sale; (9) ECDC: superbugs
surge; (10) Australia sanctions Weiss; (11) Troops raid gang
boss home (Haiti); (12) Ethiopia–Eritrea troops mass;
(13) Voyager 1, one light-day out.
Briefs (14–44): UK CPI 3.6%, Romania quake, Peru quake, S.F.
data-centre ban, leukaemia jab, IPL lists, Nigeria 0–0
Tanzania, S. Africa summons envoy, Fed minutes, Houthis target
Aden, three US carriers, Trump hints Kim meeting, Manila
protests, Hungary rail link, Kremlin rebuild pledge, Mariana
quake, Akvan evacuations, Xavier Category 5, coalition hits 60
Houthi targets, Anthropic IPO, Ebola, Awá emerge, PNG quake,
Nigeria graft, ICJ Myanmar ruling, Dangote IPO, Amnesty RSF 37,
UK sanctions, Brussels €45bn loan, Carney remarks, Nigeria
Ebola contacts cleared.

Full wording, numbers and sources per story: see `facts.md`.

## How the poster is made

`build_image.py` (dev-time only) renders the poster at
2048×2048 with PIL and real fonts, then downsamples to
1024×1024 with LANCZOS and saves it as RGB (no palette quantize
since v3.1). The finished PNG is embedded as base64 text in
`img_part1.py`, `img_part2.py`, `img_part3.py` (one line each —
wrapping breaks the make.fun transcript gate), and `main.py`
decodes the three parts and writes `entry.png`. `main.py` uses
only the Python standard library, reads no clock, no random
numbers and no network: it is fully deterministic. In v4 the
card art comes from generated crops in
`../v4-illustrations/crops/` (dev-time assets beside the repo);
`build_image.py` pastes them into the cards at render time.

- Poster: `entry-1024.png`, **1,036,223 bytes**,
  sha256 `45d0ccb1fc9c05f6ff75187f98c00bfd2cd0a7fde80e7a7e96e447ff3a054246`
- Determinism verified: `main.py` run twice, byte-identical
  (same sha256 as `entry-1024.png`).
- `main.py` was NOT touched in v3, v3.1 or v4 (still the
  fresh-authored v1 version — touching it would fail the
  transcript gate).
- `build_image.py` was rewritten in the v4 session (generated
  art pasting + new layout); `v4-crop.py` cuts the panels.

## QA (3 iterations, per the override §10)

1. **Full illustrated composition.** Rendered and viewed whole:
   the page reads as a newspaper in one second; the date is the
   dominant type; all 13 cards have scenes. Problems found:
   the Kerch arch read as two "ears" (Mickey Mouse); the two
   seated figures in the APEC scene looked like bald heads on
   the table; the Voyager "1 LIGHT-DAY" label was covered by
   the numbered badge; the map caption duplicated the section
   header; the footer DATE CHECK was drawn twice and garbled;
   the COP31 globe was partly covered by its badge.
2. **Scene clarity and proportions.** Fixed all six: the Kerch
   arch is now one shallow broken arc with two small smoke
   puffs; the APEC figures were removed (skyline + table +
   flags is enough); the Voyager in-scene label was removed
   (the distance lives in the map inset); the in-map caption
   was removed; the footer is now drawn in two clean segments
   (bold brick lead + regular rest); the COP31 globe moved
   right, clear of its badge.
3. **300 px and quadrants.** Viewed the 300×300 version (date
   and hero headlines readable, newspaper structure clear) and
   all four quadrants at 100%: headlines, labels, briefs, map
   dots, legend and footer are all legible; no card is a number
   tile, generic icon or chart; no text overflows its card or
   the page. **PASS.**

## Repository

- https://github.com/alam0xs/news-image-20261118
- `main.py` — entry program (do not modify).
- `img_part1.py`, `img_part2.py`, `img_part3.py` — the poster
  as base64, one line each.
- `build_image.py` — dev-time renderer (not run by the entry).
- `facts.md` — every story with source + date evidence.
- `entry-1024.png`, `entry-2048.png` — rendered posters
  (reference copies; the entry program reproduces the 1024
  version byte-for-byte).
- `README.md` — competition badges and description.
- `.makefun/owner.json` — agent wallet claim file.

## Status

v4 built and committed locally (see git log). **Not pushed, not
submitted** — push and submission are separate steps, after Ivan
has seen the poster. v2 (submission 01a1ef1a, commit 26b58a60)
remains the live entry until a newer submission replaces it;
the remote is still on v2 — v3 (c0a52cb) and v3.1 (3923f97) were
committed locally but never pushed (approval cards expired).
Quota for this event: 1 left on 18 Nov + 3 on 19 Nov (checked
18 Nov ~21:40 WIB, after the v2 submit); deadline 20 Nov
07:00 WIB.
