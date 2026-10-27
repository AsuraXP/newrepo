"""Builds visuals.csv for quiet_day1.

moment_text is sliced straight out of narration.txt, so the CSV can never drift
from the approved script. visual_prompt is STYLE + WORLD + CHARACTER + SCENE +
NO-TEXT, assembled here so the fixed blocks stay verbatim across 104 frames.

Run:  python3 build_visuals.py
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

HERE = Path(__file__).parent

STYLE = (
    "Clean hand-drawn doodle cartoon. Thick uniform black outlines on every shape, "
    "flat solid colour fills only, no gradients, no texture, no shading, no hatching, "
    "no detail lines. Off-white cream paper ground. One soft flat pale-grey oval ground "
    "shadow per figure. Minimal faces: big round white head, two small black dot eyes, "
    "thin eyebrows, small mouth line. Limbs are thin even noodle lines. "
    "Palette: cream, black, denim blue, night navy, one pale-yellow light. "
    "16:9 cinematic widescreen."
)

WORLD = (
    "SAME ROOM AS THE REFERENCE IMAGE where a room is shown: keep the layout exactly - door on the left "
    "wall, window on the right wall, mattress on the floor to the right, wooden chair and wardrobe "
    "against the back wall, low shelf with tins, painted-over radiator under the window. "
    "WORLD (keep consistent in every frame): a five-storey 1970s concrete apartment "
    "block, cream-painted inside, wide worn floorboards drawn with visible plank lines. "
    "The room is one room: a mattress on the floor, a wooden chair, a low shelf with a few "
    "tins, a painted-over radiator under the window, a bare bulb on a cord that is off, a "
    "plain wardrobe. Outside the door the corridor has cream walls, identical plain doors "
    "on both sides, a strip ceiling light, and a black iron railing at the far end where the "
    "stairwell drops away. The window looks onto a narrow side street: shuttered shops, lamp "
    "posts, one parked car, and the dark block of flats opposite. A metal drainpipe runs down "
    "the outside of the wall four feet left of the window, past the roof of the shop below."
)

MC = (
    "CHARACTER (the protagonist, referred to as MC below): one young adult, always seen from "
    "behind or three-quarters away, never facing the camera. Big round white head, short black "
    "hair with three thin tufts sticking up, two small black dot eyes, thin eyebrows, small "
    "flat mouth. Plain black short-sleeve t-shirt, blue jeans with rolled cuffs, white sneakers "
    "with thick black outline."
)

THEM = (
    "THE STANDING ONES (referred to as THEM below): drawn by the same hand but emptied. Same "
    "big round white head, same short black hair, two small black dot eyes, but no eyebrows and "
    "no mouth at all. Plain black t-shirt, blue jeans, white sneakers. Arms hanging straight "
    "down, heads tilted to one side, perfectly still. Posture slack and patient, never aggressive. "
    "No injury, no marks on skin, no blood, no torn clothes."
)

NOTEXT = (
    "No text, no letters, no numbers, no signage, no door numbers, no posters, no logos, "
    "no watermark, nothing printed on any surface."
)

# One entry per narration sentence, in order. beat boundaries below.
# who: mc | them | none | both
SCENES: list[tuple[str, str]] = [
    # 1-4  cold open: tonight, on the wall
    ("Wide exterior at night, seen from a low angle looking up the outside of the concrete block. MC is "
     "climbing down the drainpipe, back to us, both hands on the pipe and both feet on the metal brackets, "
     "moving carefully from bracket to bracket. Below, the street is visible but far off; above, the "
     "pipe continues up the wall. Calm and steady, like someone descending a ladder.", "mc"),
    ("Close on MC's two hands gripping the cold metal drainpipe, knuckles pale, three storeys of drop "
     "below. Far down in the street, small standing figures, each the size of a fingernail.", "mc"),
    ("Very wide night shot of the whole block. Every window dark except one. A tiny figure clings to "
     "the drainpipe on the left of the facade.", "mc"),
    ("Interior, pre-dawn, blue-grey light through the window. MC sits up on the mattress, blanket around "
     "their waist, mouth dry, listening. The room is completely still.", "mc"),
    # 5-9  the city has stopped
    ("Close three-quarter profile of MC in grey pre-dawn light, eyes open, head cocked to listen.", "mc"),
    ("Interior looking through the window: an empty street under a grey pre-dawn sky, one parked car, "
     "shutters down on the shops, nothing moving.", "none"),
    ("Looking down at the floorboards and the bottom of the shut door. Under it the corridor light lies "
     "in a thin steady line, and the limp shadows of several pairs of feet stand in it.", "none"),
    ("Extreme low close-up of the gap under the door: the pale-yellow line of corridor light, and in it "
     "the unmoving shadow of a foot.", "none"),
    ("Interior, wide from inside the room: the corridor is packed with standing figures between the "
     "doors, all facing away, all perfectly still.", "them"),
    # 10-15  the room and the bolt
    ("Wide interior of the room in the last of the dark. Everything neat and undisturbed: mattress "
     "squared, chair against the wall, bottle standing, tins in a row, wardrobe shut.", "none"),
    ("Close-up of the inside of the door: a heavy iron barrel bolt thrown across, sitting in its "
     "keeper, the metal dull and cold.", "none"),
    ("Side view: MC crosses the room and puts one flat palm against the door, leaning their weight "
     "into it, back to us.", "mc"),
    ("Medium shot of MC with their forehead against the shut door, one hand flat on the paint. The "
     "door is plain, panelled, solid.", "mc"),
    ("Very low floor-level shot: the gap under the door, the corridor light lying in it in one thin "
     "steady strip, MC's shadow falling across one end of it.", "mc"),
    ("Extreme close-up of the thin strip of pale-yellow light under the door, flat and even along its "
     "whole length. Nothing in the frame is moving.", "none"),
    # 16-21  through the gap
    ("MC flat on the floor on their stomach, cheek to the boards, one eye level with the gap under "
     "the door, looking through. Seen from above and behind.", "mc"),
    ("Extreme close-up through the gap under the door: a pair of white sneakers standing still on the "
     "corridor floor, laces hanging, toes pointing at the door.", "none"),
    ("Through the gap under the door: a crowd of shoes of every kind, all completely still, filling "
     "the strip of vision from left to right.", "none"),
    ("Through the gap under the door: across the corridor, the door of the flat opposite standing wide "
     "open onto dark, empty rooms.", "none"),
    ("The corridor from inside MC's doorway: every door along both walls standing open, dark rooms "
     "behind each one, the light strip steady above.", "none"),
    ("Wide corridor shot: standing figures have come out of every open door and fill the hall, facing "
     "away, evenly spaced, arms down.", "them"),
    # 22-28  what they are
    ("Medium shot from behind: one standing figure, arms hanging straight down at its sides, shoulders "
     "level, absolutely still.", "them"),
    ("Close on three tilted heads of standing figures, eyes open, no eyebrows and no mouths, all "
     "leaning slightly to the same side as if listening to something low down.", "them"),
    ("MC's eye at the gap under the door, watching, the pale-yellow light across their face.", "mc"),
    ("Very close on a pair of standing feet on the corridor floorboards, both flat, weight even, the "
     "boards undisturbed.", "them"),
    ("Medium shot from behind of one standing figure: the back of the black t-shirt perfectly still, "
     "shoulders level, no rise and fall at all.", "them"),
    ("Close-up of MC's face in the dark room, thinking, jaw set, eyes fixed on the door.", "mc"),
    ("Wide corridor shot, slightly off-centre: every standing figure faces the same direction, none "
     "turned toward the camera, the hall silent and level.", "them"),
    # 29-35  the knock test
    ("MC crouched beside the door, one hand raised and hovering, hesitating, half turned away.", "mc"),
    ("Extreme close-up: one knuckle rapping the floorboard beside a knee, boards, sock and knuckle "
     "filling the frame.", "mc"),
    ("The corridor seen through MC's open doorway: every head in the hall has turned at once to face "
     "the door, bodies still facing the other way.", "them"),
    ("Close on the shut door, bolt thrown, light line under it steady. Nothing has changed at the "
     "door itself.", "none"),
    ("Extreme close on the lower panel of the door and the boards beneath it: clean, unmarked, nothing "
     "touching, nothing scratching.", "none"),
    ("Close on the door handle from inside: untouched, the light under the door steady, no movement.", "none"),
    ("The corridor again: the figures have turned their heads back and stand facing away, one by one, "
     "restored to stillness.", "them"),
    # 36-47  the phone
    ("The phone lying face up on the floorboards, screen lit, three simple curved lines radiating from "
     "it, MC's shadow beside it.", "none"),
    ("Extreme close-up of the lit screen: a battery drawn as a plain outline bar, almost entirely "
     "empty, and dark rounded blocks where words would be.", "none"),
    ("Wide interior of the dark room, the small lit phone on the floor, curved sound lines filling the "
     "empty space around it, MC crouched against the far wall.", "mc"),
    ("Close on the lit screen: one soft grey rounded chip where a name would sit, a plain circle "
     "beside it, nothing readable on the glass.", "none"),
    ("MC sitting on the floor holding the phone in both hands, looking down at it, seen from behind "
     "and to the side.", "mc"),
    ("Close over MC's shoulder: their thumb hovering above the lit screen, not touching it.", "mc"),
    ("Wide from the window: the dark city, the opposite block, standing figures in the street below, "
     "one small warm window lit far off, the lit phone large in the foreground.", "none"),
    ("MC sets the phone face down on the boards and takes their hand away from it.", "mc"),
    ("MC curled on the mattress, both arms folded across their chest, the phone pressed hard against "
     "their sternum, eyes shut.", "mc"),
    ("Close-up: the phone held flat against MC's chest, the screen glowing through their fingers, the "
     "sound lines around it fading.", "mc"),
    ("The corridor: the standing figure in the doorway opposite has turned its head toward MC's door. "
     "Its body still faces away. Only the head has moved.", "them"),
    ("MC sliding the phone under the mattress, then sitting down on top of it, back against the wall.", "mc"),
    # 48-51  the afternoon
    ("The window in flat afternoon light: the street below empty and bright, shutters down, a hard "
     "edge of light on the boards inside.", "none"),
    ("The stairwell seen from the corridor railing: many feet on the steps below, all facing the same "
     "way, taking the stairs in single file.", "them"),
    ("Close on one foot on a concrete step, placed carefully, the next step empty below it.", "them"),
    ("Looking down the stairwell: eleven standing figures spread down the steps, all halted, all "
     "facing up.", "them"),
    # 52-54  the sun
    ("MC sitting on the boards inside a bright rectangle of sunlight, knees up, head back, the rest "
     "of the room in shadow.", "mc"),
    ("Profile of MC with eyes closed in the patch of sun, chin lifted, one hand open on the boards.", "mc"),
    ("The patch of sunlight has slid off MC's hands and onto the bare wall. Their hands are in shadow, "
     "and the room has gone flat and grey.", "mc"),
    # 55-64  three knocks, a voice
    ("The door at dusk. MC stands a few feet back from it, on their feet, head up, listening.", "mc"),
    ("Close on the door with three small curved sound lines knocking on it in a slow row.", "none"),
    ("The same door, held still, empty of sound, only the thin light line beneath it.", "none"),
    ("Close on the door again with three more curved sound lines, evenly spaced after a gap.", "none"),
    ("The shut door with one even row of curved sound lines in rhythm across it, steady beat, nothing "
     "else in frame.", "none"),
    ("The corridor wide: every standing figure motionless, none of them at MC's door, and a rhythm of "
     "sound lines on the door that the figures are ignoring.", "them"),
    ("Close on the gap under the door at dusk with a single soft curved line of sound rising from it, "
     "no source visible.", "none"),
    ("Profile of MC standing very still beside the door, eyes wide, listening, mouth slightly open.", "mc"),
    ("Extreme close on the gap under the door: the pale light and delicate small sound lines drifting "
     "through it, the floorboards perfectly still.", "none"),
    ("MC's hand flat against the door, low down, fingers rigid, one small sound arc near the wood.", "mc"),
    # 65-76  the arithmetic, then silence
    ("MC standing hard against the door, one hand closed around the barrel bolt, whole body angled "
     "toward it.", "mc"),
    ("Extreme close on the bolt and MC's fist wrapped around it, knuckles tight, the metal greying in "
     "the dusk.", "mc"),
    ("Close-up of MC's face in profile, eyes moving, doing the sum, mouth a flat line.", "mc"),
    ("Low shot of the floorboards where MC knocked, in a pool of grey light, the boards bare and "
     "ordinary.", "none"),
    ("Close-up of MC's mouth, closed, in profile, no sound leaving it.", "mc"),
    ("The mattress on the floor, one corner lifted by a hand, the phone lying dark underneath.", "none"),
    ("MC looking up at the shut door from the floor, the cold door filling the left of the frame.", "mc"),
    ("Close-up of MC's hand lifting away from the barrel bolt, fingers opening, leaving the metal "
     "untouched.", "mc"),
    ("The door in the deep dusk with three new slow sound lines ringing on it.", "none"),
    ("The same door, the sound lines gone, only the closed wood and the steady light strip beneath it.", "none"),
    ("The corridor seen from MC's doorway: far down the hall, curved sound lines on another door, two "
     "standing figures beside it turning toward it.", "them"),
    ("MC sitting on the floor with their back flat against the shut door, knees up, arms wrapped "
     "around them, eyes open in the dark.", "mc"),
    # 77-81  the dark, the street
    ("The room in full dark: shapes only, the mattress, the chair, the shelf, the window a flat navy "
     "rectangle.", "none"),
    ("Looking down from the window at the street: standing figures gathered under each lamp post, "
     "every head tipped back, faces up.", "them"),
    ("Close on upturned faces under a lamp: dot eyes open, no eyebrows, no mouths, all pointing up at "
     "nothing.", "them"),
    ("Wide night shot of the street: both blocks dark, every window black except one small warm "
     "rectangle opposite.", "none"),
    ("MC at the window, back to us, looking across the street at the one lit window, then turning "
     "their head away from it.", "mc"),
    # 82-87  one exit, one pipe
    ("Wide interior: the shut door on the left, the window on the right, and MC standing between them, "
     "the only two ways out of one small room.", "mc"),
    ("Exterior close on the drainpipe bolted to the wall four feet left of MC's window, brackets and "
     "cold metal running up past the sill.", "none"),
    ("Exterior vertical shot down the wall: the drainpipe running past a gutter onto the flat roof of "
     "a shuttered shop, and then the street below.", "none"),
    ("Interior: the room with its door shut and bolted, the mattress, the chair, the bottles, warm and "
     "intact.", "none"),
    ("Exterior: the drainpipe in the dark against the concrete, wet, cold, going down into blackness.", "none"),
    ("MC standing in the middle of the room facing the window, the shut door behind them, both choices "
     "in one frame.", "mc"),
    # 88-94  getting ready, waiting
    ("MC moving through the last grey light, gathering things, back to us, the room half-packed.", "mc"),
    ("Close on a water bottle being emptied into a coat pocket, hands and pocket filling the frame.", "mc"),
    ("Close on MC's hands pushed into a thick second pair of socks, fingers inside the wool.", "mc"),
    ("MC at the window with both hands on the frame, pushing it open an inch, listening, the gap narrow "
     "and dark.", "mc"),
    ("MC sitting on the floor in the dark beside the open window, doing nothing, waiting, perfectly "
     "still.", "mc"),
    ("The stairwell from above: only two pairs of feet left on the steps now, both standing still.", "them"),
    ("Wide corridor in near dark: the hall empty, every door open, nothing moving anywhere.", "none"),
    # 95-104  out, and the hook
    ("MC at the window, one leg swung over the sill and out into the night, the other still inside the "
     "room.", "mc"),
    ("Extreme close on a socked foot pressed onto the cold metal of the drainpipe, toes curling.", "mc"),
    ("Exterior from the wall, looking back in through the window: the warm lit room behind, the "
     "mattress, the chair, everything MC owns, the glass between.", "none"),
    ("Downward view from the drainpipe: three storeys of wet metal below and the street at the bottom "
     "full of standing figures, none of them looking up.", "mc"),
    ("Wide exterior: MC out on the wall, both hands on the pipe, both feet on a bracket, three floors "
     "above the street.", "mc"),
    ("Medium exterior: MC on the pipe looking down at the street below, working out the first move, "
     "the drop clear in front of them.", "mc"),
    ("Very wide night shot: the whole facade of the block, one small figure on the drainpipe, the "
     "street beneath, the city dark beyond.", "mc"),
    ("Interior of the empty room from above: the mattress on the floor with a small warm glow coming "
     "out from underneath it.", "none"),
    ("Close on the phone lying face up under the lifted edge of the mattress, its screen lit, plain "
     "grey blocks on the glass, nobody in the room.", "none"),
    ("Very wide: MC small on the drainpipe high on the dark facade, the first grey line of dawn behind "
     "the rooftops.", "mc"),
]

# first sentence index of each beat; a beat is one scene/turn of the story
BEAT_STARTS = [1, 5, 10, 16, 22, 29, 36, 48, 52, 55, 65, 77, 82, 88, 95, 101]


def sentences() -> list[str]:
    text = (HERE / "narration.txt").read_text(encoding="utf-8").replace("\n", " ")
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def main() -> None:
    sents = sentences()
    if len(sents) != len(SCENES):
        raise SystemExit(f"narration has {len(sents)} sentences, SCENES has {len(SCENES)} - fix before writing")
    out = []
    per_beat: dict[int, int] = {}
    counters: dict[int, int] = {}
    for idx, ((scene, who), text) in enumerate(zip(SCENES, sents), start=1):
        sid = max(b for b in BEAT_STARTS if b <= idx)
        sid = BEAT_STARTS.index(sid) + 1
        per_beat[sid] = per_beat.get(sid, 0) + 1
        counters[sid] = counters.get(sid, 0) + 1
        char = {"mc": MC, "them": THEM, "none": "", "both": MC + " " + THEM}[who]
        prompt = " ".join(p for p in (STYLE, WORLD, char, "SHOT: " + scene, NOTEXT) if p)
        out.append({"slide_id": sid, "moment": counters[sid],
                    "moment_text": text, "visual_prompt": prompt})
    with open(HERE / "visuals.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["slide_id", "moment", "moment_text", "visual_prompt"])
        w.writeheader()
        w.writerows(out)
    words = sum(len(r["moment_text"].split()) for r in out)
    print(f"visuals.csv: {len(out)} moments / {len(per_beat)} beats / {words} words")
    print("  per beat:", " ".join(f"{k}:{v}" for k, v in sorted(per_beat.items())))


if __name__ == "__main__":
    main()
