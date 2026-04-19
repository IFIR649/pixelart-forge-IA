#!/usr/bin/env python
"""Convert a PixelForge state JSON pixel matrix into setpixels commands."""

from __future__ import annotations

import argparse
import json
import sys


def load_pixels(path: str) -> list[list[str | None]]:
    with open(path, "r", encoding="utf-8") as fh:
        state = json.load(fh)
    rows = state.get("pixels")
    if not isinstance(rows, list):
        raise ValueError("state has no pixels matrix")
    return rows


def commands_for(path: str, chunk: int) -> list[str]:
    rows = load_pixels(path)
    triples: list[str] = []
    for y, row in enumerate(rows):
        if not isinstance(row, list):
            continue
        for x, color in enumerate(row):
            if isinstance(color, str) and color:
                triples.extend([str(x), str(y), color])
    commands = ["clear"]
    for i in range(0, len(triples), chunk * 3):
        commands.append("setpixels " + " ".join(triples[i : i + chunk * 3]))
    return commands


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("state")
    parser.add_argument("--chunk", type=int, default=180)
    ns = parser.parse_args(argv)
    for command in commands_for(ns.state, max(1, ns.chunk)):
        print(command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
