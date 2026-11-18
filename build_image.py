#!/usr/bin/env python3
"""Render the poster for make.fun news-image-20261118, v4.

Dev-time only: renders at 2048x2048 with PIL and real fonts, then
downsamples to 1024x1024 with LANCZOS and saves it as RGB (no
palette quantize since v3.1 — it blurred the poster). The finished
1024 PNG is embedded as base64 in img_part1/2/3.py (the GitHub
connector cannot push binaries); main.py decodes it at run time.
See facts.md for the stories and their sources.

v4 — generated raster illustrations. The v3 illustrations were
drawn in PIL code (rectangles, polygons, ellipses) and looked
schematic and empty next to the rank 1 poster's rich raster art.
In v4 every hero and mid card carries a generated illustration:
four contact sheets were generated (heroes triptych, two 2x2 mid
grids, one 2-panel sheet), each panel was cropped to the card art
aspect and pasted into its card. The crops live in
../v4-illustrations/crops/ (dev-time assets, not in the repo —
the entry program reproduces the poster from the embedded PNG).
One exception, hero 3 (APEC): the generated panel shows Xi
shaking hands with Trump, but the Trump-Xi meeting is Thursday
19 Nov, not Wednesday (see facts.md) — using it would contradict
the poster, so hero 3 uses a skyline-only window of that panel
(the Shenzhen towers, no people). The v3 scene_* functions are
otherwise unused in v4 (scene_apec stays as a code fallback).

Layout (all geometry in 1024-page units; S=2 render scale):
  kicker   y12, date y30-108, deck y114, double rule y134/139
  heroes   y142-398, three cards 320x256, art 308x128 on top
  mids     y406-578 and y584-756, five cols x two rows, cards
           184x172, art 176x84 on top (v3: 184x152, art 176x58)
  bottom   y764 headers, map y784-940 (536x156) + 24 briefs right
  legend   y946/958 under the map
  footer   gold rule y974, date-check y982, sources y998
Stories: 3 heroes + 10 mids + 24 briefs = 37 (v3 had 31 briefs;
7 weakest briefs were cut to make room for the taller mid art).
No navy masthead block, no giant-number tiles, no charts.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
S = 2  # render scale: 2048 canvas, 1024 output
W, H = 1024 * S, 1024 * S

# ---------------------------------------------------------------- palette
# Ivory newspaper paper, near-black ink, muted brick red + antique
# gold accents. Region colours only for small chips, dots and lines.
PALETTE = {
    "paper": (245, 240, 228),   # warm ivory #F5F0E4
    "card": (252, 249, 239),    # slightly lighter card paper
    "ink": (30, 34, 43),
    "grey": (74, 80, 96),
    "border": (216, 205, 178),
    "brick": (166, 58, 46),
    "gold": (192, 154, 62),
    "gold_dark": (150, 118, 40),
    "sea": (214, 228, 237),
    "sea_line": (196, 208, 218),
    "white": (255, 253, 247),
}
PAPER = PALETTE["paper"]
CARD = PALETTE["card"]
INK = PALETTE["ink"]
GREY = PALETTE["grey"]
BORDER = PALETTE["border"]
BRICK = PALETTE["brick"]
GOLD = PALETTE["gold"]
GOLD_DARK = PALETTE["gold_dark"]
SEA = PALETTE["sea"]
SEA_LINE = PALETTE["sea_line"]
WHITE = PALETTE["white"]

# Region base colours (map fills, dots, art tints).
REGIONS = {
    "Europe": (46, 111, 176),
    "Middle East": (217, 123, 41),
    "Asia": (179, 58, 58),
    "Africa": (46, 125, 79),
    "Americas": (123, 79, 166),
    "Oceania": (31, 138, 138),
    "Global": (90, 98, 112),
}
# Chip colours: darker variants so white bold text clears 4.5:1.
CHIPS = {
    "Europe": (46, 111, 176),
    "Middle East": (176, 88, 14),
    "Asia": (168, 50, 50),
    "Africa": (39, 107, 67),
    "Americas": (110, 69, 150),
    "Oceania": (23, 112, 112),
    "Global": (78, 85, 99),
}
REGION_ORDER = ["Europe", "Middle East", "Asia", "Africa",
                "Americas", "Oceania", "Global"]

FONT_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
# The date must fit one line inside 976 px (>= 24 px margins).
# DejaVu Serif Bold is too wide; Noto Serif Condensed Bold fits.
FONT_SERIF_DATE = "/usr/share/fonts/truetype/noto/NotoSerif-CondensedBold.ttf"


# ---------------------------------------------------------------- helpers
# All geometry below is in 1024-page units; sc() converts to render px.
def sc(v):
    return int(round(v * S))


def pt(x, y):
    return (sc(x), sc(y))


def box(x0, y0, x1, y1):
    return [sc(x0), sc(y0), sc(x1), sc(y1)]


def F(path, size):
    """Font of `size` 1024-page px, rendered at 2x."""
    return ImageFont.truetype(path, sc(size))


def text_w(d, s, f):
    return d.textlength(s, font=f) / S


def wrap(d, text, f, max_w):
    """Greedy word wrap; returns lines that fit max_w (1024 units)."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(d, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_text(d, text, f_path, size, max_w, max_lines, min_size):
    """Shrink font until text fits max_lines at max_w.

    Returns (font, lines, size_used). Raises if it still does not fit
    at min_size — the build must fail rather than print overflow.
    """
    while size >= min_size:
        f = F(f_path, size)
        lines = wrap(d, text, f, max_w)
        if len(lines) <= max_lines:
            return f, lines, size
        size -= 0.5
    raise AssertionError(
        "fit_text overflow: %r needs %d lines at min size %d (max %d)"
        % (text, len(wrap(d, text, F(f_path, min_size), max_w)),
           min_size, max_lines))


def draw_centered(d, cx, y, s, f, fill):
    d.text((sc(cx) - d.textlength(s, font=f) / 2, sc(y)), s, font=f,
           fill=fill)


def letterspaced(d, x, y, s, f, fill, spacing=2):
    """Draw caps text with extra space between letters, left at x.
    Returns the total width drawn (1024 units)."""
    total = 0.0
    for ch in s:
        w = text_w(d, ch, f)
        d.text((sc(x + total), sc(y)), ch, font=f, fill=fill)
        total += w + spacing
    return total - spacing


def rounded_rect(d, b, radius, fill=None, outline=None, width=2):
    # v3.1: default outline 2 (1024 units) — a 1 px card border
    # at 1024 went soft under the old quantize and stays faint in
    # RGB; 2 px reads as a deliberate frame.
    d.rounded_rectangle(box(*b), radius=sc(radius), fill=fill,
                        outline=outline, width=sc(width))


def tint(color, frac=0.85):
    """Mix `color` toward white; frac=0.85 is a pale tint."""
    return tuple(int(c * (1 - frac) + 255 * frac) for c in color)


def chip(d, x, y, label, color, size=12):
    """Small rounded region chip; returns its width (1024 units)."""
    f = F(FONT_SANS_B, size)
    pad_x, pad_y = 7, 3
    w = text_w(d, label, f) + pad_x * 2
    h = size + pad_y * 2
    rounded_rect(d, [x, y, x + w, y + h], radius=h // 2, fill=color)
    d.text(pt(x + pad_x, y + pad_y - 1), label, font=f, fill=WHITE)
    return w


def dashed(d, x0, y0, x1, y1, color, width=3, steps=14):
    """Dashed line in 1024 units (used for drone paths, flight lines).
    v3.1: width 3 — the old 2 px dashes blurred into the sea."""
    for i in range(steps):
        if i % 2:
            continue
        t0, t1 = i / steps, (i + 1) / steps
        d.line([pt(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0),
                pt(x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)],
               fill=color, width=sc(width))


def starburst(d, cx, cy, r, color, width=3):
    """Eight-spoke explosion star centred at (cx, cy).
    v3.1: width 3 — the old 2 px spokes went faint."""
    for k in range(8):
        ang = math.pi * k / 4
        dx, dy = r * math.cos(ang), r * math.sin(ang)
        d.line([pt(cx, cy), pt(cx + dx, cy + dy)], fill=color,
               width=sc(width))

# ---------------------------------------------------------------- v4 art
# Generated raster illustrations, cropped per card by v4-crop.py.
# v4-illustrations/crops/ holds one PNG per card (2x render size);
# paste_art resizes it into the card art box with LANCZOS. These
# are dev-time assets: they live beside the repo, not in it, and
# the entry program (main.py) never reads them — it reproduces the
# finished poster from the embedded base64 PNG.
ART_DIR = os.path.join(HERE, "..", "v4-illustrations", "crops")
_ART_CACHE = {}


def paste_art(img, ax, ay, aw, ah, name):
    """Paste a generated illustration crop into the art box
    (ax, ay, aw, ah) in 1024-page units, onto the base image."""
    if name not in _ART_CACHE:
        path = os.path.join(ART_DIR, name + ".png")
        assert os.path.exists(path), "missing art crop: %s" % path
        _ART_CACHE[name] = Image.open(path).convert("RGB")
    art = _ART_CACHE[name]
    art = art.resize((sc(aw), sc(ah)), Image.LANCZOS)
    img.paste(art, (sc(ax), sc(ay)))


# ---------------------------------------------------------------- hero art
# v4: the scene_* functions below are the v3 PIL illustrations.
# Only scene_apec is still used (hero 3 fallback — see docstring);
# the rest are kept for reference and are no longer called.

def scene_gulf(d, ax, ay, aw, ah):
    """Hero 1: the Gulf as a map. Iran along the top, the Arabian
    Peninsula along the bottom, the sea channel between them. Dashed
    red drone paths run from Iran toward Kuwait and Bahrain, with
    interception starbursts; a tanker burns in the Strait of Hormuz
    at the right edge."""
    d.rectangle(box(ax, ay, ax + aw, ay + ah), fill=SEA)
    # Iran (top land): coastline dipping toward the Gulf.
    # v3.1: darker land (214,190,148) — the old pale fill was
    # barely distinct from the sea after quantize.
    d.polygon([pt(ax, ay), pt(ax + aw, ay), pt(ax + aw, ay + 26),
               pt(ax + 268, ay + 34), pt(ax + 210, ay + 40),
               pt(ax + 150, ay + 32), pt(ax + 90, ay + 40),
               pt(ax + 40, ay + 30), pt(ax, ay + 34)],
              fill=(214, 190, 148))
    # Arabia (bottom land): coastline rising toward the Gulf
    d.polygon([pt(ax, ay + ah), pt(ax + aw, ay + ah),
               pt(ax + aw, ay + ah - 28), pt(ax + 262, ay + ah - 34),
               pt(ax + 200, ay + ah - 30), pt(ax + 150, ay + ah - 40),
               pt(ax + 96, ay + ah - 32), pt(ax + 46, ay + ah - 40),
               pt(ax, ay + ah - 30)],
              fill=(214, 190, 148))
    # Bahrain: a small island in the channel
    d.ellipse(box(ax + 122, ay + 58, ax + 136, ay + 70),
              fill=(214, 190, 148), outline=INK, width=sc(2))
    # Qeshm: a long island in the strait, right side
    d.polygon([pt(ax + 250, ay + 62), pt(ax + 292, ay + 56),
               pt(ax + 296, ay + 66), pt(ax + 254, ay + 74)],
              fill=(214, 190, 148), outline=INK, width=sc(2))
    # dashed drone paths from Iran toward Kuwait and Bahrain
    dashed(d, ax + 118, ay + 34, ax + 44, ay + 58, BRICK, width=3)
    dashed(d, ax + 178, ay + 36, ax + 130, ay + 58, BRICK, width=3)
    # interception starbursts at Kuwait and Bahrain
    starburst(d, ax + 44, ay + 60, 8, BRICK)
    starburst(d, ax + 129, ay + 60, 8, BRICK)
    # tanker in the strait, hull + bridge + fire
    d.polygon([pt(ax + 228, ay + 86), pt(ax + 282, ay + 86),
               pt(ax + 274, ay + 98), pt(ax + 236, ay + 98)],
              fill=(140, 40, 40), outline=INK, width=sc(2))
    d.rectangle(box(ax + 244, ay + 76, ax + 262, ay + 86), fill=WHITE)
    d.polygon([pt(ax + 248, ay + 76), pt(ax + 256, ay + 60),
               pt(ax + 264, ay + 76)], fill=(217, 123, 41))
    d.ellipse(box(ax + 250, ay + 52, ax + 262, ay + 64),
              fill=(217, 123, 41))
    # labels
    f_lab = F(FONT_SANS_B, 11)
    d.text(pt(ax + 118, ay + 6), "IRAN", font=f_lab, fill=INK)
    d.text(pt(ax + 8, ay + 46), "KUWAIT", font=f_lab, fill=INK)
    d.text(pt(ax + 140, ay + 52), "BAHRAIN", font=f_lab, fill=INK)
    d.text(pt(ax + 8, ay + ah - 16), "SAUDI ARABIA", font=f_lab, fill=INK)
    d.text(pt(ax + 228, ay + ah - 16), "UAE", font=f_lab, fill=INK)
    d.text(pt(ax + 258, ay + 10), "HORMUZ", font=f_lab, fill=INK)
    d.text(pt(ax + 244, ay + 40), "QESHM", font=f_lab, fill=INK)


def scene_kerch(d, ax, ay, aw, ah):
    """Hero 2: the Kerch Bridge. A pale sky, the sea at the bottom,
    land wedges at the corners, and the bridge deck in two segments
    with a gap in the middle where the 227 m road arch has fallen
    into the strait; smoke rises over the gap, two drones cross
    the sky."""
    d.rectangle(box(ax, ay, ax + aw, ay + ah),
                fill=tint(REGIONS["Europe"], 0.88))
    # sea at the bottom, land wedges at the corners
    d.rectangle(box(ax, ay + ah - 30, ax + aw, ay + ah),
                fill=(110, 160, 195))
    d.polygon([pt(ax, ay + ah), pt(ax, ay + ah - 36),
               pt(ax + 78, ay + ah - 36), pt(ax + 104, ay + ah)],
              fill=(222, 205, 170))
    d.polygon([pt(ax + aw, ay + ah), pt(ax + aw, ay + ah - 36),
               pt(ax + aw - 78, ay + ah - 36), pt(ax + aw - 104, ay + ah)],
              fill=(222, 205, 170))
    f_lab = F(FONT_SANS_B, 11)
    d.text(pt(ax + 12, ay + ah - 26), "CRIMEA", font=f_lab, fill=INK)
    d.text(pt(ax + aw - 66, ay + ah - 26), "RUSSIA", font=f_lab, fill=INK)
    # two small drones in the sky (body + rotors)
    for (dx, dy) in ((56, 22), (238, 14)):
        d.ellipse(box(ax + dx - 6, ay + dy - 3, ax + dx + 6, ay + dy + 3),
                  fill=INK)
        d.line([pt(ax + dx - 10, ay + dy - 5), pt(ax + dx + 10, ay + dy - 5)],
               fill=INK, width=sc(3))
    # bridge deck: two segments, gap in the middle, falling span
    deck_y = ay + 56
    col = INK
    d.rectangle(box(ax + 12, deck_y, ax + 128, deck_y + 8), fill=col)
    d.rectangle(box(ax + 182, deck_y, ax + aw - 12, deck_y + 8), fill=col)
    d.line([pt(ax + 12, deck_y + 8), pt(ax + 12, deck_y + 44)], fill=col,
           width=sc(5))
    d.line([pt(ax + aw - 12, deck_y + 8), pt(ax + aw - 12, deck_y + 44)],
           fill=col, width=sc(5))
    # the fallen span, tilted down into the water
    d.polygon([pt(ax + 140, deck_y + 12), pt(ax + 172, deck_y + 26),
               pt(ax + 164, deck_y + 36), pt(ax + 132, deck_y + 22)],
              fill=col)
    # the great arch, shallow and broken at the gap: two low arcs,
    # so the bridge reads as a bridge, not two ears
    d.arc(box(ax + 30, deck_y - 16, ax + 150, deck_y + 20), 200, 340,
          fill=col, width=sc(5))
    d.arc(box(ax + 162, deck_y - 16, ax + 280, deck_y + 20), 200, 340,
          fill=col, width=sc(5))
    # two small smoke puffs over the gap
    for (sx, sy, sr) in ((152, 30, 6), (162, 26, 5)):
        d.ellipse(box(ax + sx - sr, ay + sy - sr, ax + sx + sr, ay + sy + sr),
                  fill=(120, 124, 132))
    # water ripples under the gap (v3.1: 3 px, the old 2 px lines
    # vanished against the sea)
    for yy in (ay + ah - 20, ay + ah - 11):
        d.line([pt(ax + 110, yy), pt(ax + aw - 110, yy)],
               fill=WHITE, width=sc(3))


def scene_apec(d, ax, ay, aw, ah):
    """Hero 3: APEC opens in Shenzhen. A skyline of towers along the
    back, a long conference table in front with three small flags
    (China, Russia, US) and two side-profile figures seated at it."""
    d.rectangle(box(ax, ay, ax + aw, ay + ah),
                fill=tint(REGIONS["Asia"], 0.90))
    # sky: a pale band, then the Shenzhen skyline (towers + windows)
    sky = (238, 232, 214)
    d.rectangle(box(ax, ay, ax + aw, ay + 74), fill=sky)
    towers = [(8, 30, 26), (40, 52, 30), (76, 22, 24), (106, 44, 34),
              (146, 58, 28), (180, 34, 30), (216, 48, 26),
              (248, 26, 30), (278, 40, 22)]
    for (tx, th, tw) in towers:
        d.rectangle(box(ax + tx, ay + 74 - th, ax + tx + tw, ay + 74),
                    fill=(120, 128, 142), outline=INK, width=sc(2))
        for wy in range(ay + 74 - th + 6, ay + 70, 10):
            for wx in range(ax + tx + 5, ax + tx + tw - 4, 9):
                d.rectangle(box(wx, wy, wx + 4, wy + 5),
                            fill=(232, 226, 200))
    # spire on the tallest tower
    d.line([pt(ax + 155, ay + 74 - 58), pt(ax + 155, ay + 74 - 70)],
           fill=(120, 128, 142), width=sc(3))
    # conference table: long dark trapezoid in the foreground.
    # v3.1: INK outline so the table edge reads against the pale sky.
    d.polygon([pt(ax + 30, ay + 96), pt(ax + aw - 30, ay + 96),
               pt(ax + aw - 12, ay + ah - 6), pt(ax + 12, ay + ah - 6)],
              fill=(96, 68, 48), outline=INK, width=sc(2))
    d.rectangle(box(ax + 30, ay + 92, ax + aw - 30, ay + 96),
                fill=(70, 48, 34))
    # three small flags on the table (China, Russia, US)
    def flag(fx, kind):
        d.line([pt(fx + 8, ay + 92), pt(fx + 8, ay + 76)], fill=INK,
               width=sc(3))
        if kind == "cn":
            d.rectangle(box(fx + 8, ay + 76, fx + 26, ay + 88),
                        fill=(179, 58, 58))
            d.ellipse(box(fx + 11, ay + 78, fx + 16, ay + 83), fill=GOLD)
        elif kind == "ru":
            d.rectangle(box(fx + 8, ay + 76, fx + 26, ay + 80), fill=WHITE)
            d.rectangle(box(fx + 8, ay + 80, fx + 26, ay + 84),
                        fill=(46, 111, 176))
            d.rectangle(box(fx + 8, ay + 84, fx + 26, ay + 88),
                        fill=(179, 58, 58))
        else:
            for j in range(4):
                d.rectangle(box(fx + 8, ay + 76 + j * 3, fx + 26,
                                ay + 76 + j * 3 + 3),
                            fill=(179, 58, 58) if j % 2 == 0 else WHITE)
            d.rectangle(box(fx + 8, ay + 76, fx + 15, ay + 82),
                        fill=(46, 111, 176))
    flag(ax + 96, "cn")
    flag(ax + 142, "ru")
    flag(ax + 188, "us")

# ---------------------------------------------------------------- mid art
# Ten distinct flat-vector scenes, one per mid card. Each draws
# inside (ax, ay, aw, ah) = a 176x58 box. Bold shapes only: at this
# size a scene needs three to six elements, nothing smaller than a
# few pixels, no text below 8 px.

def scene_cop31(d, ax, ay, aw, ah):
    """COP31: a globe on the left, two smokestacks with grey smoke
    on the right, a small gold sun above them."""
    d.rectangle(box(ax, ay, ax + aw, ay + ah),
                fill=tint(REGIONS["Global"], 0.90))
    # globe (shifted right so the numbered badge does not cover it)
    cx, cy, r = ax + 42, ay + 32, 20
    d.ellipse(box(cx - r, cy - r, cx + r, cy + r), fill=(110, 160, 195),
              outline=INK, width=sc(2))
    d.polygon([pt(cx - 14, cy - 8), pt(cx - 2, cy - 14), pt(cx + 6, cy - 6),
               pt(cx - 2, cy + 2), pt(cx - 12, cy + 2)], fill=(86, 160, 90))
    d.polygon([pt(cx + 4, cy + 8), pt(cx + 14, cy + 4), pt(cx + 16, cy + 12),
               pt(cx + 6, cy + 16), pt(cx, cy + 12)], fill=(86, 160, 90))
    # sun
    d.ellipse(box(ax + 148, ay + 6, ax + 162, ay + 20), fill=GOLD,
              outline=GOLD_DARK, width=sc(2))
    # two smokestacks with smoke (v3.1: INK outlines so the grey
    # stacks read against the pale sky instead of melting into it)
    for sx in (96, 122):
        d.rectangle(box(ax + sx, ay + 22, ax + sx + 18, ay + ah - 6),
                    fill=(120, 124, 132), outline=INK, width=sc(2))
        d.rectangle(box(ax + sx - 2, ay + 18, ax + sx + 20, ay + 22),
                    fill=(90, 94, 102), outline=INK, width=sc(2))
    for (sx, sy, sr) in ((105, 12, 5), (114, 7, 4), (131, 12, 5),
                         (140, 7, 4)):
        d.ellipse(box(ax + sx - sr, ay + sy - sr, ax + sx + sr, ay + sy + sr),
                  fill=(170, 174, 182))
    # ground line
    d.line([pt(ax + 8, ay + ah - 6), pt(ax + aw - 8, ay + ah - 6)],
           fill=INK, width=sc(2))


def scene_gaza(d, ax, ay, aw, ah):
    """Gaza: a white negotiating table in the middle, two figures
    seated at it in back view (one with a headscarf), a small blue
    flag and a document on the table, tent silhouettes behind."""
    d.rectangle(box(ax, ay, ax + aw, ay + ah),
                fill=tint(REGIONS["Middle East"], 0.88))
    # tent silhouettes at the back (v3.1: darker, the old pale
    # tents were barely visible on the tinted background)
    for tx in (12, 44, 128):
        d.polygon([pt(ax + tx, ay + 34), pt(ax + tx + 12, ay + 16),
                   pt(ax + tx + 24, ay + 34)], fill=(184, 164, 118))
    # table
    d.rectangle(box(ax + 52, ay + 34, ax + aw - 52, ay + 40), fill=WHITE,
                outline=INK, width=sc(2))
    d.line([pt(ax + 58, ay + 40), pt(ax + 58, ay + 52)], fill=INK,
           width=sc(3))
    d.line([pt(ax + aw - 58, ay + 40), pt(ax + aw - 58, ay + 52)],
           fill=INK, width=sc(3))
    # document on the table
    d.rectangle(box(ax + 82, ay + 28, ax + 94, ay + 34), fill=WHITE,
                outline=GREY, width=sc(2))
    # small blue flag on the table
    d.line([pt(ax + 104, ay + 34), pt(ax + 104, ay + 20)], fill=INK,
           width=sc(2))
    d.rectangle(box(ax + 104, ay + 20, ax + 116, ay + 27),
                fill=(46, 111, 176))
    # two seated figures, backs to the viewer
    for fx in (62, 116):
        d.ellipse(box(ax + fx - 6, ay + 18, ax + fx + 6, ay + 30),
                  fill=(52, 44, 38))
        d.polygon([pt(ax + fx - 10, ay + 34), pt(ax + fx + 10, ay + 34),
                   pt(ax + fx + 7, ay + 30), pt(ax + fx - 7, ay + 30)],
                  fill=(40, 52, 74))
    # headscarf on the left figure
    d.polygon([pt(ax + 56, ay + 20), pt(ax + 68, ay + 20),
               pt(ax + 66, ay + 30), pt(ax + 58, ay + 30)],
              fill=(196, 178, 140))


def scene_drones(d, ax, ay, aw, ah):
    """Russia fires drones: a night sky, three drone silhouettes
    with dotted flight paths, a city skyline at the bottom with lit
    windows, one orange interception burst."""
    d.rectangle(box(ax, ay, ax + aw, ay + ah), fill=(44, 56, 76))
    # stars
    for (sx, sy) in ((20, 8), (60, 14), (100, 6), (150, 12), (168, 20)):
        d.ellipse(box(ax + sx, ay + sy, ax + sx + 2, ay + sy + 2),
                  fill=WHITE)
    # city skyline at the bottom
    for (bx, bw, bh) in ((6, 26, 18), (36, 20, 26), (60, 30, 14),
                         (94, 22, 24), (120, 28, 16), (152, 20, 22)):
        d.rectangle(box(ax + bx, ay + ah - bh, ax + bx + bw, ay + ah),
                    fill=(24, 30, 44))
    for (wx, wy) in ((14, 44), (44, 38), (102, 40), (130, 44), (158, 40)):
        d.rectangle(box(ax + wx, ay + wy, ax + wx + 4, ay + wy + 5),
                    fill=GOLD)
    # three drones with dotted paths (v3.1: thicker dashes + rotors)
    for (dx, dy, px, py) in ((34, 14, 20, 30), (86, 10, 70, 28),
                             (138, 16, 122, 32)):
        dashed(d, ax + px, ay + py, ax + dx, ay + dy, WHITE, width=2,
               steps=8)
        d.ellipse(box(ax + dx - 5, ay + dy - 2, ax + dx + 5, ay + dy + 2),
                  fill=(200, 204, 212))
        d.line([pt(ax + dx - 9, ay + dy - 3), pt(ax + dx + 9, ay + dy - 3)],
               fill=(200, 204, 212), width=sc(2))
    # interception burst near the middle drone
    starburst(d, ax + 108, ay + 22, 7, (217, 123, 41))


def scene_bangladesh(d, ax, ay, aw, ah):
    """Bangladesh: a garment factory floor. Two sewing machines on
    tables, two workers seated at them in back view, and a small
    wall sign with the real wage demand, Tk 30,000."""
    d.rectangle(box(ax, ay, ax + aw, ay + ah),
                fill=tint(REGIONS["Asia"], 0.88))
    # wall sign with the wage demand (real, sourced figure)
    d.rectangle(box(ax + 118, ay + 6, ax + 168, ay + 20), fill=WHITE,
                outline=BRICK, width=sc(2))
    f_sign = F(FONT_SANS_B, 8)
    d.text(pt(ax + 122, ay + 8), "Tk 30,000", font=f_sign, fill=BRICK)
    # two sewing machines on tables
    for tx in (14, 66):
        d.rectangle(box(ax + tx, ay + 34, ax + tx + 44, ay + 38),
                    fill=(120, 96, 66))
        d.line([pt(ax + tx + 4, ay + 38), pt(ax + tx + 4, ay + 52)],
               fill=(120, 96, 66), width=sc(3))
        d.line([pt(ax + tx + 40, ay + 38), pt(ax + tx + 40, ay + 52)],
               fill=(120, 96, 66), width=sc(3))
        d.rectangle(box(ax + tx + 8, ay + 24, ax + tx + 36, ay + 34),
                    fill=(52, 56, 66))
        d.rectangle(box(ax + tx + 30, ay + 18, ax + tx + 36, ay + 24),
                    fill=(52, 56, 66))
    # two workers, backs to the viewer
    for fx in (26, 78):
        d.ellipse(box(ax + fx - 6, ay + 26, ax + fx + 6, ay + 38),
                  fill=(52, 44, 38))
        d.polygon([pt(ax + fx - 10, ay + 52), pt(ax + fx + 10, ay + 52),
                   pt(ax + fx + 7, ay + 38), pt(ax + fx - 7, ay + 38)],
                  fill=(168, 50, 50))
    # headscarf on the left worker
    d.polygon([pt(ax + 20, ay + 28), pt(ax + 32, ay + 28),
               pt(ax + 30, ay + 38), pt(ax + 22, ay + 38)],
              fill=(212, 168, 56))
    # fabric roll on the floor
    d.ellipse(box(ax + 140, ay + 40, ax + 168, ay + 52), fill=(46, 111, 176),
              outline=INK, width=sc(2))


def scene_gta(d, ax, ay, aw, ah):
    """GTA VI: a game shop at midnight. Striped awning, a gold VI
    sign over the door, a queue of three silhouettes in front, and
    a clock showing midnight."""
    d.rectangle(box(ax, ay, ax + aw, ay + ah), fill=(38, 48, 66))
    # shopfront: awning + wall + door
    for i in range(6):
        d.rectangle(box(ax + 8 + i * 26, ay + 8, ax + 8 + (i + 1) * 26,
                        ay + 18),
                    fill=(179, 58, 58) if i % 2 == 0 else WHITE)
    d.rectangle(box(ax + 8, ay + 18, ax + 164, ay + 48), fill=(96, 84, 66))
    # gold VI sign over the door
    f_vi = F(FONT_SERIF_B, 16)
    d.text(pt(ax + 74, ay + 20), "VI", font=f_vi, fill=GOLD)
    # door, glowing
    d.rectangle(box(ax + 66, ay + 34, ax + 96, ay + 48), fill=GOLD,
                outline=INK, width=sc(2))
    # clock showing midnight, top right
    d.ellipse(box(ax + 140, ay + 24, ax + 164, ay + 48), fill=WHITE,
              outline=INK, width=sc(2))
    d.line([pt(ax + 152, ay + 36), pt(ax + 152, ay + 27)], fill=INK,
           width=sc(3))
    d.line([pt(ax + 152, ay + 36), pt(ax + 152, ay + 27)], fill=INK,
           width=sc(3))
    # queue of three silhouettes, backs to the viewer
    for fx in (30, 56, 118):
        d.ellipse(box(ax + fx - 5, ay + 40, ax + fx + 5, ay + 50),
                  fill=(20, 24, 34))
        d.polygon([pt(ax + fx - 8, ay + 56), pt(ax + fx + 8, ay + 56),
                   pt(ax + fx + 6, ay + 50), pt(ax + fx - 6, ay + 50)],
                  fill=(20, 24, 34))


def scene_ecdc(d, ax, ay, aw, ah):
    """ECDC: a laboratory bench with a microscope, three vials of
    coloured liquid and a petri dish with culture dots."""
    d.rectangle(box(ax, ay, ax + aw, ay + ah),
                fill=tint(REGIONS["Europe"], 0.88))
    # bench
    d.rectangle(box(ax + 8, ay + 38, ax + aw - 8, ay + 44), fill=(120, 96, 66))
    d.line([pt(ax + 14, ay + 44), pt(ax + 14, ay + 54)], fill=(120, 96, 66),
           width=sc(3))
    d.line([pt(ax + aw - 14, ay + 44), pt(ax + aw - 14, ay + 54)],
           fill=(120, 96, 66), width=sc(3))
    # microscope (base + arm + tube + stage)
    d.rectangle(box(ax + 20, ay + 34, ax + 44, ay + 38), fill=INK)
    d.rectangle(box(ax + 40, ay + 14, ax + 44, ay + 34), fill=INK)
    d.line([pt(ax + 42, ay + 14), pt(ax + 54, ay + 20)], fill=INK,
           width=sc(3))
    d.rectangle(box(ax + 52, ay + 18, ax + 58, ay + 24), fill=INK)
    d.rectangle(box(ax + 24, ay + 30, ax + 40, ay + 34), fill=GREY)
    # three vials with coloured liquid
    for (vx, col) in ((72, (179, 58, 58)), (88, (46, 125, 79)),
                      (104, (217, 123, 41))):
        d.rectangle(box(ax + vx, ay + 18, ax + vx + 10, ay + 38),
                    fill=WHITE, outline=INK, width=sc(2))
        d.rectangle(box(ax + vx + 1, ay + 28, ax + vx + 9, ay + 37),
                    fill=col)
        d.rectangle(box(ax + vx + 2, ay + 14, ax + vx + 8, ay + 18),
                    fill=INK)
    # petri dish with culture dots
    d.ellipse(box(ax + 126, ay + 20, ax + 156, ay + 38), fill=WHITE,
              outline=INK, width=sc(2))
    for (px, py) in ((134, 26), (142, 30), (148, 25), (138, 33), (146, 33)):
        d.ellipse(box(ax + px, ay + py, ax + px + 3, ay + py + 3),
                  fill=(179, 58, 58))


def scene_australia(d, ax, ay, aw, ah):
    """Australia sanctions: a classical courthouse (pediment, four
    columns, steps) and a document with a red seal at the right."""
    d.rectangle(box(ax, ay, ax + aw, ay + ah),
                fill=tint(REGIONS["Oceania"], 0.88))
    # courthouse (v3.1: darker pediment so the white columns read)
    d.polygon([pt(ax + 14, ay + 22), pt(ax + 66, ay + 6),
               pt(ax + 118, ay + 22)], fill=(186, 166, 124),
              outline=INK)
    d.ellipse(box(ax + 60, ay + 12, ax + 72, ay + 20), fill=GOLD)
    for cx in (24, 48, 72, 96):
        d.rectangle(box(ax + cx, ay + 22, ax + cx + 8, ay + 44), fill=WHITE,
                    outline=INK, width=sc(2))
    d.rectangle(box(ax + 10, ay + 44, ax + 122, ay + 48), fill=(196, 178, 140))
    d.rectangle(box(ax + 6, ay + 48, ax + 126, ay + 52), fill=(178, 160, 122))
    # document with a red seal, bottom right
    d.rectangle(box(ax + 132, ay + 28, ax + 168, ay + 52), fill=WHITE,
                outline=INK, width=sc(2))
    d.line([pt(ax + 137, ay + 34), pt(ax + 163, ay + 34)], fill=GREY,
           width=sc(2))
    d.line([pt(ax + 137, ay + 39), pt(ax + 163, ay + 39)], fill=GREY,
           width=sc(2))
    d.ellipse(box(ax + 140, ay + 42, ax + 152, ay + 52), fill=BRICK)
    d.text(pt(ax + 144, ay + 44), "§", font=F(FONT_SANS_B, 8), fill=WHITE)


def scene_voyager(d, ax, ay, aw, ah):
    """Voyager 1: deep space, stars, the gold probe with its big
    dish and long boom, and a dotted trajectory curving away."""
    d.rectangle(box(ax, ay, ax + aw, ay + ah), fill=(16, 24, 44))
    # stars
    for (sx, sy) in ((10, 8), (30, 20), (52, 6), (76, 14), (120, 8),
                     (150, 18), (166, 6), (140, 40), (18, 44)):
        d.ellipse(box(ax + sx, ay + sy, ax + sx + 2, ay + sy + 2),
                  fill=WHITE)
    # dotted trajectory (v3.1: 2 px — the old 1 px dots vanished)
    dashed(d, ax + 8, ay + 50, ax + 150, ay + 12, (120, 128, 142),
           width=2, steps=16)
    # probe body (gold hexagon) + big dish + boom
    d.polygon([pt(ax + 92, ay + 22), pt(ax + 104, ay + 16),
               pt(ax + 116, ay + 22), pt(ax + 116, ay + 34),
               pt(ax + 104, ay + 40), pt(ax + 92, ay + 34)], fill=GOLD)
    d.ellipse(box(ax + 112, ay + 10, ax + 138, ay + 36), fill=WHITE,
              outline=(200, 204, 212), width=sc(2))
    d.line([pt(ax + 104, ay + 28), pt(ax + 124, ay + 28)], fill=WHITE,
           width=sc(3))
    d.line([pt(ax + 92, ay + 28), pt(ax + 74, ay + 20)], fill=GOLD,
           width=sc(3))
    d.ellipse(box(ax + 70, ay + 18, ax + 76, ay + 24), fill=GOLD)


def scene_haiti(d, ax, ay, aw, ah):
    """Haiti: a helicopter over a hillside mansion, a smoke plume
    rising from the house, a palm tree on the left."""
    d.rectangle(box(ax, ay, ax + aw, ay + ah),
                fill=tint(REGIONS["Americas"], 0.90))
    # hillside
    d.polygon([pt(ax, ay + ah), pt(ax, ay + 40), pt(ax + 70, ay + 26),
               pt(ax + aw, ay + 34), pt(ax + aw, ay + ah)],
              fill=(140, 160, 100))
    # mansion on the hill (white, columns, red roof)
    d.polygon([pt(ax + 96, ay + 22), pt(ax + 128, ay + 12),
               pt(ax + 160, ay + 22)], fill=(179, 58, 58))
    d.rectangle(box(ax + 100, ay + 22, ax + 156, ay + 38), fill=WHITE,
                outline=INK, width=sc(2))
    for cx in (106, 122, 138):
        d.line([pt(ax + cx, ay + 24), pt(ax + cx, ay + 36)], fill=GREY,
               width=sc(2))
    # smoke plume from the mansion
    for (sx, sy, sr) in ((128, 8, 5), (134, 3, 4), (120, 4, 3)):
        d.ellipse(box(ax + sx - sr, ay + sy - sr, ax + sx + sr, ay + sy + sr),
                  fill=(120, 124, 132))
    # helicopter above, with motion lines
    d.ellipse(box(ax + 30, ay + 8, ax + 58, ay + 18), fill=(52, 56, 66))
    d.line([pt(ax + 18, ay + 10), pt(ax + 70, ay + 10)], fill=INK,
           width=sc(3))
    d.line([pt(ax + 58, ay + 12), pt(ax + 72, ay + 18)], fill=(52, 56, 66),
           width=sc(3))
    d.line([pt(ax + 30, ay + 20), pt(ax + 30, ay + 24)], fill=INK,
           width=sc(2))
    d.line([pt(ax + 44, ay + 20), pt(ax + 44, ay + 24)], fill=INK,
           width=sc(2))
    # palm tree, left foreground
    d.line([pt(ax + 14, ay + 52), pt(ax + 14, ay + 34)], fill=(96, 68, 48),
           width=sc(3))
    for (dx, dy) in ((-8, -4), (8, -4), (-6, 2), (6, 2)):
        d.line([pt(ax + 14, ay + 34), pt(ax + 14 + dx, ay + 34 + dy)],
               fill=(46, 125, 79), width=sc(3))


def scene_horn(d, ax, ay, aw, ah):
    """Ethiopia–Eritrea: arid mountain ridges, a dirt road with two
    military trucks carrying small flags, a low sun."""
    d.rectangle(box(ax, ay, ax + aw, ay + ah),
                fill=tint(REGIONS["Africa"], 0.90))
    # sun
    d.ellipse(box(ax + 148, ay + 4, ax + 162, ay + 18), fill=GOLD)
    # two mountain ridges
    d.polygon([pt(ax, ay + 34), pt(ax + 30, ay + 12), pt(ax + 60, ay + 34),
               pt(ax + 90, ay + 18), pt(ax + 120, ay + 34),
               pt(ax + 150, ay + 20), pt(ax + aw, ay + 34)],
              fill=(178, 150, 110))
    d.polygon([pt(ax, ay + 44), pt(ax + 40, ay + 26), pt(ax + 80, ay + 44),
               pt(ax + 120, ay + 28), pt(ax + aw, ay + 44)],
              fill=(150, 122, 84))
    # dirt road
    d.polygon([pt(ax, ay + ah), pt(ax + 20, ay + 46), pt(ax + aw - 20, ay + 46),
               pt(ax + aw, ay + ah)], fill=(196, 172, 128))
    # two trucks with small flags (v3.1: INK outlines so the dark
    # trucks read against the road instead of blurring into it)
    for (tx, flag_col) in ((34, (46, 125, 79)), (104, (179, 58, 58))):
        d.rectangle(box(ax + tx, ay + 38, ax + tx + 26, ay + 48),
                    fill=(72, 86, 52), outline=INK, width=sc(1))
        d.rectangle(box(ax + tx + 16, ay + 32, ax + tx + 26, ay + 38),
                    fill=(72, 86, 52), outline=INK, width=sc(1))
        d.ellipse(box(ax + tx + 4, ay + 48, ax + tx + 10, ay + 54),
                  fill=INK)
        d.ellipse(box(ax + tx + 16, ay + 48, ax + tx + 22, ay + 54),
                  fill=INK)
        d.line([pt(ax + tx + 4, ay + 32), pt(ax + tx + 4, ay + 24)],
               fill=INK, width=sc(2))
        d.rectangle(box(ax + tx + 4, ay + 24, ax + tx + 14, ay + 29),
                    fill=flag_col)

# ---------------------------------------------------------------- world map
# Hand-authored simplified continent polygons, equirectangular.
# Panel (1024 units): x24..x560, y784..y940 (536x156). v4: the map
# is 24 px shorter than v3 so the taller mid cards fit above it.
MAP_X, MAP_Y, MAP_W, MAP_H = 24, 784, 536, 156

CONTINENTS = [
    ("Americas", [(-168, 66), (-158, 71), (-140, 70), (-128, 71),
                  (-115, 68), (-100, 68), (-90, 66), (-85, 66), (-80, 70),
                  (-75, 68), (-65, 62), (-60, 58), (-55, 52), (-60, 47),
                  (-65, 44), (-70, 42), (-75, 39), (-76, 35), (-80, 32),
                  (-81, 26), (-84, 30), (-89, 29), (-91, 19), (-97, 26),
                  (-97, 16), (-94, 17), (-90, 14), (-86, 13), (-83, 9),
                  (-80, 8), (-79, 9), (-83, 10), (-88, 15), (-92, 15),
                  (-97, 16), (-102, 18), (-105, 20), (-110, 23), (-114, 28),
                  (-117, 33), (-122, 37), (-124, 42), (-124, 48), (-128, 50),
                  (-133, 56), (-140, 60), (-148, 61), (-155, 58),
                  (-162, 55), (-168, 66)]),
    ("Americas", [(-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74),
                  (-25, 78), (-35, 80), (-50, 78), (-58, 75), (-55, 70),
                  (-52, 64), (-48, 60)]),  # Greenland
    ("Americas", [(-79, 9), (-77, 7), (-75, 10), (-72, 12), (-64, 10),
                  (-60, 8), (-55, 6), (-52, 4), (-50, 0), (-48, -2),
                  (-44, -3), (-41, -5), (-37, -6), (-35, -9), (-38, -15),
                  (-40, -22), (-46, -24), (-48, -28), (-52, -32),
                  (-57, -38), (-62, -41), (-65, -45), (-67, -50),
                  (-69, -52), (-71, -54), (-73, -50), (-73, -44),
                  (-73, -37), (-72, -30), (-70, -23), (-70, -18),
                  (-75, -15), (-78, -8), (-81, -5), (-81, -1), (-80, 2),
                  (-79, 6)]),
    ("Africa", [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15),
                (-15, 11), (-13, 8), (-8, 5), (-4, 5), (0, 6), (6, 4),
                (9, 4), (9, -1), (12, -5), (13, -12), (12, -17), (14, -22),
                (16, -28), (18, -32), (20, -35), (25, -34), (28, -33),
                (31, -29), (33, -26), (35, -22), (36, -18), (40, -15),
                (40, -10), (42, -4), (46, -1), (51, 2), (51, 11), (48, 11),
                (44, 11), (43, 12), (40, 15), (38, 18), (37, 22), (35, 28),
                (34, 31), (32, 31), (28, 32), (22, 33), (15, 33), (11, 34),
                (10, 37), (5, 37), (0, 36), (-6, 35)]),
    ("Africa", [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24),
                (45, -25), (43, -22), (43, -18)]),  # Madagascar
    ("Europe", [(-10, 36), (-9, 37), (-9, 43), (-4, 44), (-2, 47), (-1, 49),
                (0, 50), (2, 51), (4, 53), (6, 53), (8, 55), (8, 57),
                (10, 59), (12, 56), (15, 56), (18, 56), (21, 55), (21, 57),
                (24, 58), (24, 60), (28, 60), (30, 61), (30, 64), (30, 68),
                (28, 71), (24, 71), (20, 70), (18, 69), (15, 67), (12, 65),
                (10, 62), (5, 60), (5, 58), (8, 57), (10, 55), (8, 54),
                (4, 53), (0, 51), (-2, 50), (-5, 50), (-5, 48), (-2, 47),
                (-4, 44), (-9, 43), (-10, 38)]),
    ("Europe", [(-5, 50), (-4, 53), (-5, 56), (-3, 58), (-1, 57), (0, 54),
                (1, 51), (-2, 50)]),  # Britain
    ("Asia", [(28, 41), (30, 36), (33, 36), (36, 36), (40, 37), (43, 40),
              (46, 42), (49, 44), (52, 46), (56, 47), (60, 45), (64, 45),
              (68, 46), (70, 52), (73, 58), (76, 64), (79, 69), (83, 73),
              (90, 75), (97, 76), (104, 77), (111, 75), (118, 73),
              (125, 72), (133, 71), (141, 72), (150, 71), (158, 69),
              (162, 65), (160, 60), (156, 53), (150, 51), (143, 49),
              (141, 44), (138, 39), (134, 34), (130, 32), (127, 34),
              (124, 32), (121, 28), (118, 25), (112, 22), (109, 19),
              (108, 12), (106, 10), (104, 9), (101, 7), (99, 9), (98, 13),
              (97, 16), (94, 17), (92, 21), (89, 22), (87, 21), (85, 19),
              (82, 17), (80, 14), (78, 9), (77, 8), (75, 10), (73, 16),
              (71, 20), (68, 22), (65, 25), (62, 25), (59, 25), (57, 26),
              (54, 26), (52, 27), (50, 29), (48, 30), (46, 30), (44, 29),
              (42, 31), (40, 32), (37, 33), (35, 33), (33, 34), (30, 36)]),
    ("Asia", [(130, 31), (132, 33), (134, 34), (137, 35), (139, 37),
              (141, 40), (142, 43), (144, 44), (142, 42), (140, 39),
              (138, 36), (135, 34), (132, 33), (130, 31)]),  # Japan
    ("Asia", [(95, 6), (98, 4), (101, 1), (104, -2), (106, -6), (103, -6),
              (100, -2), (97, 2), (95, 6)]),  # Sumatra
    ("Asia", [(109, 1), (112, 4), (116, 4), (119, 1), (117, -3), (113, -4),
              (110, -2), (109, 1)]),  # Borneo
    ("Asia", [(105, -6), (109, -7), (113, -7), (114, -8), (110, -8),
              (106, -7), (105, -6)]),  # Java
    ("Asia", [(131, -1), (135, -2), (139, -3), (141, -4), (141, -8),
              (137, -8), (133, -5), (131, -1)]),  # New Guinea
    ("Oceania", [(113, -22), (114, -28), (115, -33), (115, -35), (118, -35),
                 (121, -34), (124, -33), (129, -32), (132, -32), (134, -33),
                 (136, -35), (138, -35), (140, -38), (142, -38), (145, -38),
                 (147, -39), (150, -37), (153, -32), (153, -27), (152, -24),
                 (150, -22), (148, -20), (146, -19), (143, -15), (142, -11),
                 (141, -13), (139, -17), (136, -15), (135, -12), (132, -12),
                 (130, -13), (128, -14), (126, -14), (124, -15), (122, -17),
                 (120, -19), (117, -20), (114, -21)]),
    ("Oceania", [(167, -45), (169, -43), (171, -42), (173, -41), (175, -38),
                 (177, -38), (176, -40), (174, -41), (172, -43), (170, -44),
                 (167, -45)]),  # New Zealand
]


def map_xy(lon, lat):
    """Equirectangular projection into map-panel coordinates."""
    return (MAP_X + (lon + 180.0) / 360.0 * MAP_W,
            MAP_Y + (90.0 - lat) / 180.0 * MAP_H)


# Numbered dots: (story no., lon, lat, dx, dy) — dx/dy are small manual
# nudges (map px) so crowded dots do not touch. The Europe / Middle
# East cluster (Kyiv, Kerch, Gaza, Antalya, Stockholm) is nudged
# apart; a hairline joins each nudged dot to its true spot.
# Story 13 (Voyager 1) has no place on Earth: it is marked in the
# deep-space inset at the bottom right of the panel instead.
DOTS_NUM = [
    (1, 50.5, 26.2, 0, 0), (2, 36.5, 45.3, 10, -6),
    (3, 114.1, 22.5, 0, 0), (4, 30.7, 36.9, -14, -4),
    (5, 34.5, 31.5, -8, -4), (6, 30.5, 50.4, -12, -10),
    (7, 90.4, 23.8, 0, 0), (8, 174.8, -36.9, -8, 0),
    (9, 18.1, 59.3, -6, -8), (10, 149.1, -35.3, 0, 0),
    (11, -72.3, 18.5, 0, 0), (12, 37.9, 14.7, 0, 0),
]
# Brief dots: (lon, lat, dx, dy, region), in the same order as
# BRIEFS (24 now — the 7 dropped briefs' dots were removed too).
DOTS_BRIEF = [
    (-0.1, 51.5, 10, 10, "Europe"), (26.1, 44.4, 0, 0, "Europe"),
    (-77.0, -10.0, 0, 0, "Americas"),
    (45.0, 12.8, 8, 0, "Middle East"),
    (56.0, 26.0, 6, -6, "Middle East"), (116.4, 39.9, 0, 0, "Asia"),
    (121.0, 14.6, 0, 0, "Asia"), (22.7, 48.4, -10, -8, "Europe"),
    (37.6, 55.8, 0, 0, "Europe"),
    (80.3, 15.9, 0, 0, "Asia"), (-160.0, -10.5, 0, 0, "Oceania"),
    (44.2, 15.3, 0, 0, "Middle East"), (-122.4, 37.8, -10, -10, "Americas"),
    (29.5, 1.0, 0, 0, "Africa"), (-46.0, -4.5, 0, 0, "Americas"),
    (145.8, -5.2, 0, 0, "Oceania"), (7.5, 9.1, 0, -7, "Africa"),
    (96.0, 21.0, 8, 8, "Asia"), (7.0, 4.8, 0, 0, "Africa"),
    (30.4, 13.2, 0, 0, "Africa"), (-0.1, 51.5, -10, -8, "Europe"),
    (4.35, 50.85, 0, 14, "Europe"), (-75.7, 45.4, -10, -6, "Americas"),
    (7.5, 9.1, 7, 7, "Africa"),
]
NUM_REGION = {1: "Middle East", 2: "Europe", 3: "Asia", 4: "Global",
              5: "Middle East", 6: "Europe", 7: "Asia", 8: "Global",
              9: "Europe", 10: "Oceania", 11: "Americas", 12: "Africa"}


def check_dots():
    """Fail the build if any map dots would touch or overlap."""
    pts = []
    for n, lon, lat, dx, dy in DOTS_NUM:
        x, y = map_xy(lon, lat)
        pts.append((x + dx, y + dy, 5.0, "num %d" % n))
    for lon, lat, dx, dy, _reg in DOTS_BRIEF:
        x, y = map_xy(lon, lat)
        pts.append((x + dx, y + dy, 2.0, "brief"))
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            x1, y1, r1, l1 = pts[i]
            x2, y2, r2, l2 = pts[j]
            dist = math.hypot(x1 - x2, y1 - y2)
            need = r1 + r2 + 0.5
            assert dist >= need, "map dots too close: %s vs %s (%.1f < %.1f)" \
                % (l1, l2, dist, need)


def draw_map(d):
    rounded_rect(d, [MAP_X, MAP_Y, MAP_X + MAP_W, MAP_Y + MAP_H], radius=8,
                 fill=SEA, outline=INK, width=2)
    for region, poly in CONTINENTS:
        pts = [pt(*map_xy(lon, lat)) for lon, lat in poly]
        d.polygon(pts, fill=tint(REGIONS[region], 0.55),
                  outline=REGIONS[region])
    hair = (150, 140, 120)
    for n, lon, lat, dx, dy in DOTS_NUM:
        x0, y0 = map_xy(lon, lat)
        x, y = x0 + dx, y0 + dy
        if math.hypot(dx, dy) >= 8:
            d.line([pt(x, y), pt(x0, y0)], fill=hair, width=sc(2))
            d.ellipse(box(x0 - 2, y0 - 2, x0 + 2, y0 + 2), fill=hair)
        col = REGIONS[NUM_REGION[n]]
        d.ellipse(box(x - 5, y - 5, x + 5, y + 5), fill=col, outline=WHITE,
                  width=2)
        f_n = F(FONT_SANS_B, 8)
        num = str(n)
        d.text((sc(x) - d.textlength(num, font=f_n) / 2, sc(y - 4.5)), num,
               font=f_n, fill=WHITE)
    for lon, lat, dx, dy, region in DOTS_BRIEF:
        x0, y0 = map_xy(lon, lat)
        x, y = x0 + dx, y0 + dy
        if math.hypot(dx, dy) >= 8:
            d.line([pt(x, y), pt(x0, y0)], fill=hair, width=sc(2))
            d.ellipse(box(x0 - 2, y0 - 2, x0 + 2, y0 + 2), fill=hair)
        d.ellipse(box(x - 2, y - 2, x + 2, y + 2),
                  fill=REGIONS[region])
    # Deep-space inset, bottom right: story 13, Voyager 1, has no
    # place on Earth. A small dark box with a gold star and the
    # number 13 marks it over the empty southern ocean.
    ix, iy, iw, ih = MAP_X + MAP_W - 124, MAP_Y + MAP_H - 52, 116, 44
    rounded_rect(d, [ix, iy, ix + iw, iy + ih], radius=6,
                 fill=(16, 24, 44), outline=GOLD, width=2)
    starburst(d, ix + 12, iy + 12, 5, GOLD)
    f_i1 = F(FONT_SANS_B, 9)
    d.text(pt(ix + 22, iy + 6), "13 · VOYAGER 1", font=f_i1, fill=WHITE)
    f_i2 = F(FONT_SANS, 8)
    d.text(pt(ix + 22, iy + 20), "ONE LIGHT-DAY OUT", font=f_i2,
           fill=(200, 204, 212))
    d.text(pt(ix + 8, iy + 32), "25.9 BILLION KM", font=f_i2,
           fill=(200, 204, 212))


def draw_legend(d, x, y):
    """Two rows of region swatches under the map; row 2 ends with
    a note explaining the numbers and dots."""
    f_l = F(FONT_SANS, 10)
    rows = [["Europe", "Middle East", "Asia", "Africa"],
            ["Americas", "Oceania", "Global"]]
    yy = y
    for row in rows:
        xx = x
        for region in row:
            d.rectangle(box(xx, yy, xx + 8, yy + 8), fill=REGIONS[region])
            d.text(pt(xx + 11, yy - 1), region, font=f_l, fill=INK)
            xx += 11 + text_w(d, region, f_l) + 14
        if row is rows[1]:
            note = "· 1–12 heroes & mids · 13 in deep space · dots are briefs"
            d.text(pt(xx, yy - 1), note, font=f_l, fill=GREY)
        yy += 12

# ---------------------------------------------------------------- content
# Headlines were kept short on purpose so they fit the required sizes.
# Full wording and sources: see facts.md.

DECK = ("Iran widens its Gulf war, the Kerch Bridge falls, and APEC "
        "opens in Shenzhen — the world in one picture.")

HEROES = [
    # (region, art crop name or None, headline, subline).
    # Hero 3 uses a skyline-only window of the generated APEC
    # panel (hero3-apec-skyline): the full panel shows Xi shaking
    # hands with Trump, but the Trump-Xi meeting is Thursday
    # 19 Nov, not Wednesday (see the docstring) — the window keeps
    # only the Shenzhen towers, no people. art=None would fall
    # back to the v3.1 PIL scene_apec.
    ("Middle East", "hero1-gulf", "Iran widens Gulf war to Kuwait",
     "Ali Al Salem targeted; Bahrain intercepts again — ADNOC ship: "
     "1 missing, 11 hurt"),
    ("Europe", "hero2-kerch", "Kerch Bridge span falls into the sea",
     "Second day of strikes; 227m road arch collapses, traffic halted"),
    ("Asia", "hero3-apec-skyline", "APEC opens in Shenzhen",
     "Xi meets Putin in Shenzhen; Trump–Xi talks Thursday"),
]

# Mid tuple: (region, category, headline, subline, art crop name).
# Every card carries its own generated illustration on top.
MIDS = [
    ("Global", "CLIMATE", "COP31 splits on fossil fuels",
     "Draft offers two rival texts; 35-by-35 pledge", "mid4-cop31"),
    ("Middle East", "GAZA", "Gaza rebuild stalls",
     "Board warns truce may collapse; $18bn unspent", "mid5-gaza"),
    ("Europe", "UKRAINE WAR", "Russia fires 141 drones",
     "Kyiv: 126 shot down; 5 killed, 15 hurt", "mid6-drones"),
    ("Asia", "LABOUR", "Bangladesh factories shut",
     "BGMEA: 535 halted today; wage Tk 30,000 sought", "mid7-bangladesh"),
    ("Global", "GAMES", "GTA VI goes on sale",
     "Midnight rollout in New Zealand; $1.54bn preorders", "mid8-gta"),
    ("Europe", "HEALTH", "ECDC: superbugs surge",
     "Klebsiella up 72% since 2019 in Europe", "mid9-ecdc"),
    ("Oceania", "DIPLOMACY", "Australia sanctions Weiss",
     "Settler leader Weiss among 3 people, 4 groups", "mid10-australia"),
    ("Americas", "HAITI", "Troops raid gang boss home",
     "Salvadoran helicopters hit Jeff Larose mansion", "mid11-haiti"),
    ("Africa", "HORN", "Ethiopia–Eritrea troops mass",
     "Armies within striking distance; clashes at Badme", "mid12-horn"),
    ("Global", "SPACE", "Voyager 1, one light-day out",
     "First human-made object that far; 49 years on", "mid13-voyager"),
]

BRIEFS = [
    # v4: 24 briefs (v3 had 31). The 7 weakest were cut to make
    # room for the taller mid art: S.F. data-centre ban, leukaemia
    # jab (both single-source), IPL lists, Nigeria 0-0 Tanzania,
    # S. Africa summons envoy, Fed minutes (scheduled, not news),
    # Mariana quake.
    ("UK CPI:", "3.6%, a one-year high", "Europe"),
    ("Romania:", "5.3 quake in Bucharest", "Europe"),
    ("Peru:", "strong quake off the coast", "Americas"),
    ("Houthis target", "Aden airport", "Middle East"),
    ("Three US carriers", "now in the Gulf", "Middle East"),
    ("Trump hints", "at Kim meeting", "Asia"),
    ("Protests greet", "Trump in Manila", "Asia"),
    ("Hungary halts", "Ukraine rail link", "Europe"),
    ("Kremlin vows", "to rebuild bridge", "Europe"),
    ("Akvan:", "Odisha to evacuate 204,070", "Asia"),
    ("Cyclone Xavier", "hits Category 5", "Oceania"),
    ("Coalition hits", "60 Houthi targets", "Middle East"),
    ("Anthropic to price", "$1.4tn IPO", "Americas"),
    ("Ebola out", "of control, WHO warns", "Africa"),
    ("Awá emerge", "from Amazon", "Americas"),
    ("Quake shakes", "Papua New Guinea", "Oceania"),
    ("Nigeria loses", "$125bn to graft", "Africa"),
    ("ICJ to rule", "on Myanmar Thursday", "Asia"),
    ("Dangote IPO", "grows to $2.1bn", "Africa"),
    ("Amnesty:", "RSF drones killed 37", "Africa"),
    ("UK sanctions", "8 settler firms", "Europe"),
    ("Brussels proposes", "€45bn loan", "Europe"),
    ("Carney:", "China trade no worry", "Americas"),
    ("Nigeria:", "Ebola contacts cleared", "Africa"),
]

DATE_CHECK = ("DATE CHECK — Left out on purpose: first reported 17 Nov, "
              "not today: Peltola's Alaska win, Nvidia's $115.8bn "
              "quarter, the Prague train crash, Mongolia's president "
              "resigning.")
FOOTER_L2 = ("Every story happened or was first reported on Wednesday "
             "18 November 2026. Contested claims are attributed. "
             "Sources: Reuters, AP, AFP, Al Jazeera, Bloomberg.")


def build():
    check_dots()
    total = len(HEROES) + len(MIDS) + len(BRIEFS)
    assert total == 37, "story count is %d, expected 37" % total
    assert len(DOTS_BRIEF) == len(BRIEFS), "brief dots != briefs"

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- kicker line
    f_kick = F(FONT_SANS_B, 14)
    left_w = letterspaced(d, 24, 12, "THE WORLD'S NEWS IN ONE PICTURE",
                          f_kick, INK, spacing=2)
    right = "%d STORIES · 6 CONTINENTS · ONE DAY" % total
    right_w = text_w(d, right, f_kick) + 2 * (len(right) - 1)
    assert 24 + left_w + 20 <= 1000 - right_w, "kicker overlaps"
    letterspaced(d, 1000 - right_w, 12, right, f_kick, BRICK, spacing=2)

    # ---- date: largest text on the page, title case, one line
    df, dlines, dsize = fit_text(d, "Wednesday 18 November 2026",
                                 FONT_SERIF_DATE, 78, 976, 1, 66)
    assert dsize >= 66, "date shrank below 66 px"
    draw_centered(d, 512, 30, dlines[0], df, INK)

    # ---- deck line under the date, serif
    f_deck = F(FONT_SERIF, 14)
    dw = text_w(d, DECK, f_deck)
    assert dw <= 976, "deck too wide (%.0f px)" % dw
    d.text(pt(512 - dw / 2, 114), DECK, font=f_deck, fill=GREY)

    # ---- thin double rule (v3.1: 2/3 px — the old 1 px top rule
    # was barely visible)
    d.line([pt(24, 134), pt(1000, 134)], fill=INK, width=sc(2))
    d.line([pt(24, 139), pt(1000, 139)], fill=INK, width=sc(3))

    # ---- heroes: 3 cards 320x256 at y142
    for i, (region, art, headline, subline) in enumerate(HEROES):
        x, y = 24 + i * 328, 142
        rounded_rect(d, [x, y, x + 320, y + 256], radius=10, fill=CARD,
                     outline=BORDER, width=2)
        if art:
            paste_art(img, x + 6, y + 6, 308, 128, art)
        else:
            # hero 3 fallback: v3.1 PIL scene (see HEROES comment)
            scene_apec(d, x + 6, y + 6, 308, 128)
        chip(d, x + 16, y + 140, region, CHIPS[region], size=12)
        hf, hlines, hsize = fit_text(d, headline, FONT_SERIF_B, 26, 296, 2, 24)
        yy = y + 162
        for ln in hlines:
            d.text(pt(x + 12, yy), ln, font=hf, fill=INK)
            yy += hsize * 1.12
        sf, slines, ssize = fit_text(d, subline, FONT_SANS, 13, 296, 2, 12.5)
        yy += 3
        for ln in slines:
            d.text(pt(x + 12, yy), ln, font=sf, fill=GREY)
            yy += ssize * 1.18
        assert yy <= y + 254, "hero %d text overflows card (%d)" % (i + 1, yy - y)

    # ---- mids: 5 cols x 2 rows, cards 184x172 at y406 / y584.
    # v4: taller cards (was 184x152) so the art is 176x84 — 49%
    # of the card instead of 38% — and the text still fits.
    col_x = [24, 220, 416, 612, 808]
    for i, (region, category, headline, subline, art) in enumerate(MIDS):
        col_i, row_i = i % 5, i // 5
        x, y = col_x[col_i], 406 + row_i * 178
        col = REGIONS[region]
        rounded_rect(d, [x, y, x + 184, y + 172], radius=10, fill=CARD,
                     outline=BORDER, width=2)
        # generated illustration on top, full card width
        paste_art(img, x + 4, y + 4, 176, 84, art)
        # numbered badge, upper-left over the art
        bx, by = x + 16, y + 16
        d.ellipse(box(bx - 10, by - 10, bx + 10, by + 10), fill=INK)
        nf = F(FONT_SANS_B, 11)
        num = str(i + 4)
        d.text((sc(bx) - d.textlength(num, font=nf) / 2, sc(by - 6)), num,
               font=nf, fill=WHITE)
        # label, headline, description
        lf = F(FONT_SANS_B, 10)
        label = "%s · %s" % (region.upper(), category)
        lw = text_w(d, label, lf)
        assert lw <= 168, "mid %d label too wide (%.0f)" % (i + 4, lw)
        d.text(pt(x + 8, y + 92), label, font=lf, fill=col)
        hf, hlines, hsize = fit_text(d, headline, FONT_SERIF_B, 16, 168, 2, 15)
        sf, slines, ssize = fit_text(d, subline, FONT_SANS, 11.5, 168, 2, 11)
        yy = y + 104
        for ln in hlines:
            d.text(pt(x + 8, yy), ln, font=hf, fill=INK)
            yy += hsize * 1.12
        yy += 2
        for ln in slines:
            d.text(pt(x + 8, yy), ln, font=sf, fill=GREY)
            yy += ssize * 1.18
        assert yy <= y + 170, "mid %d text overflows card (%d)" \
            % (i + 4, yy - y)

    # ---- bottom: map left, briefs right
    f_bh = F(FONT_SANS_B, 15)
    letterspaced(d, 24, 764, "WHERE IT HAPPENED", f_bh, INK, spacing=2)
    letterspaced(d, 576, 764, "ALSO ON WEDNESDAY 18 NOVEMBER", f_bh, INK,
                 spacing=2)
    draw_map(d)
    draw_legend(d, 24, 946)
    f_lead = F(FONT_SANS_B, 11)
    f_rest = F(FONT_SANS, 11)
    for i, (lead, rest, _reg) in enumerate(BRIEFS):
        col_i, row_i = (0, i) if i < 12 else (1, i - 12)
        x = 576 + col_i * 218
        y = 784 + row_i * 13
        w = text_w(d, lead, f_lead) + text_w(d, " " + rest, f_rest)
        assert w <= 210, "brief %d too wide (%.0f px): %s %s" \
            % (i + 14, w, lead, rest)
        d.text(pt(x, y), lead, font=f_lead, fill=INK)
        d.text(pt(x + text_w(d, lead, f_lead), y), " " + rest,
               font=f_rest, fill=INK)

    # ---- footer: gold rule, date check, sources
    d.line([pt(24, 974), pt(1000, 974)], fill=GOLD, width=sc(3))
    ff = F(FONT_SANS, 10)
    fb = F(FONT_SANS_B, 10)
    # Date-check line in two segments: bold brick lead, then the
    # rest in regular ink (drawn once each, no overlap).
    lead = "DATE CHECK — "
    rest = DATE_CHECK[len(lead):]
    dc_w = text_w(d, lead, fb) + text_w(d, rest, ff)
    assert dc_w <= 976, "date check too wide (%.0f px)" % dc_w
    dc_x = 512 - dc_w / 2
    d.text(pt(dc_x, 982), lead, font=fb, fill=BRICK)
    d.text(pt(dc_x + text_w(d, lead, fb), 982), rest, font=ff, fill=INK)
    f2_w = text_w(d, FOOTER_L2, ff)
    assert f2_w <= 976, "footer line 2 too wide (%.0f px)" % f2_w
    d.text(pt(512 - f2_w / 2, 998), FOOTER_L2, font=ff, fill=GREY)

    out1024 = img.resize((1024, 1024), Image.LANCZOS)
    # v3.1: keep RGB, no palette quantize. The old
    # convert("P", palette=Image.ADAPTIVE, colors=256) merged
    # near-identical pastel tones, softened thin lines and washed
    # out pale fills; RGB at ~610 KB is far under the 1 MiB cap.
    out1024.save(os.path.join(HERE, "entry-1024.png"), optimize=True)
    img.save(os.path.join(HERE, "entry-2048.png"))
    import hashlib
    data = open(os.path.join(HERE, "entry-1024.png"), "rb").read()
    print("entry-1024.png: %d bytes, sha256 %s"
          % (len(data), hashlib.sha256(data).hexdigest()))
    assert len(data) <= 1048576, "entry-1024.png over 1 MiB"
    print("saved entry-1024.png and entry-2048.png")


def qa_crops():
    """Export the crops used for the visual check (not part of the repo)."""
    import pathlib
    qdir = pathlib.Path(HERE).parent / "qa"
    qdir.mkdir(exist_ok=True)
    im = Image.open(os.path.join(HERE, "entry-1024.png")).convert("RGB")
    im.crop((0, 0, 1024, 142)).save(qdir / "top150.png")
    im.crop((0, 142, 1024, 398)).save(qdir / "heroes.png")
    im.crop((0, 406, 1024, 756)).save(qdir / "mids.png")
    im.crop((0, 764, 565, 975)).save(qdir / "map.png")
    im.crop((565, 764, 1024, 975)).save(qdir / "briefs.png")
    im.crop((0, 0, 512, 512)).save(qdir / "q_tl.png")
    im.crop((512, 0, 1024, 512)).save(qdir / "q_tr.png")
    im.crop((0, 512, 512, 1024)).save(qdir / "q_bl.png")
    im.crop((512, 512, 1024, 1024)).save(qdir / "q_br.png")
    im.resize((300, 300), Image.LANCZOS).save(qdir / "small300.png")
    print("qa crops in", qdir)


if __name__ == "__main__":
    build()
    qa_crops()
