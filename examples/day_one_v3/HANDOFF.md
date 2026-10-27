# HANDOFF — paste this into a fresh chat

---

I'm building an animated zombie-survival fiction series. You're continuing work
that's already in progress. Read this carefully, then check the repo before doing
anything.

## Repo and branch
- Repo: `AsuraXP/newrepo`, work on branch **`arena/d212a50b-newrepo`** only. Never
  create, switch to, or push any other branch.
- Current HEAD is `d561d88` and the tree is clean. **17 of 91 frames are rendered.**
- Project folder: `examples/day_one_v3/`

## What the series is
"Day One" — Episode 1 of a 10-part arc. Second person, present tense, played
completely straight. Fiction, not fact: no statistics, no cited studies, no
"here's the science". No character name and no channel name anywhere, ever.

Arc: Day 1 the message · Day 2 the knock · Day 3 water · Day 5 the road ·
Day 8 the group · Day 12 the wrong safe place · Day 15 the mall · Day 20 the
north wing · Day 30 winter · finale.

Episode lengths: Ep 1 about 5:30–6:00. Days 2–5: 4:00–4:30. Day 8 onward: 3:30–4:00.
Never pad with pace — add events.

## Read these files first (in this order)
1. `examples/day_one_v3/script.md` — the approved narration. **Do not change the
   story without asking me.**
2. `examples/day_one_v3/CONTINUITY.md` — canon, timeline, shot list, hard rules.
3. `examples/day_one_v3/PROMPT_RULES.md` — the image rules that actually work.
4. `examples/day_one_v3/visuals.csv` — 91 rows: `slide_id, moment, moment_text,
   visual_prompt`. The prompts are already written and approved. **Use them as-is.**
5. `examples/day_one_v3/batch1_sheet.png` — what the finished frames look like.
6. `examples/day_one_v3/style_tests/s1_halftone_A.png` — the locked style reference.

## LOCKED art direction — halftone comic ink
Every prompt already begins with this block. Keep it verbatim:

> Bold black INK COMIC panel, halftone dot texture, heavy solid blacks, white paper,
> high contrast, graphic and cinematic. Not a photograph, not 3D. 16:9 landscape.
> NO text, no letters, no numbers, no signage, no logos, no watermark, nothing
> printed on any surface.

Character block (included automatically where the stick figure appears):

> CHARACTER: minimalist stick figure, round white head, EXACTLY TWO solid black dot
> eyes, NO mouth, thin black pen-line limbs, FOUR digits per hand, FLAT BRIGHT RED
> short-sleeved t-shirt with a visible hem. Red is the ONLY colour in the frame.

The infected:

> THE INFECTED: tall featureless BLACK HUMAN SILHOUETTE, no face, no wounds, no
> blood. Wrong posture is the whole horror — head tilted, one shoulder low, one arm
> hanging out of time.

## THE ONE RULE THAT MATTERS
**Each frame must literally illustrate its own sentence.** Count the people the
sentence mentions and draw exactly that many. Match the action, the direction of
gaze, and the location to the words. Never improve on the narration, never add a
cooler composition than the line asks for.

Earlier versions failed exactly here: one drew two pursuers on the line "she is
behind you", and another drew the man *looking back* on the line "you do not look
back". Do not repeat it.

## Current state
- 91 moments total, 932 words, about 5:39 of narration.
- **Rendered: beats 1.1–1.5, 2.1, 3.1–3.4, 4.1–4.7 = 17 frames.**
- Remaining: everything from `4.8` onward (beats 4.8, 5, 6, 7, 8, 9, 10, 11, 12,
  13, 14, 15, 16) = 74 frames.

## How to render
- Pull the exact prompt for each key straight out of `visuals.csv`. Call
  `generate_image` once per frame, saving to
  `examples/day_one_v3/frames/beat{NN}m{NN}.png` — zero-padded, e.g. `beat05m03.png`.
- **Hard cap: 10 images per turn.** Don't waste calls; if a prompt gets rejected or
  returns a diagram, fix the shot description, not the negative list.
- Generated images come back at 1672×941. **Resize every one to 1376×768** with
  PIL LANCZOS before committing. Native landscape, never crop, never stretch.
- After each batch: build a contact sheet, look at it, flag the rejects, re-roll
  them in the next turn, commit and push.

Contact sheet snippet:
```python
from PIL import Image, ImageDraw
import glob
for f in glob.glob("frames/*.png"):
    im = Image.open(f).convert("RGB")
    if im.size != (1376, 768): im.resize((1376, 768), Image.LANCZOS).save(f, optimize=True)
files = sorted(glob.glob("frames/*.png")); ims = [Image.open(f).convert("RGB") for f in files]
cols, tw = 5, 380
rows = (len(ims) + cols - 1) // cols
rh = int(ims[0].height * tw / ims[0].width)
sheet = Image.new("RGB", (cols*tw + (cols+1)*10, rows*rh + (rows+1)*10 + 34), "white")
d = ImageDraw.Draw(sheet); y = 28
for r in range(rows):
    x = 10
    for im in ims[r*cols:(r+1)*cols]:
        sheet.paste(im.resize((tw, rh), Image.LANCZOS), (x, y)); x += tw + 10
    y += rh + 10
d.text((12, 8), f"day_one_v3 - batch N ({len(files)}/91)", fill="black")
sheet.save("batchN_sheet.png", optimize=True)
```

## Assembly (after all 91 frames)
```bash
export PYTHONPATH=/home/user/newrepo
cd /tmp && rm -rf d1v3 && mkdir d1v3 && cd d1v3
cp /home/user/newrepo/examples/day_one_v3/{visuals.csv,beats.jsonl,voices.json} .
python3 -m cartoonstyle.tts_multi --beats beats.jsonl --out-dir . --visuals visuals.csv --voices voices.json --simulate
python3 -m cartoonstyle.stitch --timing beats_with_timing.json --images-dir pool --out VIDEO.mp4 --pick 0
```
Stitch needs moment-keyed filenames (`beatNNmNN_v00_s00000.png`) — symlink the pool.
There is no system `ffmpeg`/`PIL` in this sandbox: install with
`pip install pillow imageio-ffmpeg --break-system-packages`. Real voices only
render in Kaggle, via `bash newrepo/run_video_kaggle.sh day_one 2>&1 | tail -40`.

## Hard don'ts
- **No fantasy, no supernatural rule, nothing uncanny.** The viewer must believe
  they are standing in that flat. Only ordinary things doing the wrong ordinary thing.
- No chase, no kill, no breach in Day 1. The infected appear twice only: the woman
  in the road (6.5–6.8) and one silhouette at the peephole in the last frame (16.4).
- No text baked into frames. Screens are abstract bars, bubbles and chips only.
- Never show a wound, blood, a bite, or a face on the infected.
- Never re-do the thumbnail with PIL type. All words must be rendered by the image
  model itself, no font overlays.
- Don't ask me to preview or watch anything mid-run. Batch → sheet → commit → short
  report. "No need to trim", "just continue".

## Style decisions already rejected — don't revisit
- Door/knob/socket-only framing with a tiny figure (old Ep 1): me reading "boring".
- A chase-and-kill version of Day 1 that ate the Day 2 knock: off track.
- Woodcut, ink wash and risograph: all tested and rejected. Halftone comic only.

## First thing to do
Tell me in two lines what you understand the style and the rule to be, then start
rendering from `4.8` — 10 frames, contact sheet, commit, short report.
