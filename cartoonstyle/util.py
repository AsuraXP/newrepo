"""Small shared helpers. Falls back to imageio_ffmpeg when system ffmpeg is absent."""
from __future__ import annotations

import os
import re
import subprocess
import wave

SR = 44100


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def probe_duration(path: str) -> float:
    """Duration in seconds, via ffprobe if present, else parsing ffmpeg's banner."""
    ff = ffmpeg_exe()
    probe = os.path.join(os.path.dirname(ff), "ffprobe")
    if not os.path.exists(probe):
        probe = "ffprobe"
    try:
        out = subprocess.run(
            [probe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, check=True).stdout.strip()
        if out:
            return float(out)
    except Exception:
        pass
    res = subprocess.run([ff, "-hide_banner", "-i", path, "-f", "null", "-"],
                         capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", res.stderr)
    if not m:
        raise RuntimeError(f"could not probe duration of {path}: {res.stderr[-800:]}")
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def write_silence(path: str, seconds: float, rate: int = SR) -> None:
    n = max(0, int(round(seconds * rate)))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        chunk = b"\x00\x00" * min(n, rate)
        left = n
        while left > 0:
            take = min(left, rate)
            w.writeframes(chunk[:take * 2])
            left -= take


def hms(seconds: float) -> str:
    m, s = divmod(seconds, 60)
    return f"{int(m)}m{s:05.2f}s"


def run(cmd: list[str], quiet: bool = True) -> subprocess.CompletedProcess:
    if quiet:
        return subprocess.run(cmd, check=True, capture_output=True, text=True)
    return subprocess.run(cmd, check=True)
