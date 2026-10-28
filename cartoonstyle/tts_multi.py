"""Multi-voice narration: one segment per beat, each cast to its own voice.

Why this exists: `tts.py` reads the whole script as ONE continuous take, which
gives perfect prosody but only one voice. Episodes that contain characters (a
voice through a door, a neighbour shouting) need several. This module keeps the
word-locked timing model intact by synthesizing per beat, then concatenating
with explicit silence gaps and offsetting every word time by its segment start.

Everything downstream is identical: the same `beats_with_timing.json`
`moments_timing.json` and `narration.mp3` that stitch.py reads.

Cast file (`voices.json`, lives in the episode dir):

    {
      "default": {"voice": "en-US-AndrewNeural", "rate": "+10%"},
      "beats": {
        "1": {"voice": "en-GB-RyanNeural", "gap_before": 1.5, "sfx": "knock x3"},
        "2": {"voice": "en-GB-RyanNeural", "gap_before": 1.5, "sfx": "knock x3"},
        "3": {"gap_before": 0.6},
        "9": {"voice": "en-GB-SoniaNeural", "rate": "+0%", "gap_before": 0.3}
      }
    }

`gap_before` is filled with real silence, so any on-screen knock that the editor
adds later has a home. Because the silence is *inside* the render, the picture
stays in sync with the words either way.

`sfx` is documentation only: it is exported to `sfx_cues.csv` with absolute
times so the editor knows exactly where to drop the knock without moving
anything.

Usage (Kaggle or local, inside the repo):
    python3 -m cartoonstyle.tts_multi --beats <dir>/beats.jsonl --out-dir <dir> \
        --visuals <dir>/visuals.csv --voices <dir>/voices.json

    # no network? --simulate makes silence + evenly spaced word times so the
    # whole stitch/package path can be exercised end to end.
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from .tts import (
    audio_duration,
    finalize,
    load_beats,
    strip_sfx,
)


def _ffmpeg() -> str:
    """ffmpeg binary: PATH first, then imageio-ffmpeg's bundled build."""
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def ff() -> str:
    return _ffmpeg()


def silence_wav(dest: Path, seconds: float, rate: int = 24000) -> Path:
    subprocess.run([ff(), "-y", "-loglevel", "error", "-f", "lavfi",
                    "-i", f"anullsrc=r={rate}:cl=mono", "-t", f"{seconds:.3f}",
                    "-c:a", "pcm_s16le", str(dest)], check=True)
    return dest


def to_wav(src: Path, dest: Path, rate: int = 24000) -> Path:
    subprocess.run([ff(), "-y", "-loglevel", "error", "-i", str(src),
                    "-ar", str(rate), "-ac", "1", "-c:a", "pcm_s16le", str(dest)],
                   check=True)
    return dest


async def synth_segment(text: str, voice: str, rate: str, dest: Path) -> list[dict]:
    """One beat, one voice. Returns word events timed from the segment start."""
    import edge_tts

    try:
        comm = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    except TypeError:  # edge-tts < 7 has no boundary kwarg and always sends words
        comm = edge_tts.Communicate(text, voice, rate=rate)

    audio = bytearray()
    words: list[dict] = []
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            audio += chunk["data"]
        elif chunk["type"] == "WordBoundary":
            words.append({"w": chunk["text"], "t": chunk["offset"] / 1e7})
    if not words:
        raise SystemExit(f"edge-tts returned 0 WordBoundary events for voice {voice}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(bytes(audio))
    return words


def simulate_segment(text: str, dest: Path, wps: float = 2.75) -> list[dict]:
    """Offline stand-in: silence of the right length + evenly spaced words."""
    toks = text.split()
    words = [{"w": t, "t": round(i / wps, 3)} for i, t in enumerate(toks)]
    dur = len(toks) / wps + 0.25
    silence_mp3(dest, dur)
    return words


def silence_mp3(dest: Path, seconds: float, rate: int = 24000) -> Path:
    subprocess.run([ff(), "-y", "-loglevel", "error", "-f", "lavfi",
                    "-i", f"anullsrc=r={rate}:cl=mono", "-t", f"{seconds:.3f}",
                    "-c:a", "libmp3lame", "-q:a", "6", str(dest)], check=True)
    return dest


def load_cast(path: Path) -> dict:
    if not path.exists():
        return {"default": {}, "beats": {}}
    cast = json.loads(path.read_text(encoding="utf-8"))
    cast.setdefault("default", {})
    cast.setdefault("beats", {})
    return cast


def main() -> None:
    ap = argparse.ArgumentParser(description="multi-voice narration with word timings")
    ap.add_argument("--beats", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--visuals", default="")
    ap.add_argument("--voices", default="", help="voices.json cast file")
    ap.add_argument("--voice", default="en-US-AndrewNeural", help="default narrator")
    ap.add_argument("--rate", default="+10%")  # picked pace, per voice json
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--simulate", action="store_true",
                    help="no network: silence + evenly spaced word times")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    items = load_beats(args.beats)
    spoken = {int(b["beat"]): strip_sfx(b["text"]) for b in items}
    cast = load_cast(Path(args.voices)) if args.voices else {"default": {}, "beats": {}}
    default = {"voice": args.voice, "rate": args.rate,
               "gap_before": 0.18, **cast.get("default", {})}

    narr = out_dir / "narration.mp3"
    print(f"[tts] {len(items)} beats | multi-voice | default {default['voice']} "
          f"{default['rate']}" + (" | SIMULATED" if args.simulate else ""), flush=True)

    work = Path(tempfile.mkdtemp(prefix="ttsmulti_"))
    parts: list[Path] = []
    gaps: list[float] = []
    global_words: list[dict] = []
    clock = 0.0
    cues: list[dict] = []
    voices_used: dict[int, str] = {}

    for b in items:
        beat = int(b["beat"])
        cfg = {**default, **cast["beats"].get(str(beat), {})}
        voice = cfg.get("voice", default["voice"])
        rate = cfg.get("rate", default["rate"])
        gap = float(cfg.get("gap_before", 0.0))

        if gap > 0:
            parts.append(silence_wav(work / f"gap{beat:02d}.wav", gap))
            gaps.append(gap)
            clock += gap
        else:
            gaps.append(0.0)

        seg_mp3 = work / f"beat{beat:02d}.mp3"
        if args.simulate:
            words = simulate_segment(spoken[beat], seg_mp3)
        else:
            words = asyncio.run(synth_segment(spoken[beat], voice, rate, seg_mp3))

        seg_wav = to_wav(seg_mp3, work / f"beat{beat:02d}.wav")
        parts.append(seg_wav)
        seg_dur = audio_duration(str(seg_wav))

        for w in words:
            global_words.append({"w": w["w"], "t": round(clock + w["t"], 3)})
        voices_used[beat] = voice

        cue = cfg.get("sfx", "")
        if cue:
            cues.append({"time": round(clock - gap, 3), "beat": beat, "sfx": cue})
        clock += seg_dur
        print(f"[tts] beat {beat:02d} {voice:22s} gap {gap:4.2f}s  {seg_dur:6.2f}s  "
              f"{len(words):3d} words", flush=True)

    if cues:
        with open(out_dir / "sfx_cues.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["time", "beat", "sfx"])
            w.writeheader()
            w.writerows(cues)
        print(f"[tts] {len(cues)} sfx cues -> sfx_cues.csv", flush=True)

    # concat all wav parts into one take, then encode to mp3
    lst = work / "parts.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    full_wav = work / "narration.wav"
    subprocess.run([ff(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(lst), "-c:a", "pcm_s16le", str(full_wav)], check=True)
    subprocess.run([ff(), "-y", "-loglevel", "error", "-i", str(full_wav),
                    "-c:a", "libmp3lame", "-q:a", "4", str(narr)], check=True)

    total = audio_duration(str(narr))
    print(f"[tts] cast: " + ", ".join(
        f"beat{k:02d}={v}" for k, v in sorted(voices_used.items())), flush=True)

    finalize(items, spoken, global_words, total, out_dir, args.visuals, args.force, narr)
    shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
