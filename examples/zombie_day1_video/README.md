# zombie_day1_video

Episode 1: one day, one problem (the knock at the door), one decision (don't open it —
reach the water tower before dark).

## Files
- `narration.txt` — approved narration, one sentence per line.
- `narration_v1.txt` — first draft, kept for reference.
- `build_visuals.py` — regenerates `visuals.csv`; holds the fixed STYLE block verbatim.
- `visuals.csv` — 107 moments / 13 beats, word-locked `moment_text`.
- `voices.json` — multi-voice config + sfx cues anchored to moment cuts.
- `frames/` — raw generated images `beat{NN}m{NN}.png` (originals, never renamed).
- `pool/` — stitched naming `beat{NN}m{NN}_v00_s00000.png`, all 1376x768.
- `title_description.txt`, `thumbnail.png` — deliverable metadata.
- `kaggle_download.py` — prints the clickable zip link in a Kaggle notebook.

## Sandbox commands
```
export PYTHONPATH=/home/user/newrepo
python3 -m cartoonstyle.csv_to_beats --visuals visuals.csv --out beats.jsonl
python3 -m cartoonstyle.tts_multi --beats beats.jsonl --out-dir . --visuals visuals.csv --voices voices.json --simulate
python3 -m cartoonstyle.sfx --cues sfx_cues.csv --out sfx.wav --gain 0.9
python3 -m cartoonstyle.pool_frames --frames frames --out pool --pick 0
python3 -m cartoonstyle.stitch --timing beats_with_timing.json --images-dir pool --out VIDEO.mp4 --pick 0 --sfx sfx.wav --qc qc.jsonl --fps 30
```

## Kaggle
`!bash newrepo/run_video_kaggle.sh zombie_day1` then run `kaggle_download.py` as a cell.
