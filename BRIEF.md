# PROJECT BRIEF — locked at STEP 1

Confirmed 2026-10-27. This file is the project law. Everything downstream obeys it.

```
TYPE:          Explainer — Episode 1 of an ongoing channel series.
               Arc: one curiosity question per episode about human
               behaviour/history, answered with named research,
               ending on "this is still you."
RUNTIME:       Script-length-driven. Target 9:00–10:00 (~1,500 words,
               ~100 image moments at ~5s each).
AUDIENCE/TONE: Everyone, all ages. Plain English, curious, warm,
               slightly wry. No lecturing, no jargon.
ASPECT:        16:9 landscape, 1920x1080. Resize, never crop.
STYLE:         "INK & GOUACHE" (see below). Locked with 2–3 test
               frames at STEP 5, then reused verbatim channel-wide.
MUST APPEAR:   Nothing fixed — whatever each narration sentence names,
               drawn exactly. Style block on every frame. Source list
               in the description.
MUST NEVER
APPEAR:        Other channels' names/logos/watermarks; photoreal or
               3D-gloss rendering; gore/graphic injury; real brand
               names on objects.
ON-SCREEN
TEXT:          ALLOWED — short hand-lettered words, only when the
               sentence calls for them; spelling verified in-frame.
NUMBERS/
LABELS:        ALLOWED — simple hand-drawn diagrams/labels when the
               sentence calls for them.
LOGOS/
BRANDING:      FORBIDDEN in frames; title/description only.
VOICE:         ONE narrator — en-US-AndrewNeural, rate +0%,
               one continuous take.
TONE RULES:    All-ages. No invented statistics — every number gets
               a real named source. Hook in first two lines.
               No "in this video we'll…" throat-clearing. A real
               ending, not a fade-out.
TOPIC:         "Why Did Humans Start Cooking? The Accident That
               Rewired Us."
```

## STYLE LOCK — "INK & GOUACHE" (channel-wide)

**Reference:** `reference/ink_explainer_thumbnail.webp` — a low-resolution
thumbnail supplied by the user from the reference channel *Ink Explainer*
(@Inkexplainer96). Internal style reference only; never shipped in the
deliverable.

**Extracted from the reference channel** (channel page, video descriptions
and transcripts, plus the supplied frame):
- Curiosity-question titles; 6–15 minute runtimes; faceless 2D cartoon.
- Narration opens in second person, present tense; rewinds to deep time;
  turns the answer back on the viewer at the end.
- Named evidence in the narration (researcher + study + year), full
  source list in the description.
- Thumbnail: one big cartoon character + one oversized shouty word.

**Keep:** chunky black outlines, flat saturated cartoon colour, simple
shapes, exaggerated expressions, comic proportions, wide savanna / fire /
sky backdrops, one huge hand-lettered yellow headline on thumbnails.

**Our twist:** pen-and-ink contours with visible brush wobble and gouache
flat fills on warm cream paper, light paper grain. Restrained earthy
palette (ink black, ochre, terracotta, teal) with ONE electric yellow
accent used only on the object that matters. Generous empty space.
Hand-drawn arrows and margin doodles. No gradients, no 3D gloss, no
photorealism.

## TIMING AMENDMENT (user, 2026-10-27)

Frames are **moment-driven, not duration-driven**. One image per moment in
`visuals.csv`, whatever that moment needs — a 3-word beat gets its own 1–2
second frame, a 17-word beat gets a longer one. We do NOT pad or merge
moments to hit a 4–6 second target. Cuts are still word-locked: image N
changes on the exact word its `moment_text` starts on.

**OBSERVER NOTE (research limitation):** the sandbox blocked direct
retrieval of video frames, so the channel read is based on its public
page, descriptions, transcripts, auto-described thumbnails, and the one
frame the user supplied. Not a frame-by-frame study. The style block is
therefore an interpretation, to be proven by test frames at STEP 5.


## FRAME DENSITY DECISION (locked 2026-10-27)

Question asked three times: is 100+ frames enough for a ~9 minute video?
**Yes.** Verdict and the math that settles it:

| narration rate | runtime | mean cut | shortest | longest | cuts > 6 s |
|---|---|---|---|---|---|
| 2.50 w/s | 10:09 | 5.2 s | 1.2 s | 6.8 s | 22 |
| 2.75 w/s (target) | 9:13 | 4.7 s | 1.1 s | 6.2 s | 7 |
| 3.00 w/s | 8:28 | 4.3 s | 1.0 s | 5.7 s | 0 |

- `visuals.csv`: 117 frames / 1,522 words = 13.0 words per frame.
- At target rate: 12.8 frames/min = one cut every 4.7 s. Even 100 frames
  over 9:13 would be 5.5 s per cut. Both sit inside the normal 3-6 s
  explainer range. More frames would mean sub-4 s cuts for their own sake,
  which breaks the moment-driven TIMING AMENDMENT above.
- The actual risk is NOT frame count, it is the 7 long static holds at
  2.75 w/s (max 6.2 s). Fix in the Kaggle build: slow Ken Burns push-in
  (scale 1.00 -> 1.045) on every frame, stronger on 15-17 word moments.
  Do NOT add filler frames or pad durations.
- Final frame count stays 117. Chapters come from the final audio, never
  from these estimates.
