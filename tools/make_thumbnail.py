#!/usr/bin/env python3
"""Build a 1280x720 YouTube thumbnail: big condensed black caps on a white
panel, art bleeding in from the right.

Matches the channel's existing thumbnail look (see
examples/crowd_crush_video/thumbnail.jpg). Text is rendered with DejaVu Bold
and horizontally squeezed to fake a condensed face, because the sandbox has no
condensed display font.

Usage:
    python tools/make_thumbnail.py examples/night_one_video/frames/beat09m04.png \
        --out examples/night_one_video/thumbnail.jpg \
        --line1 "NIGHT ONE" --line2 "IT FAILS IN ORDER"
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, H = 1280, 720
PANEL = 640          # white text panel width
SQUEEZE = 0.78       # horizontal scale -> condensed look


def condensed(text: str, size: int, squeeze: float) -> Image.Image:
    """Render text black on transparent, then squeeze horizontally."""
    font = ImageFont.truetype(FONT, size)
    box = font.getbbox(text)
    w, h = box[2] - box[0], box[3] - box[1]
    layer = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((4 - box[0], 4 - box[1]), text, font=font, fill=(0, 0, 0, 255))
    nw = max(1, int(layer.width * squeeze))
    return layer.resize((nw, layer.height), Image.LANCZOS)


def fit(text: str, max_w: int, start: int, squeeze: float) -> Image.Image:
    size = start
    while size > 20:
        img = condensed(text, size, squeeze)
        if img.width <= max_w:
            return img
        size -= 4
    return condensed(text, 20, squeeze)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("art")
    ap.add_argument("--out", required=True)
    ap.add_argument("--line1", required=True)
    ap.add_argument("--line2", required=True)
    ap.add_argument("--panel", type=int, default=PANEL)
    ap.add_argument("--art-crop", default="center", help="center|right|left")
    ap.add_argument("--inset", type=float, default=0.03,
                    help="crop this fraction off each art edge to kill the paper border")
    ap.add_argument("--valign", default="center", help="center|top")
    args = ap.parse_args()

    art = Image.open(args.art).convert("RGB")
    if args.inset > 0:
        ix, iy = int(art.width * args.inset), int(art.height * args.inset)
        art = art.crop((ix, iy, art.width - ix, art.height - iy))
    # Cover-fit into the full frame, then the white panel will sit over it.
    scale = max(W / art.width, H / art.height)
    art = art.resize((int(art.width * scale + 0.5), int(art.height * scale + 0.5)), Image.LANCZOS)
    if args.art_crop == "right":
        off = (art.width - W, (art.height - H) // 2)
    elif args.art_crop == "left":
        off = (0, (art.height - H) // 2)
    else:
        off = ((art.width - W) // 2, (art.height - H) // 2)
    canvas = art.crop((off[0], off[1], off[0] + W, off[1] + H))

    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, args.panel, H], fill=(255, 255, 255))

    pad = 46
    inner = args.panel - pad * 2
    l1 = fit(args.line1, inner, 190, SQUEEZE)
    l2 = fit(args.line2, inner, 96, SQUEEZE)
    gap = 34
    total = l1.height + gap + l2.height
    y = 74 if args.valign == "top" else (H - total) // 2
    canvas.paste(l1, (pad, y), l1)
    canvas.paste(l2, (pad, y + l1.height + gap), l2)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=92)
    print(f"[thumb] {out} {canvas.size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
