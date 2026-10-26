# NIGHT ONE — production rules

Second-person, present-tense, **no character name, no channel name anywhere**. The narrator
says "you". Nothing is spoken that requires a proper noun.

## The realism spine (do not violate this)

The premise is **gradual degradation**, not instant apocalypse. The order of failure is the
story. Every frame must sit at the correct point on this timeline:

| Clock | What is actually true | What the video shows |
|---|---|---|
| 9:14pm | lights out, nothing else | dark rooms, the fridge stopping |
| +10 min | whole street dark | neighbourhood aerial, empty windows |
| 0–4 h | fridge cold, freezer cold, phones fine, taps fine | fridge rule, phone rule, fill water |
| 0–6 h | cell towers on battery | text don't call |
| evening | traffic lights dead, pumps dead, cards dead | the junction, the cash point |
| 9pm–2am | candles, grills, generators | CO and fire are the only real killers tonight |
| overnight | house slowly cools | night one uncomfortable, night two dangerous |
| morning | fridge lost, freezer alive | throw it out, leave freezer shut |
| day 2 | taps dry or unsafe | stored water is the plan |
| day 3 | water, sanitation, heat, medical power | the real emergency |

**Never show:** looting, gunfights, military, panic crowds, zombies, firebombs, dead bodies,
or a city in flames. None of that is true on night one, and faking it is what made the
earlier zombie video weak.

## Style block — paste at the start of every image prompt

```
HARD RULES — MUST BE FOLLOWED OR THE IMAGE IS WRONG:
1. ALL people are MINIMALIST STICK FIGURES: round white circle head, EXACTLY TWO black dot
   eyes, NO mouth, thin black line arms and legs (NO trousers, NO jeans, NO shoes, NO boots,
   NO double outlines — legs are a single thin pen line), simple mitten hands.
2. The protagonist ALWAYS wears a FLAT RED SHORT-SLEEVED T-SHIRT with a visible hem at the
   hip. Red is their only colour.
3. EXACTLY ONE red accent per frame unless the prompt says otherwise. Red is reserved for
   that shirt and for single diagram marks.
4. Style: B&W inkwash on white, high contrast, thick confident black line, paper grain.
5. ONE clear subject per frame. Domestic, quiet, unglamorous. Ordinary rooms, plain objects.
6. No faces beyond two dot eyes. No mouths. No blood, no wounds, no bodies, no gore.
7. NO TEXT, NO LETTERS, NO NUMBERS, NO SIGNAGE anywhere in the image.
8. 16:9 widescreen.
```

## Numbers and type are NOT generated
Any on-screen number (`4 HOURS`, `48`, `1 GALLON`) is burned in afterwards with PIL onto the
native 1376×768 frame using a real font — the same technique as the existing caption burner.
That keeps type pixel-crisp and re-editable, and it keeps the image model out of the
typography business. Never prompt for text in a frame.

## Prompt phrases that must always be present
- "EXACTLY TWO black dot eyes" — otherwise an eye disappears on small heads.
- "visible hem at the hip" — otherwise the red shirt renders as a long dress.
- "single thin pen line, no double outlines" — otherwise legs read as trousers.
- For any frame with a bottle, jug or bucket: "plain, no markings, no labels, no text".

## Runtime
77 frames, 607 words. At AndrewNeural ~2.75 wps that is **~3:40**. If it needs to come down
to 3:20, cut moments from beats 7 (money) and 11 (day three) — they are the least
irreplaceable.
