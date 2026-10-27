#!/bin/bash
# =============================================================================
# one-shot Kaggle build for any episode in this repo.
#
# USAGE (two cells in a Kaggle notebook):
#   !git clone --depth 1 --branch <branch> https://github.com/AsuraXP/newrepo.git
#   !bash newrepo/run_video_kaggle.sh <slug>
#
# <branch> is the arena/<hash>-newrepo branch the agent is working on. It is
# printed at the end of every agent report; it is NOT main (main carries the
# tooling only, episodes live on their session branch).
#
# Then, in a third cell, print the download link:
#   import os; from IPython.display import FileLink, display
#   z = "/kaggle/working/<slug>_DELIVERABLE.zip"; assert os.path.exists(z), z
#   print(os.path.getsize(z)/1e6, "MB"); display(FileLink(z))
# (a FileLink is only valid while the Kaggle session is alive - see WORKFLOW.md)
#
# Optional env overrides:
#   VIDEO_DIR=examples/apoc_day1_video   OUT_DIR=/kaggle/working
#   VOICE=en-US-AndrewNeural             RATE=+0%
#   SKIP_TTS=1        reuse cached narration.mp3 + beats_with_timing.json (no pip, no edge-tts)
#   NARRATION_MODE=prebuilt   use a committed narration.mp3 + forced alignment
#   ZIP_NAME=custom_name      BRAND_WORDS="word1,word2"  branding guard
#   CAPTIONS=1        burn word-locked subtitles
#
# Multi-voice: drop a voices.json in the episode dir. The runner then switches
# to cartoonstyle.tts_multi (one segment per beat, per-beat voices, real silence
# gaps). Any beat with an "sfx" field emits sfx_cues.csv; sfx.wav is synthesized
# and mixed at stitch time automatically.
#
# Output: $OUT_DIR/<slug>_DELIVERABLE.zip  =  <slug>.mp4 + thumbnail + title_description.txt
#         (+ script.md / metadata.json when the episode ships them)
# =============================================================================
set -euo pipefail

STAGE="init"
trap 'rc=$?; echo "" >&2; echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" >&2; \
      echo "!!! BUILD FAILED in stage: $STAGE  (line $LINENO, exit $rc)" >&2; \
      echo "!!! nothing was packaged, so the FileLink will not resolve." >&2; \
      echo "!!! re-run with  bash -x newrepo/run_video_kaggle.sh $SLUG  for the full trace" >&2; \
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" >&2' ERR

SLUG="${1:-}"
if [ -z "$SLUG" ]; then
  echo "usage: bash run_video_kaggle.sh <slug>   (e.g. apoc_day1)" >&2
  echo "env:   VIDEO_DIR, OUT_DIR, VOICE, RATE, SKIP_TTS=1, NARRATION_MODE, ZIP_NAME, CAPTIONS=1" >&2
  exit 2
fi

WORK="${OUT_DIR:-/kaggle/working}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VIDEO_DIR="${VIDEO_DIR:-$REPO/examples/${SLUG}_video}"
FRAMES="$VIDEO_DIR/frames"
POOL="$WORK/pool_$SLUG"
VOICE="${VOICE:-en-US-AndrewNeural}"
RATE="${RATE:-+0%}"
ZIP="$WORK/${ZIP_NAME:-${SLUG}}_DELIVERABLE.zip"
CANVAS="${CANVAS:-1376x768}"
BRANCH="$(cd "$REPO" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '(not a git checkout)')"

echo "=== [0/7] Config ==="
echo "   repo      : $REPO"
echo "   branch    : $BRANCH"
echo "   episode   : $VIDEO_DIR"
echo "   work      : $WORK"
echo "   canvas    : $CANVAS   voice: $VOICE $RATE"

# --- [1/7] preflight: fail in 5 seconds, not 5 minutes -----------------------
STAGE="preflight"
echo "=== [1/7] Preflight ==="
missing=0
for f in visuals.csv; do
  [ -f "$VIDEO_DIR/$f" ] || { echo "   MISSING: $VIDEO_DIR/$f"; missing=1; }
done
# thumbnail: either extension is fine
THUMB=""
for ext in jpg jpeg png; do
  for c in "$VIDEO_DIR/thumbnail.$ext"; do
    [ -f "$c" ] && THUMB="$c"
  done
done
if [ -z "$THUMB" ]; then
  echo "   MISSING: $VIDEO_DIR/thumbnail.{jpg,png}"
  echo "            (the agent generates it with type baked in and commits it)"
  missing=1
fi
# title + description: one .txt, either name
YT=""
for cand in "$VIDEO_DIR/title_description.txt" "$VIDEO_DIR/youtube.txt"; do
  [ -f "$cand" ] && YT="$cand"
done
if [ -z "$YT" ]; then
  echo "   MISSING: $VIDEO_DIR/title_description.txt  (title + description + tags)"
  missing=1
fi
[ -d "$FRAMES" ] || { echo "   MISSING: $FRAMES/"; missing=1; }
if [ -f "$VIDEO_DIR/voices.json" ]; then
  python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$VIDEO_DIR/voices.json" \
    || { echo "   BROKEN: voices.json is not valid JSON"; missing=1; }
  echo "   cast      : voices.json (multi-voice -> tts_multi)"
fi
[ "$missing" -eq 0 ] || { echo "!!! preflight failed - fix the above and re-run"; exit 1; }

# every visuals.csv row must have a frame on disk, or stitch silently skips it
python3 - "$VIDEO_DIR" "$FRAMES" <<'PY'
import csv, glob, os, sys
video_dir, frames = sys.argv[1], sys.argv[2]
with open(os.path.join(video_dir, "visuals.csv"), newline="", encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))
expected = ["beat%02dm%02d" % (int(r["slide_id"]), int(r["moment"])) for r in rows]
on_disk = {os.path.basename(p)[:-4].split("_v")[0] for p in glob.glob(os.path.join(frames, "*.png"))}
lost = [k for k in expected if k not in on_disk]
print(f"   frames: {len(expected) - len(lost)}/{len(expected)} moments have an image")
if lost:
    print(f"!!! {len(lost)} moments have NO image: " + ", ".join(lost[:12])
          + (" ..." if len(lost) > 12 else ""))
    print("!!! generating these is the agent's job in the sandbox - stopping before encode")
    sys.exit(1)
PY

# --- [2/7] deps --------------------------------------------------------------
STAGE="deps"
echo "=== [2/7] Deps ==="
if ! command -v ffmpeg >/dev/null 2>&1; then
  (apt-get -qq update && apt-get -qq install -y ffmpeg) || apt-get -qq install -y ffmpeg
fi
if [ "${SKIP_TTS:-0}" = "1" ]; then
  echo "   SKIP_TTS=1 -> reusing cached audio, not installing edge-tts"
  [ -f "$VIDEO_DIR/narration.mp3" ] || { echo "!!! SKIP_TTS=1 but narration.mp3 is missing"; exit 1; }
  [ -f "$VIDEO_DIR/beats_with_timing.json" ] || { echo "!!! SKIP_TTS=1 but beats_with_timing.json is missing"; exit 1; }
  [ -f "$VIDEO_DIR/moments_timing.json" ] || { echo "!!! SKIP_TTS=1 but moments_timing.json is missing"; exit 1; }
else
  pip install -q edge-tts pillow requests
fi

# --- [3/7] spine + gate -----------------------------------------------------
STAGE="beats"
echo "=== [3/7] visuals.csv -> beats.jsonl (+ pacing gate) ==="
cd "$REPO"
python3 -m cartoonstyle.csv_to_beats \
    --visuals "$VIDEO_DIR/visuals.csv" \
    --out "$VIDEO_DIR/beats.jsonl"

PLAN_ARGS=(--visuals "$VIDEO_DIR/visuals.csv")
[ -f "$VIDEO_DIR/narration.txt" ] && PLAN_ARGS+=(--narration "$VIDEO_DIR/narration.txt")
[ -f "$VIDEO_DIR/voices.json" ] && PLAN_ARGS+=(--voices "$VIDEO_DIR/voices.json")
python3 -m cartoonstyle.plan "${PLAN_ARGS[@]}" || {
  echo "!!! plan gate failed: a moment_text is unspeakable or out of sequence."
  echo "!!! fix visuals.csv and re-run - do not spend Kaggle time on a broken spine."
  exit 1
}

# --- [4/7] narration ---------------------------------------------------------
STAGE="narration"
echo "=== [4/7] Narration (word timings) ==="
LOG=/tmp/tts_log_$SLUG.txt
TTS_ARGS=(--beats "$VIDEO_DIR/beats.jsonl" --out-dir "$VIDEO_DIR"
          --visuals "$VIDEO_DIR/visuals.csv" --voice "$VOICE" --rate="$RATE")

if [ -f "$VIDEO_DIR/voices.json" ]; then
  TTS_MODULE=cartoonstyle.tts_multi
  TTS_ARGS+=(--voices "$VIDEO_DIR/voices.json")
  [ "${NARRATION_MODE:-edgetts}" = "prebuilt" ] && \
    echo "   (prebuilt narration is single-voice only - ignoring NARRATION_MODE)"
elif [ "${NARRATION_MODE:-edgetts}" = "prebuilt" ] && [ -f "$VIDEO_DIR/narration.mp3" ]; then
  TTS_MODULE=cartoonstyle.tts
  echo "   prebuilt narration.mp3 -> forced alignment (no edge-tts)"
  pip install -q faster-whisper 2>/dev/null || \
    echo "   (faster-whisper unavailable - align.py will fall back to chunk timing)"
  python3 -m cartoonstyle.align \
      --audio "$VIDEO_DIR/narration.mp3" \
      --chunks "$VIDEO_DIR/narration_chunks.json" \
      --out "$VIDEO_DIR/words.json" \
      --model "${WHISPER_MODEL:-small.en}"
  TTS_ARGS+=(--words-json "$VIDEO_DIR/words.json")
else
  TTS_MODULE=cartoonstyle.tts
  echo "   synthesizing with edge-tts ($VOICE $RATE)"
fi

if [ "${SKIP_TTS:-0}" = "1" ]; then
  # tts_multi always re-synthesizes (no cache probe), so SKIP_TTS means: do not
  # touch the TTS stage at all, just prove the cached timings match the spine.
  echo "   SKIP_TTS=1 -> reusing cached narration, TTS stage skipped"
  python3 - "$VIDEO_DIR" <<'PYVERIFY'
import csv, json, os, sys
d = sys.argv[1]
rows = list(csv.DictReader(open(os.path.join(d, "visuals.csv"), newline="", encoding="utf-8")))
mom = json.load(open(os.path.join(d, "moments_timing.json"), encoding="utf-8"))
want = {"beat%02dm%02d" % (int(r["slide_id"]), int(r["moment"])) for r in rows}
have = {m["key"] for m in mom}
missing = sorted(want - have)
print(f"   cached timings: {len(want) - len(missing)}/{len(want)} moments locked")
if missing:
    print("!!! cached moments_timing.json does not cover: " + ", ".join(missing[:10]))
    sys.exit(1)
PYVERIFY
else
  python3 -m "$TTS_MODULE" "${TTS_ARGS[@]}" 2>&1 | tee "$LOG"
  if ! grep -qE "moments locked.*\[OK\]" "$LOG"; then
    echo "!!! NARRATION DID NOT LOCK ALL MOMENTS - inspect $LOG"
    echo "!!! a moment_text token is not present in the spoken word stream"
    exit 1
  fi
fi

# --- [5/7] frames -> pool at exactly $CANVAS ---------------------------------
STAGE="frames"
echo "=== [5/7] Frames -> pool ($CANVAS) ==="
rm -rf "$POOL"
python3 -m cartoonstyle.prep_frames --frames "$FRAMES" --out "$POOL" --size "$CANVAS"
python3 -m cartoonstyle.prep_frames --frames "$POOL" --out "$POOL" --size "$CANVAS" --check

# --- [6/7] stitch ------------------------------------------------------------
STAGE="stitch"
echo "=== [6/7] Stitch ==="
STITCH_ARGS=(--timing "$VIDEO_DIR/beats_with_timing.json"
             --images-dir "$POOL" --out "$VIDEO_DIR/$SLUG.mp4"
             --pick 0 --fps 30 --canvas "$CANVAS")
[ "${CAPTIONS:-0}" = "1" ] && STITCH_ARGS+=(--captions --caption-method pil)

if [ -f "$VIDEO_DIR/sfx_cues.csv" ] && grep -q . "$VIDEO_DIR/sfx_cues.csv"; then
  echo "   sfx cues found -> synthesizing sfx.wav"
  python3 -m cartoonstyle.sfx --cues "$VIDEO_DIR/sfx_cues.csv" \
      --out "$VIDEO_DIR/sfx.wav" --gain 0.9
  STITCH_ARGS+=(--sfx "$VIDEO_DIR/sfx.wav")
else
  echo "   no sfx cues - narration only"
fi

python3 -m cartoonstyle.stitch "${STITCH_ARGS[@]}"

# verify what came out, instead of trusting the encoder
python3 - "$VIDEO_DIR/$SLUG.mp4" "$CANVAS" <<'PY'
import json, shutil, subprocess, sys
from pathlib import Path
mp4, want = sys.argv[1], sys.argv[2]
ff = shutil.which("ffmpeg")
probe = shutil.which("ffprobe")
if not Path(mp4).exists() or Path(mp4).stat().st_size < 100_000:
    sys.exit(f"!!! {mp4} is missing or suspiciously small")
if probe:
    out = subprocess.run([probe, "-v", "error", "-select_streams", "v:0",
                          "-show_entries", "stream=width,height,codec_name",
                          "-show_entries", "format=duration,size",
                          "-of", "json", mp4], capture_output=True, text=True).stdout
    j = json.loads(out or "{}")
    st = (j.get("streams") or [{}])[0]
    fmt = j.get("format", {})
    got = f'{st.get("width")}x{st.get("height")}'
    print(f"   output: {got} {st.get('codec_name')} "
          f"{float(fmt.get('duration', 0)) / 60:.2f} min "
          f"{int(fmt.get('size', 0)) / 1e6:.1f} MB")
    if got != want:
        sys.exit(f"!!! expected {want}, got {got}")
PY

# --- [7/7] packaging ---------------------------------------------------------
STAGE="package"
echo "=== [7/7] Package ==="

# branding guard: nothing branded in the video or its metadata
if [ -n "${BRAND_WORDS:-}" ]; then
  IFS=',' read -ra BANNED <<< "$BRAND_WORDS"
  bad=0
  for w in "${BANNED[@]}"; do
    w="$(echo "$w" | xargs)"; [ -z "$w" ] && continue
    if grep -rilF "$w" "$VIDEO_DIR" --include="*.csv" --include="*.txt" \
         --include="*.json" --include="*.jsonl" 2>/dev/null | grep -v "beats_with_timing\|moments_timing"; then
      echo "   BRANDED: '$w' appears above - strip it before publishing"
      bad=1
    fi
  done
  [ "$bad" -eq 0 ] && echo "   branding guard: clean"
fi

rm -f "$ZIP"
PKG=("$VIDEO_DIR/$SLUG.mp4" "$THUMB" "$YT")
for f in script.md metadata.json; do
  [ -f "$VIDEO_DIR/$f" ] && PKG+=("$VIDEO_DIR/$f")
done

# normalise the metadata name so the zip always looks the same
if [ "$(basename "$YT")" != "title_description.txt" ]; then
  cp "$YT" "$WORK/title_description.txt"
  PKG[2]="$WORK/title_description.txt"
fi

if command -v zip >/dev/null 2>&1; then
  zip -j -q "$ZIP" "${PKG[@]}"
else
  python3 -c "import sys,zipfile,os; z=zipfile.ZipFile(sys.argv[1],'w',zipfile.ZIP_DEFLATED); [z.write(p, os.path.basename(p)) for p in sys.argv[2:]]" "$ZIP" "${PKG[@]}"
fi

[ -s "$ZIP" ] || { echo "!!! $ZIP was not created"; exit 1; }

echo ""
echo "==========================================="
ls -lh "$ZIP"
python3 -c "import sys,zipfile; [print('  ', i.filename, f'{i.file_size/1048576:.1f} MB') for i in zipfile.ZipFile(sys.argv[1]).infolist()]" "$ZIP"
echo "==========================================="
echo "DONE  (branch: $BRANCH)"
echo "Next cell:"
echo "   import os; from IPython.display import FileLink, display"
echo "   z='$ZIP'; print(f'{os.path.getsize(z)/1e6:.1f} MB'); display(FileLink(z))"
echo "   # FileLink only lives as long as this session. To keep the file, also"
echo "   # copy it to /kaggle/working and use 'Save Version -> Save & Run All'."
