#!/bin/bash
# =============================================================================
# kaggle_day_zero.sh — ONE-SHOT BUILD for Day One, Episode One.
#
# Does literally everything: clones (or updates) the repo, builds the video,
# writes the thumbnails/metadata into the zip, and prints the download link.
#
# USAGE — paste this as the ONLY cell you need in a fresh Kaggle notebook:
#
#   !bash -c "$(curl -sL https://raw.githubusercontent.com/AsuraXP/newrepo/arena/d212a50b-newrepo/kaggle_day_zero.sh)"
#
# Or, if you have already cloned the repo:
#
#   !bash newrepo/kaggle_day_zero.sh
#
# Optional env overrides:
#   BRANCH=...      default arena/d212a50b-newrepo
#   SLUG=...        default day_zero
#   OUT_DIR=...     default /kaggle/working
#   SKIP_TTS=1      reuse cached narration (only works if audio was committed)
#   REUSE=1         don't re-clone if the repo is already there
# =============================================================================
set -euo pipefail

BRANCH="${BRANCH:-arena/d212a50b-newrepo}"
SLUG="${SLUG:-day_zero}"
WORK="${OUT_DIR:-/kaggle/working}"
REPO_URL="${REPO_URL:-https://github.com/AsuraXP/newrepo.git}"
REPO_DIR="$WORK/newrepo"

STAGE="bootstrap"
trap 'rc=$?; echo "" >&2; echo "!!!!! FAILED in stage: $STAGE (exit $rc) !!!!!" >&2' ERR

mkdir -p "$WORK"

# ---------------------------------------------------------------- 1. repo ----
echo "=== [1/3] Repo ==="
if [ -d "$REPO_DIR/.git" ]; then
  echo "   existing checkout found -> fetching $BRANCH"
  git -C "$REPO_DIR" fetch --depth 1 origin "$BRANCH" -q
  git -C "$REPO_DIR" checkout -q "$BRANCH" 2>/dev/null || git -C "$REPO_DIR" checkout -q -B "$BRANCH" "origin/$BRANCH"
  git -C "$REPO_DIR" reset --hard -q "origin/$BRANCH"
else
  echo "   cloning $BRANCH"
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$REPO_DIR" -q
fi
echo "   HEAD: $(git -C "$REPO_DIR" log --oneline -1)"
ls -1 "$REPO_DIR/examples/${SLUG}_video" | head -20

# --------------------------------------------------------------- 2. build ----
STAGE="build"
echo "=== [2/3] Build (voices -> sfx -> stitch -> zip) ==="
cd "$WORK"
bash "$REPO_DIR/run_video_kaggle.sh" "$SLUG"

# ----------------------------------------------------------- 3. verify/dl ----
STAGE="verify"
echo "=== [3/3] Verify ==="
ZIP="$WORK/${ZIP_NAME:-${SLUG}}_DELIVERABLE.zip"
[ -s "$ZIP" ] || { echo "!!! zip missing: $ZIP"; exit 1; }
echo "   zip  : $ZIP"
echo "   size : $(du -h "$ZIP" | cut -f1)"
python3 - "$ZIP" <<'PY'
import sys, zipfile
z = zipfile.ZipFile(sys.argv[1])
print("   contents:")
for i in z.infolist():
    print(f"     {i.filename:<24} {i.file_size/1048576:6.2f} MB")
need = {"VIDEO.mp4", "thumbnail.jpg", "metadata.json", "youtube.txt"}
have = {i.filename for i in z.infolist()}
missing = need - have
if missing:
    print(f"!!! missing from zip: {sorted(missing)}")
    sys.exit(1)
print("   all required files present")
PY

echo ""
echo "==============================================================="
echo " DONE — in the NEXT cell, download it with:"
echo ""
echo "   from IPython.display import FileLink"
echo "   FileLink('$ZIP')"
echo "==============================================================="
