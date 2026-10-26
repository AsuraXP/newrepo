# PROMPT RULES — `crowd_crush` (Saiki Survives, Ep. 01)

Locked after style tests. Paste the HARD RULES block verbatim at the start of **every** image prompt.

## Anchor order (mandatory)
- `anchor[0]` = `style_tests/ref_saiki_fullbody.png` → body type, red shirt, stance.
- `anchor[1]` = `style_tests/styleA_inkwash_contrast.png` → inkwash texture, contrast, ground rendering.
- `anchor[2]` (only for crowd-scale or diagram frames) = `style_tests/ref_crowd_field_diagram.png`.

## MANDATORY OPENING BLOCK — paste verbatim
```
HARD RULES — MUST BE FOLLOWED OR THE IMAGE IS WRONG:
1. ALL people are MINIMALIST STICK FIGURES: round white circle head, thin black line arms,
   thin black line legs (NO pants, NO jeans, NO shorts, NO shoes, NO boots — legs are a
   plain black line, same thickness as the arms), simple mitten stick hands, flat-color
   fills only. No photorealism, no musculature, no wrinkles on limbs, no detailed fingers.
2. Saiki (the protagonist) ALWAYS wears a FLAT RED SHORT-SLEEVED T-SHIRT. Red is his only
   color. Every OTHER figure is pure black line and white fill with NO color at all.
3. EXACTLY ONE red accent per frame unless the row's prompt says otherwise. Red is reserved
   for: Saiki's shirt, and single diagram arrows. Never a second red object.
4. Style: B&W inkwash on white. High contrast. Gritty but clean. Thick confident black line.
5. Crowd members have NO faces beyond two simple black dot eyes, and NO mouths.
   No screaming faces, no teeth, no tongues, no skulls, no wounds, no blood, no gore.
6. ONE clear subject per frame. Empty white background unless the prompt names a location.
7. NO TEXT, NO LETTERS, NO NUMBERS, NO SIGNAGE, NO CAPTIONS anywhere in the image.
8. 16:9 widescreen.
```

## Per-frame prompt structure
```
[verbatim HARD RULES block above]
SHOT: <top-down / wide / medium / close-up> + <camera height or angle>
SCENE: <the one thing in frame>
SAIKI: <where he is, what his body is doing, or "not in this frame">
RED: <exactly what is red — one item only>
[REFERENCE] images=[ref_saiki_fullbody, styleA_inkwash_contrast]
```

## Locked decisions (Post-it notes for every future turn)
- **Voice:** `en-US-AndrewNeural`, rate **+0%**. One continuous take. Never per-beat gluing.
- **Runtime:** 3:01–3:11, 78 frames, 6.4 words/frame. Do not "fix" pacing by adding motion —
  add frames or cut words.
- **No Ken Burns, no zoompan, no transitions.** Hard cuts locked to spoken words.
- **Native resolution only.** Pad to even with PIL; never resize, never `-vf pad` post-concat.
- **Captions OFF** for the first clean mux.

## Frame naming
`frames/beat{slide:02d}m{moment:02d}.png` — e.g. `beat07m03.png`.
`run_video_kaggle.sh` also accepts `_v00_s00000000` suffixes, so either scheme works.

## Moderation-safe phrasing (this topic is unusually risky)
Crowd-crush material sits close to "mass death" content, so:
- Never say or prompt **"corpses", "bodies piling", "massacre", "decapitated", "gore"**.
- Prefer **"the crowd", "the mass", "compression", "pressure"**.
- The autopsy beat (4.8) is a **plain white sheet on a low table**, nothing clinical, no instruments.
- Say **"compressive asphyxia"**, not "suffocation deaths" — more precise and less trigger-y.
- Anatomy frames (4.1–4.7) are **thin-line schematics**, not medical illustration of a person.

## Common bugs to block
- Extra red objects (red arrows + red phone + red shirt) → FAIL, one accent only.
- Any figure with pants/shoes/boots on a stick body → FAIL.
- Crowd members given faces, mouths, or expressions → FAIL.
- Diagram frames becoming photoreal or 3D → FAIL, must stay 2D ink diagram.
- Text creeping into frames (e.g. numbers on the density tile) → FAIL. Numbers are spoken, never drawn.
- Saiki drawn as a generic stick figure without the red shirt → FAIL.
