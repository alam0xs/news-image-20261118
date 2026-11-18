#!/usr/bin/env python3
"""Entry program for make.fun bounty news-image-20261118.

Writes the poster "THE WORLD - WEDNESDAY, 18 NOVEMBER 2026" (1024x1024 PNG,
38 stories, 6 continents) to $MAKEFUN_OUTPUT_DIR/entry.png, or to
/output/entry.png when that variable is not set.

Standard library only, no network, fully deterministic: the PNG bytes are
embedded in this repository as base64 text (img_part1.py, img_part2.py,
img_part3.py) because the repository hosting used here cannot store binary
files. The embedded bytes are the finished poster rendered by
build_image.py (PIL + DejaVu fonts, rendered at 2048 and downsampled to
1024, palette-quantized). See facts.md for the story list and sources.
"""
import base64
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from img_part1 import DATA as _P1
from img_part2 import DATA as _P2
from img_part3 import DATA as _P3


def main():
    png = base64.b64decode(_P1 + _P2 + _P3)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
