#!/usr/bin/env python
"""PixelForge pixel operations.

This module works on PixelForge state JSON files. It intentionally avoids
external dependencies so it can run in the same local workflow as server.py.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from copy import deepcopy
from datetime import datetime


SNAPSHOT_DIR = "snapshots"


def safe_id(raw: str | None, prefix: str = "pixelop") -> str:
    if raw:
        value = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(raw).strip()).strip("._-")
        if value:
            return value[:80]
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{prefix}_{stamp}"


def load_state(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        state = json.load(fh)
    if not isinstance(state, dict):
        raise ValueError("state JSON must be an object")
    return state


def normalize_rows(state: dict) -> list[list[str | None]]:
    size = int(state.get("gridSize") or 0)
    rows = state.get("pixels")
    if size <= 0 or not isinstance(rows, list):
        raise ValueError("state must include gridSize and pixels")
    out: list[list[str | None]] = []
    for y in range(size):
        src = rows[y] if y < len(rows) and isinstance(rows[y], list) else []
        row: list[str | None] = []
        for x in range(size):
            value = src[x] if x < len(src) else None
            row.append(value if isinstance(value, str) and value else None)
        out.append(row)
    return out


def clone_rows(rows: list[list[str | None]]) -> list[list[str | None]]:
    return [row[:] for row in rows]


def in_bounds(rows: list[list[str | None]], x: int, y: int) -> bool:
    return 0 <= y < len(rows) and 0 <= x < len(rows[y])


def bbox(rows: list[list[str | None]]) -> tuple[int, int, int, int] | None:
    points = [
        (x, y)
        for y, row in enumerate(rows)
        for x, value in enumerate(row)
        if value is not None
    ]
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def neighbors(rows: list[list[str | None]], x: int, y: int, diagonals: bool = True) -> list[str]:
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if diagonals:
        dirs += [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    out: list[str] = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if in_bounds(rows, nx, ny) and rows[ny][nx]:
            out.append(str(rows[ny][nx]))
    return out


def majority(values: list[str]) -> tuple[str | None, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    if not counts:
        return None, 0
    color = max(counts, key=counts.get)
    return color, counts[color]


def is_edge(rows: list[list[str | None]], x: int, y: int) -> bool:
    if not rows[y][x]:
        return False
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if not in_bounds(rows, nx, ny) or rows[ny][nx] is None:
            return True
    return False


def op_smooth(rows: list[list[str | None]], passes: int = 1) -> list[list[str | None]]:
    current = clone_rows(rows)
    passes = max(1, min(8, int(passes)))
    for _ in range(passes):
        new_rows = clone_rows(current)
        for y, row in enumerate(current):
            for x, value in enumerate(row):
                near = neighbors(current, x, y, True)
                color, count = majority(near)
                if value is None and color and count >= 5:
                    new_rows[y][x] = color
                elif value is not None and color and color != value and count >= 6:
                    new_rows[y][x] = color
                elif value is not None and len(near) <= 1:
                    new_rows[y][x] = None
        current = new_rows
    return current


def op_despeckle(rows: list[list[str | None]], min_size: int = 2) -> list[list[str | None]]:
    min_size = max(1, min(128, int(min_size)))
    h = len(rows)
    w = len(rows[0]) if rows else 0
    out = clone_rows(rows)
    seen = [[False for _ in range(w)] for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if seen[y][x] or rows[y][x] is None:
                continue
            stack = [(x, y)]
            seen[y][x] = True
            component: list[tuple[int, int]] = []
            while stack:
                cx, cy = stack.pop()
                component.append((cx, cy))
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = cx + dx, cy + dy
                    if in_bounds(rows, nx, ny) and not seen[ny][nx] and rows[ny][nx]:
                        seen[ny][nx] = True
                        stack.append((nx, ny))
            if len(component) < min_size:
                for cx, cy in component:
                    out[cy][cx] = None
    return out


def op_outline(rows: list[list[str | None]], color: str = "#000000") -> list[list[str | None]]:
    out = clone_rows(rows)
    for y, row in enumerate(rows):
        for x, value in enumerate(row):
            if value is None:
                continue
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if in_bounds(rows, nx, ny) and rows[ny][nx] is None:
                    out[ny][nx] = color
    return out


def op_lean(rows: list[list[str | None]], dx_top: int, dx_bottom: int) -> list[list[str | None]]:
    h = len(rows)
    out = [[None for _ in row] for row in rows]
    for y, row in enumerate(rows):
        t = y / (h - 1) if h > 1 else 0
        dx = round(dx_top * (1 - t) + dx_bottom * t)
        for x, value in enumerate(row):
            if value is not None and in_bounds(rows, x + dx, y):
                out[y][x + dx] = value
    return out


def op_smear(
    rows: list[list[str | None]],
    x: int,
    y: int,
    w: int,
    h: int,
    dx: int,
    dy: int,
) -> list[list[str | None]]:
    out = clone_rows(rows)
    steps = max(1, abs(dx), abs(dy))
    for sy in range(y, y + h):
        for sx in range(x, x + w):
            if not in_bounds(rows, sx, sy) or rows[sy][sx] is None:
                continue
            for step in range(1, steps + 1):
                nx = round(sx + dx * step / steps)
                ny = round(sy + dy * step / steps)
                if in_bounds(rows, nx, ny):
                    out[ny][nx] = rows[sy][sx]
    return out


def op_jitter(
    rows: list[list[str | None]],
    amount: int = 1,
    mask_color: str | None = None,
) -> list[list[str | None]]:
    amount = max(0, min(4, int(amount)))
    if amount == 0:
        return clone_rows(rows)
    out = clone_rows(rows)
    for y, row in enumerate(rows):
        for x, value in enumerate(row):
            if value is None or not is_edge(rows, x, y):
                continue
            if mask_color and value.lower() != mask_color.lower():
                continue
            seed = (x * 73856093) ^ (y * 19349663) ^ sum(ord(c) for c in value)
            dx = seed % (amount * 2 + 1) - amount
            dy = (seed // 7) % (amount * 2 + 1) - amount
            if abs(dx) + abs(dy) > amount + 1:
                continue
            nx, ny = x + dx, y + dy
            if in_bounds(rows, nx, ny) and rows[ny][nx] is None:
                out[ny][nx] = value
    return out


def op_zombiestep(rows: list[list[str | None]]) -> list[list[str | None]]:
    box = bbox(rows)
    if box is None:
        return clone_rows(rows)
    left, top, right, bottom = box
    width = max(1, right - left + 1)
    height = max(1, bottom - top + 1)
    mid_x = left + width // 2

    out = op_lean(rows, -2, 2)
    # Recompute after lean, then smear body regions. This preserves the palette
    # because every new pixel is copied from the original pixel matrix.
    box = bbox(out) or (left, top, right, bottom)
    left, top, right, bottom = box
    width = max(1, right - left + 1)
    height = max(1, bottom - top + 1)
    mid_x = left + width // 2
    upper_y = top + round(height * 0.28)
    torso_y = top + round(height * 0.42)
    lower_y = top + round(height * 0.62)

    out = op_smear(out, left, upper_y, max(1, mid_x - left + 1), max(1, round(height * 0.28)), -2, 1)
    out = op_smear(out, mid_x, torso_y, max(1, right - mid_x + 1), max(1, round(height * 0.22)), 3, 1)
    out = op_smear(out, left, lower_y, max(1, mid_x - left + 1), max(1, bottom - lower_y + 1), -1, 2)
    out = op_smear(out, mid_x, lower_y, max(1, right - mid_x + 1), max(1, bottom - lower_y + 1), 2, 2)
    out = op_jitter(out, 1)
    out = op_smooth(out, 1)
    out = op_despeckle(out, 2)
    return out


def apply_operation(op: str, rows: list[list[str | None]], args: list[str]) -> list[list[str | None]]:
    name = op.lower()
    if name == "cloneframe":
        return clone_rows(rows)
    if name == "smoothpixels":
        return op_smooth(rows, int(args[0]) if args else 1)
    if name == "despeckle":
        return op_despeckle(rows, int(args[0]) if args else 2)
    if name == "outline":
        return op_outline(rows, args[0] if args else "#000000")
    if name == "jitter":
        return op_jitter(rows, int(args[0]) if args else 1, args[1] if len(args) > 1 else None)
    if name == "lean":
        if len(args) < 2:
            raise ValueError("lean requires <dxTop> <dxBottom>")
        return op_lean(rows, int(args[0]), int(args[1]))
    if name == "smear":
        if len(args) < 6:
            raise ValueError("smear requires <x> <y> <w> <h> <dx> <dy>")
        x, y, w, h, dx, dy = [int(v) for v in args[:6]]
        return op_smear(rows, x, y, w, h, dx, dy)
    if name == "zombiestep":
        return op_zombiestep(rows)
    raise ValueError(f"unknown op: {op}")


def write_state(source: dict, rows: list[list[str | None]], capture_id: str) -> str:
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    state = deepcopy(source)
    state["id"] = capture_id
    state["pixels"] = rows
    state["timestamp"] = datetime.now().isoformat(timespec="milliseconds")
    state["savedAt"] = datetime.now().isoformat(timespec="seconds")
    path = os.path.abspath(os.path.join(SNAPSHOT_DIR, f"{capture_id}.json"))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)
    return path


def queue_command(server: str, command: str) -> None:
    payload = json.dumps({"cmd": command}).encode("utf-8")
    request = urllib.request.Request(
        server.rstrip("/") + "/cmd",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=3) as response:
        response.read()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="PixelForge pixel operations")
    parser.add_argument("--source", default=os.path.join(SNAPSHOT_DIR, "current.json"))
    parser.add_argument("--id", default=None)
    parser.add_argument("--op", required=True)
    parser.add_argument("--queue", choices=["none", "loadpixels", "loadstate"], default="none")
    parser.add_argument("--server", default="http://localhost:3000")
    parser.add_argument("args", nargs="*")
    ns = parser.parse_args(argv)

    state = load_state(ns.source)
    rows = normalize_rows(state)
    out_rows = apply_operation(ns.op, rows, ns.args)
    capture_id = safe_id(ns.id, f"pixelop_{ns.op.lower()}")
    path = write_state(state, out_rows, capture_id)

    if ns.queue != "none":
        queue_command(ns.server, f"{ns.queue} {capture_id}")

    print(json.dumps({"ok": True, "id": capture_id, "jsonPath": path, "op": ns.op}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(1)
