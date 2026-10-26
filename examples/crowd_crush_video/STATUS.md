# STATUS — `crowd_crush` (Ep. 01) — **FIXED, READY FOR ENCODE**

**78 / 78 frames.** Silent animatic runs **3:01** at 2.75 words/sec.
Frame production done. Next step is the Kaggle encode.

## Name fix (2026-10-26)

The spoken line `Saiki survives. See you next time.` was the one place the name
appeared in the audio, and edge-tts pronounced it wrong. It is now:

> **You survive. See you next time.**

Same six words, so **every timing, chapter and the 3:01 runtime are unchanged** —
no beat re-timing needed. Changed in `visuals.csv` (row 12/7), `script.md`
(paragraph + subtitle) and `beats.jsonl`. The visible description signature in
`metadata.json` also lost the series name.

**Not changed:** the search tag `saiki survives` in `youtube.txt` / `metadata.json`
tags and the `#saikisurvives` hashtag. Invisible in the video; keep for reach, or
strip with a find-and-replace if it should go.

### Three frames were 1365x768

`beat06m02`, `beat08m05`, `beat12m03` were 11 px short of native width. The Kaggle
runner pad-extends odd widths, which would have put a pale stripe on the right
edge of three dark frames. Fixed here instead by replicating the last real column
across the shortfall — seamless on all three, verified by eye. **All 78 frames are
now exactly 1376x768.**

### Re-running the build

The audio has to be regenerated, so **do not set `SKIP_TTS=1`** — that flag would
reuse the cached narration and keep the old line.

```python
!git clone --depth 1 --branch arena/d212a50b-newrepo https://github.com/AsuraXP/newrepo.git
!bash newrepo/run_video_kaggle.sh crowd_crush
```

## Preflight: passing

```
missing packable files: none
frames: 78/78 moments have an image
missing moments: none
```

Verified with the same logic `run_video_kaggle.sh` uses, so the Kaggle run will not
fail at the packaging step.

## Deliverable inputs, all present
| File | State |
|---|---|
| `frames/*.png` (78) | complete, all 1376×768, matched 1:1 to `visuals.csv` |
| `thumbnail.jpg` | 1280×720, 192 KB (YouTube limit 2 MB) |
| `metadata.json` | chapters regenerated from frame count/durations |
| `youtube.txt` | title, description, chapters, sources, tags |
| `script.md` | derived mechanically from `visuals.csv` — token match guaranteed |
| `PROMPT_RULES.md` | locked style + the 3 fixes this video earned |
| `CONTINUITY.md` | density states + stance progression |

## Run it on Kaggle

```python
!git clone --depth 1 --branch arena/d212a50b-newrepo https://github.com/AsuraXP/newrepo.git
!bash newrepo/run_video_kaggle.sh crowd_crush
from IPython.display import FileLink; FileLink('/kaggle/working/crowd_crush_DELIVERABLE.zip')
```

The runner preflights, rebuilds `beats.jsonl`, runs edge-tts with word timings, verifies
every moment locked, stitches, and zips VIDEO.mp4 + thumbnail + metadata + script + youtube.

## QC ledger
- **Re-rolls: 2 / 78 (~2.6%)** — `beat01m02` (one eye missing), `beat07m04` (legs read as
  trousers; failed twice, fixed with explicit "single thin pen line, no double outlines").
- **Accepted nitpicks (story reads, not re-rolled):** `02m03`, `02m04` (small subject in
  big white frame), `04m07` (faint grey rings), `04m03` (lean reads ambiguous over ribs),
  `06m03` (black mass reads cylindrical), `06m05` (curvy legs), `07m01` (faint arrows),
  `07m02`+`07m03` (near-duplicate guard poses), `10m01` (fallen figure very small),
  `12m05` (torsos read as heads touching).
- **Zero moderation trips** on the entire anatomy block (beat 4), including the
  white-sheet frame.

## Lessons worth carrying to episode 02
1. **The 10-image cap counts failures too.** Over-requesting a batch costs a whole turn.
2. **Budget the pilot turn separately:** 4 style tests + up to 2 re-rolls + 4 story frames.
3. **Two registers work well together** — inkwash for story frames, flat thin-line diagrams
   for expository frames. Do not mix them inside one frame.
4. **Prompt phrases that must always be present:** "EXACTLY TWO black dot eyes",
   "visible hem at the hip", "single thin black pen line, no double outlines".
5. **`tools/make_animatic.py` is the QC gate that matters** — it renders the real cut rhythm
   without TTS, so pacing is judged before any Kaggle time is spent.

## Voice decision (settled)
Narration stays **edge-tts `en-US-AndrewNeural` at +0%**. A better voice was built and
measured (external TTS + forced alignment + gapless assembly, all committed and working —
78/78 moments locked at 3:22), but it cost a **manual re-chunk every time the content
filter refused a passage**, and each hand-split is a chance to desync. Andrew renders the
whole script in one pass and returns word timings with it. Not worth the throughput.

The alternative path is kept but is **opt-in**, not automatic:
- `NARRATION_MODE=prebuilt` + a committed `narration.mp3` switches to forced alignment.
- `cartoonstyle/align.py` and `tts.py --words-json` remain for a future human read or a
  paid voice, without forking the matching logic.

## Still outstanding (post-encode)
- **Chapters are estimates** from word count (assume 2.75 wps). Real TTS came in at
  3:22 vs the 3:01 estimate on a test render, so regenerate the chapter stamps from
  `moments_timing.json` after the first Kaggle run — the drift is larger than expected.
- **No music bed.** If single-voice narration drags, add a bed at the stitch layer; this is
  a code change, not a re-generation. Cheapest quality win available.
- Captions are intentionally off for the first mux. If wanted later:
  `--captions --caption-method pil`.
