#!/usr/bin/env python3
"""
main.py -- entry program for the make.fun "news-image-20261118" bounty.

What this program does
-----------------------
Running this file produces exactly one file: ``entry.png``, a
1024 x 1024 pixel poster, written into the directory named by the
``MAKEFUN_OUTPUT_DIR`` environment variable. When that variable is
not set, the poster is written into ``/output`` instead. The
output directory is created first if it does not already exist.

The poster it writes
---------------------
The picture is a newspaper-style front page summing up world news
from Wednesday 18 November 2026. It carries 38 stories in total
-- three large hero stories at the top, twelve mid-size stories
in the middle, and twenty-three short briefs at the bottom -- drawn
from six continents, plus a small numbered world map that shows
where the fifteen headline stories took place. Every story on the
page happened, or was first reported, on that one day.

Why the picture lives here as base64 text
------------------------------------------
The finished poster is a binary PNG, but the tooling that moves
source files into the competition repository handles plain text
far more reliably than binary data: a binary blob pushed through
a text-based file API can arrive mangled or double-encoded. To
keep the poster byte-perfect, the PNG bytes are stored as base64
text instead, split across three companion modules in this same
directory -- ``img_part1.py``, ``img_part2.py`` and
``img_part3.py`` -- each of which holds one third of the encoded
picture in a string constant called ``DATA``. This program joins
the three pieces back together, decodes the base64 into the
original PNG bytes, and writes those bytes out unchanged.

Determinism
-----------
This program is fully deterministic: it reads no clock, no
random numbers, no network and no other input besides the three
``DATA`` strings above. Every run therefore writes exactly the
same bytes, so the output can be reproduced bit for bit.

Only the Python standard library is used.
"""

import base64
import os
import sys

# Make the three companion modules importable no matter which
# directory this script is launched from: the script's own
# directory always belongs at the front of the module search path.
_OWN_DIR = os.path.dirname(os.path.abspath(__file__))
if _OWN_DIR not in sys.path:
    sys.path.insert(0, _OWN_DIR)

from img_part1 import DATA as _FIRST_THIRD
from img_part2 import DATA as _SECOND_THIRD
from img_part3 import DATA as _LAST_THIRD


def _pick_output_dir():
    """Return the directory the poster should be written into."""
    chosen = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if chosen:
        return chosen
    return "/output"


def main():
    """Decode the stored poster and write it out as entry.png."""
    encoded_text = _FIRST_THIRD + _SECOND_THIRD + _LAST_THIRD
    poster_bytes = base64.b64decode(encoded_text)

    out_dir = _pick_output_dir()
    os.makedirs(out_dir, exist_ok=True)

    out_path = os.path.join(out_dir, "entry.png")
    with open(out_path, "wb") as sink:
        sink.write(poster_bytes)

    print("wrote {} ({} bytes)".format(out_path, len(poster_bytes)))


if __name__ == "__main__":
    main()
