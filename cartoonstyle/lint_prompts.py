"""Literalness gate: does each visual_prompt actually draw its own moment_text?

The failure this exists to stop is the seductive one: writing a shot that LOOKS
great but illustrates a different sentence. "The door is shut, and the bolt is
across it, and you did not put it there" is three claims; a macro of a bolt
answers one of them and quietly drops two. Multiply that by 104 frames and the
film stops matching its own narration.

How it scores: take the concrete words out of moment_text (nouns, verbs,
adjectives - not "the", "you", "is"), and check how many of them survive into
the SHOT section of the prompt (the part after "SHOT:" - the fixed style/world
blocks are excluded, because they contain door/window/mattress by default and
would make every row look fine).

Words that are legitimately undrawable ("say", "know", "decide") are waived with
--waive or by editing UNDRAWABLE below. Everything else must be either present
or explicitly abstracted, e.g. "know your name" -> describe the bolt, the
stillness, the listening.

Usage:
    python3 -m cartoonstyle.lint_prompts --visuals visuals.csv
    python3 -m cartoonstyle.lint_prompts --visuals visuals.csv --min 0.6 --strict
Exit code 1 with --strict if any row scores below --min.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys

# words that name something you cannot put in a drawing
UNDRAWABLE = {
    "say", "says", "said", "know", "knows", "knew", "think", "decide", "decided",
    "understand", "understands", "remember", "try", "trying", "learn", "learns",
    "worth", "afford", "mean", "means", "happen", "happened", "notice", "noticed",
    "need", "needs", "want", "wants", "get", "gets", "got", "going", "make",
    "makes", "made", "let", "lets", "come", "comes", "came", "put", "puts",
    "keep", "keeps", "kept", "leave", "leaves", "left", "stay", "stays", "stayed",
    "use", "used", "answer", "answered", "dialled", "ring", "rings", "rang",
    "sound", "sounds", "noise", "worth", "alive", "dead", "nobody", "somebody",
    "everything", "anything", "something", "nothing", "anybody", "everybody",
    "one", "two", "three", "four", "eleven", "nineteen", "twenty", "forty",
    "hundred", "thousand", "percent", "first", "second", "last", "next", "day",
    "today", "tomorrow", "tonight", "now", "then", "still", "again", "already",
    "never", "always", "not", "no", "yes", "and", "but", "because", "like",
    "just", "only", "very", "so", "if", "that", "this", "there", "here", "your",
    "you", "their", "them", "they", "its", "it", "his", "her", "him", "she",
    "he", "we", "our", "us", "my", "me", "i", "a", "an", "the", "is", "are",
    "was", "were", "be", "been", "being", "has", "have", "had", "do", "does",
    "did", "can", "could", "would", "should", "will", "shall", "may", "might",
    "must", "of", "to", "in", "on", "at", "by", "for", "with", "from", "into",
    "onto", "out", "up", "down", "off", "over", "under", "about", "as", "than",
    "more", "most", "all", "any", "each", "every", "both", "few", "many", "much",
    "some", "such", "own", "same", "other", "another", "who", "what", "when",
    "where", "why", "how", "which", "while", "after", "before", "through",
    "across", "past", "toward", "towards", "against", "behind", "beside",
    "between", "beyond", "along", "around", "without", "within", "near", "away",
    "back", "front", "top", "bottom", "side", "middle", "end", "way", "thing",
    "things", "kind", "sort", "part", "piece", "lot", "bit", "time", "times",
    "much", "enough", "exactly", "completely", "quietly", "carefully", "slowly",
}

# crude stem: enough to match "knocks" to "knock" and "shut" to "shut"
def stem(w: str) -> str:
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > 4 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def content_words(text: str) -> list[str]:
    out = []
    for raw in re.findall(r"[a-z']+", text.lower().replace("'", "")):
        if raw in UNDRAWABLE or len(raw) < 3:
            continue
        out.append(stem(raw))
    return out


def shot_section(prompt: str) -> str:
    """Only the part that describes THIS frame, not the reused style/world text."""
    if "SHOT:" in prompt:
        body = prompt.split("SHOT:", 1)[1]
        for stop in ("No text, no letters", "STYLE:", "WORLD", "CHARACTER"):
            body = body.split(stop, 1)[0]
        return body.lower()
    return prompt.lower()


def main() -> None:
    p = argparse.ArgumentParser(description="check prompts against their moment_text")
    p.add_argument("--visuals", required=True)
    p.add_argument("--min", type=float, default=0.6,
                   help="share of drawable words that must appear in the SHOT (default 0.6)")
    p.add_argument("--strict", action="store_true", help="exit 1 if any row fails")
    p.add_argument("--waive", default="", help="comma-separated stems to ignore")
    args = p.parse_args()

    waive = {stem(w.strip().lower()) for w in args.waive.split(",") if w.strip()}
    rows = list(csv.DictReader(open(args.visuals, newline="", encoding="utf-8")))

    fails, total_missing = [], 0
    print(f"{'key':<11}{'score':>7}  missing from the shot")
    print("-" * 74)
    for r in rows:
        key = f"beat{int(r['slide_id']):02d}m{int(r['moment']):02d}"
        want = [w for w in content_words(r["moment_text"]) if w not in waive]
        shot = shot_section(r["visual_prompt"])
        missing = [w for w in want if w not in shot]
        score = 1.0 if not want else 1 - len(missing) / len(want)
        if score < args.min:
            fails.append((key, score, missing, r["moment_text"]))
            total_missing += len(missing)
        flag = "  <<<" if score < args.min else ""
        print(f"{key:<11}{score:>7.2f}  {', '.join(missing) if missing else '-'}{flag}")

    print("-" * 74)
    print(f"{len(rows)} rows | {len(fails)} below {args.min:.2f} | {total_missing} undrawn words")
    if fails:
        print("\nframes that risk illustrating the wrong sentence:")
        for key, score, missing, text in fails:
            print(f"  {key}  {score:.2f}  '{text[:70]}'")
            print(f"           not drawn: {', '.join(missing)}")
    sys.exit(1 if (fails and args.strict) else 0)


if __name__ == "__main__":
    main()
