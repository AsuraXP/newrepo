#!/usr/bin/env python3
"""Voice rate audition - hear one narrator at several speeds, pick one, get the
projected runtime for the whole script.

Standalone. Needs only `edge-tts` and an ffmpeg (system, or imageio-ffmpeg).

What it does
  1. Speaks the same sample text at each rate you ask for.
  2. Measures the real spoken words-per-second of each take.
  3. Projects the full script's runtime at each rate, using the real word
     count of your script (so "+8% puts Episode 1 at 4:44" is arithmetic, not
     a guess from a different passage).
  4. Builds ONE audition mp3, each take announced by the narrator at that
     rate, so you can hear the pace instead of reading a table.
  5. Zips the lot with the table, prints a download line.

Usage (Kaggle)
  !pip -q install edge-tts imageio-ffmpeg
  !python voice_rate_audition.py --text-file script.md
  !python voice_rate_audition.py --text-file script.md --rates 0,+5,+8,+12
  !python voice_rate_audition.py --rates="-5,0,+8"     # note the = for negatives

Fallback if edge-tts is having a bad day
  !python voice_rate_audition.py --simulate
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

VOICE = "en-US-AndrewNeural"
DEFAULT_RATES = ["-5", "0", "+5", "+8", "+10", "+12", "+15"]
SAMPLE_WORDS = 140
SR = 24000
GAP = 0.8

# Used only when no --text-file is given. Plain narration rhythm, no tricks.
FALLBACK_TEXT = (
    "You know this room better than your own face. Every creak has a reason. "
    "Every shadow has a name. At eleven fifty-two the wifi dies, and you do "
    "what you always do: you unplug the router, wait thirty seconds, plug it "
    "back in. It comes back. Then it goes again. The phone still has signal, "
    "and you do not notice that it is the strange part for another eleven "
    "minutes. At eleven fifty-nine a video arrives. Twelve seconds long. "
    "Tilted, dark, and completely quiet."
)


# ---------------------------------------------------------------- audio tools
def ffmpeg_bin() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        raise SystemExit("no ffmpeg: `pip install imageio-ffmpeg` or use --simulate")


def duration(path: Path) -> float:
    probe = shutil.which("ffprobe")
    if probe:
        out = subprocess.run(
            [probe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(path)],
            capture_output=True, text=True, check=True).stdout.strip()
        return float(out)
    ff = ffmpeg_bin()
    err = subprocess.run([ff, "-i", str(path), "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    for line in reversed(err.splitlines()):
        if "time=" in line:
            h, m, s = line.split("time=")[1].split()[0].split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise SystemExit(f"could not measure {path}")


def to_pcm(src: Path) -> bytes:
    """Decode to raw 24k mono s16le, so takes can be joined sample-exactly."""
    return subprocess.run(
        [ffmpeg_bin(), "-v", "error", "-i", str(src),
         "-f", "s16le", "-acodec", "pcm_s16le", "-ar", str(SR), "-ac", "1", "-"],
        capture_output=True, check=True).stdout


def pcm_to_mp3(pcm: bytes, dest: Path) -> None:
    subprocess.run(
        [ffmpeg_bin(), "-v", "error", "-y",
         "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-",
         "-codec:a", "libmp3lame", "-b:a", "96k", str(dest)],
        input=pcm, check=True)


SILENCE = b"\x00\x00" * int(SR * GAP)


# ------------------------------------------------------------------- synth
async def _say(text: str, rate: str, dest: Path) -> None:
    import edge_tts
    last = None
    for attempt in range(3):
        try:
            await edge_tts.Communicate(text, VOICE, rate=f"{rate}%").save(str(dest))
            if dest.exists() and dest.stat().st_size > 1000:
                return
        except Exception as e:                      # noqa: BLE001
            last = e
            await asyncio.sleep(2 + attempt * 3)
    raise SystemExit(f"edge-tts failed for rate {rate}%: {last}")


def synth(text: str, rate: str, dest: Path, simulate: bool) -> float:
    if simulate:
        words = len(text.split())
        # edge-tts Andrew runs ~2.75 wps at +0%, near-linear thereafter
        wps = 2.75 * (1 + int(rate) / 100.0)
        pcm = b"\x00\x00" * int(SR * words / wps)
        pcm_to_mp3(pcm, dest)
        return duration(dest)
    asyncio.run(_say(text, rate, dest))
    return duration(dest)


# -------------------------------------------------------------------- main
def main() -> None:
    global VOICE
    ap = argparse.ArgumentParser()
    ap.add_argument("--text-file", help="script.md / any .txt - its FULL word "
                                        "count drives the projected runtime")
    ap.add_argument("--rates", default=",".join(DEFAULT_RATES),
                    help='comma list, e.g. "0,+5,+8,+12" (default: wide sweep)')
    ap.add_argument("--voice", default=VOICE)
    ap.add_argument("--out-dir", default="rate_test")
    ap.add_argument("--sample-words", type=int, default=SAMPLE_WORDS)
    ap.add_argument("--simulate", action="store_true")
    args = ap.parse_args()

    VOICE = args.voice
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rates = [r.strip().lstrip("+") if r.strip().startswith("+") else r.strip()
             for r in args.rates.split(",") if r.strip()]
    rates = [r.replace("%", "") for r in rates]

    full_text = Path(args.text_file).read_text(encoding="utf-8") if args.text_file else FALLBACK_TEXT
    full_words = len(full_text.split())
    sample = " ".join(full_text.split()[: args.sample_words])
    sample_words = len(sample.split())

    print(f"[rate-test] voice {VOICE} | {len(rates)} rates | sample {sample_words} w"
          f" | full script {full_words} w"
          + ("" if args.text_file else "  (FALLBACK text - pass --text-file for"
                                       " real projections)"), flush=True)
    if args.simulate:
        print("[rate-test] SIMULATE - no audio is really spoken, plumbing only",
              flush=True)

    rows, pieces = [], []
    for i, r in enumerate(rates):
        label = (f"Rate {r} percent." if r != "0"
                 else "Rate zero percent, the default.")
        slug = f"{'p' if not r.startswith('-') else 'm'}{r.lstrip('+-').zfill(2)}"
        take = out / f"rate_{slug}.mp3"
        dur = synth(sample, r, take, args.simulate)
        wps = sample_words / dur
        proj = full_words / wps
        rows.append({"rate": f"{r}%", "file": take.name, "sample_s": round(dur, 2),
                     "words_per_sec": round(wps, 3),
                     "full_script_hms": hms(proj), "full_script_s": round(proj, 1)})
        print(f"  {r:>4}%  sample {dur:5.1f}s  {wps:4.2f} wps"
              f"  -> full script {hms(proj)}", flush=True)

        spoken_label = out / f"_label_{slug}.mp3"
        synth(label, "0", spoken_label, args.simulate)
        pieces += [to_pcm(spoken_label), SILENCE, to_pcm(take), SILENCE]
        spoken_label.unlink(missing_ok=True)

    audition = out / "audition.mp3"
    pcm_to_mp3(b"".join(pieces), audition)

    base = next((r for r in rows if r["rate"] == "0%"), rows[0])
    print(f"\n  {base['rate']} baseline = {base['full_script_hms']}")
    for r in rows:
        d = r["full_script_s"] - base["full_script_s"]
        r["vs_0pct_s"] = round(d, 1)
        print(f"  {r['rate']:>5}  full {r['full_script_hms']:>7}"
              f"   {d:+6.1f}s vs +0%")

    (out / "results.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    with (out / "results.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    readme = ["RATE AUDITION - " + VOICE, "",
              f"sample: {sample_words} words   full script: {full_words} words", "",
              f"{'rate':>6} {'sample':>8} {'wps':>6} {'full script':>12} {'vs 0%':>8}"]
    for r in rows:
        readme.append(f"{r['rate']:>6} {r['sample_s']:>7.1f}s {r['words_per_sec']:>6.2f}"
                      f" {r['full_script_hms']:>12} {r['vs_0pct_s']:>+7.1f}s")
    readme += ["", f"apply the winner with:  --rate +N%   (cartoonstyle.tts)",
               "audition.mp3 plays every rate in that order, announced.",
               "rate_*.mp3 is each take on its own.", "",
               "Projection is sample-measured, not a rule of thumb. Still confirm",
               "the winner on the real script before committing to it."]
    (out / "README.txt").write_text("\n".join(readme), encoding="utf-8")

    zp = out / "rate_audition.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(out.iterdir()):
            if f.is_file() and f != zp:
                z.write(f, f.name)
    print(f"\n[rate-test] {zp}  ({zp.stat().st_size/1e6:.1f} MB)")
    print("contents:", ", ".join(sorted(i.filename for i in zipfile.ZipFile(zp).infolist())))
    print(f"\nfrom IPython.display import FileLink; FileLink('{zp.resolve()}')")


def hms(s: float) -> str:
    return f"{int(s)//60}:{int(s)%60:02d}"


if __name__ == "__main__":
    sys.exit(main())
