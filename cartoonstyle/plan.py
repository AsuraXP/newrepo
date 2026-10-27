"""Stage 2.5 gate: read visuals.csv before spending a single image on it.

Answers the three questions that cost a rebuild if you get them wrong:

  1. How long is this going to be, really? (words / wps + voice gaps)
  2. Is any image moment too short to read or too long to hold?
  3. Does visuals.csv still say exactly what narration.txt says?

That last one is the quiet killer: `tts` matches every moment_text against the
spoken word stream, and a single reworded sentence in the script leaves a
moment that can never lock - which only surfaces at Kaggle, after the images
are done.

Usage:
    python3 -m cartoonstyle.plan --visuals visuals.csv
    python3 -m cartoonstyle.plan --visuals visuals.csv --narration narration.txt
    python3 -m cartoonstyle.plan --visuals visuals.csv --voices voices.json --wps 2.75
Exit code 1 when a hard problem is found (unspeakable moment, missing key),
0 when only soft warnings (pacing outside 2.5-6.5s) are raised.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

PUNCT = ".,!?;:\u2014\u2013-\"\u201c\u201d'()"


def toks(text: str) -> list[str]:
    """Same normalisation family the TTS matcher uses: lowercase alnum only."""
    out = []
    for w in text.split():
        w = "".join(ch for ch in w.lower() if ch.isalnum())
        if w:
            out.append(w)
    return out


def sentences(text: str) -> int:
    core = text.strip().rstrip(".!?")
    return 1 + len(re.findall(r"[.!?]\s+[A-Z\u201c\"']", core))


def load_rows(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    p = argparse.ArgumentParser(description="pacing / coverage report for visuals.csv")
    p.add_argument("--visuals", required=True)
    p.add_argument("--narration", default="", help="narration.txt to check coverage against")
    p.add_argument("--voices", default="", help="voices.json (for real gap_before values)")
    p.add_argument("--wps", type=float, default=2.75, help="words per second (simulate pace)")
    p.add_argument("--min-sec", type=float, default=2.5)
    p.add_argument("--max-sec", type=float, default=6.5)
    p.add_argument("--max-words", type=int, default=18)
    args = p.parse_args()

    rows = load_rows(args.visuals)
    if not rows:
        raise SystemExit("visuals.csv has no rows")
    missing_cols = {"slide_id", "moment", "moment_text", "visual_prompt"} - set(rows[0])
    if missing_cols:
        raise SystemExit(f"visuals.csv is missing columns: {sorted(missing_cols)}")

    hard, soft = [], []
    beats: dict[str, list[dict]] = {}
    order: list[str] = []
    for r in rows:
        sid, mom = str(r["slide_id"]).strip(), str(r["moment"]).strip()
        if sid not in beats:
            beats[sid] = []
            order.append(sid)
        beats[sid].append({"moment": mom, "text": (r["moment_text"] or "").strip(),
                           "prompt": (r["visual_prompt"] or "").strip()})

    # --- keys ---------------------------------------------------------------
    seen = set()
    for sid in order:
        mom_nums = [int(b["moment"]) for b in beats[sid]]
        if mom_nums != list(range(1, len(mom_nums) + 1)):
            hard.append(f"beat {sid}: moments are not 1..N in order ({mom_nums[:8]})")
        for b in beats[sid]:
            key = f"beat{int(sid):02d}m{int(b['moment']):02d}"
            if key in seen:
                hard.append(f"duplicate key {key}")
            seen.add(key)
            if not b["text"]:
                hard.append(f"{key}: empty moment_text")
            if not b["prompt"]:
                hard.append(f"{key}: empty visual_prompt")
            if sentences(b["text"]) > 1:
                soft.append(f"{key}: {sentences(b['text'])} sentences in one moment "
                            f"(word-lock cuts mid-sentence)")
    try:
        nums = [int(s) for s in order]
        if nums != list(range(1, len(nums) + 1)):
            soft.append(f"slide_id is not 1..N ({nums[:10]}...)")
    except ValueError:
        pass

    # --- pacing -------------------------------------------------------------
    per_moment = []
    for sid in order:
        for b in beats[sid]:
            wc = len(b["text"].split())
            sec = wc / args.wps
            per_moment.append((f"beat{int(sid):02d}m{int(b['moment']):02d}", sec, wc))
            if wc > args.max_words:
                soft.append(f"beat{int(sid):02d}m{int(b['moment']):02d}: {wc} words "
                            f"(> {args.max_words}) = {sec:.1f}s on screen")
            elif sec < args.min_sec:
                soft.append(f"beat{int(sid):02d}m{int(b['moment']):02d}: {sec:.1f}s "
                            f"(< {args.min_sec}s, will feel like a flash frame)")
            elif sec > args.max_sec:
                soft.append(f"beat{int(sid):02d}m{int(b['moment']):02d}: {sec:.1f}s "
                            f"(> {args.max_sec}s, long hold)")

    words = sum(wc for _k, _s, wc in per_moment)
    body = words / args.wps
    gaps = 0.0
    cast = {}
    if args.voices and Path(args.voices).exists():
        cast = json.loads(Path(args.voices).read_text(encoding="utf-8")).get("beats", {})
    for sid in order:
        cfg = cast.get(str(int(sid)), {})
        gaps += float(cfg.get("gap_before", 0.18))
    total = body + gaps

    # --- coverage against narration.txt ------------------------------------
    coverage = None
    if args.narration and Path(args.narration).exists():
        nar = toks(Path(args.narration).read_text(encoding="utf-8"))
        cursor, unmatched, matched_words = 0, [], 0
        for sid in order:
            for b in beats[sid]:
                t = toks(b["text"])
                if not t:
                    continue
                hit = None
                for i in range(cursor, len(nar) - len(t) + 1):
                    if nar[i:i + len(t)] == t:
                        hit = i
                        break
                if hit is None:
                    unmatched.append(f"beat{int(sid):02d}m{int(b['moment']):02d}")
                else:
                    matched_words += len(t)
                    cursor = hit + len(t)
        coverage = {"narration_words": len(nar), "covered": matched_words,
                    "unmatched": unmatched, "unused": len(nar) - matched_words}

    # --- report -------------------------------------------------------------
    print(f"visuals.csv   : {args.visuals}")
    print(f"beats         : {len(order)}")
    print(f"image moments : {len(per_moment)}")
    print(f"words         : {words}  ({words / max(1, len(per_moment)):.1f} per moment)")
    print(f"narration     : {body:.1f}s @ {args.wps} wps  +  {gaps:.1f}s gaps")
    print(f"EST RUNTIME   : {int(total // 60)}:{total % 60:04.1f}  ({total:.1f}s)")
    if coverage:
        print(f"script match  : {coverage['covered']}/{coverage['narration_words']} narration "
              f"words covered by moments, {coverage['unused']} left over")
    else:
        print("script match  : (pass --narration narration.txt to check)")

    if coverage and coverage["unmatched"]:
        hard.append("moments that do not appear word-for-word in narration.txt: "
                    + ", ".join(coverage["unmatched"][:12])
                    + (" ..." if len(coverage["unmatched"]) > 12 else ""))
    if coverage and coverage["unused"] > max(8, 0.02 * coverage["narration_words"]):
        soft.append(f"{coverage['unused']} narration words are spoken under no moment "
                    f"(they will land on whatever image is current)")

    print()
    if hard:
        print("HARD PROBLEMS (would break tts / stitch):")
        for h in hard:
            print("  x " + h)
    if soft:
        print("warnings:")
        for s in soft[:20]:
            print("  - " + s)
        if len(soft) > 20:
            print(f"  ... and {len(soft) - 20} more")
    if not hard and not soft:
        print("clean: every moment is speakable, sequential, and 2.5-6.5s long.")
    sys.exit(1 if hard else 0)


if __name__ == "__main__":
    main()
