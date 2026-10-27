"""Stage 8: word-locked image cuts + narration + sfx -> one MP4."""
from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
import tempfile
import textwrap

from PIL import Image, ImageDraw, ImageFont

from .util import ffmpeg_exe, hms


def find_image(images_dir: str, key: str, pick: int):
    """Same glob the spec requires. Missing match = moment silently skipped."""
    pat = os.path.join(images_dir, f"{key}_v{pick:02d}_s*.png")
    hits = sorted(glob.glob(pat))
    return hits[0] if hits else None


def load_font(size: int):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def burn_pil(src: str, dst: str, text: str, size: tuple[int, int]) -> None:
    im = Image.open(src).convert("RGB")
    im = im.resize(size, Image.LANCZOS)
    d = ImageDraw.Draw(im, "RGBA")
    font = load_font(34)
    lines = textwrap.wrap(text, width=48)
    widths = [d.textbbox((0, 0), ln, font=font)[2] for ln in lines]
    box_w = min(size[0] - 80, max(widths) + 44)
    box_h = sum(d.textbbox((0, 0), ln, font=font)[3] for ln in lines) + 22 * len(lines) + 18
    x0, y0 = (size[0] - box_w) // 2, size[1] - box_h - 46
    d.rounded_rectangle([x0, y0, x0 + box_w, y0 + box_h], radius=14, fill=(12, 14, 18, 205))
    y = y0 + 12
    for ln in lines:
        b = d.textbbox((0, 0), ln, font=font)
        d.text(((size[0] - (b[2] - b[0])) // 2, y), ln, font=font, fill=(245, 244, 238, 255))
        y += b[3] + 22
    im.save(dst, "PNG")


def ass_time(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def write_ass(path: str, records: list[dict]) -> None:
    head = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1376\nPlayResY: 768\n"
            "WrapStyle: 2\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, "
            "Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV\n"
            "Style: Default,DejaVu Sans,34,&H00F2F0EA,&H000C0E12,&H800C0E12,-1,3,2,1,2,60,60,52\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write(head)
        for r in records:
            txt = r["text"].replace("\n", " ").replace("{", "(").replace("}", ")")
            f.write(f"Dialogue: 0,{ass_time(r['start'])},{ass_time(r['end'])},"
                    f"Default,,0,0,0,,{txt}\n")


def esc_filter_path(p: str) -> str:
    return p.replace("\\", "/").replace(":", r"\:").replace("'", r"\'")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timing", required=True)
    ap.add_argument("--images-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pick", type=int, default=0)
    ap.add_argument("--sfx", default=None)
    ap.add_argument("--captions", action="store_true")
    ap.add_argument("--caption-method", choices=["ass", "pil"], default="ass")
    ap.add_argument("--qc", default=None)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--no-loudnorm", action="store_true")
    ap.add_argument("--size", default="1376x768")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    tw, th = (int(x) for x in args.size.lower().split("x"))
    timing = json.load(open(args.timing, encoding="utf-8"))
    fps = args.fps or timing.get("fps", 30)
    base = os.path.dirname(os.path.abspath(args.timing))
    narration = os.path.join(base, timing.get("narration", "narration.wav"))

    records = []
    for b in timing["beats"]:
        records.extend(b["moments"])
    print(f"[stitch] {len(records)} moments / timeline {hms(timing['total_duration'])}")

    work = tempfile.mkdtemp(prefix="stitch_")
    frames_txt = os.path.join(work, "frames.txt")
    qc_rows, used = [], []
    cap_records = []
    for r in records:
        hit = find_image(args.images_dir, r["key"], args.pick)
        row = {"key": r["key"], "beat": r["beat"], "moment": r["moment"],
               "start": r["start"], "end": r["end"], "text": r["text"],
               "image": os.path.basename(hit) if hit else None, "status": "ok"}
        if not hit:
            row["status"] = "missing"
            qc_rows.append(row)
            continue
        src_size = Image.open(hit).size
        row["source_size"] = list(src_size)
        src = hit
        if args.captions and args.caption_method == "pil":
            src = os.path.join(work, f"cap_{r['key']}.png")
            burn_pil(hit, src, r["text"], (tw, th))
        if src_size != (tw, th):
            norm = os.path.join(work, f"norm_{r['key']}.png")
            Image.open(src).convert("RGB").resize((tw, th), Image.LANCZOS).save(norm, "PNG")
            src = norm
            row["normalised"] = True
        used.append((src, max(0.04, r["end"] - r["start"])))
        if args.captions and args.caption_method == "ass":
            cap_records.append(r)
        qc_rows.append(row)

    if not used:
        raise SystemExit("[stitch] no frames matched the pool glob - check filenames")
    with open(frames_txt, "w", encoding="utf-8") as f:
        for p, d in used:
            f.write(f"file '{p}'\nduration {d:.4f}\n")
        f.write(f"file '{used[-1][0]}'\n")

    loud = "" if args.no_loudnorm else "loudnorm=I=-14:TP=-1.5:LRA=11,"
    sfx_path = args.sfx
    if sfx_path and not os.path.exists(sfx_path) and not os.path.isabs(sfx_path):
        sfx_path = os.path.join(base, sfx_path)
    has_sfx = bool(sfx_path and os.path.exists(sfx_path))
    audio_filter = (f"[1:a]aresample={44100}[a0];[2:a]aresample={44100}[a1];"
                    f"[a0][a1]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[mix];"
                    f"[mix]{loud}alimiter=limit=0.95[a]") if has_sfx else \
                   f"[1:a]{loud}alimiter=limit=0.95[a]"

    vf = f"scale={tw}:{th}:flags=lanczos,fps={fps}"
    if args.captions and args.caption_method == "ass":
        ass = os.path.join(work, "captions.ass")
        write_ass(ass, cap_records)
        vf += f",subtitles=filename={esc_filter_path(ass)}"
    vf += ",format=yuv420p"

    cmd = [ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
           "-f", "concat", "-safe", "0", "-i", frames_txt,
           "-i", narration]
    if has_sfx:
        cmd += ["-i", sfx_path]
    cmd += ["-filter_complex", audio_filter, "-map", "0:v", "-map", "[a]",
            "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(fps),
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            "-movflags", "+faststart", "-shortest", os.path.abspath(args.out)]

    if args.qc:
        with open(args.qc, "w", encoding="utf-8") as f:
            for row in qc_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    missing = [r["key"] for r in qc_rows if r["status"] == "missing"]
    print(f"[stitch] frames={len(used)} missing={len(missing)} "
          f"captions={args.captions and args.caption_method} loudnorm={not args.no_loudnorm}")
    if missing and len(missing) <= 12:
        print(f"[stitch] WARNING missing frames: {', '.join(missing)}")
    if args.dry_run:
        print("[stitch] dry-run, ffmpeg not executed")
        return
    subprocess.run(cmd, check=True)
    print(f"[stitch] wrote {args.out} ({os.path.getsize(args.out)/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
