"""Stage 5: beats.jsonl -> beats_with_timing.json, moments_timing.json, sfx_cues.csv.

--simulate estimates duration from word count (sandbox; no edge-tts / no internet).
Without --simulate it uses edge-tts (Kaggle) and probes the real audio length.
One audio file per beat is always written; narration.wav is the concatenated track.
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import subprocess

from .util import SR, ffmpeg_exe, hms, probe_duration, run, write_silence

DEFAULT_WPS = 2.75
DEFAULT_VOICE = "en-US-AndrewNeural"


def rate_factor(rate: str) -> float:
    try:
        return 1.0 + float(str(rate).strip().replace("%", "")) / 100.0
    except Exception:
        return 1.0


def words(text: str) -> int:
    return len(text.split())


def load_voices(path: str | None) -> dict:
    if not path or not os.path.exists(path):
        return {"default": {"voice": DEFAULT_VOICE, "rate": "+0%"}, "beats": {}}
    with open(path, encoding="utf-8") as f:
        v = json.load(f)
    v.setdefault("default", {"voice": DEFAULT_VOICE, "rate": "+0%"})
    v.setdefault("beats", {})
    return v


def read_visuals(path: str) -> dict:
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[(int(r["slide_id"]), int(r["moment"]))] = {
                "moment_text": r["moment_text"].strip(),
                "visual_prompt": r["visual_prompt"].strip(),
            }
    return out


def synth_edge(text: str, voice: str, rate: str, out_mp3: str) -> None:
    import edge_tts

    async def go():
        await edge_tts.Communicate(text, voice, rate=rate).save(out_mp3)

    asyncio.run(go())


def to_wav(src: str, dst: str) -> None:
    run([ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error", "-i", src,
         "-ar", str(SR), "-ac", "1", dst])


def concat_wavs(parts: list[str], out: str) -> None:
    lst = os.path.join(os.path.dirname(os.path.abspath(out)), "_audio_concat.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for p in parts:
            safe = os.path.abspath(p).replace("'", "'\\''")
            f.write(f"file '{safe}'\n")
    run([ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", lst,
         "-c:a", "pcm_s16le", "-ar", str(SR), "-ac", "1", out])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--beats", required=True)
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--visuals", default="visuals.csv")
    ap.add_argument("--voices", default=None)
    ap.add_argument("--simulate", action="store_true")
    ap.add_argument("--wps", type=float, default=DEFAULT_WPS)
    ap.add_argument("--fps", type=int, default=30)
    args = ap.parse_args()

    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    beats = [json.loads(l) for l in open(args.beats, encoding="utf-8") if l.strip()]
    voices = load_voices(args.voices)
    visuals = read_visuals(args.visuals)

    timeline, all_moments, cues, wav_parts = [], [], [], []
    t = 0.0

    for b in beats:
        sid = int(b.get("slide_id", b.get("beat")))
        spec = dict(voices["default"])
        spec.update(voices["beats"].get(str(sid), {}))
        spec.update(voices["beats"].get(sid, {}))  # tolerate integer keys
        voice = spec.get("voice", DEFAULT_VOICE)
        rate = str(spec.get("rate", "+0%"))
        gap = float(spec.get("gap_before", 0) or 0)
        text = b.get("text") or " ".join(m["text"] for m in b["moments"])

        if gap > 0:
            gap_wav = os.path.join(out_dir, f"_gap{sid:02d}.wav")
            write_silence(gap_wav, gap, SR)
            wav_parts.append(gap_wav)
            t += gap

        if args.simulate:
            dur = words(text) / (args.wps * rate_factor(rate))
            audio = os.path.join(out_dir, f"beat{sid:02d}.wav")
            write_silence(audio, dur, SR)
            wav_parts.append(audio)
        else:
            mp3 = os.path.join(out_dir, f"beat{sid:02d}.mp3")
            synth_edge(text, voice, rate, mp3)
            dur = probe_duration(mp3)
            audio = os.path.join(out_dir, f"beat{sid:02d}.wav")
            to_wav(mp3, audio)
            wav_parts.append(audio)

        start, end = t, t + dur
        wc = [max(1, words(m["text"])) for m in b["moments"]]
        total_w = sum(wc)
        acc, moments = 0, []
        for i, m in enumerate(b["moments"]):
            mstart = start + dur * (acc / total_w)
            acc += wc[i]
            mend = start + dur * (acc / total_w)
            key = f"beat{sid:02d}m{int(m['moment']):02d}"
            v = visuals.get((sid, int(m["moment"])), {})
            rec = {"key": key, "beat": sid, "moment": int(m["moment"]),
                   "start": round(mstart, 4), "end": round(mend, 4),
                   "duration": round(mend - mstart, 4),
                   "text": m["text"],
                   "visual_prompt": v.get("visual_prompt", m.get("visual_prompt", ""))}
            moments.append(rec)
            all_moments.append(rec)

        sfxspec = spec.get("sfx")
        if sfxspec:
            items = sfxspec if isinstance(sfxspec, list) else [{"sound": str(sfxspec)}]
            for it in items:
                if isinstance(it, str):
                    it = {"sound": it}
                sound = it["sound"]
                if "at_moment" in it:
                    mm = next((x for x in moments
                               if x["moment"] == int(it["at_moment"])), None)
                    ct = mm["start"] if mm else start
                else:
                    ct = start + float(it.get("at", 0.0))
                cues.append({"time": round(ct, 4), "sound": sound,
                             "gain": it.get("gain", 1.0)})

        timeline.append({"beat": sid, "slide_id": sid, "key": f"beat{sid:02d}",
                         "audio": os.path.basename(audio), "start": round(start, 4),
                         "end": round(end, 4), "duration": round(dur, 4),
                         "gap_before": gap, "voice": voice, "rate": rate,
                         "text": text, "moments": moments})
        t = end

    narration = os.path.join(out_dir, "narration.wav")
    concat_wavs(wav_parts, narration)

    timing = {"fps": args.fps, "simulate": args.simulate, "wps": args.wps,
              "total_duration": round(t, 4), "narration": "narration.wav",
              "beats": timeline}
    with open(os.path.join(out_dir, "beats_with_timing.json"), "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "moments_timing.json"), "w", encoding="utf-8") as f:
        json.dump({m["key"]: m for m in all_moments}, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "sfx_cues.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["time", "sound", "gain"])
        w.writeheader()
        for c in sorted(cues, key=lambda x: x["time"]):
            w.writerow(c)

    print(f"[tts_multi] mode={'SIMULATE' if args.simulate else 'edge-tts'} "
          f"beats={len(timeline)} moments={len(all_moments)} sfx_cues={len(cues)}")
    print(f"[tts_multi] RUNTIME = {hms(t)}  ({t:.2f} s)  "
          f"= {int(t)//60}m{int(t)%60:02d}s at {args.fps} fps")


if __name__ == "__main__":
    main()
