# Night One — status

Episode 02. **Day One / Part 1 only.** Branch `arena/d212a50b-newrepo`.

## Where it stands

| Stage | State |
|---|---|
| Script (`script.md`, 561 words) | done |
| `visuals.csv` (72 moments, 11 beats) | done, locked |
| Frames (72 / 72 @ 1376×768) | **done** |
| Animatic (`preview_full.mp4`, 204 s = 3:24) | done |
| Thumbnail (`thumbnail.jpg`) | done |
| Number stamps (`stamps.json` + `tools/apply_stamps.py`) | done, 4 frames |
| `beats.jsonl` (11 beats) | done |
| Preflight (frames/thumbnail/metadata) | **passing** |
| Narration (edge-tts AndrewNeural) | not run yet — needs Kaggle |
| Final encode | not run — needs Kaggle |

Runtime target 3:23 at 2.75 wps; animatic measures **3:24** (204.0 s, chapters 11,
last chapter opens 3:04).

`script.md` token-matches `visuals.csv` exactly (562 tokens), so the narration and
the frames cannot drift.

## Encode it

```python
!git clone --depth 1 --branch arena/d212a50b-newrepo https://github.com/AsuraXP/newrepo.git
!bash newrepo/run_video_kaggle.sh night_one
from IPython.display import FileLink; FileLink('/kaggle/working/night_one_DELIVERABLE.zip')
```

The runner preflights, rebuilds `beats.jsonl`, runs edge-tts with word timings,
verifies every moment is locked to a frame, stitches, and zips VIDEO.mp4 +
thumbnail + metadata + script + youtube. Do **not** set `SKIP_TTS=1` here — there
is no cached narration for this episode.

## Beat map

1. 9:14pm, lights out (6) · 2. not your fuse box, whole street dark (6) · 3. fridge 4 h / freezer 48 h (7) · 4. water window, fill everything, 1 gal/person/day (8) · 5. text don't call (7) · 6. dead traffic lights, don't drive out (6) · 7. cash beats cards (5) · 8. what actually kills: candle, grill indoors, generator in garage, CO (9) · 9. thermal mass, night one uncomfortable not dangerous (5) · 10. morning fridge/freezer, smell is not a test (5) · 11. close: nothing dramatic, fails in order, "see you on night two" (8)

Total 72.

## Known frame flaws (accepted, story reads)

- `beat02m03` — needed three attempts. "Aerial rooftops" failed twice (returned a wall of windows). Fixed by switching register to *flat plan/site map*. **Lesson: change register, not wording, after two failures.**
- `beat02m01` — fuse-box hand reads as a floating red rectangle.
- `beat02m05` — raised arm reads as a wave.
- `beat04m02` — water tower legs are a dense fan, not four splayed legs.
- `beat05m02` — cell tower has inkwash splatter that reads as debris.
- `beat06m01` — very sparse, almost empty junction.
- `beat07m03` — paper notes read as a fan of blank playing cards.
- `beat08m01` — house came out *lit*, contradicting "unlit".
- `beat08m04` — dry tap has heavy inkwash noise; the red X carries the meaning.
- `beat08m09` — 20-ft rule diagram is quiet; generator drawn small, measurement line thin.
- `beat09m02` — brick warmth haze reads as a smudge. Weakest diagram.
- ~~`beat10m01` / `beat10m02` — fridge frames are thin architectural line, not inkwash.~~ **Re-rolled and fixed.** Fix was naming the medium outright ("wet black ink on white paper, no ruled drafting lines") instead of relying on a style reference image.
- `beat11m01` — darker than the scripted "dusk"; still pairs correctly with `11m02`.

## Number stamps

Four frames carry a burned-in figure, applied in PIL at native 1376x768 after
generation — never model-rendered, because the model cannot spell:

| frame | stamp | spoken line |
|---|---|---|
| `beat03m02` | **4 HOURS** — FRIDGE, DOOR SHUT | "your fridge holds cold for about four hours" |
| `beat03m06` | **48 HOURS** — FULL FREEZER | "a full freezer is different. Forty eight hours" |
| `beat04m08` | **1 GALLON** — PER PERSON, PER DAY | "one gallon per person, per day, is the number" |
| `beat08m09` | **20 FEET** — FROM EVERY DOOR | "outdoors. Twenty feet from every door and window" |

This is a **deliberate exception** to Ep 01's "numbers are spoken, never drawn"
rule: drawn only on frames that *are* the fact, never as decoration. Colour is
picked per frame from the luminance of the stamp area, so it flips to white on
inkwash. `beat04m07` (the four-bottle gauge) was rejected for a stamp — the
bottles fill the frame and anything placed on it collided; `04m08` has the space.

## Open decisions

1. Cash beat trim — **declined by the user, kept at 5 frames.**
2. Ep 01 `Saiki` fix (one line in `visuals.csv`, ~30 s rebuild) — still unposted.

## Commands

```bash
python tools/make_animatic.py examples/night_one_video --wps 2.75 \
    --out examples/night_one_video/preview_full.mp4
python tools/apply_stamps.py examples/night_one_video   # after any frame re-roll
python tools/make_thumbnail.py examples/night_one_video/frames/beat09m04.png \
    --out examples/night_one_video/thumbnail.jpg \
    --line1 "NIGHT ONE" --line2 "IT FAILS IN ORDER" --art-crop right --valign top
```
