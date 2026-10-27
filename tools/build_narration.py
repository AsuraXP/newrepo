#!/usr/bin/env python3
"""Build a narration track from pre-rendered clips, with a chunk manifest.

Used when narration is produced outside Kaggle (a better voice, a human read,
or an external TTS API). The clips must be rendered in beat order; this script:

  1. prints the exact text to render for each chunk (`--print-chunks`),
  2. concatenates the clips gaplessly into narration.mp3,
  3. writes narration_chunks.json = [{index, text, start, sec}] so
     cartoonstyle/align.py can fall back to proportional timing if whisper
     is unavailable on the encode box.

Usage
-----
    python tools/build_narration.py examples/X_video --print-chunks
    python tools/build_narration.py examples/X_video \
        --clips clip1.mp3 clip2.mp3 clip3.mp3
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def duration(path: str) -> float:
    out = subprocess.run(
        [ffmpeg_exe(), "-i", path, "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    for line in out.splitlines():
        if "time=" in line:
            stamp = line.split("time=")[1].split()[0]
            h, m, s = stamp.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise SystemExit(f"could not measure {path}")


def beats_of(video_dir: Path) -> list[tuple[int, str]]:
    """Group visuals.csv moment_text into per-beat paragraphs (spoken text)."""
    import csv

    rows = list(csv.DictReader(open(video_dir / "visuals.csv", newline="", encoding="utf-8")))
    beats: dict[int, list[str]] = {}
    for r in rows:
        beats.setdefault(int(r["slide_id"]), []).append(r["moment_text"].strip())
    return [(b, " ".join(ms)) for b, ms in sorted(beats.items())]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video_dir")
    ap.add_argument("--print-chunks", action="store_true", help="show text per chunk")
    ap.add_argument("--group", type=int, default=4, help="beats per chunk (default 4)")
    ap.add_argument("--clips", nargs="*", default=[], help="rendered clips, in order")
    ap.add_argument("--plan", nargs="*", default=[],
                    help="explicit beat ranges per clip, e.g. 1-4=a.mp3 5-6=b.mp3. "
                         "Use when a content filter forces uneven chunking.")
    args = ap.parse_args()

    vd = Path(args.video_dir)
    if not (vd / "visuals.csv").exists():
        raise SystemExit(f"no visuals.csv in {vd}")

    beats = beats_of(vd)
    chunks = []
    for i in range(0, len(beats), args.group):
        group = beats[i:i + args.group]
        text = " ".join(t for _, t in group)
        chunks.append({"index": len(chunks), "beats": [b for b, _ in group], "text": text})

    # --plan: explicit beat-range -> clip mapping (uneven chunks)
    if args.plan:
        by_beat = dict(beats)
        plan = []
        for item in args.plan:
            rng, _, clip = item.partition("=")
            lo, _, hi = rng.partition("-")
            lo, hi = int(lo), int(hi or lo)
            text = " ".join(t for b, t in sorted(by_beat.items()) if lo <= b <= hi)
            plan.append((clip, text))
        chunks = [{"index": i, "text": t} for i, (_, t) in enumerate(plan)]
        for c, (clip, _) in zip(chunks, plan):
            c["sec"] = round(duration(clip), 3)
        lst = Path(vd) / ".narration_tmp_concat.txt"
        lst.parent.mkdir(parents=True, exist_ok=True)
        lst.write_text("\n".join(f"file '{Path(c).resolve().as_posix()}'"
                                 for c, _ in plan) + "\n")
        out = Path(vd) / "narration.mp3"
        subprocess.run([ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "concat",
                        "-safe", "0", "-i", str(lst), "-c:a", "libmp3lame",
                        "-q:a", "3", str(out)], check=True)
        t = 0.0
        for c in chunks:
            c["start"] = round(t, 3)
            t += c["sec"]
        (Path(vd) / "narration_chunks.json").write_text(json.dumps(chunks, indent=1),
                                                        encoding="utf-8")
        print(f"[narration] plan: {len(chunks)} clips -> {out} ({duration(str(out)):.1f}s)")
        print(f"[narration] wrote {Path(vd) / 'narration_chunks.json'}")
        return 0

    if args.print_chunks:
        for c in chunks:
            print(f"--- chunk {c['index']}  beats {c['beats'][0]}-{c['beats'][-1]}  "
                  f"{len(c['text'])} chars, {len(c['text'].split())} words ---")
            print(c["text"])
            print()
        return 0

    if not args.clips:
        raise SystemExit("pass --clips a.mp3 b.mp3 ... or --print-chunks")
    if len(args.clips) != len(chunks):
        raise SystemExit(f"{len(args.clips)} clips vs {len(chunks)} chunks - must match")

    work = vd / ".narration_tmp"
    work.mkdir(exist_ok=True)
    lst = work / "concat.txt"
    lines = []
    for c, clip in zip(chunks, args.clips):
        lines.append(f"file '{Path(clip).resolve().as_posix()}'")
        c["sec"] = duration(clip)
    lst.write_text("\n".join(lines) + "\n")

    out = vd / "narration.mp3"
    subprocess.run(
        [ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(lst), "-c:a", "libmp3lame", "-q:a", "3", str(out)],
        check=True,
    )

    t = 0.0
    for c in chunks:
        c["start"] = round(t, 3)
        c["sec"] = round(c["sec"], 3)
        t += c["sec"]
    (vd / "narration_chunks.json").write_text(json.dumps(chunks, indent=1), encoding="utf-8")

    total = duration(str(out))
    print(f"[narration] {len(chunks)} chunks -> {out} ({total:.1f}s)")
    print(f"[narration] wrote {vd / 'narration_chunks.json'}")
    if abs(total - t) > 0.5:
        print(f"[narration] note: manifest sums to {t:.1f}s, file is {total:.1f}s - "
              f"good enough for fallback timing, whisper will do better", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
