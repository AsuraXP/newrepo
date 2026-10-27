"""Stage 3: visuals.csv -> beats.jsonl (one line per consecutive slide_id run)."""
from __future__ import annotations

import argparse
import csv
import json
import os


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--visuals", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    beats: list[dict] = []
    with open(args.visuals, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sid = int(row["slide_id"])
            moment = int(row["moment"])
            if not beats or beats[-1]["slide_id"] != sid:
                beats.append({"beat": sid, "slide_id": sid, "key": f"beat{sid:02d}",
                              "moments": []})
            beats[-1]["moments"].append({
                "moment": moment,
                "text": row["moment_text"].strip(),
                "visual_prompt": row["visual_prompt"].strip(),
            })
    for b in beats:
        b["text"] = " ".join(m["text"] for m in b["moments"])

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for b in beats:
            f.write(json.dumps(b, ensure_ascii=False) + "\n")
    print(f"[csv_to_beats] {len(beats)} beats / "
          f"{sum(len(b['moments']) for b in beats)} moments -> {args.out}")


if __name__ == "__main__":
    main()
