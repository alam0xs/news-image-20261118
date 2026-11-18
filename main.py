#!/usr/bin/env python3
"""Entrypoint for the make.fun news-image-20261118 entry.

Writes the finished poster for Wednesday 18 November 2026 (one 1024x1024
PNG, 38 stories across 6 continents) to $MAKEFUN_OUTPUT_DIR/entry.png,
falling back to /output/entry.png when that variable is unset.

The program uses only the Python standard library, makes no network
requests, and is fully deterministic: the poster bytes live in this
repository as base64 text split across img_part1.py, img_part2.py and
img_part3.py (the hosting used here cannot store binary files). Those
bytes are the poster produced by build_image.py — rendered at 2048,
downsampled to 1024 with LANCZOS and palette-quantized. The story list
and its sources are in facts.md.
"""
import base64
import os
import sys

_REPO = os.path.dirname(os.path.abspath(__file__))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from img_part1 import DATA as _A
from img_part2 import DATA as _B
from img_part3 import DATA as _C


def main():
    data = base64.b64decode(_A + _B + _C)
    dest = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(dest, exist_ok=True)
    with open(os.path.join(dest, "entry.png"), "wb") as handle:
        handle.write(data)


if __name__ == "__main__":
    main()
