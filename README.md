# newrepo — narrated video pipeline

One episode = one folder in `examples/<slug>_video/`. The tooling is in `cartoonstyle/`.
Narration is word-locked to images, so a cut happens on the exact syllable you wrote.

**Branch rule:** `main` carries the tooling only. Every episode lives on the arena
session branch it was produced on, because `run_video_kaggle.sh` clones one branch.
The agent prints the branch name at the end of every report — clone *that*, not `main`.

## Modules

| module | does |
|---|---|
| `csv_to_beats` | `visuals.csv` → `beats.jsonl`, one beat per `slide_id` |
| `plan` | **gate**: runtime estimate, per-moment pacing, and whether every `moment_text` still appears word-for-word in `narration.txt` |
| `tts_multi` | one audio segment per beat, per-beat voices, real silence gaps; writes `beats_with_timing.json`, `moments_timing.json`, `sfx_cues.csv` |
| `tts` | single-voice path (also handles `NARRATION_MODE=prebuilt` with `align`) |
| `sfx` | procedural knock / thud / click / rumble, stdlib only, no asset licences |
| `prep_frames` | `frames/` → `pool/` at exactly `1376x768`, LANCZOS, no crop, edge-coloured letterbox only when the aspect is genuinely off |
| `contact_sheet` | QC sheet, optionally printing each `moment_text` under its tile |
| `stitch` | word-locked cuts + narration + sfx + optional burned captions, canvas locked to `1376x768` |

## Local (sandbox) run — no real voices

```bash
pip install pillow imageio-ffmpeg --break-system-packages
export PYTHONPATH=$PWD
cd examples/<slug>_video

python3 -m cartoonstyle.csv_to_beats --visuals visuals.csv --out beats.jsonl
python3 -m cartoonstyle.plan      --visuals visuals.csv --narration narration.txt --voices voices.json
python3 -m cartoonstyle.tts_multi --beats beats.jsonl --out-dir . --visuals visuals.csv \
        --voices voices.json --simulate
python3 -m cartoonstyle.sfx       --cues sfx_cues.csv --out sfx.wav --gain 0.9   # only if cues exist
python3 -m cartoonstyle.prep_frames --frames frames --out pool
python3 -m cartoonstyle.stitch    --timing beats_with_timing.json --images-dir pool \
        --out VIDEO.mp4 --pick 0 --sfx sfx.wav --canvas 1376x768

python3 -m cartoonstyle.contact_sheet --frames frames --out batch1.png \
        --label "BATCH 1" --visuals visuals.csv --cols 3 --thumb 620
```

`--simulate` writes silent audio of the right length, so the MP4 you get locally is
timing-accurate and mute. Real narration is `edge-tts`, Kaggle only.

## Kaggle run — real voices, real deliverable

```python
!git clone --depth 1 --branch <session-branch> https://github.com/AsuraXP/newrepo.git
!bash newrepo/run_video_kaggle.sh <slug>
```

```python
import os
from IPython.display import FileLink, display
z = f"/kaggle/working/<slug>_DELIVERABLE.zip"
print(f"{os.path.getsize(z)/1e6:.1f} MB"); display(FileLink(z))
```

The zip holds exactly: `<slug>.mp4` (1376×768, 30 fps, h264+aac), `thumbnail.jpg`,
`title_description.txt` (+ `script.md` / `metadata.json` if the episode has them).
A `FileLink` dies with the Kaggle session — "Save Version → Save & Run All" if you
want the file to survive.

Env overrides: `VIDEO_DIR`, `OUT_DIR`, `VOICE`, `RATE`, `SKIP_TTS=1`, `NARRATION_MODE`,
`ZIP_NAME`, `CAPTIONS=1`, `BRAND_WORDS="name1,name2"`, `CANVAS`.

## Frame contract

* `frames/beat05m03.png` — original, never renamed.
* `pool/beat05m03_v00_s00000.png` — what the stitcher globs: `{key}_v{pick:02d}_s*.png`.
* `prep_frames` is the only place the size rule is enforced; `stitch` then refuses to
  invent a different canvas.
