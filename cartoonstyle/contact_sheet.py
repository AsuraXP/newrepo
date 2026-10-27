"""QC helper: 5-column contact sheet of a batch of frames."""
from __future__ import annotations

import argparse
import glob
import math
import os

from PIL import Image, ImageDraw, ImageFont


def font(sz: int):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    try:
        return ImageFont.load_default(size=sz)
    except TypeError:
        return ImageFont.load_default()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default="frames")
    ap.add_argument("--keys", default=None, help="comma separated frame keys")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--thumb", type=int, default=380)
    ap.add_argument("--label", default="BATCH")
    args = ap.parse_args()

    if args.keys:
        keys = [k.strip() for k in args.keys.split(",") if k.strip()]
        srcs = [os.path.join(args.frames, k + ".png") for k in keys]
    else:
        srcs = sorted(glob.glob(os.path.join(args.frames, "beat*m*.png")))
        keys = [os.path.splitext(os.path.basename(s))[0] for s in srcs]
    srcs = [s for s in srcs if os.path.exists(s)]
    if not srcs:
        raise SystemExit("no frames found")

    tw = args.thumb
    th = round(tw * 9 / 16)
    pad, top, cap, label_h = 10, 10, 26, 46
    rows = math.ceil(len(srcs) / args.cols)
    W = args.cols * tw + (args.cols + 1) * pad
    H = label_h + top + rows * (th + cap + pad) + pad
    sheet = Image.new("RGB", (W, H), (24, 26, 29))
    d = ImageDraw.Draw(sheet)
    f_label, f_cap = font(22), font(15)
    d.text((pad + 4, 12), f"{args.label}  |  {len(srcs)} frames  |  {args.cols} cols",
           font=f_label, fill=(236, 232, 222))
    for i, (s, k) in enumerate(zip(srcs, keys)):
        r, c = divmod(i, args.cols)
        x = pad + c * (tw + pad)
        y = label_h + top + r * (th + cap + pad)
        im = Image.open(s).convert("RGB")
        im.thumbnail((tw, th), Image.LANCZOS)
        tile = Image.new("RGB", (tw, th), (12, 13, 15))
        tile.paste(im, ((tw - im.width) // 2, (th - im.height) // 2))
        sheet.paste(tile, (x, y))
        d.rectangle([x, y, x + tw, y + th], outline=(70, 74, 78), width=1)
        d.text((x + 2, y + th + 5), k, font=f_cap, fill=(222, 216, 204))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    sheet.save(args.out, "PNG", optimize=True)
    print(f"[contact_sheet] {args.out} ({W}x{H}, {len(srcs)} frames)")


if __name__ == "__main__":
    main()
