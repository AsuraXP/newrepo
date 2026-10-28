#!/bin/bash
# =============================================================================
# CartoonStyle — generic one-shot Kaggle build.
#
# Replaces the per-video run_<slug>_kaggle.sh copies (which hardcode a session
# branch hash and therefore break on every new video).
#
# USAGE (Kaggle notebook cell, run from inside the cloned repo):
#   !git clone --depth 1 --branch <branch> https://github.com/AsuraXP/CartoonStyle.git
#   !bash CartoonStyle/run_video_kaggle.sh <slug>
#
#   e.g.  !bash CartoonStyle/run_video_kaggle.sh apoc_day1
#
# Optional env overrides:
#   VIDEO_DIR=examples/apoc_day1_video   OUT_DIR=/kaggle/working
#   VOICE=en-US-AndrewNeural             RATE=+10%
#   SKIP_TTS=1 (reuse cached narration.mp3 + beats_with_timing.json; no pip)
#
# Multi-voice: drop a voices.json in the episode dir and the runner switches to
# cartoonstyle.tts_multi automatically (one segment per beat, per-beat voices,
# real silence gaps). Any beat with an "sfx" field emits sfx_cues.csv; the
# runner synthesizes sfx.wav (cartoonstyle.sfx) and mixes it at stitch time.
#   ZIP_NAME=custom_name
#
# Output: $OUT_DIR/<slug>_DELIVERABLE.zip
# =============================================================================
set -euo pipefail

# --- Failure reporting ------------------------------------------------------
# set -e exits silently otherwise, and "the zip isn't there" is not a diagnosis.
STAGE="init"
trap 'rc=$?; echo "" >&2; echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" >&2; \
      echo "!!! BUILD FAILED in stage: $STAGE  (line $LINENO, exit $rc)" >&2; \
      echo "!!! nothing was packaged, so the FileLink will not resolve." >&2; \
      echo "!!! re-run with  bash -x run_video_kaggle.sh $SLUG  for the full trace" >&2; \
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" >&2' ERR

SLUG="${1:-}"
if [ -z "$SLUG" ]; then
  echo "usage: bash run_video_kaggle.sh <slug>   (e.g. apoc_day1)" >&2
  exit 2
fi

WORK="${OUT_DIR:-/kaggle/working}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VIDEO_DIR="${VIDEO_DIR:-$REPO/examples/${SLUG}_video}"
FRAMES="$VIDEO_DIR/frames"
IMG_POOL="$WORK/img_pool_$SLUG"
VOICE="${VOICE:-en-US-AndrewNeural}"
RATE="${RATE:-+10%}"
ZIP="$WORK/${ZIP_NAME:-${SLUG}}_DELIVERABLE.zip"

echo "=== [0/6] Config ==="
echo "   repo      : $REPO"
echo "   branch    : $(cd "$REPO" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '(not a git checkout)')"
echo "   video dir : $VIDEO_DIR"
echo "   voice     : $VOICE $RATE"

# --- Preflight: fail in 5 seconds, not 5 minutes -----------------------------
STAGE="preflight"
echo "=== [1/6] Preflight ==="
missing=0
for f in visuals.csv script.md metadata.json youtube.txt; do
  [ -f "$VIDEO_DIR/$f" ] || { echo "   MISSING: $VIDEO_DIR/$f"; missing=1; }
done
if [ ! -f "$VIDEO_DIR/thumbnail.jpg" ]; then
  echo "   MISSING: $VIDEO_DIR/thumbnail.jpg"
  echo "            (the agent generates this in the sandbox and commits it;"
  echo "             Kaggle does not create thumbnails)"
  missing=1
fi
[ -d "$FRAMES" ] || { echo "   MISSING: $FRAMES/"; missing=1; }
if [ -f "$VIDEO_DIR/voices.json" ]; then
  python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$VIDEO_DIR/voices.json" \
    || { echo "   BROKEN: $VIDEO_DIR/voices.json is not valid JSON"; missing=1; }
  echo "   cast       : $VIDEO_DIR/voices.json (multi-voice)"
fi
[ "$missing" -eq 0 ] || { echo "!!! preflight failed - fix the above and re-run"; exit 1; }

# Fail loudly if any visuals.csv row has no frame on disk (the old runner let
# stitch silently skip these and still call the build a success).
python3 - "$VIDEO_DIR" "$FRAMES" <<'PY'
import csv, glob, os, sys
video_dir, frames = sys.argv[1], sys.argv[2]
with open(os.path.join(video_dir, "visuals.csv"), newline="", encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))
def key(r):
    return "beat%02dm%02d" % (int(r["slide_id"]), int(r["moment"]))
expected = [key(r) for r in rows]
on_disk = set()
for p in glob.glob(os.path.join(frames, "*.png")):
    base = os.path.basename(p)[:-4]
    on_disk.add(base.split("_v")[0])          # beat06m05_v00_s000 -> beat06m05
have = [k for k in expected if k in on_disk]
lost = [k for k in expected if k not in on_disk]
print(f"   frames: {len(have)}/{len(expected)} moments have an image")
if lost:
    preview = ", ".join(lost[:12]) + (" ..." if len(lost) > 12 else "")
    print(f"!!! {len(lost)} moments have NO image: {preview}")
    print("!!! generating these is the agent's job in the sandbox - stopping before encode")
    sys.exit(1)
PY

STAGE="deps"
echo "=== [2/6] Deps ==="
if ! command -v ffmpeg >/dev/null 2>&1; then
  (apt-get -qq update && apt-get -qq install -y ffmpeg) || apt-get -qq install -y ffmpeg
fi
if [ "${SKIP_TTS:-0}" = "1" ]; then
  echo "   SKIP_TTS=1 -> not installing edge-tts, reusing cached audio"
  [ -f "$VIDEO_DIR/narration.mp3" ] || { echo "!!! SKIP_TTS=1 but $VIDEO_DIR/narration.mp3 is missing"; exit 1; }
  [ -f "$VIDEO_DIR/beats_with_timing.json" ] || { echo "!!! SKIP_TTS=1 but beats_with_timing.json is missing (no word timings to reuse)"; exit 1; }
else
  pip install -q edge-tts pillow requests
fi

STAGE="beats"
echo "=== [3/6] visuals.csv -> beats.jsonl ==="
cd "$REPO"
python3 -m cartoonstyle.csv_to_beats \
    --visuals "$VIDEO_DIR/visuals.csv" \
    --out "$VIDEO_DIR/beats.jsonl"

STAGE="narration"
echo "=== [4/6] Narration (word timings) ==="
# Two modes:
#   edgetts   DEFAULT. Synthesize here with edge-tts (AndrewNeural), which
#             supplies WordBoundary timings for free. One pass, no manual chunking.
#   prebuilt  Opt-in via NARRATION_MODE=prebuilt. Use a committed narration.mp3
#             made elsewhere; word timings are recovered by forced alignment.
#             Costs a hand-split whenever a content filter refuses a chunk.
LOG=/tmp/tts_log_$SLUG.txt
TTS_ARGS=(--beats "$VIDEO_DIR/beats.jsonl" --out-dir "$VIDEO_DIR"
          --visuals "$VIDEO_DIR/visuals.csv")

# TAKE=single  the whole script in ONE edge-tts call: seamless prosody, no
#              seams, no per-beat gaps. SFX cues are derived from the beat
#              spans afterwards (tools/sfx_cues_from_beats.py).
# TAKE=multi   one edge-tts segment per beat: per-beat voices, real silence
#              gaps, sfx_cues.csv written by tts_multi.
# TAKE=auto    single if every beat uses the same voice, multi if the cast
#              file actually changes voice partway through.
TAKE="${TAKE:-auto}"
DISTINCT_VOICES=1
if [ -f "$VIDEO_DIR/voices.json" ]; then
  DISTINCT_VOICES=$(python3 - "$VIDEO_DIR/voices.json" <<'PYJSON'
import json, sys
c = json.load(open(sys.argv[1]))
d = c.get("default", {}).get("voice", "")
voices = {d} | {v.get("voice") for v in c.get("beats", {}).values() if v.get("voice")}
voices.discard(None); voices.discard("")
print(len(voices) or 1)
PYJSON
)
fi

if [ "$TAKE" = "auto" ]; then
  if [ "$DISTINCT_VOICES" -le 1 ]; then TAKE=single; else TAKE=multi; fi
fi

if [ "$TAKE" = "single" ] && [ "$DISTINCT_VOICES" -gt 1 ]; then
  echo "!!! TAKE=single requested, but voices.json uses $DISTINCT_VOICES voices."
  echo "!!! one continuous take can only read one voice. Use TAKE=multi, or"
  echo "!!! set every beat to the same voice in voices.json."
  exit 1
fi

if [ "$TAKE" = "single" ]; then
  echo "   take mode: SINGLE (one continuous edge-tts call, no seams)"
  TTS_MODULE=cartoonstyle.tts
else
  echo "   take mode: MULTI ($DISTINCT_VOICES voices, one segment per beat)"
  TTS_MODULE=cartoonstyle.tts_multi
  TTS_ARGS+=(--voices "$VIDEO_DIR/voices.json")
fi

if [ "${NARRATION_MODE:-edgetts}" = "prebuilt" ] && [ -f "$VIDEO_DIR/narration.mp3" ]; then
  echo "   prebuilt narration.mp3 found -> forced alignment (no edge-tts)"
  pip install -q faster-whisper 2>/dev/null || \
    echo "   (faster-whisper unavailable - align.py will fall back to chunk timing)"
  python3 -m cartoonstyle.align \
      --audio "$VIDEO_DIR/narration.mp3" \
      --chunks "$VIDEO_DIR/narration_chunks.json" \
      --out "$VIDEO_DIR/words.json" \
      --model "${WHISPER_MODEL:-small.en}"
  if [ "$TTS_MODULE" = "cartoonstyle.tts" ]; then
    TTS_ARGS+=(--words-json "$VIDEO_DIR/words.json")
  else
    echo "   NOTE: forced alignment is single-voice only; tts_multi will"
    echo "         synthesize per beat instead (set NARRATION_MODE=edgetts)."
  fi
else
  echo "   synthesizing with edge-tts ($VOICE $RATE)"
  TTS_ARGS+=(--voice "$VOICE" --rate="$RATE")
fi

python3 -m "$TTS_MODULE" "${TTS_ARGS[@]}" 2>&1 | tee "$LOG"

# tts prints "[OK]" at the END of the line: "... moments_timing.json [OK]"
if ! grep -qE "moments locked.*\[OK\]" "$LOG"; then
  echo "!!! NARRATION DID NOT LOCK ALL MOMENTS - inspect $LOG"
  echo "!!! a moment_text token is not present in the spoken word stream"
  exit 1
fi

# Single take has no per-beat synthesis, so sfx times must be derived from the
# beat spans rather than emitted by tts_multi.
if [ "$TAKE" = "single" ] && [ -f "$VIDEO_DIR/voices.json" ]; then
  STAGE="sfx-cues"
  echo "   deriving sfx_cues.csv from beat spans"
  python3 -m tools.sfx_cues_from_beats \
      --beats "$VIDEO_DIR/beats_with_timing.json" \
      --voices "$VIDEO_DIR/voices.json" \
      --out "$VIDEO_DIR/sfx_cues.csv" \
      --offset "${SFX_OFFSET:-0.25}" || echo "   (no sfx cues produced)"
  cd "$REPO"
fi

STAGE="stitch"
echo "=== [5/6] Stitch (+ mux narration) ==="
# stitch.py globs {key}_v{pick:02d}_s*.png. Accept either frame naming scheme by
# building one alias dir, instead of assuming frames were saved as bare beatNNmMM.png.
rm -rf "$IMG_POOL"; mkdir -p "$IMG_POOL"
aliased=0
for f in "$FRAMES"/*.png; do
  [ -e "$f" ] || continue
  base=$(basename "$f" .png)
  case "$base" in
    *_v[0-9][0-9]_s*) ln -sf "$f" "$IMG_POOL/$base.png" ;;   # already stitch-shaped
    *)                ln -sf "$f" "$IMG_POOL/${base}_v00_s00000.png" ;;
  esac
  aliased=$((aliased + 1))
done
echo "   $aliased frame aliases ready"

# Sound effects: tts_multi writes sfx_cues.csv when a beat carries "sfx".
STITCH_ARGS=()
if [ -f "$VIDEO_DIR/sfx_cues.csv" ]; then
  echo "   sfx cues found -> synthesizing sfx.wav"
  python3 -m cartoonstyle.sfx --cues "$VIDEO_DIR/sfx_cues.csv" \
      --out "$VIDEO_DIR/sfx.wav" --gain 0.9
  STITCH_ARGS+=(--sfx "$VIDEO_DIR/sfx.wav")
fi

python3 -m cartoonstyle.stitch \
    --timing "$VIDEO_DIR/beats_with_timing.json" \
    --images-dir "$IMG_POOL" \
    --out "$VIDEO_DIR/VIDEO.mp4" \
    --pick 0 "${STITCH_ARGS[@]}"

STAGE="package"
echo "=== [6/6] Package ==="
rm -f "$ZIP"
PKG=("$VIDEO_DIR/VIDEO.mp4" "$VIDEO_DIR/thumbnail.jpg" "$VIDEO_DIR/metadata.json"
     "$VIDEO_DIR/script.md" "$VIDEO_DIR/youtube.txt")
# Optional extras: a 9:16 portrait thumbnail, and any per-episode style notes.
for extra in "$VIDEO_DIR/thumb_portrait.png" "$VIDEO_DIR/STYLE.md"; do
  [ -f "$extra" ] && PKG+=("$extra")
done
if command -v zip >/dev/null 2>&1; then
  zip -j "$ZIP" "${PKG[@]}"
else
  python3 -c "import sys,zipfile,os; z=zipfile.ZipFile(sys.argv[1],'w',zipfile.ZIP_DEFLATED); [z.write(p, os.path.basename(p)) for p in sys.argv[2:]]" "$ZIP" "${PKG[@]}"
fi

echo ""
echo "==========================================="
ls -lh "$ZIP"
python3 -c "import sys,zipfile; [print('  ', i.filename, f'{i.file_size/1048576:.1f} MB') for i in zipfile.ZipFile(sys.argv[1]).infolist()]" "$ZIP"
echo "==========================================="
if [ ! -s "$ZIP" ]; then
  echo "!!! $ZIP was not created"; exit 1
fi
echo "DONE. In the notebook, download with:"
echo "   from IPython.display import FileLink; FileLink('$ZIP')"
echo "   (verify first:  !ls -lh $ZIP)"
