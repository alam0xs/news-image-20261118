# DOSSIER — news-image-20261118 (Palette A)

## What this entry is

One 1024x1024 PNG front page, "THE WORLD — WEDNESDAY, 18 NOVEMBER
2026", summing up the day's world news: **38 stories across 6
continents** (3 heroes, 12 mid stories, 23 briefs) plus a numbered
world map. The judge has no news feed, so the image carries the news
itself: a prominent date, specific recognisable events of that day,
breadth across regions and fields, and clean craft legible at
~300 px wide.

This entry reuses the layout and Palette A (cream `#F7F1E3`, navy
`#10213F`, gold `#D4A838`) of the 17 Nov v3a poster (rank 52,
98.73%). The content is entirely new for 18 November: the news day
was still in progress at build time (~09:00 UTC), so the poster uses
the best-confirmed stories available so far — the entry can be
iterated tomorrow morning with the complete day. See `facts.md` for
the full fact pass, the stories dropped as unconfirmable or off-date,
and the number conflicts that were resolved.

## How the image is made

`build_image.py` (dev-time only) renders the poster with PIL 10.2.0
and real fonts at 2048x2048, downsamples to 1024x1024 with LANCZOS,
and quantizes to a 256-colour palette PNG (flat vector art quantizes
cleanly — no visible difference from the RGB render). Layout: cream
`#F7F1E3`, navy `#10213F`, gold `#D4A838` (Palette A); region
colours (Europe blue, Middle East orange, Asia red, Africa green,
Americas purple, Oceania teal, Global grey) with darker chip variants
so white text on the chips clears 4.5:1 contrast; mixed-case
headlines; one simple original flat icon per story; no real faces, no
brand logos.

Two details worth recording. First, the date font: DejaVu Serif Bold
at >= 66 px cannot fit "WEDNESDAY 18 NOVEMBER 2026" on one line
inside 1024 minus margins. The date therefore uses Liberation Serif
Bold (a real serif on this machine), set at 68 px and drawn centred
so it keeps >= 24 px margins on both sides; hero headlines keep
DejaVu Serif Bold. Second, the masthead is 120 px tall, not 104: a
66+ px date plus the required 24 px clear space below the top row
does not fit in 104 px, so the masthead grew and the heroes start at
y128.

New art for this poster: a ballot-box hero scene with a Senate tally
(56–44 bars), five new mid icons (bridge, cyclone, rising chart,
seismograph, factory), and Gulf-scene labels (KUWAIT, QESHM) with
drone arrows flying towards the radar. Briefs are set at 14 px, up
from 13.5 px in the 17 Nov poster. The date font changed too:
Liberation Serif Bold (66 px, 1,057 px wide) cannot fit "WEDNESDAY
18 NOVEMBER 2026" on one line, so the date uses Noto Serif Condensed
Bold (66 px, 961 px wide), drawn centred with >= 24 px margins on
both sides; its larger ascent moved the date's top up to y40 so the
baseline still lands at 112, as in the 17 Nov poster.

`main.py` is standard library only. It does not draw the poster at
run time: the finished PNG is embedded in the repo as base64 text
(`img_part1.py`, `img_part2.py`, `img_part3.py`) because the
repository hosting used here cannot store binary files, and `main.py`
decodes those bytes and writes them to `$MAKEFUN_OUTPUT_DIR` (or
`/output/entry.png`). Each part stores its base64 as a single line:
the PNG is data, not code, so wrapping it over thousands of lines
would misrepresent the file. No network, no randomness, no
timestamps.

## Facts

Every story was checked against live reporting of 18 November 2026
(AP, Reuters, AFP, Al Jazeera, Xinhua, ONS, USGS, EMSC, GFZ, UN,
QNA, Nairametrics, Vanguard and others — see `facts.md` for the
per-story source). Headline claims:

- Iran/Gulf: Iran's army says drones targeted US Patriot systems at
  Kuwait's Ali Al Salem Air Base (first attack on Kuwait since
  September); Kuwait says the drones were downed, no casualties;
  Bahrain intercepted Iranian attacks for a third time this week.
- APEC: Xi opened the APEC summit in Shenzhen on Wednesday 18 Nov;
  Xi and Putin met in Shenzhen; Trump is in Manila and flies to
  Shenzhen late Wednesday; the first-ever trilateral Trump–Xi–Putin
  meeting is Thursday 19 Nov in Shenzhen, nuclear arms the stated
  focus, no agreement expected.
- Peltola: Democrat Mary Peltola won Alaska's US Senate race, called
  17 Nov 22:27 EST (= 18 Nov 03:27 UTC), 144,302 votes (50.12%) to
  131,844 (45.80%); Democrats reach 56–44; first Democrat to win an
  Alaska Senate race since 2008 and the first Alaska Native senator.
- Kerch Bridge: the 227-metre road arch span collapsed into the
  Kerch Strait (Reuters-verified video); the bridge is no longer
  usable, the road link is severed, the rail link is standing but
  damaged and partly resumed; the full extent was confirmed and
  reported on 18 Nov. Zelensky says it was a 7-stage SBU operation.
- Nvidia: Q3 revenue $115.84bn (vs ~$109bn expected), EPS $2.68,
  data centre $107.6bn, Q4 guide ~$130bn; shares jumped after hours
  (no percentage printed — sources vary 1.7%–5%).
- Cyclone Xavier: Category 5, Northern Cook Islands, sustained
  220 km/h, gusts to 315 km/h, 910 hPa; shelters activated.
- Ebola: outbreak in DR Congo passed 11,000 cases (UN); no death
  toll printed (sources disagree 5,400 vs 5,572 vs 5,500).
- Coalition: Saudi-led coalition destroyed 60 Houthi targets and
  downed a Houthi cruise missile towards Riyadh.
- Anthropic: expected to price shares on Wednesday 18 Nov, Nasdaq
  debut Thursday 19 Nov as ANT, $70–78 range, valuation up to
  ~$1.4tn fully diluted, ~$64bn raise, ~6x oversubscribed.
- UK inflation: CPI 3.6% in October (one-year high); petrol
  174.7p/litre (highest since August 2022), diesel 199.5p (record).
- Awá: about 20 uncontacted Awá people emerged in Maranhão, Brazil
  (encounter Mon 16 Nov, images shared Tue 17 Nov, widely reported
  Wed 18 Nov); first close contact in decades.
- PNG quake: strong earthquake off Madang, 03:42 UTC; no magnitude
  printed (GFZ 6 vs USGS 5.8 disagree).
- Nigeria: an AU anti-graft body says Nigeria and others lose $125bn
  yearly to illicit financial flows, $80bn to corruption.
- ICJ: the International Court of Justice rules Thursday 19 Nov on
  whether Myanmar's 2017 campaign against the Rohingya was genocide;
  first final ruling in a decade.
- Dangote: the refinery IPO expanded its share sale up to 30%
  (~$1.6bn → ~$2.1bn), orders nearly 4.4tn naira, retail investors
  get full allocation.
- Briefs: Romania 5.3 quake (USGS + EMSC agree); Peru M6 quake;
  San Francisco extends its data-centre moratorium by 10 months;
  leukaemia vaccine cuts death risk (no number printed); AFP
  investigation of a US deep-sea mining firm's claims; IPL 2027
  retention lists filed; Nigeria 0–0 Tanzania (AFCON qualifiers);
  South Africa summons the Nigerian envoy; Cyclone Akvan nears the
  Andhra coast; Fed October minutes due today; Nigeria's Ebola
  contacts clear quarantine (62 contacts, 0 new infections); DRC,
  Rwanda row over Francophonie; Houthi missiles target Aden airport;
  three US carrier groups now in the Gulf; Trump hints at a Kim
  meeting in China; Xi meets Canada's Carney at APEC; protests greet
  Trump in Manila; Hungary suspends rail services with Ukraine for
  17–18 Nov; Russia claims 1,441 drones fired overnight (attributed);
  Kremlin vows to rebuild the Kerch Bridge; M1.1 solar flare;
  Ramaphosa challenges Musk to "give back"; quake south of the
  Mariana Islands (5.6).

Dropped vs the 17 Nov poster: measles (17 Nov story, case count
disputed); Gaza IOM hypothermia warning (17 Nov); Dhoni IPL
retirement (announced 17 Nov — the 18 Nov angle is the retention
lists); Macron/Malaysia rare-earths deal (announced 17 Nov); UK–EU
summit package / Burnham (16–17 Nov, summit is Friday 20 Nov); Pope
Leo XIV ends tour (ended 16 Nov); Moldova airspace closure + NSA
outage (17 Nov); "six US troops killed in Kuwait" (single aggregator,
Kuwait reported no casualties); "at least six killed in US strikes
on Qeshm" (single aggregator, unconfirmed); the Houthi claim of 15
killed in a Hodeidah foam-factory strike (a Houthi claim); the Ebola
death toll (disputed); the PNG quake magnitude (GFZ vs USGS
disagree); the Nvidia share-jump percentage (sources vary); Tuesday's
Wall Street session (a 17 Nov story, already used in the 17 Nov
poster); "five charged under SA mercenary law" (sourcing could not
be confirmed for 18 Nov — replaced by the Mariana Islands quake).

## Verification

- Output: valid PNG, 1024x1024, palette mode, 200,434 bytes
  (< 1 MiB).
- `main.py` run twice from a different working directory into two
  different output directories: outputs byte-identical, sha256
  `6e292d8560f9263b177fab52ff76c97ce503ba7d8c7327545317b606710385c8`,
  matching the rendered `entry-1024.png` exactly.
- Build asserts all passed: 38 stories (masthead count matches);
  date 68 px on one line with >= 24 px clear of the top row and
  >= 24 px margins on both sides; hero headlines <= 2 lines at
  >= 26 px, sublines <= 2 lines at >= 13.5 px; mid headlines <= 3
  lines at >= 17 px, sublines <= 2 lines at >= 12 px; every brief
  fits one line at 14 px; no map dots touch or overlap.
- The final 1024 image was read visually (top 120 px, four quadrants
  at 100%, and a 300 px copy): masthead, date and the 3 hero
  headlines are readable at 300 px; no overlap, no clipped words, no
  typos found.
- `main.py` imports only `base64`, `os`, `sys` (stdlib) plus the
  three sibling data modules; no network, no randomness, no
  timestamps, no file reads besides the program itself.
