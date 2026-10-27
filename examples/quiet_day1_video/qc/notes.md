# QC notes — quiet_day1

## Batch 01 — establishing (8/10 landed)

| key | verdict | note |
|---|---|---|
| beat03m02 bolt | **KEEP** | best frame of the batch. Thick outline, flat grey metal, pale light line. |
| beat05m02 three heads | **KEEP** | no mouths, dot eyes, all tilted the same way. This is the series' face. |
| beat05m01 arms down | **KEEP** | one figure from behind, dead-level shoulders, white wall. |
| beat07m01 phone ringing | **KEEP** | sound arcs read instantly, screen blank. |
| beat04m05 corridor, doors open | KEEP | strong, but bluer than the palette rule; corridor is the set now. |
| beat03m01 empty room | KEEP as **master room** | everything in one frame: door L, window R, mattress, chair, wardrobe, shelf. |
| beat10m01 dusk at the door | KEEP | MC's silhouette holds at dusk. |
| beat01m04 room at 4am | **RE-ROLL** | a proper bed with pillows and a headboard. The script says mattress on the floor. |
| beat01m01 on the wall | **BLOCKED** | moderation, `self-harm`. "spread flat against the concrete / three floors up" reads as a fall risk. |
| beat04m06 seven figures | **RATE LIMITED** | 429, input-images/min. Ten parallel calls is over the ceiling. |

## Fixes applied before batch 02
1. `beat01m01` shot rewritten: "climbing down the drainpipe, bracket to bracket, calm and steady" —
   describing **descent**, not a figure stuck on a wall. No "high", no "drop", no "fall".
2. `beat01m04` re-prompted: mattress on the floor, no bed frame, no pillows, no headboard.
3. WORLD block now names the reference frame and fixes the layout: door left, window right,
   mattress right, chair + wardrobe back wall, radiator under the window. **Every room shot from
   batch 02 on passes `beat03m01` as a reference image**, so the set cannot drift.
4. Generation is capped at **5 parallel calls**, not 10, to stay under the input-image rate limit.

## Locked look (do not restate differently)
Cream paper ground, thick uniform outline, flat fills, no texture, no gradients. Night navy sky.
Denim blue only on jeans and the corridor doors/floor. One pale-yellow light source per frame.
THE STANDING ONES: same body, dot eyes, **no eyebrows, no mouth**. Arms straight down.
MC: never faces camera. Back or three-quarters only.
