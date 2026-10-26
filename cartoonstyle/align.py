"""Word-align a pre-supplied narration track.

Why this exists
---------------
The original pipeline got word timings for free from edge-tts WordBoundary
events, which locked every image cut to the exact spoken word. edge-tts voices
are serviceable but robotic; better TTS (or a human read) gives no timings.

This module recovers them: it runs forced alignment over whatever audio you
supply and emits `words.json` in the same shape the matcher already consumes:

    [{"w": "crowd", "t": 1.234}, ...]

`tts.py --words-json words.json` then does all the moment matching exactly as
before. Same matching code, different timing source - no second code path.

Backends
--------
1. faster-whisper (preferred). Word-level timestamps. Runs on Kaggle's GPU,
   or CPU with int8 for a 3-minute file. Model weights come from HuggingFace,
   so this needs full internet (Kaggle has it; the build sandbox does not).
2. chunks (fallback). If whisper is unavailable, distribute each audio chunk's
   measured span across its words by length. Monotonic and gapless, but cuts
   inside a beat can drift by a few hundred ms. Clearly reported.

Usage
-----
    python -m cartoonstyle.align \
        --audio narration.mp3 \
        --chunks narration_chunks.json \
        --out words.json
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def audio_duration(path: str) -> float:
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        out = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", path],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return float(out)
    # fallback: parse ffmpeg's own stderr (no ffprobe on this box)
    ff = shutil.which("ffmpeg")
    if ff:
        err = subprocess.run([ff, "-i", path, "-f", "null", "-"],
                             capture_output=True, text=True).stderr
        for line in reversed(err.splitlines()):
            if "time=" in line:
                h, m, s = line.split("time=")[1].split()[0].split(":")
                return int(h) * 3600 + int(m) * 60 + float(s)
    raise SystemExit("neither ffprobe nor ffmpeg could measure " + path)

def _clean(tok: str) -> str:
    return tok.strip().strip(".,!?;:\"'")


def align_whisper(audio: str, model_size: str) -> list[dict] | None:
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except Exception as exc:  # noqa: BLE001
        print(f"[align] faster-whisper unavailable ({exc})", flush=True)
        return None
    try:
        model = WhisperModel(model_size, device="auto", compute_type="int8")
        segments, info = model.transcribe(
            audio, language="en", word_timestamps=True,
            vad_filter=False, beam_size=5,
        )
        words: list[dict] = []
        for seg in segments:
            for w in (seg.words or []):
                tok = _clean(w.word)
                if tok:
                    words.append({"w": tok, "t": round(float(w.start), 3)})
        print(f"[align] whisper {model_size}: {len(words)} words "
              f"({getattr(info, 'duration', 0):.1f}s audio)", flush=True)
        return words or None
    except Exception as exc:  # noqa: BLE001
        print(f"[align] whisper failed ({exc})", flush=True)
        return None


def align_chunks(chunks: list[dict], total: float) -> list[dict]:
    """Fallback: spread each chunk's measured span across its own words."""
    words: list[dict] = []
    for c in chunks:
        toks = [t for t in (_clean(t) for t in re.findall(r"\S+", c["text"])) if t]
        if not toks:
            continue
        start, end = float(c["start"]), float(c["start"]) + float(c["sec"])
        weights = [max(3, len(t)) for t in toks]  # crude: longer word, longer slot
        span = end - start
        acc = 0.0
        for tok, w in zip(toks, weights):
            words.append({"w": tok, "t": round(start + span * (acc / sum(weights)), 3)})
            acc += w
    if words and words[-1]["t"] > total:
        words[-1]["t"] = max(0.0, total - 0.1)
    return words


def main() -> int:
    ap = argparse.ArgumentParser(description="recover word timings for a pre-made narration track")
    ap.add_argument("--audio", required=True, help="narration mp3/wav to align")
    ap.add_argument("--chunks", default="", help="narration_chunks.json (fallback timing)")
    ap.add_argument("--out", default="words.json")
    ap.add_argument("--model", default="small.en", help="faster-whisper model size")
    ap.add_argument("--force-fallback", action="store_true", help="skip whisper")
    args = ap.parse_args()

    if not Path(args.audio).exists():
        raise SystemExit(f"audio not found: {args.audio}")
    total = audio_duration(args.audio)
    print(f"[align] {args.audio} -> {total:.2f}s", flush=True)

    words = None if args.force_fallback else align_whisper(args.audio, args.model)

    if words is None:
        if not args.chunks or not Path(args.chunks).exists():
            print("[align] ERROR: no whisper and no --chunks manifest; cannot time audio",
                  file=sys.stderr)
            return 1
        chunks = json.loads(Path(args.chunks).read_text(encoding="utf-8"))
        words = align_chunks(chunks, total)
        print(f"[align] FALLBACK: {len(words)} words estimated by chunk span "
              f"(intra-beat cuts may drift)", flush=True)

    Path(args.out).write_text(json.dumps(words, indent=0), encoding="utf-8")
    print(f"[align] wrote {len(words)} words -> {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
