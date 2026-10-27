"""Build visuals.csv from the word-locked moments + hand-authored SCENES.

visual_prompt = [STYLE BLOCK] + [SUBJECT BLOCK] + SCENE: <literal sentence> + [NEG]
The style and subject blocks are reused VERBATIM on every single frame.
"""
import csv
import json
from scenes import SCENES

STYLE_BLOCK = (
    "Hand-drawn 2D cartoon explainer illustration for a 16:9 landscape video frame, "
    "based on a chunky black-ink cartoon look: thick wobbly black outlines about 4 px "
    "at 1920 px width, flat saturated gouache colour fills, fine visible paper grain on "
    "warm cream paper, simple shapes, comic proportions, expressive dot eyes and curved "
    "closed eyes, flat even lighting, generous empty space around the subject, one or two "
    "small hand-drawn margin doodles or arrows, restrained palette of ink black, ochre, "
    "terracotta, teal and sky blue, with exactly ONE electric yellow accent used only on "
    "the single most important object named in the scene; no gradients, no soft shading, "
    "no 3D, no photorealism, no lens flare, no glossy plastic texture. "
    "No on-screen text, numbers or labels except ONE short hand-lettered string when the "
    "SCENE explicitly requests one, spelled exactly as written in thick black ink and "
    "large enough to read on a phone."
)

SUBJECT_BLOCK = (
    "Recurring subject design, identical in every frame: any human is one stocky cartoon "
    "early-human figure with a large round head, spiky dark-brown hair, two small dot eyes "
    "or two curved closed eyes, a tiny nose, a wide simple mouth, flat ochre-brown skin, "
    "and a plain grey animal-hide tunic with one shoulder strap, drawn with thick black "
    "outlines and no realistic facial detail; any fire is ONE small orange-and-yellow "
    "flame with a thick black outline; any tuber is ONE knobbly oval root; modern humans "
    "appear only in plain unbranded modern clothes. Draw ONLY the exact number of people, "
    "animals and objects the SCENE names, never more and never fewer, and put no extra "
    "figures in the background. Match the action, gaze direction, location and time of "
    "day stated in the SCENE exactly."
)

NEG = (
    "NEGATIVE: photorealistic, 3D render, glossy, airbrushed, gradient, lens flare, depth "
    "of field, cinematic lighting, extra people, extra limbs, extra fingers, distorted "
    "anatomy, cropped subject, misspelled text, garbled letters, watermark, logo, brand "
    "name, gore, blood, violence, modern cars, modern buildings, screens, UI, tiny "
    "illegible text, cluttered background, collage, multiple panels unless the SCENE asks "
    "for a split frame."
)


def main():
    rows = json.load(open("tools/moments.json", encoding="utf-8"))
    scenes = [s.strip() for s in SCENES.strip().split("\n") if s.strip()]
    assert len(scenes) == len(rows), f"{len(scenes)} scenes vs {len(rows)} moments"
    assert all(s.endswith(".") for s in scenes), "a SCENE does not end with a full stop"

    with open("visuals.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["slide_id", "moment", "moment_text", "visual_prompt"])
        for r, scene in zip(rows, scenes):
            prompt = f"{STYLE_BLOCK} {SUBJECT_BLOCK} SCENE: {scene} {NEG}"
            w.writerow([f"{r['beat']:02d}", f"{r['moment']:02d}",
                        r["moment_text"], prompt])

    with open("visuals.csv", encoding="utf-8") as f:
        out = list(csv.DictReader(f))
    print(f"wrote visuals.csv: {len(out)} rows")
    print(f"beats: {sorted(set(r['slide_id'] for r in out))}")
    print(f"prompt chars: min={min(len(r['visual_prompt']) for r in out)} "
          f"max={max(len(r['visual_prompt']) for r in out)}")
    print("first moment_text:", out[0]["moment_text"])
    print("last  moment_text:", out[-1]["moment_text"])


if __name__ == "__main__":
    main()
