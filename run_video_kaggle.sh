#!/usr/bin/env bash
# =============================================================================
#  run_video_kaggle.sh <slug>
#  One-shot render for examples/<slug>_video, run from a Kaggle notebook:
#      !bash newrepo/run_video_kaggle.sh zombie_day1
#
#  Repository : https://github.com/AsuraXP/newrepo.git
#  Branch     : arena/e7642839-newrepo
#  Clone with :
#      git clone -b arena/e7642839-newrepo https://github.com/AsuraXP/newrepo.git newrepo
#
#  NOTE: an earlier header said to clone https://github.com/AsuraXP/CartoonStyle.git.
#  That URL is wrong for this project - the pipeline lives in AsuraXP/newrepo on
#  the branch above. It has been corrected here.
#
#  Env overrides: VIDEO_DIR, OUT_DIR, VOICE, RATE, SKIP_TTS=1, ZIP_NAME,
#                 REPO_DIR, NO_LOUDNORM=1.
# =============================================================================
set -euo pipefail

SLUG="${1:?usage: bash run_video_kaggle.sh <slug>}"
REPO_DIR="${REPO_DIR:-/kaggle/working/newrepo}"
VIDEO_DIR="${VIDEO_DIR:-$REPO_DIR/examples/${SLUG}_video}"
OUT_DIR="${OUT_DIR:-/kaggle/working/out}"
VOICE="${VOICE:-en-US-AndrewNeural}"
RATE="${RATE:-+0%}"
ZIP_NAME="${ZIP_NAME:-${SLUG}_DELIVERABLE.zip}"
SKIP_TTS="${SKIP_TTS:-0}"
NO_LOUDNORM="${NO_LOUDNORM:-0}"

echo "== [$SLUG] repo=$REPO_DIR"
echo "== [$SLUG] video=$VIDEO_DIR"
echo "== [$SLUG] out=$OUT_DIR"

python3 -m pip install -q edge-tts pillow imageio-ffmpeg

export PYTHONPATH="$REPO_DIR"
cd "$VIDEO_DIR"

# Stage 3 - beats
python3 -m cartoonstyle.csv_to_beats --visuals visuals.csv --out beats.jsonl

# Stage 5 - real edge-tts narration (multi-voice if voices.json exists)
if [[ "$SKIP_TTS" != "1" ]]; then
  if [[ -f voices.json ]]; then
    VCFG="voices.json"
    echo "== [$SLUG] multi-voice mode"
  else
    VCFG="_voices_single.json"
    python3 - "$VOICE" "$RATE" "$VCFG" <<'PY'
import json, sys
json.dump({"default": {"voice": sys.argv[1], "rate": sys.argv[2]}, "beats": {}},
          open(sys.argv[3], "w"), indent=2)
PY
    echo "== [$SLUG] single-voice mode: $VOICE $RATE"
  fi
  python3 -m cartoonstyle.tts_multi --beats beats.jsonl --out-dir . \
      --visuals visuals.csv --voices "$VCFG"
else
  echo "== [$SLUG] SKIP_TTS=1, reusing beats_with_timing.json"
fi

# Stage 6 - synthesized sfx
if [[ -f sfx_cues.csv ]]; then
  python3 -m cartoonstyle.sfx --cues sfx_cues.csv --out sfx.wav --gain 0.9
fi

# Stage 7 - normalise frames into the pool if the clone did not ship the pool
if [[ ! -d pool ]] || [[ -z "$(ls -A pool 2>/dev/null)" ]]; then
  python3 -m cartoonstyle.pool_frames --frames frames --out pool --pick 0
fi

# Stage 8 - stitch
SFX_ARGS=()
[[ -f sfx.wav ]] && SFX_ARGS+=(--sfx sfx.wav)
LN_ARGS=()
[[ "$NO_LOUDNORM" == "1" ]] && LN_ARGS+=(--no-loudnorm)
python3 -m cartoonstyle.stitch --timing beats_with_timing.json \
    --images-dir pool --out VIDEO.mp4 --pick 0 \
    "${SFX_ARGS[@]}" "${LN_ARGS[@]}" --qc qc.jsonl --fps 30

# Stage 9 - deliverable zip
mkdir -p "$OUT_DIR"
STAGE="$OUT_DIR/_${SLUG}_stage"
rm -rf "$STAGE" && mkdir -p "$STAGE"
cp VIDEO.mp4                 "$STAGE/${SLUG}.mp4"
[[ -f thumbnail.png ]]        && cp thumbnail.png "$STAGE/${SLUG}_thumbnail.png" || true
[[ -f title_description.txt ]] && cp title_description.txt "$STAGE/title_description.txt" || true
[[ -f qc.jsonl ]]              && cp qc.jsonl "$STAGE/qc.jsonl" || true

python3 - "$STAGE" "$OUT_DIR" "$ZIP_NAME" <<'PY'
import os, sys, zipfile
stage, out, name = sys.argv[1], sys.argv[2], sys.argv[3]
dest = os.path.join(out, name)
with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(stage)):
        z.write(os.path.join(stage, fn), fn)
print(f"== deliverable: {dest} ({os.path.getsize(dest)/1e6:.1f} MB)")
PY

echo "== [$SLUG] done. Now run kaggle_download.py as a notebook cell for the link."
