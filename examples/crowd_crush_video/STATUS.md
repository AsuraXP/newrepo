# STATUS — `crowd_crush` (Saiki Survives, Ep. 01)

**Progress: 57 / 78 frames.** Silent animatic renders at **2:11** of the final 3:01.
Last updated: batch 6.

## Remaining frames (21) — exact queue for the next turns

| Batch | Frames | Beat purpose |
|---|---|---|
| 7 (cut short) | `beat09m03`, `09m04`, `09m05`, `10m01`–`10m06`, `11m01` | falling, don't scream, chin up · ground level · curl left · get up · crawl to the edge · the move that scales |
| 8 | `beat11m02`–`11m05`, `12m01`–`12m06` | floor-plan exits · stand at the rim · know two exits · never the funnel · density vs panic · watch the shoulder gap |
| 9 (partial) | `beat12m07` | end card — Saiki from behind, empty horizon |

Each batch is capped at **10 images per turn**. A turn that hits the cap cannot generate
more until the next user message resets it — including failed calls, so never over-request.

## Prompt rules that were earned in this video (see PROMPT_RULES.md)
- Say **"EXACTLY TWO black dot eyes"** — otherwise an eye goes missing on small faces.
- Say **"visible hem at the hip"** — otherwise the red shirt renders as a long dress.
- For leg-only frames say **"single thin black pen line, same weight as the arms, no double
  outlines"** — otherwise legs render as trousers (`beat07m04` failed twice on this).
- For any crowd-scale frame pass a crowd anchor as the third `images` reference.

## QC ledger
- Re-rolls used: **2** (`beat01m02` eye fix at pilot, `beat07m04` trousers fix). ~4% of frames,
  well under the 10–40% the workflow budgeted.
- Accepted nitpicks (not re-rolled, per the story-break rule): `beat02m03`, `beat02m04`
  (small subject in big white frame), `beat04m07` (faint grey rings), `beat04m03` (lean reads
  ambiguous over the ribs), `beat06m03` (black mass reads as a cylinder), `beat06m05`
  (curvy legs), `beat07m01` (faint arrows), `beat07m02`+`07m03` (near-duplicate poses).
- Zero moderation trips on the entire anatomy block (beat 4). The white-sheet frame passed.

## When all 78 frames are in

```bash
# 1. final animatic, for a last look at pacing
python tools/make_animatic.py examples/crowd_crush_video

# 2. commit + push
git add examples/crowd_crush_video/frames/
git commit -m "crowd_crush: COMPLETE 78/78 frames"
git push origin <branch>
```

Then on Kaggle (one cell):

```python
!git clone --depth 1 --branch <branch> https://github.com/<owner>/<repo>.git
!bash <repo>/run_video_kaggle.sh crowd_crush
from IPython.display import FileLink; FileLink('/kaggle/working/crowd_crush_DELIVERABLE.zip')
```

`run_video_kaggle.sh` preflights every `visuals.csv` row against `frames/` **before** spending
TTS or encode time, and accepts both frame naming schemes.

## Still outstanding
- **thumbnail.jpg** — not yet generated. Needed before the zip will build (preflight will
  block without it). Generate in the sandbox, not on Kaggle.
- Chapter timestamps in `youtube.txt` and `metadata.json` are **estimates from word counts**.
  Once TTS produces `moments_timing.json`, regenerate them from real timings.
- No music bed. If the single-voice narration feels flat, that is the cheapest fix, and it
  is a stitch-layer change, not a re-generation.
