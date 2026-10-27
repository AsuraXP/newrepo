#!/usr/bin/env python3
"""Build a silent animatic preview from generated frames.

Holds each frame for its word-locked duration (words / wps) so you can judge
CUT RHYTHM and frame-to-frame consistency before spending Kaggle time on TTS.

This is a preview tool only — it does not replace cartoonstyle/stitch.py, which
does the real narration-locked encode.

Usage:
    python tools/make_animatic.py examples/crowd_crush_video --wps 2.75
    python tools/make_animatic.py examples/crowd_crush_video --limit 10
"""
from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def even(n: int) -> int:
    return n if n % 2 == 0 else n + 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video_dir")
    ap.add_argument("--wps", type=float, default=2.75, help="words per second")
    ap.add_argument("--limit", type=int, default=0, help="only first N moments")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    vd = Path(args.video_dir)
    rows = list(csv.DictReader(open(vd / "visuals.csv", newline="", encoding="utf-8")))
    if args.limit:
        rows = rows[: args.limit]

    # PIL-normalise: x264 needs even width AND height; never resize.
    tmp = Path(tempfile.mkdtemp(prefix="animatic_"))
    concat: list[str] = []
    total = 0.0
    used, missing = 0, []
    for r in rows:
        key = "beat%02dm%02d" % (int(r["slide_id"]), int(r["moment"]))
        hits = sorted((vd / "frames").glob(key + ".png")) or sorted(
            (vd / "frames").glob(key + "_v*_s*.png")
        )
        if not hits:
            missing.append(key)
            continue
        secs = max(0.8, len(r["moment_text"].split()) / args.wps)
        jpg = tmp / f"{key}.jpg"
        from PIL import Image

        im = Image.open(hits[0]).convert("RGB")
        if im.width % 2 or im.height % 2:
            im = im.crop((0, 0, even(im.width), even(im.height)))
        im.save(jpg, quality=92)
        concat.append(f"file '{jpg.as_posix()}'")
        concat.append(f"duration {secs:.3f}")
        total += secs
        used += 1
    if not concat:
        print("no frames found", file=sys.stderr)
        return 1

    # concat demuxer quirk: repeat the last entry bare or the final frame drops.
    concat.append(concat[-2])

    lst = tmp / "list.txt"
    lst.write_text("\n".join(concat) + "\n")
    out = Path(args.out) if args.out else vd / "preview_pilot.mp4"

    cmd = [
        ffmpeg_exe(), "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(lst),
        "-fps_mode", "cfr", "-r", "30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
        str(out),
    ]
    subprocess.run(cmd, check=True)
    print(f"[animatic] {used}/{len(rows)} frames, {total:.1f}s -> {out}")
    if missing:
        print(f"[animatic] no frame yet for: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
