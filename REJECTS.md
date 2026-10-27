# Frame reject log

| id | moment_text | problem | fix | status |
|----|-------------|---------|-----|--------|
| b01m06 | women under forty-five ... They were eating. | SCENE omitted the eating action; frame had no food. | Added "each holding one plain bowl of raw food and eating from it". | FIXED in batch 02 (verified). |
| b01m08 | Try eating a raw potato. Your teeth can break it. Your gut mostly can't use it. | Frame shows a hand, a potato and a stomach, but NO teeth — the "your teeth can break it" clause is unillustrated. | Added "one open cartoon mouth showing four square teeth beside the potato" and an arrow from teeth to gut. Prompt updated in tools/scenes.py + visuals.csv. | FIXED in batch 03 (verified — open mouth with four square teeth present). |

| b02m08 | On a fixed calorie budget, a primate can afford a large gut or a large brain, | Frame put BOTH organs on the left pan, a pointing human on the right pan, and a huge CALORIES weight in the middle — the SCENE named zero people, and the trade-off is unreadable. | Rewrote SCENE: exactly two pans, one organ each, pans level, no people or figures anywhere, CALORIES only on the centre stand. | FIXED in batch 04 (verified). |

| b04m02 | Heat and water burst them open so digestive enzymes can get inside. | Model drew six spiky star/explosion shapes with no readable granules and no visible enzyme shapes. Reads as fireworks, not starch gelatinisation. | Rewrote SCENE: ROUND granules cracked like split peas, explicitly NOT stars/explosions, three round enzyme dots entering the cracks. | FIXED in batch 06 (verified). |

Rejected v1 frames kept in `rejects/` for comparison.

## WEAK BUT KEPT (observer flags, not rejects)

| batch | frames | issue |
|---|---|---|
| 06 | `b04m10` | brain/coin/2012 frame has a stray question-mark doodle; coin is grey instead of the electric-yellow accent. Moment fidelity is intact. |
| 07 | `b04m13`, `b04m16`, `b04m17`, `b04m18`, `b05m01`, `b05m02` | No electric-yellow accent applied, or it landed on an ochre/terracotta fill instead of the named object. Line work, counts, actions and all four text strings remain correct. Style accent drift only — not a fidelity failure. |
| 07 | `b04m18` | Almost monochrome brown; flattest frame in the batch. Kept because the two technologies (stone axe + fire) and the invention spark are all present and nothing extra was added. |
| 08 | `b05m05` | Narration says "twenty-six" (percent implied from the previous clause); frame shows `26%`. Scientifically correct and matches the locked SCENE, but it is a digit-plus-symbol rendering of a word the sentence does not spell out. Kept for consistency with our established `30%` / `5%` convention. |
| 08 | `b05m10` | The three trait icons sit slightly spread along the timeline rather than stacked on the one dot. "Arriving all at once" still reads, but it is the weakest fidelity frame in this batch. |
| 08 | `b05m12` | `2009` label is on the book cover, not beneath the book as the SCENE asked. Both strings are spelled correctly. |
| 08 | `b05m06`, `b05m07`, `b05m08`, `b05m11`, `b05m12`, `b05m13` | Electric-yellow accent missing again or rendered as ochre. Counts, actions, gaze and all text are correct — style accent drift only. |
