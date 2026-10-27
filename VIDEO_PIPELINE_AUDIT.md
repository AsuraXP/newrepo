## Audit: what was wrong, and what changed

The previous version had 16 defects. Several were contradictions with itself.

**1. "Show it; do not explain what it means" — listed as *universal* craft.**
This is the worst one. Three lines later the same step says "if it is an
explainer, explain with evidence and mechanism." An explainer's entire job is
explaining meaning. A narrative rule was sitting in the universal slot.
→ Craft is now split into two columns: story/narrative vs explainer/documentary.

**2. "Short sentences. Concrete nouns. Cut the first paragraph."**
House style presented as law. Fine for a 5-minute horror story, wrong for a
technical explainer that needs subordinate clauses to state a condition.
→ Moved under the type-specific column.

**3. "Is the hook in the first two lines?"**
Format bias. That is YouTube-retention thinking. Wrong for a slow essay, a
tutorial, or a documentary that opens on a place.
→ Now: "Does the opening earn the next thirty seconds?" Works for every type.

**4. The document broke its own rule.**
It opened with "Everything below is PROCESS and is fixed... this has no house
style," then hardcoded a narrator voice, single-take doctrine, and a thumbnail
spec. Four contradictions with its own first paragraph.
→ Split into PROCESS (fixed) vs DEFAULTS (overwritable), stated plainly.

**5. "10 images per turn" plus "the batch isn't done until every frame works."**
An operational contradiction that actually cost us repeatedly. Ten calls spent,
three failures found, batch dead until the next turn.
→ Budget rule: generate 7-8, hold 2-3 back for same-turn re-rolls.

**6. "Never ask twice" sitting above three hard approval gates.**
Could license skipping the script gate, which is the most expensive gate there
is.
→ Scoped: applies to execution, not to brief / script / style.

**7. "Count the people the sentence names. Draw exactly that many."**
Over-literal. Fails on "dozens", "a crowd", "the street was full of them" — a
line I actually hit, and it produced pedantic frames.
→ Literal count when the line gives a number; read the sense of the line when
it gives a mass.

**8. No escape hatch for an impossible brief.**
Nothing told the agent what to do when asked for 60 seconds and 200 frames.
→ Name the contradiction in one line, propose the closest workable version, let
me choose.

**9. No runtime check before rendering.**
You discovered the script was the wrong length *after* 100 frames existed.
→ Word count and estimated runtime are stated at the script gate.

**10. The package assumed YouTube.**
`youtube.txt`, portrait thumbnail, chapters — baked in as though every video
goes to YouTube.
→ Package now matches the platform named at intake; captions and vertical cut
are conditional.

**11. No captions. No music.**
Bias by omission, inherited from a project that needed neither. Most videos
need at least one of them.
→ Both are now intake questions and both appear in the audio and package steps.

**12. Thumbnail spec: "the strongest face, object or moment."**
Assumes there is a face. An abstract explainer has none.
→ "The strongest image this particular video has, whatever that is."

**13. The build step assumed a repo, Kaggle, and edge-tts.**
Infrastructure bias from one project's stack.
→ Environment-agnostic: cloud, CI, or local; standalone script if there is no
repo.

**14. Aspect ratio never connected to the image prompts.**
Vertical video was treated as a later crop, which produces dead compositions.
→ Style lock records the aspect and composition is built for it.

**15. No continuity system for recurring subjects.**
The reason characters drifted mid-project, and why a hand changed colour for
four frames.
→ Running continuity list, full description every time.

**16. The four roles were decorative.**
"Name the hat when it matters" was never referenced again; OBSERVER appeared
once.
→ OBSERVER is operational at two named gates only.

### The pattern in the mistakes

Every one of the sixteen came from the same source: **rules learned on one
project being written as universal law.** The prompt kept saying "no house
style" while smuggling a specific film's taste into the plumbing.

The correction is structural, not cosmetic: the prompt now separates what is
genuinely process (batching, naming, verification, handoff) from what is preference
(voice, craft rules, package contents), and it says out loud which is which.
