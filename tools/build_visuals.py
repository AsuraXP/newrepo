#!/usr/bin/env python3
"""Build visuals.csv for a slug directly from narration.txt.

moment_texts are DERIVED from the narration (never re-typed), then asserted to
reconstruct it token-for-token — word-lock is a build-time guarantee.

Usage: python3 tools/build_visuals.py examples/apoc_day1_video
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- style blocks
STYLE = (
    "CINEMATIC 2D ANIMATION STILL: hand-painted digital animation frame, soft cel "
    "shading with visible brush texture, muted pre-dawn palette of cold blue-grey "
    "and deep teal with warm amber streetlight accents, atmospheric haze, filmic "
    "lighting, clean confident linework. Not a photograph, not 3D, not anime. 16:9 "
    "landscape. NO text, no letters, no numbers, no signage, no logos, no "
    "watermark, nothing printed on any surface."
)
YOU_HOME = ("CHARACTER: ONE adult, average build, short dark hair, plain calm face, "
            "wearing a plain grey t-shirt; exactly one person in this frame. ")
YOU_OUT = ("CHARACTER: THE SAME adult, average build, short dark hair, plain calm "
           "face, wearing a dark-green field jacket and dark trousers; exactly one "
           "person in this frame unless the sentence names more. ")
STAND = ("THE STANDING: tall dim grey-black human silhouettes, featureless vague "
         "faces, slack wrong posture; no wounds, no blood, no gore - threat from "
         "posture only. ")
WOMAN = ("the woman: ONE adult in a light grey coat with a canvas shoulder bag over "
         "one shoulder. ")
NEIGH = "the neighbour: ONE adult man in a brown coat, hand on a wheeled suitcase. "
NOBODY = "No people in this frame. "

# ---------------------------------------------------------------------- spec
# op forms: ("s", [sent...])          -> one row, whole sentences joined
#           ("x", sent, needle)       -> two rows, split sent before needle
#           ("mix", a, b, needle)     -> two rows: [sent a + b-up-to-needle], [b-from-needle]
# prompts: one per resulting row, literal to that row's moment_text.
SCENES: list[list[tuple[list[tuple], list[str]]]] = [


    # ---- B1 waking -----------------------------------------------------------
    [
        ([("s", [1])],
         [STYLE + YOU_HOME + "SCENE: dark bedroom before dawn, the adult jerking awake "
          "flat in bed, head lifted from the pillow, eyes open, room blue-grey; " + "only this one person."]),
        ([("s", [2, 3])],
         [STYLE + "SCENE: the view from the bedroom window: an empty residential street "
          "lined with parked cars under amber streetlights, several cars with hazard "
          "lights flashing, wet asphalt. " + NOBODY]),
        ([("s", [4])],
         [STYLE + YOU_HOME + "SCENE: the adult sitting up on the edge of the bed in grey "
          "dawn light, head tilted toward the window, listening hard; one person."]),
        ([("s", [5])],
         [STYLE + "SCENE: the same street from a higher angle, every parked car still "
          "flashing, sidewalks empty, nobody coming out of any building. " + NOBODY]),
    ],
    # ---- B2 phone ------------------------------------------------------------
    [
        ([("s", [6, 7, 8])],
         [STYLE + YOU_HOME + "SCENE: close over his shoulder in the dark bed: a phone in "
          "ONE hand, screen glowing with an abstract row of four solid signal bars at "
          "the top and NOTHING else on screen - no words, no numbers, no icons; one "
          "person."]),
        ([("s", [9])],
         [STYLE + "SCENE: extreme close on the phone: a thumb mid-swipe over a blank "
          "grey loading screen, faint motion blur, no text anywhere; ONE hand only."]),
        ([("x", 10, "and it freezes")],
         [STYLE + "SCENE: the phone screen fills the frame: a tiny shaky video showing "
          "EXACTLY THREE people running away down a dim street, grainy light, screen "
          "bezel visible, no interface, no text; only those three inside the video.",
          STYLE + "SCENE: the same phone screen FROZEN on the same THREE runners caught "
          "mid-stride, one foot hung in the air, image held rigid; only those three in "
          "the video, no text."]),
        ([("s", [11])],
         [STYLE + YOU_HOME + "SCENE: close on his face lit by the phone in the dark "
          "room, thumb pressing the glass again, brows tight; one person."]),
        ([("s", [12])],
         [STYLE + "SCENE: extreme close: the phone screen still showing the same frozen "
          "frame, ONE thumb pressed flat on the glass; one hand only."]),
        ([("s", [13])],
         [STYLE + "SCENE: the building lobby below seen dim from the stairwell: a heavy "
          "equipment stand tipped over on the tile, dust settling in one shaft of light. "
          + NOBODY]),
    ],
    # ---- B3 dress / window ---------------------------------------------------
    [
        ([("s", [14])],
         [STYLE + YOU_HOME + "SCENE: bedroom, the adult pulling the dark-green field "
          "jacket on, one arm through, unmade bed behind; one person."]),
        ([("s", [15])],
         [STYLE + "SCENE: the bedroom window in pale grey light with faint amber alarm "
          "flashes reflecting across the glass, curtain edge still. " + NOBODY]),
        ([("s", [16])],
         [STYLE + YOU_HOME + "SCENE: from behind: the adult crossing the dark bedroom "
          "toward the window, hand reaching for the frame, dawn glow ahead; one person, "
          "seen from behind."]),
    ],
    # ---- B4 the man in the road ---------------------------------------------
    [
        ([("s", [17])],
         [STYLE + STAND + "SCENE: looking down from the window: EXACTLY ONE dim figure "
          "walking down the middle of the empty road, parked cars either side; one "
          "figure only."]),
        ([("s", [18, 19])],
         [STYLE + STAND + "SCENE: closer from above: that SAME single figure mid-stride, "
          "unhurried, arms loose, dead centre on the road; one figure only."]),
        ([("s", [20, 21])],
         [STYLE + STAND + "SCENE: the SAME single figure now standing still in the middle "
          "of the road, feet together, arms hanging, facing away; one figure only, road "
          "otherwise empty."]),
        ([("s", [22])],
         [STYLE + STAND + "SCENE: the street from above: the first figure still standing "
          "mid-road AND across the street a SECOND dim figure just out of a doorway, "
          "stopped on the step; exactly two figures, nobody else."]),
    ],
    # ---- B5 six + the woman --------------------------------------------------
    [
        ([("s", [23])],
         [STYLE + STAND + "SCENE: wide street view: EXACTLY SIX dim standing figures "
          "scattered between doorways and parked cars, spaced apart; six figures only."]),
        ([("s", [24])],
         [STYLE + STAND + "SCENE: the SAME EXACTLY SIX figures standing idle where they "
          "are, weight slack, none moving toward anything; six figures only."]),
        ([("s", [25])],
         [STYLE + STAND + "SCENE: the EXACTLY SIX figures caught mid-drift between "
          "doorways, sparse spacing, slow wandering poses; six figures only."]),
        ([("x", 26, "and six heads")],
         [STYLE + WOMAN + "SCENE: street level: the woman in the light grey coat with the "
          "canvas shoulder bag running past the building frontage, mid-stride; one "
          "person only.",
          STYLE + STAND + "SCENE: the EXACTLY SIX standing figures with all six heads "
          "turned the same direction, tracking something off-frame; six figures only."]),
        ([("s", [27])],
         [STYLE + WOMAN + "SCENE: the woman alone reaching the street corner, feet "
          "planting, bag swinging; one person."]),
        ([("s", [28])],
         [STYLE + WOMAN + STAND + "SCENE: the corner: the woman pulling up short AND "
          "EXACTLY ONE dim figure already standing at the corner facing her; exactly "
          "two people."]),
        ([("s", [29])],
         [STYLE + WOMAN + "SCENE: the woman pivoting mid-corner to turn back the way she "
          "came, coat flaring; one person."]),
        ([("s", [30])],
         [STYLE + STAND + "SCENE: behind her: the EXACTLY SIX figures drifting on slowly, "
          "indifferent, the woman gone from frame; six figures only."]),
    ],
    # ---- B6 door -------------------------------------------------------------
    [
        ([("s", [31])],
         [STYLE + YOU_OUT + "SCENE: interior: the adult stepping back from the window, "
          "one hand still raised off the glass, room dim; one person."]),
        ([("s", [32, 33, 34])],
         [STYLE + "SCENE: close on the apartment door: ONE hand testing the knob then "
          "sliding the deadbolt home; one hand only, no other people."]),
        ([("s", [35])],
         [STYLE + YOU_OUT + "SCENE: his face close in the dim hall, palm flat on the "
          "locked door, quiet fear; one person."]),
    ],
    # ---- B7 quiet ------------------------------------------------------------
    [
        ([("s", [36, 37])],
         [STYLE + "SCENE: the empty apartment hallway with the stairwell door standing "
          "ajar, thin grey light, worn carpet. " + NOBODY]),
        ([("s", [38])],
         [STYLE + "SCENE: exterior: the apartment block at dawn, every window dark, "
          "street empty, air motionless in haze. " + NOBODY]),
    ],
    # ---- B8 water ------------------------------------------------------------
    [
        ([("s", [39])],
         [STYLE + "SCENE: kitchen: ONE hand under the running tap filling the sink, "
          "water swirling; one hand only."]),
        ([("s", [40])],
         [STYLE + "SCENE: the kitchen counter crowded edge to edge with water-filled "
          "pots, jars and glasses, tap still running behind them. " + NOBODY]),
        ([("s", [41])],
         [STYLE + "SCENE: extreme close on ONE glass jar brim-full of clear water "
          "catching grey window light, perfectly still. " + NOBODY]),
    ],
    # ---- B9 kitchen count ----------------------------------------------------
    [
        ([("x", 42, "bread, rice")],
         [STYLE + YOU_OUT + "SCENE: the adult at the kitchen counter, head bowed, fingers "
          "hovering over items as he counts them; one person.",
          STYLE + "SCENE: top-down on the counter: a loaf of bread, a bag of rice, ONE "
          "jar of peanut butter and a coffee pot, plain arrangement. " + NOBODY]),
        ([("s", [43])],
         [STYLE + YOU_OUT + "SCENE: close on his face, eyes narrowed doing mental "
          "arithmetic, kitchen dim behind; one person."]),
        ([("s", [44])],
         [STYLE + "SCENE: his TWO open hands palms-up beside the food - no paper, no "
          "phone, no pen anywhere near. " + NOBODY.replace("No people", "Only his hands")]),
        ([("s", [45])],
         [STYLE + YOU_OUT + "SCENE: he presses one finger to his temple, keeping the "
          "number in his head; one person."]),
    ],
    # ---- B10 the bag ---------------------------------------------------------
    [
        ([("s", [46, 47])],
         [STYLE + YOU_OUT + "SCENE: room floor: ONE dark duffel bag open, him kneeling "
          "over it; one person."]),
        ([("s", [48])],
         [STYLE + "SCENE: close: his hands placing a folded item into the bag with "
          "deliberate care; ONE pair of hands only."]),
        ([("s", [49, 50, 51])],
         [STYLE + "SCENE: top-down beside the open bag: EXACTLY THREE items laid out - a "
          "folded blank document, a coiled charging cable, and a kitchen knife; no "
          "people."]),
        ([("s", [52])],
         [STYLE + YOU_OUT + "SCENE: him sitting on the floor against the wall, packed bag "
          "at his feet, head canted listening; one person."]),
    ],
    # ---- B11 neighbour -------------------------------------------------------
    [
        ([("s", [53])],
         [STYLE + "SCENE: looking down the stairwell: the ground-floor door just shut, "
          "slice of light gone, empty stairs. " + NOBODY]),
        ([("s", [54])],
         [STYLE + NEIGH + "SCENE: the hallway: the neighbour in the brown coat stepping "
          "out with his wheeled suitcase; one person."]),
        ([("s", [55])],
         [STYLE + NEIGH + "SCENE: over the neighbour's shoulder: his gaze fixed on the "
          "closed door across the hall, hand on suitcase handle; one person."]),
        ([("s", [56])],
         [STYLE + NEIGH + YOU_OUT + "SCENE: from your doorway across the hall: YOU at "
          "frame edge from behind and the neighbour by his door - your view lands on HIS "
          "closed door; exactly two people."]),
        ([("s", [57])],
         [STYLE + NEIGH + YOU_OUT + "SCENE: wide hall: BOTH men standing at their own "
          "closed doors, neither raising a hand; exactly two people."]),
        ([("s", [58])],
         [STYLE + NEIGH + YOU_OUT + "SCENE: the hallway from above: BOTH men motionless "
          "at their doors, heads canted listening; exactly two people."]),
    ],
    # ---- B12 stairs ----------------------------------------------------------
    [
        ([("s", [59, 60])],
         [STYLE + "SCENE: the stairwell: empty stairs rising into shadow, one dim "
          "landing, nothing on them. " + NOBODY]),
        ([("s", [61, 62])],
         [STYLE + "SCENE: close on a single worn wooden stair tread in dim light, deep "
          "shadow above and below, absolute stillness. " + NOBODY]),
        ([("s", [63])],
         [STYLE + NEIGH + "SCENE: the neighbour in the hall turning his head toward the "
          "stairwell door, brow tight; one person."]),
        ([("s", [64])],
         [STYLE + YOU_OUT + "SCENE: you in your own doorway, also turned toward the "
          "stairwell, seen over-shoulder; one person."]),
        ([("s", [65])],
         [STYLE + NEIGH + YOU_OUT + "SCENE: wide: BOTH men in the hall with the stairwell "
          "door between them, neither stepping closer; exactly two people."]),
        ([("s", [66])],
         [STYLE + NEIGH + "SCENE: the neighbour pulling his suitcase through his own "
          "doorway, door swinging shut, your view from down the hall; one person."]),
    ],
    # ---- B13 the math --------------------------------------------------------
    [
        ([("s", [67])],
         [STYLE + YOU_OUT + "SCENE: him alone in the middle of the room, arms loose, eyes "
          "down, thinking; one person."]),
        ([("s", [68])],
         [STYLE + "SCENE: the room as it stands - four plain walls, the locked front "
          "door, the counter row of water vessels, the stairwell door beyond: the whole "
          "world of staying, one still frame. " + NOBODY]),
        ([("s", [69])],
         [STYLE + STAND + "SCENE: through the window: the street below with a dozen dim "
          "standing figures scattered its length, his dark bag resting on the sill in "
          "foreground; the figures are the only people."]),
        ([("s", [70])],
         [STYLE + YOU_OUT + "SCENE: him standing squarely between the locked door and the "
          "window, the literal fork of the room; one person."]),
        ([("s", [71])],
         [STYLE + YOU_OUT + "SCENE: close on his face, set jaw, cold light on one side, "
          "decision forming; one person."]),
    ],
    # ---- B14 lobby bangs -----------------------------------------------------
    [
        ([("s", [72, 73, 74, 75])],
         [STYLE + STAND + "SCENE: ground-floor lobby interior: the glass entrance door "
          "rattling in its frame from a blow, ONE dim silhouette barely visible through "
          "the frosted glass outside; exactly one figure outside, lobby empty inside."]),
        ([("s", [76])],
         [STYLE + "SCENE: the lobby interior held still - glass doors, one horizontal "
          "push bar, the empty street visible beyond. " + NOBODY]),
        ([("s", [77])],
         [STYLE + "SCENE: close on the push bar and door edge vibrating with each knock, "
          "faint motion blur, cold light at the seams. " + NOBODY]),
        ([("s", [78, 79])],
         [STYLE + STAND + "SCENE: through the frosted glass: the dim figure standing "
          "outside unhurried and still - silhouette only; exactly one figure."]),
    ],
    # ---- B15 leave -----------------------------------------------------------
    [
        ([("s", [80])],
         [STYLE + YOU_OUT + "SCENE: him stooping to lift the packed duffel off the floor; "
          "one person."]),
        ([("s", [81, 82])],
         [STYLE + "SCENE: the counter: the row of filled vessels and the coffee pot left "
          "behind, ONE hand just leaving the frame edge. " + NOBODY]),
        ([("s", [83])],
         [STYLE + YOU_OUT + "SCENE: him standing ready: bag slung on ONE shoulder, the "
          "dark phone in his other hand, a knife handle just showing from the bag's side "
          "pocket; one person."]),
        ([("s", [84])],
         [STYLE + "SCENE: from inside: ONE hand on the handle swinging the apartment door "
          "open onto the dark hall; one hand only."]),
    ],
    # ---- B16 empty hall ------------------------------------------------------
    [
        ([("s", [85])],
         [STYLE + "SCENE: the hallway empty end to end, lights low, still. " + NOBODY]),
        ([("s", [86])],
         [STYLE + "SCENE: down the hall: ONE door standing ajar at the far end with the "
          "wheeled suitcase abandoned beside it. " + NOBODY]),
    ],
    # ---- B17 lobby -----------------------------------------------------------
    [
        ([("s", [87])],
         [STYLE + "SCENE: the stairwell descending, flights curving down into shadow, "
          "handrail catching grey light. " + NOBODY]),
        ([("s", [88])],
         [STYLE + YOU_OUT + "SCENE: seen from above: him descending the stairs, bag in "
          "hand; one person."]),
        ([("x", 89, "and beyond it")],
         [STYLE + "SCENE: lobby interior: the glass door flexing in its frame, hairline "
          "gaps of light at its edges, street blurred beyond. " + NOBODY,
          STYLE + STAND + "SCENE: through the lobby glass: the street beyond with "
          "EXACTLY FOUR dim figures drifting sparse across it; four figures only."]),
        ([("s", [90])],
         [STYLE + YOU_OUT + "SCENE: close: his TWO hands - one gripping the bag strap on "
          "his shoulder, one flat on the horizontal push bar; one person, torso and "
          "hands only."]),
    ],
    # ---- B18 hesitate --------------------------------------------------------
    [
        ([("mix", 91, 92, "you could go back up")],
         [STYLE + YOU_OUT + "SCENE: him frozen at the lobby door, head half-turned back "
          "toward the stairs behind him; one person.",
          STYLE + "SCENE: his view: the stairwell rising back up toward his floor, the "
          "door above half-lit - the path not taken. " + NOBODY]),
    ],
    # ---- B19 push through ----------------------------------------------------
    [
        ([("s", [93])],
         [STYLE + "SCENE: close: his palm pressing the push bar, the door beginning to "
          "swing outward; ONE hand and shoulder only."]),
        ([("s", [94])],
         [STYLE + YOU_OUT + "SCENE: the lobby doors swinging outward onto the street: "
          "wind pulling his jacket, dark building windows across the road, him stepping "
          "through in silhouette; one person."]),
        ([("s", [95])],
         [STYLE + "SCENE: street view: his dark car parked two blocks down under an amber "
          "light, solid and real, street around it motionless. " + NOBODY]),
    ],
    # ---- B20 walk ------------------------------------------------------------
    [
        ([("s", [96, 97])],
         [STYLE + YOU_OUT + STAND + "SCENE: him walking - not running - along the "
          "pavement, steady-armed, while FAR behind EXACTLY TWO dim figures stand facing "
          "away; one near person plus two far figures."]),
        ([("x", 98, "while behind you")],
         [STYLE + YOU_OUT + "SCENE: side view: him mid-stride at a fast walk, eyes fixed "
          "ahead, one foot reaching forward; one person.",
          STYLE + YOU_OUT + "SCENE: from BEHIND him: his back walking away, the apartment "
          "block looming behind, head staying forward, face not visible; one person."]),
        ([("x", 99, "then the whole street")],
         [STYLE + YOU_OUT + "SCENE: mid-block: him walking past parked cars as two cars' "
          "hazard flashes die out one after the other; one person plus cars.",
          STYLE + YOU_OUT + "SCENE: wide: the street hushed and empty around him, him "
          "small alone in frame, air still; one person."]),
    ],
    # ---- B21 ending ----------------------------------------------------------
    [
        ([("s", [100, 101, 102])],
         [STYLE + YOU_OUT + "SCENE: wide: him crossing the last of the street toward his "
          "waiting car two blocks on, bag over shoulder, dawn light strengthening; one "
          "person."]),
        ([("s", [103])],
         [STYLE + YOU_OUT + "SCENE: final wide: him at the car door, hand reaching for "
          "the handle, pale sun clearing the rooftops; one person."]),
    ],
]


def main() -> None:
    episode = Path(sys.argv[1])
    text = (episode / "narration.txt").read_text(encoding="utf-8")
    text = re.sub(r"\s+", " ", text).strip()
    sents = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    sent = lambda n: sents[n - 1]  # noqa: E731  1-based

    rows: list[tuple[int, int, str, str]] = []
    cells = [(op, pr) for scene in SCENES for (op, pr) in scene]
    for beat, scene in enumerate(SCENES, start=1):
        out_texts: list[str] = []
        scene_prompts: list[str] = []
        for ops, prompts in scene:
            scene_prompts += prompts
            for op in ops:
                if op[0] == "s":
                    out_texts.append(" ".join(sent(n) for n in op[1]))
                elif op[0] == "x":
                    s = sent(op[1])
                    pos = s.index(op[2])
                    out_texts += [s[:pos].rstrip(), s[pos:]]
                elif op[0] == "mix":
                    a, b = sent(op[1]), sent(op[2])
                    pos = b.index(op[3])
                    out_texts += [(a + " " + b[:pos].rstrip()).strip(), b[pos:]]
                else:
                    raise SystemExit(f"bad op {op}")
        assert len(out_texts) == len(scene_prompts), f"beat {beat}: {len(out_texts)} texts vs {len(scene_prompts)} prompts"
        for m, (t, p) in enumerate(zip(out_texts, scene_prompts), start=1):
            rows.append((beat, m, t, p))

    # word-lock guarantee: rows must reconstruct the narration token-for-token
    rebuilt = " ".join(r[2] for r in rows)
    assert rebuilt.split() == text.split(), (
        "RECONSTRUCTION FAILED\n"
        f"expected {len(text.split())} tokens, got {len(rebuilt.split())}\n"
        + next(f"diff at {i}: {a!r} vs {b!r}\n"
               for i, (a, b) in enumerate(zip(text.split(), rebuilt.split())) if a != b)
    )

    out = episode / "visuals.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["slide_id", "moment", "moment_text", "visual_prompt"])
        w.writerows(rows)

    words = len(text.split())
    print(f"OK {out}: {len(rows)} moments, {len(SCENES)} beats, {words} words, "
          f"~{words / 2.75 / 60:.1f} min, avg {words / len(rows):.1f} w/moment")


if __name__ == "__main__":
    main()
