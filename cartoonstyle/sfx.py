"""Stage 6: render sfx_cues.csv into one wav, fully synthesized with the stdlib.

Add new sounds by putting a zero-argument function returning a list of floats
into SOUNDS. Samples are mono at SR Hz, in [-1, 1].
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import random
import wave
from array import array

from .util import SR

# ---------------------------------------------------------------- sound design
def _decay(n: int, sharp: float) -> list[float]:
    return [math.exp(-sharp * i / SR) for i in range(n)]


def _lp_noise(n: int, cutoff: float, seed: int) -> list[float]:
    rnd = random.Random(seed)
    a = math.exp(-2 * math.pi * cutoff / SR)
    out, last = [], 0.0
    for _ in range(n):
        last = a * last + (1 - a) * rnd.uniform(-1, 1)
        out.append(last)
    return out


def knock() -> list[float]:
    n = int(0.20 * SR)
    env = _decay(n, 26)
    noise = _lp_noise(n, 900, 11)
    return [0.75 * e * (0.55 * math.sin(2 * math.pi * 88 * i / SR) + 0.45 * nz)
            for i, (e, nz) in enumerate(zip(env, noise))]


def knock_x3() -> list[float]:
    one = knock()
    gap = int(0.34 * SR)
    out = [0.0] * (len(one) * 3 + gap * 2)
    for k in range(3):
        off = k * (len(one) + gap)
        for i, v in enumerate(one):
            out[off + i] += v * (1.0 - 0.12 * k)
    return out


def thud() -> list[float]:
    n = int(0.38 * SR)
    env = _decay(n, 13)
    noise = _lp_noise(n, 320, 23)
    return [0.9 * e * (0.7 * math.sin(2 * math.pi * 62 * i / SR) + 0.5 * nz)
            for i, (e, nz) in enumerate(zip(env, noise))]


def click() -> list[float]:
    n = int(0.045 * SR)
    env = _decay(n, 150)
    noise = _lp_noise(n, 6500, 31)
    return [0.85 * e * nz for e, nz in zip(env, noise)]


def rumble() -> list[float]:
    n = int(2.6 * SR)
    noise = _lp_noise(n, 110, 47)
    out = []
    for i, nz in enumerate(noise):
        x = i / SR
        env = min(1.0, x / 0.5) * min(1.0, (2.6 - x) / 0.9)
        out.append(0.55 * env * (nz * 2.2 + 0.35 * math.sin(2 * math.pi * 43 * x)))
    return out


SOUNDS = {
    "knock": knock,
    "knock x3": knock_x3,
    "thud": thud,
    "click": click,
    "rumble": rumble,
}


def render(sound: str) -> list[float]:
    key = str(sound).strip().lower()
    if key not in SOUNDS:
        raise KeyError(f"unknown sfx {sound!r}; supported: {sorted(SOUNDS)}")
    return SOUNDS[key]()


# ------------------------------------------------------------------------- CLI
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cues", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gain", type=float, default=0.9)
    ap.add_argument("--duration", type=float, default=0.0,
                    help="pad the wav to this length in seconds")
    args = ap.parse_args()

    with open(args.cues, newline="", encoding="utf-8") as f:
        cues = list(csv.DictReader(f))
    if not cues:
        write_silence_wav(args.out, args.duration)
        print(f"[sfx] no cues -> empty {args.out}")
        return

    length = max(args.duration, 0.0)
    for c in cues:
        t = float(c["time"])
        length = max(length, t + len(render(c["sound"])) / SR + 0.3)
    buf = [0.0] * int(math.ceil(length * SR))

    for c in cues:
        t = float(c["time"])
        samples = render(c["sound"])
        g = float(c.get("gain", 1.0) or 1.0)
        off = int(t * SR)
        for i, v in enumerate(samples):
            if off + i < len(buf):
                buf[off + i] += v * g

    peak = max((abs(v) for v in buf), default=0.0)
    scale = args.gain * (0.95 / peak if peak > 0.95 else 1.0)
    pcm = array("h", (int(max(-1.0, min(1.0, v * scale)) * 32767) for v in buf))
    with wave.open(args.out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"[sfx] {len(cues)} cues -> {args.out} ({length:.2f}s, gain {args.gain})")


def write_silence_wav(path: str, seconds: float) -> None:
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"\x00\x00" * int(seconds * SR))


if __name__ == "__main__":
    main()
