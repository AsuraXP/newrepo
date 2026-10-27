# Frame reject log

| id | moment_text | problem | fix | status |
|----|-------------|---------|-----|--------|
| b01m06 | women under forty-five ... They were eating. | SCENE omitted the eating action; frame had no food. | Added "each holding one plain bowl of raw food and eating from it". | FIXED in batch 02 (verified). |
| b01m08 | Try eating a raw potato. Your teeth can break it. Your gut mostly can't use it. | Frame shows a hand, a potato and a stomach, but NO teeth — the "your teeth can break it" clause is unillustrated. | Added "one open cartoon mouth showing four square teeth beside the potato" and an arrow from teeth to gut. Prompt updated in tools/scenes.py + visuals.csv; frame NOT yet re-rolled. | PENDING — first image of next turn. |

| b02m08 | On a fixed calorie budget, a primate can afford a large gut or a large brain, | Frame put BOTH organs on the left pan, a pointing human on the right pan, and a huge CALORIES weight in the middle — the SCENE named zero people, and the trade-off is unreadable. | Rewrote SCENE: exactly two pans, one organ each, pans level, no people or figures anywhere, CALORIES only on the centre stand. | PENDING — first image of next turn. |

Rejected v1 frames kept in `rejects/` for comparison.
