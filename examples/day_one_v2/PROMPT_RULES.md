# PROMPT RULES — `day_one_v2` (Day One, rebuilt)

## What changed from v1
v1 banned the infected from frame and kept the figure small. It produced 122
beautiful frames of doors and knobs and no character. **v2 puts the protagonist
in two thirds of the frames and shows the infected from beat 6 onward.**

## Style block (prepend to every prompt)

```
Bold black INK COMIC panel, halftone dot texture, heavy solid blacks, white
paper, high contrast, dramatic graphic composition. Not a photograph, not 3D,
not an architectural line drawing.

PEOPLE: minimalist stick figures — round white circle head, EXACTLY TWO solid
black dot eyes, NO mouth, thin black pen-line limbs, simple hands, NO double
outlines. The protagonist wears a FLAT BRIGHT RED short-sleeved t-shirt with a
visible hem. Red is the ONLY colour in any frame, and there is at most ONE red
element plus his shirt.

THE INFECTED: tall featureless BLACK SILHOUETTES. No faces, no wounds, no gore,
no blood. Wrong posture is the whole horror — head tilted, one shoulder low, one
arm hanging out of time, standing still where a person would move.

16:9 widescreen. NO text, no letters, no numbers, no signage, no logos, no
watermark. Nothing printed on any surface.
```

## Rules that earned their place

1. **Never say "aerial rooftops".** It returns a wall of windows. Say "flat plan
   map of house footprints" instead. (v1 lesson, still true.)
2. **Name the medium, don't imply it.** "B&W inkwash on white paper, wet loaded
   brush, NOT clean architectural line" — the model ignores a style *reference*
   image but obeys a medium *sentence*.
3. **Hands on screens fail.** Four attempts in v1. Show the screen, not the thumb.
4. **One person per frame unless deliberately stating otherwise.** Adding "exactly
   ONE person" prevents the model inventing a second body — which in a horror
   episode is a catastrophic misread (v1 `20m04`).
5. **Impact needs a verb.** "mid-swing, arms driving the pipe across the frame"
   works; "fighting" does not.
6. **No text ever.** The title is a frame with negative space, not a caption.
   All numerals are spoken.

## Frame size
Native 1376x768 landscape. Never resize. Stitch pads to a uniform even canvas.
