"""Procedural sound effects, mixed at stitch time.

No downloads, no licences, no missing asset files: every cue here is synthesized
from scratch with the standard library, then written as a 48 kHz mono WAV track
that `stitch.py` mixes under the narration.

Cue times come from `sfx_cues.csv`, which `tts.py` writes from the episode's
`sfx.csv` (key,sfx[,offset] - a sound anchored to an image moment). Because those times are absolute
seconds inside the rendered narration, the knock lands in the gap that was
reserved for it — the picture never drifts.

Supported cues (add to SOUNDS to extend):
    knock       one closed-fist knock on a wooden door
    knock x2    two knocks
    knock x3    three evenly spaced knocks
    thud        a single heavy body-against-door bump
    click       a small latch/switch sound
    rumble      a low distant swell (grid going down, something far away)
    ring        a phone ringing on a hard surface, one burst
    steps       six uneven footfalls, patient, approaching

Usage:
    python3 -m cartoonstyle.sfx --cues <dir>/sfx_cues.csv --out <dir>/sfx.wav
    python3 -m cartoonstyle.sfx --cues ... --out ... --total 351.2
    python3 -m cartoonstyle.sfx --list
"""
from __future__ import annotations

import argparse
import csv
import math
import random
import shutil
import struct
import subprocess
import wave
from pathlib import Path

SR = 48000


def _env(t: float, attack: float, decay: float) -> float:
    """Fast attack, exponential decay. t in seconds since onset."""
    if t < 0:
        return 0.0
    a = min(1.0, t / attack) if attack > 0 else 1.0
    return a * math.exp(-t / decay)


def knock(seed: int = 0, strength: float = 1.0) -> list[float]:
    """A closed fist on wood: low thump + short body resonance + a click."""
    rnd = random.Random(seed)
    dur = 0.22
    n = int(SR * dur)
    out = [0.0] * n
    f0 = 92.0 + rnd.uniform(-8, 8)          # fundamental of the door panel
    f1 = 205.0 + rnd.uniform(-15, 15)       # panel overtone
    for i in range(n):
        t = i / SR
        e = _env(t, 0.0015, 0.055)
        body = math.sin(2 * math.pi * f0 * t) * 0.75
        over = math.sin(2 * math.pi * f1 * t) * 0.28
        # wooden creak: tiny noise burst at the very start
        click = rnd.uniform(-1, 1) * _env(t, 0.0004, 0.006) * 0.35
        out[i] = (body + over) * e * strength + click * strength
    return out


def thud(seed: int = 1, strength: float = 1.0) -> list[float]:
    rnd = random.Random(seed)
    dur = 0.45
    n = int(SR * dur)
    out = [0.0] * n
    for i in range(n):
        t = i / SR
        e = _env(t, 0.003, 0.11)
        low = math.sin(2 * math.pi * 58 * t) * 0.9
        rub = rnd.uniform(-1, 1) * _env(t, 0.001, 0.03) * 0.4
        out[i] = (low + rub) * e * strength
    return out


def click(seed: int = 2, strength: float = 1.0) -> list[float]:
    rnd = random.Random(seed)
    n = int(SR * 0.045)
    out = [0.0] * n
    for i in range(n):
        t = i / SR
        out[i] = rnd.uniform(-1, 1) * _env(t, 0.0002, 0.006) * 0.6 * strength
    return out


def rumble(seed: int = 3, strength: float = 1.0) -> list[float]:
    rnd = random.Random(seed)
    dur = 3.0
    n = int(SR * dur)
    out = [0.0] * n
    ph = 0.0
    for i in range(n):
        t = i / SR
        # slow swell in and out
        env = math.sin(math.pi * min(1.0, t / dur)) ** 2
        ph += 2 * math.pi * (38 + 3 * math.sin(2 * math.pi * 0.3 * t)) / SR
        out[i] = (math.sin(ph) * 0.7 + rnd.uniform(-1, 1) * 0.25) * env * 0.5 * strength
    return out


def ring(seed: int = 4, strength: float = 1.0) -> list[float]:
    """A phone ringing flat on a table: 440+480 Hz, warble, no reverb."""
    rnd = random.Random(seed)
    dur = 1.30
    n = int(SR * dur)
    out = [0.0] * n
    for i in range(n):
        t = i / SR
        # ring cadence: 0.9s of tone, then the handset runs out of breath
        if t > 0.95:
            continue
        warble = 0.55 + 0.45 * math.sin(2 * math.pi * 20.0 * t)
        tone = (math.sin(2 * math.pi * 440.0 * t) * 0.6
                + math.sin(2 * math.pi * 480.0 * t) * 0.4)
        env = _env(t, 0.008, dur) * (1.0 if t < 0.88 else max(0.0, (0.95 - t) / 0.07))
        out[i] = tone * warble * env * 0.95 * strength
    return out


def steps(seed: int = 5, strength: float = 1.0) -> list[float]:
    """Six slow footfalls on a hard floor - the weight wrong, the spacing off."""
    rnd = random.Random(seed)
    buf: list[float] = []
    for k in range(6):
        buf += thud(seed + k, 0.55 * strength)
        buf += gap(rnd.uniform(0.42, 0.72))
    return buf


def gap(seconds: float) -> list[float]:
    return [0.0] * int(SR * seconds)


def concat(*parts: list[float]) -> list[float]:
    out: list[float] = []
    for p in parts:
        out.extend(p)
    return out


def three_knocks(seed: int = 0) -> list[float]:
    return concat(knock(seed), gap(0.33), knock(seed + 1), gap(0.33),
                  knock(seed + 2, strength=0.95))


def two_knocks(seed: int = 0) -> list[float]:
    return concat(knock(seed), gap(0.33), knock(seed + 1))


RENDER = {
    "knock": lambda: knock(0),
    "knock x2": lambda: two_knocks(0),
    "knock x3": lambda: three_knocks(0),
    "thud": lambda: thud(),
    "click": lambda: click(),
    "rumble": lambda: rumble(),
    "ring": lambda: ring(),
    "steps": lambda: steps(),
}


def _ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def narration_seconds(path: Path) -> float:
    ff = _ffmpeg()
    out = subprocess.run([ff, "-i", str(path), "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    for line in reversed(out.splitlines()):
        if "time=" in line:
            h, m, s = line.split("time=")[1].split()[0].split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 0.0


def build(cues: list[tuple[float, str]], total: float, out: Path,
          gain: float = 0.9) -> Path:
    n = int(SR * max(total + 0.5, 1.0))
    track = [0.0] * n
    used = 0
    for at, name in cues:
        key = name.strip().lower()
        fn = RENDER.get(key)
        if fn is None:
            print(f"[sfx] unknown cue {name!r} - skipped (see --list)")
            continue
        buf = fn()
        start = int(at * SR)
        for i, v in enumerate(buf):
            j = start + i
            if 0 <= j < n:
                track[j] += v * gain
        used += 1
        print(f"[sfx] {at:8.2f}s  {key}")
    # soft clip
    peak = max(1e-9, max(abs(v) for v in track))
    norm = min(1.0, 0.98 / peak) if peak > 1.0 else 1.0
    out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(
            struct.pack("<h", int(max(-1.0, min(1.0, v * norm)) * 32767)) for v in track))
    print(f"[sfx] {used} cues -> {out} ({total:.1f}s of timeline)")
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="synthesize a sound-effects track")
    p.add_argument("--cues", default="", help="sfx_cues.csv (time,beat,sfx)")
    p.add_argument("--out", default="sfx.wav")
    p.add_argument("--total", type=float, default=0.0,
                   help="timeline length; falls back to narration.mp3 next to --out")
    p.add_argument("--gain", type=float, default=0.9)
    p.add_argument("--list", action="store_true")
    args = p.parse_args()

    if args.list:
        print("cues:", ", ".join(sorted(RENDER)))
        return
    if not args.cues:
        raise SystemExit("--cues is required (or --list)")

    if not Path(args.cues).exists():
        raise SystemExit(
            f"no cues file at {args.cues}.\n"
            "  This is normal when the episode has no sfx.csv - there is nothing to score.\n"
            "  Add one (key,sfx,offset with key like beat05m03), re-run cartoonstyle.tts,\n"
            "  and sfx_cues.csv will be regenerated from the moment timeline.")

    cues: list[tuple[float, str]] = []
    with open(args.cues, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                cues.append((float(row["time"]), row["sfx"]))
            except (KeyError, ValueError):
                print(f"[sfx] bad cue row: {row}")
    if not cues:
        raise SystemExit("no cues in " + args.cues)   # header-only file: nothing to score

    out = Path(args.out)
    total = args.total
    if total <= 0:
        narr = out.parent / "narration.mp3"
        total = narration_seconds(narr) if narr.exists() else max(t for t, _ in cues) + 6
    build(cues, total, out, args.gain)


if __name__ == "__main__":
    main()
