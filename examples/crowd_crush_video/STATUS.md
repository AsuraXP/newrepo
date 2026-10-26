# STATUS — `crowd_crush` (Saiki Survives, Ep. 01) — **FRAMES COMPLETE**

**78 / 78 frames.** Silent animatic runs **3:01** at 2.75 words/sec.
Frame production done. Next step is the Kaggle encode.

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

## Still outstanding (post-encode)
- **Chapters are estimates** from word count. Once TTS writes `moments_timing.json`,
  regenerate the chapter stamps from real timings — the current ones are within a few
  seconds but not exact.
- **No music bed.** If single-voice narration drags, add a bed at the stitch layer; this is
  a code change, not a re-generation. Cheapest quality win available.
- Captions are intentionally off for the first mux. If wanted later:
  `--captions --caption-method pil`.
