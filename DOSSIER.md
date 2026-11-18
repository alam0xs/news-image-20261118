# DOSSIER — news-image-20261118 v2 (Palette A)

## What this entry is

One 1024x1024 PNG front page, "THE DAY IN WORLD NEWS — WEDNESDAY,
18 NOVEMBER 2026", summing up the day's world news: **43 stories
across 6 continents** (3 heroes, 10 mid stories, 30 briefs) plus a
numbered world map. The judge has no news feed, so the image carries
the news itself: a prominent date, specific recognisable events of
that day, breadth across regions and fields, and clean craft legible
at ~300 px wide.

This entry reuses Palette A (cream `#F7F1E3`, navy `#10213F`, gold
`#D4A838`) of the 17 Nov v3a poster (rank 52, 98.73%) and the v1
18 Nov poster, but the layout and content are rebuilt for v2: the
news day was nearly complete at build time (~14:20–15:00 UTC), so
the poster uses the best-confirmed stories available so far. See
`facts.md` for the full fact pass, the stories dropped as
unconfirmable or off-date, and the number conflicts that were
resolved. The fact pass re-checked every v1 item against the 17 Nov
posters: several v1 items turned out to be 17 Nov stories and were
dropped or reframed (Knesset speaker vote, Russia "1,441 drones",
Xi–Carney meeting, Sudan UN 2,230, An-12 crash, and four weak
single-source briefs).

## How the image is made

`build_image.py` (dev-time only) renders the poster with PIL 10.2.0
and real fonts at 2048x2048, downsamples to 1024x1024 with LANCZOS,
and quantizes to a 256-colour palette PNG (flat vector art quantizes
cleanly — no visible difference from the RGB render). Layout: cream
`#F7F1E3`, navy `#10213F`, gold `#D4A838` (Palette A); region
colours (Europe blue, Middle East orange, Asia red, Africa green,
Americas purple, Oceania teal, Global grey) with darker chip variants
so white text on the chips clears 4.5:1 contrast; mixed-case
headlines; original flat-vector illustrations; no real faces, no
brand logos.

v2 layout changes vs v1 (following the rank 1–4 poster study):
- Heroes (y150–356): Kerch Bridge promoted to hero 2; the Gulf hero
  is now a geographic map (Iran / Kuwait / Bahrain / UAE / Hormuz /
  Qeshm, dashed drone paths, a burning tanker in the strait) instead
  of a tanker scene; a one-line summary sits under the date
  ("Strikes in the Gulf and on the Kerch bridge, a three-way summit
  in Shenzhen and a chipmaker's record quarter — the day in 43
  stories.").
- Mids (y362–702): rebuilt as 5 columns x 2 rows (cards 192x166),
  image-on-top as the master brief requires — a 3 px regional top
  bar, a 70 px band carrying one big verified number (or the three
  summit flags for APEC) with a numbered badge upper-left, then the
  region/category label, a 2-line serif headline and a 2-line
  description.
- Bottom (y708–984): the world map keeps its 346x230 panel, now with
  hairline leader lines joining nudged dots to their true spots, and
  a compact legend that fits above the footer; briefs grow to 30
  (two columns of 15, 13 px).
- The date font: DejaVu Serif Bold at >= 66 px cannot fit
  "WEDNESDAY 18 NOVEMBER 2026" on one line inside 1024 minus
  margins, and Liberation Serif Bold (1,057 px at 66 px) cannot
  either. The date uses Noto Serif Condensed Bold (961 px at 66 px);
  fit_text settles on 67 px, drawn centred with >= 24 px margins on
  both sides; its larger ascent moved the date's top up to y40 so the
  baseline still lands at 112, as in the 17 Nov poster. Hero
  headlines keep DejaVu Serif Bold.

`main.py` is standard library only. It does not draw the poster at
run time: the finished PNG is embedded in the repo as base64 text
(`img_part1.py`, `img_part2.py`, `img_part3.py`) because the
repository hosting used here cannot store binary files, and `main.py`
decodes those bytes and writes them to `$MAKEFUN_OUTPUT_DIR` (or
`/output/entry.png`). Each part stores its base64 as a single line:
the PNG is data, not code, so wrapping it over thousands of lines
would misrepresent the file. No network, no randomness, no
timestamps. `main.py` was written from scratch for v1 and is
untouched in v2.

## Facts

Every story was checked against live reporting of 18 November 2026
(AP, Reuters, AFP, Al Jazeera, Xinhua, ONS, ECDC, IMD, USGS, EMSC,
GFZ, UN, QNA, Nairametrics, Vanguard and others — see `facts.md`
for the per-story source). Headline claims:

- Iran/Gulf: Iran's army says drones targeted US Patriot systems at
  Kuwait's Ali Al Salem Air Base (first attack on Kuwait since
  September); Kuwait says the drones were downed, no casualties;
  Bahrain intercepted Iranian attacks for a third time this week;
  ADNOC L&S said one crew member was missing and 11 injured after
  its vessel was attacked in the Strait of Hormuz on Tuesday.
- Kerch Bridge: the 227-metre road arch span collapsed into the
  Kerch Strait (Reuters-verified video); the bridge is no longer
  usable, the road link is severed, the rail link is standing but
  damaged and partly resumed; the full extent was confirmed and
  reported on 18 Nov. Zelensky says it was a 7-stage SBU operation.
- Peltola: Democrat Mary Peltola won Alaska's US Senate race, called
  17 Nov 22:27 EST (= 18 Nov 03:27 UTC), 144,302 votes (50.12%) to
  131,844 (45.80%); Democrats reach 56–44; first Democrat to win an
  Alaska Senate race since 2008 and the first Alaska Native senator.
- APEC: Xi opened the APEC summit in Shenzhen on Wednesday 18 Nov;
  Xi and Putin met in Shenzhen; Trump is in Manila and flies to
  Shenzhen late Wednesday; the first-ever trilateral Trump–Xi–Putin
  meeting is Thursday 19 Nov in Shenzhen, nuclear arms the stated
  focus, no agreement expected.
- Nvidia: Q3 revenue $115.84bn (vs ~$109bn expected), EPS $2.68,
  data centre $107.6bn, Q4 guide ~$130bn, revenue +103% year on year;
  shares jumped after hours (no percentage printed — sources vary
  1.7%–5%).
- Russia drones: 141 strike drones overnight 17–18 Nov (Ukrainian
  Air Force), 126 downed or suppressed by 08:00; 5 killed, 15
  wounded across Ukraine in the past day.
- Gaza: the Board of Peace delivered its first report to the UN
  Security Council (submitted Tue 17 Nov, AP dispatch 18 Nov
  01:39 UTC), warning the truce may collapse; Israel has not allowed
  the interim civil administration to take up its work; 1,650 killed
  in Gaza since the ceasefire (Gaza health authorities, via AP).
- COP31: 75 countries + 94 organisations back Türkiye's "35x35"
  power goal (electricity 35% of final energy by 2035, from ~22%);
  in the first draft of the proposed final decision, not adopted.
- GTA VI: rolling midnight launch began in New Zealand (11:00 GMT
  Wed 18 Nov); first GTA in ~13 years; Sensor Tower estimates
  ~15.88m copies and ~$1.54bn pre-release sales.
- ECDC: carbapenem-resistant K. pneumoniae bloodstream infections up
  72% since 2019 (2.18 → 3.75 per 100,000); EU met 1 of 5 2030
  targets.
- Australia: sanctions on 3 Israeli individuals + 4 organisations
  for settlement expansion and settler violence; Daniella Weiss
  (Nachala) among them; Foreign Minister Penny Wong.
- Bangladesh: garment protests, third day, ~500 factories shut since
  Saturday (Al Jazeera/AFP — a top poster prints 55, which conflicts
  with the better-sourced ~500); workers seek Tk 30,000/month
  (vs Tk 12,500 now); highway blocked, police car torched.
- UK inflation: CPI 3.6% in October (one-year high); petrol
  174.7p/litre (highest since August 2022), diesel 199.5p (record).
- Briefs: Romania 5.3 quake (USGS + EMSC agree); Peru strong quake
  (no magnitude — agencies differ); San Francisco extends its
  data-centre moratorium by 10 months; leukaemia vaccine cuts death
  risk (no number printed); IPL 2027 retention lists filed; Nigeria
  0–0 Tanzania (AFCON qualifiers); South Africa summons the Nigerian
  envoy; Fed October minutes due today; Houthi missiles target Aden
  airport; three US carrier groups now in the Gulf; Trump hints at a
  Kim meeting in China; protests greet Trump in Manila; Hungary
  suspends rail services with Ukraine for 17–18 Nov; Kremlin vows to
  rebuild the Kerch Bridge; quake south of the Mariana Islands (5.6);
  Cyclone Akvan: Odisha to evacuate 204,070 (IMD landfall ~noon
  20 Nov); Cyclone Xavier reaches Category 5 (gusts 315 km/h);
  Coalition hits 60 Houthi targets; Anthropic to price its $1.4tn
  IPO tonight (fully diluted, top of the $70–78 range — final price
  not confirmed at build time); Ebola still out of control, WHO warns
  (3rd Emergency Committee, UN appeal, children hit hardest — no
  death toll printed, sources differ); Awá emerge from the Amazon;
  PNG quake off Madang (no magnitude — GFZ 6 vs USGS 5.8 disagree);
  Nigeria loses $125bn a year to graft; World Court to rule on
  Myanmar Thursday; Dangote refinery IPO grows to $2.1bn; Amnesty:
  RSF drones killed 37 in El Obeid; Britain sanctions eight
  settler-builders; Brussels proposes a €45bn Ukraine loan (leaders
  decide 26–27 Nov); Carney: China trade no worry for Trump;
  Nigeria's Ebola contacts clear quarantine (62 contacts, 0 new
  infections).

Dropped vs v1 (all 17 Nov stories, found by re-checking v1 against
the 17 Nov posters): Knesset speaker vote 66–52 (vote Tue night
17 Nov) and the deputy-speakers approval (Mon 16 Nov); Sudan UN
2,230 civilian deaths (OHCHR report Tue 17 Nov — reframed as the
Amnesty 37, released Wed 18 Nov); Russia "1,441 drones fired"
(17 Nov claim); Xi meets Carney at APEC (meeting Tue 17 Nov —
reframed as Carney's Wednesday remarks); An-12 crash in Siberia
(17 Nov); deep-sea miner's claims denied, DRC/Rwanda Francophonie
row, M1.1 solar flare, Ramaphosa vs Musk (weak single-source
briefs). Also dropped: measles (17 Nov, count disputed); Gaza IOM
hypothermia warning (17 Nov); Dhoni IPL retirement (17 Nov — the
18 Nov angle is the retention lists); Macron/Malaysia rare-earths
deal (17 Nov); UK–EU summit package / Burnham (16–17 Nov); Pope
Leo XIV ends tour (ended 16 Nov); Moldova airspace closure + NSA
outage (17 Nov); "six US troops killed in Kuwait" and "at least six
killed in US strikes on Qeshm" (single aggregators, unconfirmed);
the Houthi claim of 15 killed in a Hodeidah foam-factory strike;
the Ebola death toll (disputed); the PNG quake magnitude (GFZ vs
USGS disagree); the Nvidia share-jump percentage (sources vary);
Tuesday's Wall Street session (a 17 Nov story); the Bangladesh "55
factories" figure (conflicts with ~500, Al Jazeera/AFP); the Russia
"80+ Rivne settlements" power cut (not independently verified); the
COP31/Brussels loan splits (vary by source).

## Verification

- Output: valid PNG, 1024x1024, palette mode, 217,626 bytes
  (< 1 MiB).
- `main.py` run twice from a different working directory into two
  different output directories: outputs byte-identical, sha256
  `bf1770a528b50a25f8ec6263e4f10b7b6573100833644ba713e4cbc4fc4b3f62`,
  matching the rendered `entry-1024.png` exactly.
- Build asserts all passed: 43 stories (masthead count matches);
  date 67 px on one line with >= 24 px clear of the top row and
  >= 24 px margins on both sides; hero headlines <= 2 lines at
  >= 26 px, sublines <= 2 lines at >= 13.5 px; mid headlines <= 2
  lines at >= 16 px, sublines <= 2 lines at >= 12 px, mid text block
  fits the card; every brief fits one line at 13 px; no map dots
  touch or overlap.
- The final 1024 image was read visually (top 120 px, hero section,
  mid section, map, briefs, four quadrants at 100%, and a 300 px
  copy): masthead, date and the 3 hero headlines are readable at
  300 px; the Gulf map labels (IRAN / HORMUZ / QESHM) were fixed
  after inspection (IRAN was hidden behind the region chip, HORMUZ
  and QESHM overlapped); the map legend was compacted after
  inspection (it ran over the footer); no overlap, no clipped words,
  no typos found.
- `main.py` imports only `base64`, `os`, `sys` (stdlib) plus the
  three sibling data modules; no network, no randomness, no
  timestamps, no file reads besides the program itself.
