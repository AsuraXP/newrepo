"""Split script.md into word-locked image moments and dump them as JSON.

Moment text is a verbatim slice of the narration (whitespace only is
normalised). 4-6s of speech at 2.75 words/sec => 11-17 words per moment.
"""
import json
import re

TARGET, LO, HI = 15, 11, 17
PUNCT = set(".!?,;:—")

# paragraph index (1-based, inclusive) -> beat number
BEAT_RANGES = [
    (1, 4, 1),    # hook: you cannot live on raw food
    (5, 7, 2),    # the bones and the expensive-tissue trade
    (8, 11, 3),   # fire: the accident, the smell, the tending
    (12, 15, 4),  # chemistry, neurons, reclaimed time
    (16, 18, 5),  # honest complications: tools, meat, disputed dates
    (19, 22, 6),  # the archaeology in the ground
    (23, 28, 7),  # firelight and stories
    (29, 30, 8),  # the ending
]


def beat_for(para_no):
    for a, b, beat in BEAT_RANGES:
        if a <= para_no <= b:
            return beat
    raise ValueError(para_no)


def split_para(para):
    rest = para.strip()
    out = []
    while rest:
        words = list(re.finditer(r"\S+", rest))
        n = len(words)
        if n <= HI:
            out.append(rest)
            break
        bounds = [m.end() for m in words]
        preferred = [rest[b - 1] in PUNCT for b in bounds]
        candidates = list(range(LO - 1, min(HI, n)))
        best = None
        for i in candidates:
            count = i + 1
            score = (1 if preferred[i] else 0, -abs(count - TARGET), count)
            if best is None or score > best[0]:
                best = (score, i)
        i = best[1]
        cut = bounds[i]
        out.append(rest[:cut].strip())
        rest = rest[cut:].lstrip()
    return out


def main():
    text = open("script.md", encoding="utf-8").read().strip()
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    rows = []
    for pi, para in enumerate(paras, 1):
        for moment in split_para(para):
            rows.append({
                "beat": beat_for(pi),
                "para": pi,
                "moment_text": moment,
                "words": len(moment.split()),
            })
    # moment resets inside each beat
    seen = {}
    for r in rows:
        seen[r["beat"]] = seen.get(r["beat"], 0) + 1
        r["moment"] = seen[r["beat"]]

    original = " ".join(text.split())
    rebuilt = " ".join(" ".join(r["moment_text"].split()) for r in rows)
    assert original == rebuilt, "moment_text does not reproduce the narration"
    with open("tools/moments.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    print(f"paragraphs={len(paras)} moments={len(rows)} words={sum(r['words'] for r in rows)}")
    print(f"avg words/moment={sum(r['words'] for r in rows)/len(rows):.1f}")
    for b in sorted(seen):
        rs = [r for r in rows if r["beat"] == b]
        print(f"beat {b}: {len(rs)} moments, {sum(r['words'] for r in rs)} words")
    print("verified: moment_text reproduces script.md word-for-word")


if __name__ == "__main__":
    main()
