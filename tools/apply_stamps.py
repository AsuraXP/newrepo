#!/usr/bin/env python3
"""Burn the spoken figures onto the diagram frames — AFTER generation, in PIL,
at native frame resolution.

Why PIL and not the image model: the model cannot spell, and a wrong numeral on
screen is a fact error. Ep 01's rule was "numbers are spoken, never drawn"; this
pass is the deliberate exception for the handful of frames that *are* the fact.

Styling: one big condensed numeral plus a small tracked-out caps label, with a
thin rule above it — printed like a technical annotation on the drawing, not a
YouTube caption card. Text colour is picked per frame from the luminance of the
stamp area so it never disappears into ink.

Spec lives beside the episode, e.g. examples/night_one_video/stamps.json:

    {
      "beat03m02": {"value": "4", "unit": "HOURS", "label": "FRIDGE, DOOR SHUT"},
      "beat08m09": {"value": "20", "unit": "FT", "label": "FROM EVERY DOOR"}
    }

Usage:
    python tools/apply_stamps.py examples/night_one_video
    python tools/apply_stamps.py examples/night_one_video --dry-run
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SQUEEZE = 0.82
MARGIN_X = 72
MARGIN_Y = 62
VALUE_SIZE = 148
UNIT_SIZE = 62
LABEL_SIZE = 27
TRACK = 5  # extra px between label characters


def render(text: str, size: int, colour: tuple[int, int, int], squeeze: float = SQUEEZE, track: int = 0):
    font = ImageFont.truetype(FONT, size)
    widths = [font.getbbox(ch)[2] - font.getbbox(ch)[0] for ch in text]
    asc, desc = font.getmetrics()
    w = sum(widths) + track * max(0, len(text) - 1) + 8
    h = asc + desc + 8
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x = 4
    for ch, cw in zip(text, widths):
        d.text((x - font.getbbox(ch)[0], 4), ch, font=font, fill=colour + (255,))
        x += cw + track
    if squeeze != 1.0:
        layer = layer.resize((max(1, int(layer.width * squeeze)), layer.height), Image.LANCZOS)
    return layer


def luminance(im: Image.Image, box) -> float:
    patch = im.crop(box).convert("L").resize((32, 32))
    px = list(patch.getdata())
    return sum(px) / len(px)


def stamp(im: Image.Image, spec: dict) -> Image.Image:
    im = im.convert("RGB")
    value = str(spec["value"])
    unit = spec.get("unit", "")
    label = spec.get("label", "")

    # Compose on a transparent canvas first so we can measure the whole block.
    sc = float(spec.get("scale", 1.0))
    v = render(value, int(VALUE_SIZE * sc), (0, 0, 0))
    u = render(unit, int(UNIT_SIZE * sc), (0, 0, 0)) if unit else None
    l = render(label, int(LABEL_SIZE * sc), (0, 0, 0), squeeze=1.0, track=TRACK) if label else None

    pad = 10
    block_w = max([v.width] + ([u.width] if u else []) + ([l.width] if l else []))
    block_h = v.height + (u.height - 18 if u else 0) + (l.height + 8 if l else 0) + 20
    block = Image.new("RGBA", (block_w + pad * 2, block_h + pad * 2), (0, 0, 0, 0))
    y = pad
    block.alpha_composite(v, (pad, y))
    y += v.height - 18
    if u:
        block.alpha_composite(u, (pad + int(v.width * 0.06), y))
        y += u.height - 6
    if l:
        block.alpha_composite(l, (pad + 2, y + 4))

    pos = spec.get("pos", "bl")
    dx, dy = int(spec.get("dx", 0)), int(spec.get("dy", 0))
    x0 = (MARGIN_X - pad if pos.endswith("l") else im.width - MARGIN_X - block.width + pad) + dx
    y0 = (MARGIN_Y - pad if pos.startswith("t") else im.height - MARGIN_Y - block_h + pad) + dy
    x0 = max(4, min(x0, im.width - block.width - 4))
    y0 = max(4, min(y0, im.height - block.height - 4))
    box = (max(0, x0), max(0, y0), min(im.width, x0 + block.width), min(im.height, y0 + block.height))
    ink = (255, 255, 255) if luminance(im, box) < 118 else (0, 0, 0)

    # Re-render in the chosen colour.
    black = Image.new("RGB", im.size, (0, 0, 0))
    mask = block.split()[3]
    tinted = Image.new("RGB", block.size, ink)
    im.paste(tinted, (x0, y0), mask)

    # Thin annotation rule: above a bottom-anchored block, below a top-anchored one.
    d = ImageDraw.Draw(im)
    rule_w = max(v.width, l.width if l else 0) + 6
    rx = MARGIN_X if pos.endswith("l") else im.width - MARGIN_X - rule_w
    if pos.startswith("t"):
        ry = y0 + block.height - pad + 6
    else:
        ry = y0 + pad - 12
    if 4 < ry < im.height - 4:
        d.rectangle([rx, ry, rx + rule_w, ry + 2], fill=ink)
    return im


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video_dir")
    ap.add_argument("--spec", default="stamps.json")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    vd = Path(args.video_dir)
    spec_path = vd / args.spec
    if not spec_path.exists():
        print(f"no spec at {spec_path}")
        return 1
    specs = json.loads(spec_path.read_text())

    for key, spec in specs.items():
        f = vd / "frames" / f"{key}.png"
        if not f.exists():
            print(f"[skip] {key}: no frame")
            continue
        im = Image.open(f)
        out = stamp(im, spec)
        if out.size != im.size:
            print(f"[warn] {key}: size changed")
        if args.dry_run:
            print(f"[dry] {key}: {spec['value']} {spec.get('unit','')} / {spec.get('label','')}")
            continue
        out.save(f)
        print(f"[stamp] {key}: {spec['value']} {spec.get('unit','')} -> {f.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
