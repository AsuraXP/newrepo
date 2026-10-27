"""Stage 7 helper: frames/beatNNmNN.png -> pool/beatNNmNN_v00_s00000.png.

Keeps the originals untouched (copy, never rename) and normalises every frame
to exactly WIDTHxHEIGHT with a LANCZOS resize. No cropping, no stretching:
if the source aspect differs by more than 1% we letterbox with edge-coloured
padding instead of distorting the picture.
"""
from __future__ import annotations

import argparse
import glob
import os

from PIL import Image


def normalise(src: str, dst: str, size: tuple[int, int], colors: int = 256) -> dict:
    im = Image.open(src).convert("RGB")
    ow, oh = im.size
    tw, th = size
    src_ar, dst_ar = ow / oh, tw / th
    if abs(src_ar - dst_ar) / dst_ar <= 0.01:
        im = im.resize(size, Image.LANCZOS)
        mode = "resize"
    else:
        if src_ar > dst_ar:  # too wide -> fit width, pad top/bottom
            nw, nh = tw, max(1, round(oh * tw / ow))
        else:                # too tall -> fit height, pad left/right
            nw, nh = max(1, round(ow * th / oh)), th
        small = im.resize((nw, nh), Image.LANCZOS)
        edge = small.getpixel((nw // 2, 0)) if src_ar < dst_ar else small.getpixel((0, nh // 2))
        canvas = Image.new("RGB", size, edge)
        canvas.paste(small, ((tw - nw) // 2, (th - nh) // 2))
        im = canvas
        mode = f"pad({src_ar:.3f}->{dst_ar:.3f})"
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    if colors and 2 <= colors <= 256:
        im = im.quantize(colors=colors, method=Image.FASTOCTREE,
                        dither=Image.FLOYDSTEINBERG)
    im.save(dst, "PNG", optimize=True, compress_level=9)
    return {"source_size": [ow, oh], "mode": mode}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default="frames")
    ap.add_argument("--out", default="pool")
    ap.add_argument("--pick", type=int, default=0)
    ap.add_argument("--size", default="1376x768")
    ap.add_argument("--colors", type=int, default=256,
                    help="palette size for the pool PNG (0 keeps full RGB)")
    args = ap.parse_args()
    tw, th = (int(x) for x in args.size.lower().split("x"))

    srcs = sorted(glob.glob(os.path.join(args.frames, "beat*m*.png")))
    if not srcs:
        raise SystemExit(f"[pool_frames] no beat*m*.png in {args.frames}")
    for src in srcs:
        key = os.path.splitext(os.path.basename(src))[0]
        dst = os.path.join(args.out, f"{key}_v{args.pick:02d}_s00000.png")
        info = normalise(src, dst, (tw, th), args.colors)
        print(f"[pool_frames] {os.path.basename(src)} {info['source_size']} "
              f"-> {os.path.basename(dst)} {info['mode']}")
    print(f"[pool_frames] {len(srcs)} frames in pool, all {tw}x{th}")


if __name__ == "__main__":
    main()
