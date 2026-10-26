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
| Narration (edge-tts AndrewNeural) | not run for this script yet |
| Final encode | not run (Kaggle) |

Runtime target 3:23 at 2.75 wps; animatic measures **3:24**.

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
- `beat10m01` / `beat10m02` — fridge frames are thin architectural line, **not inkwash**. Biggest register break in the film.
- `beat11m01` — darker than the scripted "dusk"; still pairs correctly with `11m02`.

## Open decisions

1. Trim the cash beat (beat 7, 5 frames for one idea) to reach ~3:05?
2. Number stamps: PIL numerals on the diagram frames that carry a spoken figure
   (4 h, 48 h, 1 gal, 20 ft). Not built. Note that Ep 01's rule is
   "numbers are spoken, never drawn", so a stamp pass needs a decision first.
3. Ep 01 `Saiki` fix (one line in `visuals.csv`, ~30 s rebuild) — still unposted.

## Commands

```bash
python tools/make_animatic.py examples/night_one_video --wps 2.75 \
    --out examples/night_one_video/preview_full.mp4
python tools/make_thumbnail.py examples/night_one_video/frames/beat09m04.png \
    --out examples/night_one_video/thumbnail.jpg \
    --line1 "NIGHT ONE" --line2 "IT FAILS IN ORDER" --art-crop right --valign top
```
