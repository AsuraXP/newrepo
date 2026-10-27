# STYLE LOCK — "INK & GOUACHE" (locked 2026-10-27)

Winner: **T1_ref**. Every production frame uses:
`[STYLE BLOCK] + [SUBJECT BLOCK] + SCENE: <literal sentence> + [NEG]`
and is generated with the text-free style reference attached:
`images=["reference/style_ref_textfree.png"]`.

## Test frames (all 1376x768 RGB PNG, in `tests/`)

| ID | Variation | What actually happened |
|----|-----------|------------------------|
| T1_ref | full prompt + text-free reference crop | Cream paper ground, spiky hair, curved closed eyes, grey tunic, chunky ink outline. Closest to the supplied thumbnail. **WINNER.** |
| T2_written | same prompt, NO reference image | Character drifted to dot eyes, blue sky band, blackened ground. Usable but not locked. Written description alone is not enough. |
| T3_nonegs | full prompt minus NEG block | No visible quality loss — a single NEG stack is doing little work. Keep it anyway as cheap insurance; do NOT stack extra negative blocks. |
| T4_text | full prompt + reference + '30%' label | Short numeral rendered correctly and legibly at 380 px. Long labels and decimals were NOT tested — keep to ONE short string per frame and verify in the contact sheet. |

## Technical findings (recorded, not assumed)

- **Resolution:** model returns 1376x768 (ratio 1.79, not exactly 16:9). Normalise to 1920x1080 by resize + pad with warm cream (247,240,221). Never crop, never stretch. Padding is a few pixels.
- **Style reference:** attaching the crop materially improves character consistency (closed eyes, spiky hair, cream ground). Reuse it on EVERY frame. The crop is the left 92x160 px of the 240x180 thumbnail upscaled 5x, chosen because the original carries a giant "NO JOBS" caption that would otherwise bleed text into every frame.
- **Dense text / numerals / signage:** one short hand-lettered string works. Two or more strings on one frame were not tested; avoid.
- **Stacking negatives:** one compact NEG block only. No evidence a second helps.
- **Eye drift:** T2 produced dot eyes, T1/T3 produced curved closed eyes. Locked rule: curved closed eyes by default; dot eyes ONLY when the SCENE explicitly needs a gaze direction.
- **Violent / clinical / branded wording:** no refusal in the 4 tests. Batch 1 contains the clinical moment (b1m06) — report any refusal there.
- **Wrong subject / diagram:** no test returned a diagram instead of the scene. If one does, rewrite the SCENE sentence first, not the style block.

## Palette / line weight / realism / detail budget

- Palette: ink black #1A1A1A, warm cream paper #F7F0DD, ochre #C8892F, terracotta #B4552D, teal #3E8E8C, sky blue #6FB7D4, and ONE electric yellow #FFD700 accent on the single most important object.
- Line weight: thick wobbly black contour, ~4 px at 1920 px width.
- Realism: flat 2D cartoon, zero photorealism, no gradients, no soft shading, no 3D.
- Detail budget per frame: exactly the named subjects + 1-3 simple props + 1-2 margin doodles/arrows. Generous empty space. No background crowds.

## [STYLE BLOCK] (verbatim)

Hand-drawn 2D cartoon explainer illustration for a 16:9 landscape video frame, based on a chunky black-ink cartoon look: thick wobbly black outlines about 4 px at 1920 px width, flat saturated gouache colour fills, fine visible paper grain on warm cream paper, simple shapes, comic proportions, expressive eyes matching the supplied reference drawing, flat even lighting, generous empty space around the subject, one or two small hand-drawn margin doodles or arrows, restrained palette of ink black, ochre, terracotta, teal and sky blue, with exactly ONE electric yellow accent used only on the single most important object named in the scene; no gradients, no soft shading, no 3D, no photorealism, no lens flare, no glossy plastic texture. No on-screen text, numbers or labels except ONE short hand-lettered string when the SCENE explicitly requests one, spelled exactly as written in thick black ink and large enough to read on a phone.

## [SUBJECT BLOCK] (verbatim)

Recurring subject design, identical in every frame: any human is one stocky cartoon early-human figure with a large round head, spiky dark-brown hair, two curved closed eyes by default exactly like the supplied reference drawing (or two small black dot eyes aimed in the stated direction when the SCENE requires a gaze), a tiny nose, a wide simple mouth, flat ochre-brown skin, and a plain grey animal-hide tunic with one shoulder strap, drawn with thick black outlines and no realistic facial detail; any fire is ONE small orange-and-yellow flame with a thick black outline; any tuber is ONE knobbly oval root; modern humans appear only in plain unbranded modern clothes. Draw ONLY the exact number of people, animals and objects the SCENE names, never more and never fewer, and put no extra figures in the background. Match the action, gaze direction, location and time of day stated in the SCENE exactly.

## SCENE

The literal sentence from `tools/scenes.py` for that moment, as stored in
`visuals.csv.visual_prompt`. It is the only part that changes between frames.

## [NEG] (verbatim)

NEGATIVE: photorealistic, 3D render, glossy, airbrushed, gradient, lens flare, depth of field, cinematic lighting, extra people, extra limbs, extra fingers, distorted anatomy, cropped subject, misspelled text, garbled letters, watermark, logo, brand name, gore, blood, violence, modern cars, modern buildings, screens, UI, tiny illegible text, cluttered background, collage, multiple panels unless the SCENE asks for a split frame.
