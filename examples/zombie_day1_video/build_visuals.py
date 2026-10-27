"""Regenerate visuals.csv from narration.txt.

STYLE below is prepended verbatim to EVERY visual_prompt. Do not paraphrase it.
"""
import csv

STYLE = ("Cinematic painterly 2D animation still, 16:9 wide landscape, muted desaturated "
         "palette of ash grey, dust brown and cold teal, one single rust-red accent colour, "
         "heavy film grain, overcast diffused daylight, deep soft shadows, simple shapes, "
         "no outlines, atmospheric, no text, no letters, no numbers, no signage, no logos, "
         "no watermark.")

S = ("The survivor is one lean young adult with short dark hair, exactly two dark eyes, "
     "a dark charcoal jacket, dark trousers, brown boots and a rust-red backpack; "
     "rust-red is the only saturated colour in frame.")
B = ("The boy is one small barefoot child with short pale hair, exactly two eyes, "
     "a pale blue shirt with a dark brown stain down the front, dull grey shorts, "
     "holding an empty brown dog lead.")
W = ("one infected woman with pale grey skin, a long dull grey coat, head hanging forward, "
     "exactly two eyes, no blood, no wounds")
M = ("one infected man with pale grey skin, a dusty brown coat, forehead against glass, "
     "head hanging forward, exactly two eyes, no blood, no wounds")


def I(n):
    return (f"exactly {n} infected figures with pale grey skin, dull shapeless everyday "
            "clothes, heads hanging forward, exactly two eyes each, no blood, no wounds, "
            "no gore,")


ONE = "Only one person in this frame."
NONE = "No people in this frame."
EX2 = "Exactly two people in this frame."
EX3 = "Exactly three people in this frame."
EX4 = "Exactly four people in this frame."
EX6 = "Exactly six people in this frame."

SCENES = [
 f"{S} A small dim bedroom at first light, the survivor sitting bolt upright in a rumpled bed, eyes wide open, head turned toward a window, listening. {ONE}",
 f"A small round wall clock with a blank dark face and two perfectly still hands hangs on a cracked grey wall in a dim bedroom. {NONE}",
 f"{S} Close view of one black phone with a completely blank dark screen held in the survivor's single hand directly in front of their face, thumb resting on the glass, an empty dim bedroom behind them. {ONE}",
 f"{S} A small kitchen in cold grey light, one open refrigerator with a dark empty interior and still shelves, the survivor standing in front with one hand on the door. {ONE}",
 f"Close view of a faded grey curtain shifting inward under two fingers at its edge, a thin blade of bright daylight at the gap, no full figure visible. {ONE}",
 f"High window view over an ordinary empty city street at dawn, rows of parked cars, grey apartment blocks, an open bus shelter, an overcast sky. {NONE}",
 f"Street level view of one empty city bus stopped at a shelter with its folding door hanging open, no driver and no passengers anywhere. {NONE}",
 f"Close view of one traffic light glowing amber above an empty crossroads, wet asphalt below, no cars and no readable markings. {NONE}",
 f"Wide elevated view of one completely empty city street, parked cars along both kerbs, one open bus door and one amber traffic light, no moving figures. {NONE}",

 f"{W.capitalize()} steps out from a concrete bus shelter onto an empty road at dawn. {ONE}",
 f"{W.capitalize()} stands stopped in the middle of an empty road, feet apart, head down. {ONE}",
 f"{W.capitalize()} stands on an empty road with her head hanging so far forward that her face points at the asphalt. {ONE}",
 f"Low close view of one infected woman's lowered face, pale grey skin, chin near her chest, eyes directed only at the ground, exactly two eyes, no blood, no wounds, empty road behind. {ONE}",
 f"Side view of one infected woman's shoulders rising and falling very slowly under a long dull grey coat, pale grey skin, head hanging forward, exactly two eyes, no blood, no wounds, empty road behind. {ONE}",
 f"{M.capitalize()} stands with his forehead resting against a shop window on an empty pavement, arms hanging loose. {ONE}",
 f"{M.capitalize()} remains motionless with his forehead against a shop window, the empty street reflected in the glass. {ONE}",
 f"Wide street view with {W} in the road and {M} at a shop window, both facing away from each other, heads lowered, no interaction. {EX2}",
 f"Wide street view with {W} in the road and {M} at a shop window, both turning their heads in the same direction toward something off frame. {EX2}",
 f"A glass bottle tipping out of a metal bin onto an empty pavement while {W} in the road and {M} at the shop window both snap their heads toward the falling bottle. {EX2}",
 f"{W.capitalize()} in the road and {M} at the shop window both turn their heads toward one glass bottle rolling on the pavement, ignoring everything else. {EX2}",

 f"Interior view of one wooden apartment front door in a dim flat, three faint round scuffs low down on the wood, dust hanging in the light. {NONE}",
 f"Close view of the lower half of one wooden front door with three small scuff marks at knee height, a thin line of grey hallway light under the door. {NONE}",
 f"{S} Close profile view of the survivor's face inside a dim flat, eyes fixed on a door, head tilted, listening. {ONE}",
 f"{B} The boy stands seen from behind in a dim apartment hallway in front of one closed wooden door, barefoot on cold tiles. {ONE}",
 f"{B} The boy stands on tiptoe reaching one hand over a low brick wall toward a worn ball on the other side, an empty dog lead hanging from his other hand, dim courtyard. {ONE}",
 f"{S} The survivor leans forward and presses one eye to the peephole of a wooden front door inside a dim flat. {ONE}",
 f"{B} Circular peephole view of the boy standing on cold grey hallway tiles, seen from the front. {ONE}",
 f"{B} Circular peephole view of the boy's single open hand pressed flat against the wooden door at chest height, cold dim hallway behind. {ONE}",
 f"{B} Circular peephole view of the boy holding a brown dog lead up in his other hand, the lead dangling loose. {ONE}",
 f"{B} Close circular peephole view of the boy's empty brown dog lead with an unclipped metal clip hanging loose from a small hand, no dog anywhere. {ONE}",
 f"Circular peephole view down a dim empty hallway floor where one brown dog lead trails to an empty metal clip on the tiles, no dog, small bare feet at the edge of frame. {ONE}",
 f"{B} Circular peephole view of the boy's face turned sideways away from the door so his eyes look down the hallway, dim light behind. {ONE}",

 f"{B} Circular peephole view of the boy raising one small fist to knock three times on a wooden door, dim hallway. {ONE}",
 f"{S} Close view from inside a dim flat of the survivor's hand reaching up to a brass door lock, fingers extended. {ONE}",
 f"Extreme close view of the survivor's fingers frozen on a brass door lock, not turning it, knuckles tense, dim light. {ONE}",
 f"{B} Circular peephole view of the boy's pale blue shirt with a dark brown stain running down the front, his lowered chin above it. {ONE}",
 f"{B} Circular peephole view of the boy's face with exactly two wide unblinking eyes staring at the door, short pale hair. {ONE}",
 f"{B} Extreme close view through a coin-sized peephole: one circular frame of grey hallway light holding the boy's perfectly still face. {ONE}",
 f"{S} Dim interior of a flat, the survivor kneeling at a wooden door with one hand on the wood and head bowed, a small worn ball on the floor nearby. {ONE}",
 f"{B} Circular peephole view of the boy knocking again on a wooden door that stays firmly closed in the foreground. {ONE}",
 f"{S} Close view from inside a dim flat of the survivor's hand sliding a metal bolt across a wooden door, finger pads pressing gently. {ONE}",
 f"{B} Circular peephole view of the boy's head snapping toward the camera lens, short pale hair still, dim hallway. {ONE}",
 f"{B} Circular peephole view of the boy's face pressed close against the door glass, cheek flattened against the wood, dim hallway behind. {ONE}",
 f"{S} Interior of a dim flat, the survivor backing away from a wooden door with both hands clamped over their mouth, eyes wide. {ONE}",
 f"{B} Circular peephole view of the boy standing perfectly still outside a closed wooden door, head lowered, an empty dog lead hanging from one hand. {ONE}",
 f"{S} Interior of a dim flat, the survivor sitting with their back pressed against a wooden door, head tilted to listen, the rust-red backpack on the floor beside them. {ONE}",

 f"{S} Interior of a dim flat, the survivor sitting with their back against a wooden door, jaw set, looking toward a bright window. {ONE}",
 f"Close view of the survivor's hand resting flat on a closed wooden door, not reaching for the lock, brass bolt still in place. {ONE}",
 f"{S} The survivor stands up from the floor beside a closed door and turns toward a bright window. {ONE}",
 f"Window view from a dim flat over a grey city roofline, one tall old water tower standing alone on a distant ridge against an overcast sky. {NONE}",
 f"{S} The survivor seen from behind at a window, dark charcoal jacket and rust-red backpack already on, looking out at a distant water tower on a ridge under a low sun. {ONE}",

 f"{S} Dim bedroom, the survivor crouching to pull an empty rust-red backpack from the bottom of an open closet, clothes on hangers above. {ONE}",
 f"{S} Small kitchen, the survivor lining up four clear water bottles under a running tap, one bottle filling, grey light from a window. {ONE}",
 f"Close view of one kitchen tap with water slowing to a final drip into an overflowing clear bottle, metal sink below. {NONE}",
 f"Overhead view of one open rust-red backpack on a table holding a small torch, a lighter and one folded warm coat, the survivor's hands arranging them. {ONE}",
 f"Close view of one small framed photograph lying face down on a wooden shelf, its blank back visible, the survivor's hand just leaving it, dim room behind. {ONE}",
 f"Close low view of the survivor's two brown boots with laces being tied twice on a dim bedroom floor. {ONE}",
 f"Interior of a dim flat, one wooden front door with a dark peephole at its centre and no light coming through, the survivor's shoulder at the edge of frame. {ONE}",
 f"Extreme close view of a dark peephole in a wooden door with one vague pale shape pressed against the other side of the glass, no distinct features. {NONE}",
 f"Close view from inside a dim flat of the survivor's hand hovering near a brass door handle without touching it, fingers curled back. {ONE}",

 f"{S} Small bedroom with one window pushed fully open onto a rusty metal fire escape, grey curtains blowing inward, the survivor's leg already on the sill. {ONE}",
 f"{S} The survivor straddles an open bedroom window sill with one leg inside and one leg out on a metal fire escape platform. {ONE}",
 f"{S} The survivor descends a rusty metal fire escape staircase, one boot on a creaking step and both hands on the rail, seen from below. {ONE}",
 f"{S} The survivor pauses halfway down a metal fire escape and looks up at one open window above, seen from below. {ONE}",
 f"Close view of one open bedroom window high above with one grey curtain still swinging outward in the breeze, metal fire escape railing in the foreground. {NONE}",
 f"Interior view of one dim apartment hallway with a closed wooden door, three faint scuff marks low on the wood and an empty dog lead lying on the tiles. {NONE}",

 f"{S} A narrow wet alley between two grey brick buildings, rows of metal bins along one wall, puddles on the stone, the survivor pressed flat against the near wall. {ONE}",
 f"{S} A narrow wet alley with the survivor pressed against the near wall in the foreground and {I(1)} standing at the far end with its back turned, facing a bright street opening. {EX2}",
 f"{S} A narrow wet alley with the survivor crouched behind metal bins in the foreground and {I(1)} at the far end completely motionless, facing a bright street opening. {EX2}",
 f"{S} Close low view down a wet alley of the survivor taking one careful step between puddles, with {I(1)} far ahead with its back turned. {EX2}",
 f"Close view of one brown boot nudging one clear glass jar lying on wet stone in a narrow alley, a puddle reflecting grey light. Only one person in this frame.",
 f"Close view of one clear glass jar rolling once across wet stone toward a metal drain grate in a narrow alley, small ripples in a puddle. {NONE}",
 f"{S} A narrow wet alley where {I(1)} at the far end turns its head back over one shoulder toward the camera while the survivor freezes against the near wall. {EX2}",
 f"{S} Close view of the survivor standing frozen in a wet alley, lips pressed tight, eyes fixed on something ahead. {ONE}",
 f"{S} A narrow wet alley where {I(1)} takes two slow dragging steps toward the camera then stops while the survivor stays pressed against the near wall. {EX2}",

 f"Close view inside one open rust-red backpack of the survivor's fingers closing around the neck of one empty clear glass bottle, other supplies around it. {ONE}",
 f"{S} The survivor in a wet alley, seen from behind, arm drawn back, throwing one clear glass bottle toward the far end of the street. {ONE}",
 f"Close view of one clear glass bottle breaking into shards on empty asphalt beyond a street corner. {NONE}",
 f"A narrow wet alley opening onto a street where {I(1)} turns away from the camera and walks toward a far corner, head hanging forward. {ONE}",
 f"Street beyond an alley mouth with {I(3)} walking away from the camera toward a far corner, two of them stepping out of a dark doorway, heads lowered. {EX3}",
 f"Wide view of one empty city street at the mouth of an alley, no moving figures, parked cars, overcast light. {NONE}",
 f"{S} The survivor walks slowly out of an alley with a dragging step, head lowered, arms loose, seen from the side. {ONE}",

 f"{S} Wide view of one city square with {I(3)} wandering between parked cars, heads lowered, and the survivor with a rust-red backpack at the near corner. {EX4}",
 f"Street view of {I(3)} moving between parked cars without hurry, heads hanging forward, dragging steps, no interaction. {EX3}",
 f"Close view of one broken shop window with jagged glass edges and a pavement covered in scattered glass shards, no signage and no readable markings. {NONE}",
 f"{S} The survivor walks in the deep shade under a row of grey shop awnings, head down, seen from the side. {ONE}",
 f"Close view from behind of the survivor's shoulders bent under a heavy rust-red backpack, short dark hair, both hands gripping the straps. {ONE}",
 f"{S} Street view with {I(1)} turning its head toward the camera while the survivor keeps their head down and walks past. {EX2}",
 f"{S} Side view of the survivor walking with a slow dragging step, head hanging forward, arms loose, mimicking an infected gait. {ONE}",
 f"Close view of the survivor's lowered face looking only at the pavement, short dark hair falling forward, rust-red backpack strap at the shoulder. {ONE}",

 f"{S} Wide view of one empty city street beginning to climb toward a distant ridge, grey houses stepped up the slope, the survivor small in the foreground. {ONE}",
 f"View of one road turning from cracked asphalt to brown dirt as grey houses thin out into open scrubland, the survivor with a rust-red backpack walking away from the camera. {ONE}",
 f"{S} The survivor reaches the top of one low stone wall as the sun sits low behind them, long shadows on a dirt road. {ONE}",

 f"Low angle view of one tall old water tower standing on four thin metal legs against an overcast sky, the survivor at its base looking up. {ONE}",
 f"{S} The survivor climbs a tall metal ladder up the side of a water tower, hands and boots on the rungs, face turned upward, not looking down. {ONE}",
 f"Wide view from the top of a water tower over one whole grey city under a low veil of brown smoke, the survivor sitting at the edge seen from behind. {ONE}",
 f"Wide silent aerial view of one empty grey city with no vehicles moving, thin brown smoke over the rooftops, an overcast sky. {NONE}",
 f"Aerial view from a water tower down onto one grid of grey streets with one single apartment window holding a pale grey curtain among dark buildings, the survivor's shoulder at the edge of frame. {ONE}",
 f"Close aerial view through grey haze of one apartment window where a pale curtain is moving outward in the breeze, the window standing open, dark buildings around. {NONE}",
 f"Close aerial view of one open apartment window with its pale curtain pushed aside by wind, the room behind it empty and dark. {NONE}",
 f"View from a water tower toward one distant open apartment window, the survivor standing on the tower platform in the foreground with their back to the camera. {ONE}",
 f"Close aerial view of one dark apartment room through an open window where one vague pale human-shaped figure stands perfectly still deep in the shadows behind a moving curtain, no clear face. {ONE}",
 f"View from a water tower platform down at one dirt road climbing a bare hill toward the tower, the survivor's boots and rust-red backpack at the edge of frame. {ONE}",
 f"Wide view from a water tower down at {I(5)} walking slowly up one bare dirt hill toward the tower, heads hanging forward, arranged in one line. Exactly five people in this frame.",
 f"Low view from the base of a water tower up at {I(5)} following a trail of boot prints in the dirt toward the metal ladder, heads lowered. Exactly five people in this frame.",
 f"{S} The survivor stands on a water tower platform looking at one low orange sun near the horizon, long shadows, seen in profile. {ONE}",
 f"{S} The survivor stands at the top of a water tower beside the single metal ladder leading down; far below at its base {I(5)} stand in one line, seen from above. {EX6}",
]

# beat sizes (consecutive runs of slide_id)
BEAT_SIZES = [9, 11, 12, 14, 5, 9, 6, 9, 7, 8, 3, 9, 5]

lines = [l.strip() for l in open("narration.txt", encoding="utf-8") if l.strip()]
assert len(lines) == len(SCENES), f"narration {len(lines)} vs scenes {len(SCENES)}"
assert sum(BEAT_SIZES) == len(lines), f"beat sizes {sum(BEAT_SIZES)} vs {len(lines)}"

rows, idx = [], 0
for sid, size in enumerate(BEAT_SIZES, 1):
    for m in range(1, size + 1):
        rows.append({
            "slide_id": sid,
            "moment": m,
            "moment_text": lines[idx],
            "visual_prompt": STYLE + " " + SCENES[idx],
        })
        idx += 1

with open("visuals.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["slide_id", "moment", "moment_text", "visual_prompt"])
    w.writeheader()
    w.writerows(rows)
print(f"[build_visuals] wrote visuals.csv: {len(rows)} moments in {len(BEAT_SIZES)} beats")
