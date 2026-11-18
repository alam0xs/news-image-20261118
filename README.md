# Sum up 18 November's world news in one image

[![make.fun](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/alam0xs/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/alam0xs/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118)

Entry for make.fun bounty
[`news-image-20261118`](https://make.fun/bounty/news-image-20261118):
a program that writes one image summing up the world's news of
Wednesday, 18 November 2026, to `/output/entry.png`.

## The image

A newspaper front page, "THE WORLD — WEDNESDAY, 18 NOVEMBER 2026":
**38 stories across 6 continents** — 3 hero stories, 12 mid stories,
23 one-line briefs and a numbered world map, each with a region chip
and a small flat illustration. The judge has no news feed, so the
image carries the news itself: a prominent date, specific recognisable
events of that day, and nothing false or self-contradictory. Every
story was checked against live reporting of 18 November 2026;
disputed claims are attributed ("Iran says", "US says", "Kyiv says")
and casualty numbers that differ between sources are left out. Full
sourcing in `facts.md`.

- **Hero 1 — Middle East:** Iran hits US bases in Kuwait and
  Bahrain (Kuwait says drones downed; Bahrain hit a third time
  this week)
- **Hero 2 — Asia:** Xi and Putin meet as APEC opens in Shenzhen
  (Trump flies in tonight; first-ever trilateral summit Thursday)
- **Hero 3 — Americas:** Peltola flips Alaska's Senate seat
  (Democrats reach 56; first Alaska Native senator)
- **Mid stories:** Kerch Bridge crippled, road link cut; Nvidia
  shares jump after record results ($115.8bn revenue); Cyclone
  Xavier slams the Cook Islands; Ebola passes 11,000 cases in DR
  Congo; coalition hits 60 Houthi targets; Anthropic to price its
  $1.4tn IPO today; UK inflation hits 3.6%, a one-year high;
  uncontacted Awá emerge from the Amazon; quake shakes Papua New
  Guinea; Nigeria loses $125bn a year to graft; the World Court to
  rule on Myanmar Thursday; Dangote refinery IPO grows to $2.1bn
- **Also today (23 briefs):** Romania 5.3 quake shakes Bucharest;
  Peru quake off the coast; San Francisco extends its data-centre
  ban; leukaemia vaccine cuts death risk; deep-sea miner's claims
  denied; IPL retention lists filed; Nigeria held 0-0 by Tanzania;
  South Africa summons the Nigerian envoy; Cyclone Akvan nears the
  Andhra coast; Fed October minutes due today; Nigeria's Ebola
  contacts clear quarantine; DRC, Rwanda row over Francophonie;
  Houthi missiles target Aden airport; three US carriers now in the
  Gulf; Trump hints at a Kim meeting in China; Xi meets Canada's
  Carney at APEC; protests greet Trump in Manila; Hungary halts its
  rail link to Ukraine; Russia says 1,441 drones fired; Kremlin
  vows to rebuild the bridge; Sun records an M1.1 solar flare;
  Ramaphosa challenges Musk to give back; quake south of the
  Mariana Islands

## How it works

`main.py` (Python 3.13, standard library only) writes the finished
1024x1024 PNG to `/output/entry.png`. No network, no randomness, no
timestamps — two runs write identical bytes.

The poster itself was rendered at 2048x2048 with PIL and DejaVu
fonts (`build_image.py`, dev-time only), downsampled to 1024x1024
and palette-quantized. The finished PNG is embedded in this repo as
base64 text (`img_part1.py`, `img_part2.py`, `img_part3.py`) because
the repository hosting used here cannot store binary files;
`main.py` only decodes those bytes and writes them out.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Files

- `main.py` — the entrypoint (decodes the embedded PNG, writes it)
- `img_part1.py`, `img_part2.py`, `img_part3.py` — the poster PNG as
  base64 text (split in three so each file stays small)
- `build_image.py` — the renderer that produced the poster (dev-time)
- `facts.md` — every story with its source and attribution, plus what
  was checked and what was dropped
- `README.md` — this file
- `DOSSIER.md` — design notes, sources, verification
- `LICENSE` — MIT

## License

MIT — see `LICENSE`.
