# Why Did Humans Start Cooking? — explainer video production

A complete, source-backed 16:9 animated explainer. This repo is the **workspace**:
it holds the approved script, the frame spine, the style lock, and all 117 final
frames. It does **not** contain audio or a video — those are produced by the
one-cell Kaggle handoff at the very end.

## The deliverable (what to run)

**`kaggle_handoff.py`** — paste the entire file into ONE Kaggle notebook cell and
Run. In the notebook, set **Settings → Internet = ON** (needed for `git clone`,
`edge-tts`, and the Microsoft TTS endpoint).

The single cell does everything, each stage printing its name (and naming the
stage on failure):

1. `BOOTSTRAP` — install `edge-tts`, `numpy`, `pillow`; locate/install ffmpeg.
2. `CLONE / UPDATE REPO` — clone this repo at `arena/065c2e4b-newrepo`, print the commit hash.
3. `PREFLIGHT` — verify all 117 frames exist, are 1920×1080, thumbnails are correct sizes, and `visuals.csv` moment text reproduces `script.md` word-for-word.
4. `NARRATION` — one continuous `edge-tts` take, voice `en-US-AndrewNeural`, rate `+0%`, capturing word/sentence boundary events.
5. `WORD-LOCKED TIMINGS` — derive 117 cut times from the **measured final audio** (not estimates), quantised to whole frames so image N changes on the exact word its moment starts on.
6. `SOUND CUES` — soft synthesised whooshes at the 8 beat/chapter events, mixed under the narration.
7. `STITCH MP4` — per-moment slow Ken Burns push-in (stronger on 15–17 word moments), concat, then mux with EBU R128 `loudnorm` loudness normalisation.
8. `FINAL METADATA` — write `metadata.json` and `youtube.txt` with chapters derived from the final audio timeline.
9. `PACKAGE ZIP` + `VERIFY` — build and CRC-check the zip, list contents/sizes, decode-check the whole video.

It ends with the exact `FileLink('<path>/why-humans-started-cooking_DELIVERABLE.zip')`
snippet (also displayed as a clickable link).

### Final zip contents

| file | what |
|------|------|
| `VIDEO.mp4` | 1920×1080, h264 + AAC, loudness-normalised, Ken Burns motion |
| `thumbnail.jpg` | 1280×720 (16:9) |
| `thumb_portrait.png` | 1080×1920 (9:16) |
| `metadata.json` | final runtime, voice, timing method, frame durations, audio-derived chapters |
| `youtube.txt` | title, description, hashtags, tags, audio-derived chapters, full source list |
| `script.md` | the approved narration |
| `SOURCES.md` | verified citations for every number in the narration |

## Workspace contents (what was built here, in order)

- `BRIEF.md` — locked project brief, style, timing amendment, frame-density decision.
- `SOURCES.md` — 13 verified sources; every statistic resolves to one.
- `script.md` — approved narration (1,522 words, ≈9:13 at 2.75 w/s).
- `tools/moments.py`, `tools/moments.json`, `tools/scenes.py`, `tools/build_visuals.py` — split the script into word-locked moments and build `visuals.csv`.
- `visuals.csv` — the spine: 117 rows, one image moment each, `moment_text` a verbatim slice of the script.
- `STYLE_LOCK.md` — "INK & GOUACHE" style, verbatim style/subject/NEG blocks, palette.
- `reference/ink_explainer_thumbnail.webp` — supplied style anchor (internal only, not shipped).
- `reference/style_ref_textfree.png` — text-free crop of the reference, attached to **every** generated frame.
- `frames/beatNNmNN.png` — 117 verified frames, all 1920×1080, keyed to `visuals.csv`.
- `sheets/BATCH01..13.png`, `sheets/ALL_FRAMES.png` — contact sheets used to inspect every frame.
- `REJECTS.md` — reject log and honest "weak but kept" notes; zero open rejects.
- `rejects/` — v1 frames that were rejected and re-rolled.
- `thumbs/thumbnail.jpg`, `thumbs/thumb_portrait.png` + `thumbs/thumb_base_*.png` (base art) + `tools/build_thumbs.py`.
- `metadata.json`, `youtube.txt` — publish metadata (chapters here are title list; timestamps are filled from final audio by the Kaggle build).
- `kaggle_handoff.py` — the one-cell build.

## Key decisions (locked)

- **Moment-driven frames, not duration-driven.** A 3-word moment gets its own short frame; a 17-word moment gets a longer one. No padding or merging to hit a duration target.
- **Word-locked cuts.** Image N changes on the exact word its `moment_text` starts on; timings come from the generated audio.
- **One narrator, one continuous take** (`en-US-AndrewNeural`, rate `+0%`).
- **Chapters from final audio, never estimates.**
- **117 frames** over ≈9:13 → one cut every ≈4.7 s. Long static holds are handled with Ken Burns motion, not extra filler frames.
