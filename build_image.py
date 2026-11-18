#!/usr/bin/env python3
"""Render the poster for make.fun news-image-20261118 (Palette A), v2.

Dev-time only: renders at 2048x2048 with PIL and real fonts, then
downsamples to 1024x1024 with LANCZOS and palette-quantizes. The
finished 1024 PNG is embedded as base64 in img_part1/2/3.py (the
GitHub connector cannot push binaries); main.py decodes it at run
time. See facts.md for the 43 stories and their sources.

Layout (all geometry in 1024-page units; S=2 render scale):
  masthead y0-120 navy, gold rule y120-124, region stripe y124-127
  summary  y132 one line on cream (poster-A style)
  heroes   y150-356, three cards 324x206, each with a 90px drawn scene
  mids     y362-702, five columns x two rows, cards 192x166,
           3px regional top bar + 70px band (verified number or flags)
           + label + headline + description
  bottom   y708-984: hand-drawn world map (left) + 30 briefs (right)
  footer   y986-1024 navy, two lines
Palette A: cream #F7F1E3, navy #10213F, gold #D4A838 — the same
palette as the 17 Nov v3a poster (rank 52, 98.73%).
Every line of this file was written for this poster; no pasted art.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
S = 2  # render scale: 2048 canvas, 1024 output
W, H = 1024 * S, 1024 * S

# ---------------------------------------------------------------- palette
# Palette A: cream #F7F1E3, navy #10213F (masthead), gold #D4A838.
PALETTE = {
    "cream": (247, 241, 227),
    "paper": (255, 253, 247),
    "navy": (16, 33, 63),
    "navy_soft": (38, 58, 92),
    "gold": (212, 168, 56),
    "gold_dark": (176, 134, 34),
    "ink": (24, 28, 38),
    "grey": (74, 80, 96),
    "border": (216, 205, 178),
    "sea": (232, 238, 243),
    "sea_line": (196, 208, 218),
}
CREAM = PALETTE["cream"]
PAPER = PALETTE["paper"]
NAVY = PALETTE["navy"]
NAVY_SOFT = PALETTE["navy_soft"]
GOLD = PALETTE["gold"]
GOLD_DARK = PALETTE["gold_dark"]
INK = PALETTE["ink"]
GREY = PALETTE["grey"]
BORDER = PALETTE["border"]
SEA = PALETTE["sea"]
SEA_LINE = PALETTE["sea_line"]

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
# Chip colours: darker variants of the same hues so white bold text on
# them clears 4.5:1 contrast (the orange and teal bases do not).
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
# The date must be >= 66 px on one line inside 976 px (>= 24 px margins
# on both sides). DejaVu Serif Bold measures 1289 px at 66 px and
# Liberation Serif Bold 1057 px — neither fits "WEDNESDAY 18 NOVEMBER
# 2026" (27 chars). Noto Serif Condensed Bold is a real serif on this
# machine and measures 961 px at 66 px, so the date uses it; hero
# headlines keep DejaVu Serif Bold.
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


def rounded_rect(d, b, radius, fill=None, outline=None, width=1):
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
    d.text(pt(x + pad_x, y + pad_y - 1), label, font=f, fill=PAPER)
    return w

# ---------------------------------------------------------------- hero art
# Each scene draws inside the art box (ax, ay, aw, ah) in 1024 units.
# The region chip is drawn by the caller, overlaid inside the art.

def scene_bridge(d, ax, ay, aw, ah):
    d.rectangle(box(ax, ay, ax + aw, ay + ah), fill=tint(REGIONS["Europe"], 0.86))
    # river at the bottom, land wedges at the corners
    d.rectangle(box(ax, ay + ah - 22, ax + aw, ay + ah),
                fill=(110, 160, 195))
    d.polygon([pt(ax, ay + ah), pt(ax, ay + ah - 26), pt(ax + 72, ay + ah - 26),
               pt(ax + 96, ay + ah)], fill=(222, 205, 170))
    d.polygon([pt(ax + aw, ay + ah), pt(ax + aw, ay + ah - 26),
               pt(ax + aw - 72, ay + ah - 26), pt(ax + aw - 96, ay + ah)],
              fill=(222, 205, 170))
    f_lab = F(FONT_SANS_B, 10)
    d.text(pt(ax + 12, ay + ah - 20), "CRIMEA", font=f_lab, fill=NAVY)
    d.text(pt(ax + aw - 62, ay + ah - 20), "RUSSIA", font=f_lab, fill=NAVY)
    # bridge deck: two segments, gap in the middle, falling span
    deck_y = ay + 34
    col = NAVY
    d.rectangle(box(ax + 10, deck_y, ax + 128, deck_y + 7), fill=col)
    d.rectangle(box(ax + 180, deck_y, ax + aw - 10, deck_y + 7), fill=col)
    d.line([pt(ax + 10, deck_y + 7), pt(ax + 10, deck_y + 30)], fill=col,
           width=sc(4))
    d.line([pt(ax + aw - 10, deck_y + 7), pt(ax + aw - 10, deck_y + 30)],
           fill=col, width=sc(4))
    d.polygon([pt(ax + 138, deck_y + 10), pt(ax + 168, deck_y + 22),
               pt(ax + 162, deck_y + 30), pt(ax + 132, deck_y + 18)],
              fill=col)
    d.arc(box(ax + 30, deck_y - 22, ax + 278, deck_y + 40), 200, 340,
          fill=col, width=sc(4))
    # smoke over the gap
    for (sx, sy, sr) in ((150, 16, 9), (162, 10, 7), (140, 8, 6)):
        d.ellipse(box(ax + sx - sr, ay + sy - sr, ax + sx + sr, ay + sy + sr),
                  fill=(120, 124, 132))
    # water ripples
    for yy in (ay + ah - 14, ay + ah - 7):
        d.line([pt(ax + 100, yy), pt(ax + aw - 100, yy)],
               fill=(255, 255, 255), width=sc(2))


def scene_gulf_map(d, ax, ay, aw, ah):
    """Simplified geographic map of the Gulf: Iran on top, the Arabian
    Peninsula below, the sea channel between them. Dashed red lines
    trace the drone paths from Iran toward Kuwait and Bahrain; a
    tanker burns in the Strait of Hormuz at the right edge."""
    d.rectangle(box(ax, ay, ax + aw, ay + ah), fill=(205, 225, 236))
    # Iran (top): a coastline that dips down toward the Gulf
    d.polygon([pt(ax, ay), pt(ax + aw, ay), pt(ax + aw, ay + 18),
               pt(ax + 268, ay + 26), pt(ax + 210, ay + 30),
               pt(ax + 150, ay + 24), pt(ax + 90, ay + 30),
               pt(ax + 40, ay + 22), pt(ax, ay + 26)],
              fill=(228, 210, 175))
    # Arabia (bottom): a coastline that rises toward the Gulf
    d.polygon([pt(ax, ay + ah), pt(ax + aw, ay + ah),
               pt(ax + aw, ay + ah - 20), pt(ax + 262, ay + ah - 26),
               pt(ax + 200, ay + ah - 22), pt(ax + 150, ay + ah - 30),
               pt(ax + 96, ay + ah - 24), pt(ax + 46, ay + ah - 30),
               pt(ax, ay + ah - 22)],
              fill=(228, 210, 175))
    # Bahrain: a small island in the channel
    d.ellipse(box(ax + 118, ay + 44, ax + 130, ay + 54),
              fill=(228, 210, 175), outline=NAVY, width=sc(1))
    # Qeshm: a long island in the strait, right side
    d.polygon([pt(ax + 252, ay + 48), pt(ax + 292, ay + 42),
               pt(ax + 296, ay + 52), pt(ax + 254, ay + 58)],
              fill=(228, 210, 175), outline=NAVY, width=sc(1))
    # dashed drone paths from Iran toward Kuwait and Bahrain
    def dashed(x0, y0, x1, y1):
        steps = 14
        for i in range(steps):
            if i % 2:
                continue
            t0, t1 = i / steps, (i + 1) / steps
            d.line([pt(ax + x0 + (x1 - x0) * t0, ay + y0 + (y1 - y0) * t0),
                    pt(ax + x0 + (x1 - x0) * t1, ay + y0 + (y1 - y0) * t1)],
                   fill=(179, 58, 58), width=sc(2))
    dashed(120, 26, 46, 44)   # Iran -> Kuwait
    dashed(180, 28, 126, 44)  # Iran -> Bahrain
    # interception starbursts at Kuwait and Bahrain
    for (sx, sy) in ((46, 46), (124, 48)):
        for (dx, dy) in ((0, -7), (5, -5), (7, 0), (5, 5), (0, 7),
                         (-5, 5), (-7, 0), (-5, -5)):
            d.line([pt(ax + sx, ay + sy), pt(ax + sx + dx, ay + sy + dy)],
                   fill=(179, 58, 58), width=sc(2))
    # tanker in the strait, hull + fire
    d.polygon([pt(ax + 232, ay + 62), pt(ax + 282, ay + 62),
               pt(ax + 274, ay + 72), pt(ax + 240, ay + 72)],
              fill=(140, 40, 40))
    d.rectangle(box(ax + 246, ay + 54, ax + 262, ay + 62), fill=PAPER)
    d.polygon([pt(ax + 250, ay + 54), pt(ax + 258, ay + 40),
               pt(ax + 266, ay + 54)], fill=(217, 123, 41))
    # labels (IRAN sits right of the region chip, not under it)
    f_lab = F(FONT_SANS_B, 10)
    d.text(pt(ax + 118, ay + 4), "IRAN", font=f_lab, fill=NAVY)
    d.text(pt(ax + 8, ay + 34), "KUWAIT", font=f_lab, fill=NAVY)
    d.text(pt(ax + 136, ay + 40), "BAHRAIN", font=f_lab, fill=NAVY)
    d.text(pt(ax + 8, ay + ah - 14), "SAUDI ARABIA", font=f_lab, fill=NAVY)
    d.text(pt(ax + 232, ay + ah - 14), "UAE", font=f_lab, fill=NAVY)
    d.text(pt(ax + 262, ay + 8), "HORMUZ", font=f_lab, fill=NAVY)
    d.text(pt(ax + 246, ay + 30), "QESHM", font=f_lab, fill=NAVY)


def scene_ballot(d, ax, ay, aw, ah):
    # Ballot box with a paper in the slot and a big checkmark, left;
    # Senate tally bars (Democrats 56, Republicans 44), right.
    d.rectangle(box(ax, ay, ax + aw, ay + ah), fill=tint(REGIONS["Americas"], 0.88))
    # ballot box
    d.rectangle(box(ax + 24, ay + 34, ax + 104, ay + 82), fill=NAVY)
    d.rectangle(box(ax + 16, ay + 26, ax + 112, ay + 34), fill=NAVY_SOFT)
    d.rectangle(box(ax + 52, ay + 28, ax + 76, ay + 32), fill=(8, 16, 30))
    # ballot paper sticking out of the slot
    d.rectangle(box(ax + 54, ay + 6, ax + 74, ay + 28), fill=PAPER)
    d.line([pt(ax + 58, ay + 12), pt(ax + 70, ay + 12)], fill=GREY, width=sc(1))
    d.line([pt(ax + 58, ay + 17), pt(ax + 70, ay + 17)], fill=GREY, width=sc(1))
    # big checkmark on the box
    d.line([pt(ax + 40, ay + 58), pt(ax + 52, ay + 70), pt(ax + 88, ay + 44)],
           fill=PAPER, width=sc(5), joint="curve")
    # senate tally, right: caption + two bars with D/R labels
    f_cap = F(FONT_SANS_B, 11)
    d.text(pt(ax + 150, ay + 8), "SENATE", font=f_cap, fill=NAVY)
    d.text(pt(ax + 136, ay + 30), "D", font=f_cap, fill=NAVY)
    d.text(pt(ax + 136, ay + 50), "R", font=f_cap, fill=NAVY)
    d.rectangle(box(ax + 150, ay + 28, ax + 251, ay + 42), fill=(46, 111, 176))
    d.rectangle(box(ax + 150, ay + 48, ax + 229, ay + 62), fill=(179, 58, 58))
    f_n = F(FONT_SANS_B, 12)
    d.text(pt(ax + 255, ay + 30), "56", font=f_n, fill=NAVY)
    d.text(pt(ax + 233, ay + 50), "44", font=f_n, fill=NAVY)


# ---------------------------------------------------------------- mid bands
# A mid band is the top 70 px of a mid card: pastel tint, a numbered
# badge upper-left, and either one big verified number with a caption
# or (APEC) three mini flags. The band is drawn by the caller; these
# helpers draw the content inside it.

def band_number(d, x, y, w, number, caption, color):
    """Big verified number centred in the band, caption beneath it."""
    f_num = F(FONT_SANS_B, 26)
    nw = text_w(d, number, f_num)
    d.text((sc(x + (w - nw) / 2), sc(y + 16)), number, font=f_num,
           fill=color)
    f_cap = F(FONT_SANS_B, 9)
    cw = text_w(d, caption, f_cap)
    d.text((sc(x + (w - cw) / 2), sc(y + 50)), caption, font=f_cap,
           fill=GREY)


def band_flags(d, x, y, w):
    """Three mini flags (US, China, Russia) in a row, centred."""
    fw, fh, gap = 34, 22, 6
    total = fw * 3 + gap * 2
    fx0 = x + (w - total) / 2
    fy = y + 14
    for i, kind in enumerate(("us", "cn", "ru")):
        fx = fx0 + i * (fw + gap)
        if kind == "us":
            for j in range(7):
                d.rectangle(box(fx, fy + j * 3, fx + fw, fy + j * 3 + 3),
                            fill=(179, 58, 58) if j % 2 == 0 else PAPER)
            d.rectangle(box(fx, fy, fx + 14, fy + 10), fill=(46, 111, 176))
            for dx in (3, 8):
                for dy in (3, 7):
                    d.ellipse(box(fx + dx, fy + dy, fx + dx + 2, fy + dy + 2),
                              fill=PAPER)
        elif kind == "cn":
            d.rectangle(box(fx, fy, fx + fw, fy + fh), fill=(179, 58, 58))
            d.ellipse(box(fx + 4, fy + 4, fx + 10, fy + 10), fill=GOLD)
            for dx, dy in ((16, 3), (20, 7), (16, 11), (12, 7)):
                d.ellipse(box(fx + dx, fy + dy, fx + dx + 3, fy + dy + 3),
                          fill=GOLD)
        else:
            d.rectangle(box(fx, fy, fx + fw, fy + 7), fill=PAPER)
            d.rectangle(box(fx, fy + 7, fx + fw, fy + 15),
                        fill=(46, 111, 176))
            d.rectangle(box(fx, fy + 15, fx + fw, fy + fh),
                        fill=(179, 58, 58))
        d.rectangle(box(fx, fy, fx + fw, fy + fh), outline=NAVY, width=1)
    f_cap = F(FONT_SANS_B, 9)
    cap = "SHENZHEN · THU 19 NOV"
    cw = text_w(d, cap, f_cap)
    d.text((sc(x + (w - cw) / 2), sc(y + 50)), cap, font=f_cap, fill=GREY)

# ---------------------------------------------------------------- world map
# Hand-authored simplified continent polygons, equirectangular.
# Panel (1024 units): x16..x362, y708..y938 (346x230).
MAP_X, MAP_Y, MAP_W, MAP_H = 16, 708, 346, 230

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
# East cluster (Kyiv, Kerch, Gaza, Antalya, Stockholm, London) is
# nudged apart; a hairline joins each nudged dot to its true spot.
DOTS_NUM = [
    (1, 50.5, 26.2, 0, 0), (2, 36.5, 45.3, 8, 4), (3, -150.0, 64.0, 0, 0),
    (4, 114.1, 22.5, 0, 0), (5, -121.9, 37.4, 6, 6),
    (6, 30.5, 50.4, -10, -8), (7, 34.5, 31.5, -2, 10),
    (8, 30.7, 36.9, -12, -2), (9, 174.8, -36.9, -8, 0),
    (10, 18.1, 59.3, -8, -8), (11, 149.1, -35.3, 0, 0),
    (12, 90.4, 23.8, 0, 0), (13, -0.1, 51.5, 0, 0),
]
# Brief dots: (lon, lat, dx, dy, region). San Francisco carries two
# briefs (data-centre ban, Anthropic) and Nigeria three (football,
# graft, Ebola contacts); each is nudged apart.
DOTS_BRIEF = [
    (26.1, 44.4, 0, 0, "Europe"), (-77.0, -10.0, 0, 0, "Americas"),
    (-122.4, 37.8, 14, 14, "Americas"), (-74.0, 40.7, 0, 0, "Global"),
    (72.8, 19.1, 0, 0, "Asia"), (3.4, 6.5, 0, 7, "Africa"),
    (28.2, -25.7, 0, 0, "Africa"), (-77.0, 38.9, 8, 8, "Americas"),
    (45.0, 12.8, 8, 0, "Middle East"), (56.0, 26.0, 6, -6, "Middle East"),
    (116.4, 39.9, 0, 0, "Asia"), (121.0, 14.6, 0, 0, "Asia"),
    (22.7, 48.4, 0, 0, "Europe"), (37.6, 55.8, 0, 0, "Europe"),
    (145.0, 14.0, 0, 0, "Oceania"), (80.3, 15.9, 0, 0, "Asia"),
    (-160.0, -10.5, 0, 0, "Oceania"), (44.2, 15.3, 0, 0, "Middle East"),
    (-122.4, 37.8, -10, -10, "Americas"), (29.5, 1.0, 0, 0, "Africa"),
    (-46.0, -4.5, 0, 0, "Americas"), (145.8, -5.2, 0, 0, "Oceania"),
    (7.5, 9.1, 0, -7, "Africa"), (96.0, 21.0, 8, 8, "Asia"),
    (7.0, 4.8, 0, 0, "Africa"), (30.4, 13.2, 0, 0, "Africa"),
    (-0.1, 51.5, 10, 10, "Europe"), (4.35, 50.85, 0, 14, "Europe"),
    (-75.7, 45.4, -10, -6, "Americas"), (7.5, 9.1, 7, 7, "Africa"),
]
NUM_REGION = {1: "Middle East", 2: "Europe", 3: "Americas", 4: "Asia",
              5: "Americas", 6: "Europe", 7: "Middle East", 8: "Global",
              9: "Global", 10: "Europe", 11: "Oceania", 12: "Asia",
              13: "Europe"}


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
                 fill=SEA, outline=NAVY, width=2)
    for region, poly in CONTINENTS:
        pts = [pt(*map_xy(lon, lat)) for lon, lat in poly]
        d.polygon(pts, fill=tint(REGIONS[region], 0.55),
                  outline=REGIONS[region])
    f_cap = F(FONT_SANS_B, 11)
    d.text(pt(MAP_X + 8, MAP_Y + 6), "WHERE IT HAPPENED — 1–13",
           font=f_cap, fill=NAVY)
    hair = (150, 140, 120)
    for n, lon, lat, dx, dy in DOTS_NUM:
        x0, y0 = map_xy(lon, lat)
        x, y = x0 + dx, y0 + dy
        if math.hypot(dx, dy) >= 8:
            d.line([pt(x, y), pt(x0, y0)], fill=hair, width=sc(1))
            d.ellipse(box(x0 - 2, y0 - 2, x0 + 2, y0 + 2), fill=hair)
        col = REGIONS[NUM_REGION[n]]
        d.ellipse(box(x - 5, y - 5, x + 5, y + 5), fill=col, outline=PAPER,
                  width=1)
        f_n = F(FONT_SANS_B, 8)
        num = str(n)
        d.text((sc(x) - d.textlength(num, font=f_n) / 2, sc(y - 4.5)), num,
               font=f_n, fill=PAPER)
    for lon, lat, dx, dy, region in DOTS_BRIEF:
        x0, y0 = map_xy(lon, lat)
        x, y = x0 + dx, y0 + dy
        if math.hypot(dx, dy) >= 8:
            d.line([pt(x, y), pt(x0, y0)], fill=hair, width=sc(1))
            d.ellipse(box(x0 - 2, y0 - 2, x0 + 2, y0 + 2), fill=hair)
        d.ellipse(box(x - 2, y - 2, x + 2, y + 2),
                  fill=REGIONS[region])


def draw_legend(d, x, y):
    """Two rows of region swatches under the map, plus one note line."""
    f_l = F(FONT_SANS, 11)
    rows = [["Europe", "Middle East", "Asia", "Africa"],
            ["Americas", "Oceania", "Global"]]
    yy = y
    for row in rows:
        xx = x
        for region in row:
            d.rectangle(box(xx, yy, xx + 8, yy + 8), fill=REGIONS[region])
            d.text(pt(xx + 11, yy - 1), region, font=f_l, fill=INK)
            xx += 11 + text_w(d, region, f_l) + 14
        yy += 16
    d.text(pt(x, yy), "1–13: heroes and mids · dots: briefs · "
           "hairlines = true spots.", font=F(FONT_SANS, 10), fill=GREY)

# ---------------------------------------------------------------- content
# Headlines were kept short on purpose so they fit the required sizes.
# Full wording and sources: see facts.md.

SUMMARY = ("Strikes in the Gulf and on the Kerch bridge, a three-way "
           "summit in Shenzhen and a chipmaker's record quarter — the "
           "day in 43 stories.")

HEROES = [
    ("Middle East", scene_gulf_map, "Iran hits US bases in Kuwait, Bahrain",
     "Kuwait says drones downed; ADNOC ship hit, 1 missing, 11 hurt"),
    ("Europe", scene_bridge, "Kerch Bridge span falls into the sea",
     "227m road arch collapses; rail partly back"),
    ("Americas", scene_ballot, "Peltola flips Alaska Senate seat",
     "Democrats reach 56 seats; first Alaska Native senator"),
]

# Mid tuple: (region, category, headline, subline, band kind,
#              band number, band caption). Band kind "num" draws a big
# verified number; "flags" draws the three summit flags (APEC).
MIDS = [
    ("Asia", "DIPLOMACY", "Xi, Putin meet as APEC opens",
     "Trump flies in tonight; trilateral summit Thursday",
     "flags", "", ""),
    ("Americas", "BUSINESS", "Nvidia shares jump after record results",
     "Revenue $115.8bn beats forecasts; shares up",
     "num", "$115.8B", "Q3 REVENUE, +103%"),
    ("Europe", "UKRAINE WAR", "Russia fires 141 drones at Ukraine",
     "Air force: 126 downed; 5 killed, 15 injured in a day",
     "num", "141", "DRONES OVERNIGHT"),
    ("Middle East", "GAZA", "Board of Peace: Gaza truce at risk",
     "First report to UN: Israel blocked civil administration",
     "num", "1,650", "KILLED SINCE TRUCE"),
    ("Global", "CLIMATE", "COP31: 75 back '35x35' power goal",
     "Electricity 35% of energy by 2035; draft deal",
     "num", "75", "COUNTRIES BACK 35x35"),
    ("Global", "CULTURE", "Grand Theft Auto VI goes on sale",
     "Midnight launch in New Zealand; 15m+ pre-orders",
     "num", "$1.54bn", "PRE-RELEASE SALES"),
    ("Europe", "HEALTH", "ECDC: antibiotic resistance surges",
     "K. pneumoniae infections up 72% since 2019",
     "num", "72%", "RISE SINCE 2019"),
    ("Oceania", "DIPLOMACY", "Australia sanctions Daniella Weiss",
     "Settler leader among 3 people, 4 groups sanctioned",
     "num", "7", "SANCTIONED"),
    ("Asia", "LABOUR", "Bangladesh strike shuts 500",
     "Tk 30,000 wage sought; highway blocked",
     "num", "500", "FACTORIES SHUT"),
    ("Europe", "ECONOMY", "UK inflation hits 3.6%",
     "ONS: October CPI 3.6%, a one-year high",
     "num", "3.6%", "OCTOBER CPI"),
]

BRIEFS = [
    ("Romania:", "5.3 quake shakes Bucharest", "Europe"),
    ("Peru:", "strong quake off the coast", "Americas"),
    ("San Francisco:", "data-centre ban extended", "Americas"),
    ("Leukaemia vaccine", "cuts death risk", "Global"),
    ("Cricket:", "IPL retention lists filed", "Asia"),
    ("Nigeria held", "0-0 by Tanzania", "Africa"),
    ("South Africa", "summons Nigerian envoy", "Africa"),
    ("Fed October", "minutes due today", "Americas"),
    ("Houthi missiles", "target Aden airport", "Middle East"),
    ("Three US carriers", "now in the Gulf", "Middle East"),
    ("Trump hints", "at Kim meeting in China", "Asia"),
    ("Protests greet", "Trump in Manila", "Asia"),
    ("Hungary halts", "rail link to Ukraine", "Europe"),
    ("Kremlin vows", "to rebuild bridge", "Europe"),
    ("Quake south of", "Mariana Islands", "Oceania"),
    ("Cyclone Akvan:", "Odisha to evacuate 204,070", "Asia"),
    ("Cyclone Xavier", "reaches Category 5", "Oceania"),
    ("Coalition hits", "60 Houthi targets", "Middle East"),
    ("Anthropic to price", "$1.4tn IPO tonight", "Americas"),
    ("Ebola still out", "of control, WHO warns", "Africa"),
    ("Awá emerge", "from Amazon", "Americas"),
    ("Quake shakes", "Papua New Guinea", "Oceania"),
    ("Nigeria loses", "$125bn a year to graft", "Africa"),
    ("World Court to rule", "on Myanmar Thursday", "Asia"),
    ("Dangote refinery IPO", "grows to $2.1bn", "Africa"),
    ("Amnesty:", "RSF drones killed 37 in El Obeid", "Africa"),
    ("Britain sanctions", "eight settler-builders", "Europe"),
    ("Brussels proposes", "€45bn Ukraine loan", "Europe"),
    ("Carney:", "China trade no worry for Trump", "Americas"),
    ("Nigeria:", "Ebola contacts clear quarantine", "Africa"),
]

FOOTER_L1 = ("Every story happened or was first reported on Wednesday "
             "18 November 2026 (any time zone).")
FOOTER_L2 = ("Disputed claims are attributed. Sources: Reuters, AP, AFP, "
             "BBC, Al Jazeera, UN News and others. Original drawings.")


def build():
    check_dots()
    total = len(HEROES) + len(MIDS) + len(BRIEFS)
    assert total == 43, "story count is %d, expected 43" % total

    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # ---- masthead: navy y0-120, gold rule y120-124, region stripe y124-127
    d.rectangle(box(0, 0, 1024, 120), fill=NAVY)
    f_row1 = F(FONT_SANS_B, 15)
    left_w = letterspaced(d, 16, 12, "THE DAY IN WORLD NEWS", f_row1, GOLD,
                          spacing=2)
    right = "%d STORIES · 6 CONTINENTS · ONE DAY" % total
    right_w = text_w(d, right, f_row1) + 2 * (len(right) - 1)
    assert 16 + left_w + 20 <= 1008 - right_w, "masthead row 1 overlaps"
    letterspaced(d, 1008 - right_w, 12, right, f_row1, GOLD, spacing=2)
    # date: largest text on the page, >= 66 px, >= 24 px clear of row 1
    df, dlines, dsize = fit_text(d, "WEDNESDAY 18 NOVEMBER 2026", FONT_SERIF_DATE,
                                 68, 976, 1, 66)
    assert dsize >= 66, "date shrank below 66 px"
    # centred, so it keeps >= 24 px margins on both sides.
    # Noto's ascent (72 px at 67 px) is larger than Liberation's
    # (61 px at 68 px), so the top is moved up to 40: the baseline
    # still lands at 112, as in the 17 Nov poster.
    draw_centered(d, 512, 40, dlines[0], df, PAPER)
    a1, _d1 = f_row1.getmetrics()
    ad, _dd = df.getmetrics()
    row1_cap_bottom = 12 + a1 / S  # caps sit on the baseline
    date_cap_top = 40 + ad / S - 0.69 * dsize
    assert date_cap_top - row1_cap_bottom >= 24, \
        "date gap %d px < 24" % (date_cap_top - row1_cap_bottom)
    assert 40 + ad / S <= 120, "date baseline runs past the masthead"
    d.rectangle(box(0, 120, 1024, 124), fill=GOLD)
    seg = 992.0 / len(REGION_ORDER)
    for i, region in enumerate(REGION_ORDER):
        d.rectangle(box(16 + i * seg, 124, 16 + (i + 1) * seg, 127),
                    fill=REGIONS[region])

    # ---- one-line summary under the masthead, on cream
    f_sum = F(FONT_SANS, 13)
    sw = text_w(d, SUMMARY, f_sum)
    assert sw <= 976, "summary too wide (%.0f px)" % sw
    d.text(pt(512 - sw / 2, 132), SUMMARY, font=f_sum, fill=GREY)

    # ---- heroes: 3 cards 324x206 at y150
    for i, (region, scene, headline, subline) in enumerate(HEROES):
        x, y = 16 + i * 334, 150
        rounded_rect(d, [x, y, x + 324, y + 206], radius=12, fill=PAPER,
                     outline=NAVY, width=2)
        scene(d, x + 8, y + 8, 308, 90)
        chip(d, x + 16, y + 14, region, CHIPS[region], size=12)
        hf, hlines, hsize = fit_text(d, headline, FONT_SERIF_B, 27, 300, 2, 26)
        yy = y + 104
        for ln in hlines:
            d.text(pt(x + 12, yy), ln, font=hf, fill=NAVY)
            yy += int(hsize * 1.12)
        sf, slines, ssize = fit_text(d, subline, FONT_SANS, 14, 300, 2, 13.5)
        yy += 4
        for ln in slines:
            d.text(pt(x + 12, yy), ln, font=sf, fill=GREY)
            yy += int(ssize * 1.15)
        assert yy <= y + 202, "hero %d text overflows card (%d)" % (i + 1, yy - y)

    # ---- mids: 5 cols x 2 rows, cards 192x166 at y362 / y536
    col_x = [16, 216, 416, 616, 816]
    for i, (region, category, headline, subline, kind, number,
            caption) in enumerate(MIDS):
        col_i, row_i = i % 5, i // 5
        x, y = col_x[col_i], 362 + row_i * 174
        col = REGIONS[region]
        rounded_rect(d, [x, y, x + 192, y + 166], radius=10, fill=PAPER,
                     outline=BORDER, width=1)
        # 3 px regional top bar, then the 70 px band
        d.rectangle(box(x + 2, y + 2, x + 190, y + 5), fill=col)
        d.rectangle(box(x + 2, y + 5, x + 190, y + 73),
                    fill=tint(col, 0.88))
        # numbered badge, upper-left inside the band
        bx, by = x + 16, y + 19
        d.ellipse(box(bx - 10, by - 10, bx + 10, by + 10), fill=NAVY)
        nf = F(FONT_SANS_B, 11)
        num = str(i + 4)
        d.text((sc(bx) - d.textlength(num, font=nf) / 2, sc(by - 6)), num,
               font=nf, fill=PAPER)
        if kind == "flags":
            band_flags(d, x + 2, y + 5, 188)
        else:
            band_number(d, x + 2, y + 5, 188, number, caption, CHIPS[region])
        # label, headline, description
        lf = F(FONT_SANS_B, 11)
        label = "%s · %s" % (region.upper(), category)
        lw = text_w(d, label, lf)
        assert lw <= 176, "mid %d label too wide (%.0f)" % (i + 4, lw)
        d.text(pt(x + 8, y + 78), label, font=lf, fill=col)
        hf, hlines, hsize = fit_text(d, headline, FONT_SERIF_B, 17, 176, 2, 16)
        sf, slines, ssize = fit_text(d, subline, FONT_SANS, 12.5, 176, 2, 12)
        block_h = (len(hlines) * hsize * 1.12 + 3
                   + len(slines) * ssize * 1.18)
        yy = y + 92
        assert yy + block_h <= y + 164, \
            "mid %d text block too tall (%.0f)" % (i + 4, block_h)
        for ln in hlines:
            d.text(pt(x + 8, yy), ln, font=hf, fill=NAVY)
            yy += hsize * 1.12
        yy += 3
        for ln in slines:
            d.text(pt(x + 8, yy), ln, font=sf, fill=GREY)
            yy += ssize * 1.18

    # ---- bottom: map left, briefs right
    draw_map(d)
    draw_legend(d, 16, 942)
    f_bh = F(FONT_SANS_B, 16)
    letterspaced(d, 378, 708, "ALSO ON WEDNESDAY 18 NOVEMBER", f_bh, NAVY,
                 spacing=2)
    d.line([pt(378, 730), pt(1008, 730)], fill=GOLD, width=sc(2))
    f_lead = F(FONT_SANS_B, 13)
    f_rest = F(FONT_SANS, 13)
    for i, (lead, rest, _reg) in enumerate(BRIEFS):
        col_i, row_i = (0, i) if i < 15 else (1, i - 15)
        x = 378 + col_i * 319
        y = 738 + row_i * 16
        w = text_w(d, lead, f_lead) + text_w(d, " " + rest, f_rest)
        assert w <= 311, "brief %d too wide (%.0f px): %s %s" \
            % (i + 14, w, lead, rest)
        d.text(pt(x, y), lead, font=f_lead, fill=NAVY)
        d.text(pt(x + text_w(d, lead, f_lead), y), " " + rest,
               font=f_rest, fill=INK)

    # ---- footer
    d.rectangle(box(0, 986, 1024, 1024), fill=NAVY)
    ff = F(FONT_SANS, 12)
    draw_centered(d, 512, 990, FOOTER_L1, ff, PAPER)
    draw_centered(d, 512, 1006, FOOTER_L2, ff, (200, 205, 215))

    out1024 = img.resize((1024, 1024), Image.LANCZOS)
    out1024 = out1024.convert("P", palette=Image.ADAPTIVE, colors=256)
    out1024.save(os.path.join(HERE, "entry-1024.png"))
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
    im.crop((0, 0, 1024, 120)).save(qdir / "top120.png")
    im.crop((0, 120, 1024, 360)).save(qdir / "heroes.png")
    im.crop((0, 360, 1024, 705)).save(qdir / "mids.png")
    im.crop((0, 705, 370, 990)).save(qdir / "map.png")
    im.crop((370, 705, 1024, 990)).save(qdir / "briefs.png")
    im.crop((0, 0, 512, 512)).save(qdir / "q_tl.png")
    im.crop((512, 0, 1024, 512)).save(qdir / "q_tr.png")
    im.crop((0, 512, 512, 1024)).save(qdir / "q_bl.png")
    im.crop((512, 512, 1024, 1024)).save(qdir / "q_br.png")
    im.resize((300, 300), Image.LANCZOS).save(qdir / "small300.png")
    print("qa crops in", qdir)


if __name__ == "__main__":
    build()
    qa_crops()
