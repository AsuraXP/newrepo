"""Derive sfx_cues.csv from a single-take build.

`tts_multi.py` emits sfx_cues.csv because it knows the absolute start of every
beat it synthesizes. The single-take path (`tts.py`) does not: it produces one
continuous read, so a cue has nowhere to come from.

This closes that gap. It reads the beat spans out of `beats_with_timing.json`
and the `"sfx"` entries out of `voices.json`, and writes cue times measured from
the *start of the beat* — which is exactly where a knock should land when the
narration reaches that paragraph.

Usage:
    python3 -m tools.sfx_cues_from_beats \
        --beats beats_with_timing.json --voices voices.json --out sfx_cues.csv

Options:
    --offset 0.25   push every cue later (let the line settle before the knock)
    --quantise 0.0  round cue times to this many seconds
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def load_json(p: Path):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--beats", required=True, help="beats_with_timing.json")
    ap.add_argument("--voices", required=True, help="voices.json (holds the sfx map)")
    ap.add_argument("--out", default="sfx_cues.csv")
    ap.add_argument("--offset", type=float, default=0.25,
                    help="seconds added to every cue (default 0.25)")
    ap.add_argument("--quantise", type=float, default=0.0,
                    help="round cue times to N seconds (0 = off)")
    args = ap.parse_args()

    beats = load_json(Path(args.beats))
    cast = load_json(Path(args.voices))
    sfx_map = {int(k): v["sfx"] for k, v in cast.get("beats", {}).items()
               if isinstance(v, dict) and v.get("sfx")}

    starts = {int(b["beat"]): float(b["start"]) for b in beats}
    total = max(float(b["start"]) + float(b["sec"]) for b in beats)

    rows = []
    for beat in sorted(sfx_map):
        if beat not in starts:
            print(f"[sfx] WARNING: beat {beat} has an sfx cue but no timing - skipped")
            continue
        t = starts[beat] + args.offset
        if args.quantise > 0:
            t = round(t / args.quantise) * args.quantise
        if t >= total:
            print(f"[sfx] WARNING: cue for beat {beat} at {t:.2f}s is past the end "
                  f"({total:.2f}s) - skipped")
            continue
        rows.append({"time": round(t, 3), "beat": beat, "sfx": sfx_map[beat]})

    rows.sort(key=lambda r: r["time"])
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["time", "beat", "sfx"])
        w.writeheader()
        w.writerows(rows)

    print(f"[sfx] {len(rows)} cue(s) -> {out}  (narration {total:.2f}s)")
    for r in rows:
        print(f"[sfx]   {r['time']:8.2f}s  beat {r['beat']:02d}  {r['sfx']}")


if __name__ == "__main__":
    main()
