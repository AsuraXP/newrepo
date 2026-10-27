# CONTINUITY — `day_one` (Ep. 1)

## The flat
One-bedroom flat, second floor, one door to the communal hallway, one window over
the street. Everything in the story happens in four places: **the bedroom**, **the
hallway**, **the window**, **the front door**. Never anywhere else.

Objects that must stay identical across frames:
- **Front door** — plain painted panel, brass chain on the inside, a round knob,
  a peephole. The chain appears in beats 1, 2, 15, 24, 28. Same chain every time.
- **Phone** — plain black rectangle, no branding, pale grey screen. Never shows
  legible UI. Its glow is the only light in acts 1 and 2.
- **Torch** — plain cylinder, goes into a pocket in beat 15 and is never seen again.
- **Speaker** — small, plain grille, used in beat 14.
- **The car** — one car, stopped at an angle, driver's door open, headlights on at
  night and off by morning (beats 11, 19).
- **The clock** — blank face, no hands, no numerals (beat 27 only).

## The red
Red = the protagonist's shirt. One accent allowed elsewhere per frame: the
battery fill, the walking figure's mark, the red X on the hoax video. Never two.

## What the audience never sees
- The creature. Ever.
- Mr Adeyemi's face or body.
- The woman in the hall (a voice only).
- The hoax video's content.

## Voice cast (see voices.json)
- Narrator, second person: `en-US-AndrewNeural`
- Mr Adeyemi, through the door: `en-GB-RyanNeural`, -4% (calm, level, no distress)
- The woman in the hall: `en-GB-SoniaNeural`, -6% (patient, unhurried)

## The timer
Adeyemi repeats on a **40-second loop**: knock x3, then the same sentence, then
silence. `voices.json` reserves 1.4s of real silence before each repeat and
`cartoonstyle.sfx` puts the knocks at the head of that silence. Do not change the
gap without changing the loop - the 40s is the scare.
