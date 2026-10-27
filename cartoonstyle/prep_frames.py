"""Stage 7 helper: frames/beatNNmNN.png -> pool/beatNNmNN_v00_s00000.png.

The stitcher globs {key}_v{pick:02d}_s*.png and does NOT trust sizes, so this is
the only place the 1376x768 spec is actually enforced. Rules, in order:

  * originals are never renamed, moved or overwritten (copy, always)
  * exact aspect (within 1%) -> LANCZOS resize, no crop, no stretch
  * aspect off by more than 1% -> fit inside, then letterbox with the frame's
    own edge colour (never black bars on a pale frame)
  * already exactly 1376x768 -> byte copy, untouched

Usage:
    python3 -m cartoonstyle.prep_frames --frames frames --out pool
    python3 -m cartoonstyle.prep_frames --frames frames --out pool --check
    python3 -m cartoonstyle.prep_frames --frames frames --out pool --colors 256

--check only reports (exit 1 if anything is not the target size); useful as a
pre-encode gate. --colors 256 quantises to keep the repo small, at the cost of
banding in painted skies - leave it off unless size is a problem.
"""
from __future__ import annotations

import argparse
import glob
import os
import shutil
import sys

from PIL import Image

TARGET = (1376, 768)
POOL_SUFFIX = "_v00_s00000"


def _flatten(im: Image.Image) -> Image.Image:
    """Drop alpha onto white rather than black; also normalise P/LA/CMYK."""
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, im)
    return im.convert("RGB")


def normalise(src: str, dst: str, size: tuple[int, int] = TARGET,
              colors: int = 0) -> dict:
    im = _flatten(Image.open(src))
    ow, oh = im.size
    tw, th = size
    if (ow, oh) == (tw, th):
        shutil.copyfile(src, dst)
        return {"src": src, "out": dst, "from": (ow, oh), "mode": "copy"}

    src_ar, dst_ar = ow / oh, tw / th
    if abs(src_ar - dst_ar) / dst_ar <= 0.01:
        im = im.resize(size, Image.LANCZOS)
        mode = "resize"
    else:
        if src_ar > dst_ar:                      # too wide -> pad top/bottom
            nw, nh = tw, max(1, round(oh * tw / ow))
        else:                                    # too tall -> pad left/right
            nw, nh = max(1, round(ow * th / oh)), th
        small = im.resize((nw, nh), Image.LANCZOS)
        edge = (small.getpixel((nw // 2, 0)) if src_ar > dst_ar
                else small.getpixel((0, nh // 2)))
        canvas = Image.new("RGB", size, edge)
        canvas.paste(small, ((tw - nw) // 2, (th - nh) // 2))
        im = canvas
        mode = f"pad({src_ar:.3f}->{dst_ar:.3f})"

    if colors and 2 <= colors <= 256:
        im = im.quantize(colors=colors, method=Image.FASTOCTREE,
                         dither=Image.FLOYDSTEINBERG).convert("RGB")
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    im.save(dst, "PNG", optimize=True, compress_level=9)
    return {"src": src, "out": dst, "from": (ow, oh), "mode": mode}


def pool_name(base: str) -> str:
    """beat05m03 -> beat05m03_v00_s00000 (idempotent for pre-pooled names)."""
    stem = base[:-4] if base.lower().endswith(".png") else base
    if "_v" in stem and "_s" in stem.split("_v", 1)[1]:
        return stem
    return stem + POOL_SUFFIX


def main() -> None:
    p = argparse.ArgumentParser(description="normalise frames into the stitch pool")
    p.add_argument("--frames", default="frames")
    p.add_argument("--out", default="pool")
    p.add_argument("--size", default=f"{TARGET[0]}x{TARGET[1]}")
    p.add_argument("--colors", type=int, default=0,
                   help="quantise to N colours (0 = full colour, best quality)")
    p.add_argument("--check", action="store_true",
                   help="report only: exit 1 if a frame is not the target size")
    args = p.parse_args()

    size = tuple(int(v) for v in args.size.lower().split("x"))
    srcs = sorted(glob.glob(os.path.join(args.frames, "*.png")))
    if not srcs:
        raise SystemExit(f"no .png files in {args.frames}/")

    rows, bad = [], 0
    if not args.check:
        os.makedirs(args.out, exist_ok=True)

    for src in srcs:
        base = os.path.basename(src)
        if not base.startswith("beat") or "m" not in base:
            print(f"[prep] IGNORE odd name (stitcher will never find it): {base}")
            bad += 1
            continue
        with Image.open(src) as probe:
            ow, oh = probe.size
        if (ow, oh) != size:
            bad += 1
        if args.check:
            rows.append((base, f"{ow}x{oh}", "OK" if (ow, oh) == size else "NOT TARGET"))
            continue
        dst = os.path.join(args.out, pool_name(base) + ".png")
        r = normalise(src, dst, size, args.colors)
        rows.append((base, f"{ow}x{oh}", r["mode"]))

    width = max(len(r[0]) for r in rows)
    for base, dims, mode in rows:
        flag = "" if mode in ("copy", "resize", "OK") else "  <--"
        print(f"  {base:<{width}}  {dims:>9}  {mode}{flag}")

    if args.check:
        print(f"[prep] {len(rows)} frames checked, {bad} not {size[0]}x{size[1]}")
        sys.exit(1 if bad else 0)

    print(f"[prep] {len(rows)} frames -> {args.out}/ as *_v00_s00000.png "
          f"({bad} needed work) | {size[0]}x{size[1]}")


if __name__ == "__main__":
    main()
