"""Check the profile's inscriptions against the sign table.

    python3 signs/check.py

Reads every image back into text and compares it with what the profile says it
says, checks the rules the README states about the script, and reports what a
single lost mark does to each sign. Exits non-zero if anything fails.
"""
import hashlib
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import read  # noqa: E402
import table  # noqa: E402
import write  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent

# What each image says. The inscription between the pillars is left untranslated
# on the profile, so only a digest of its reading is kept here.
SAYS = {
    "header.svg": "QUIGLES1337",
    "nodes.svg": "Q",
    "glyphs.svg": table.LETTERS + table.DIGITS + "Q",
    "footer.svg": "WE COME IN PEACE / AND PULL REQUESTS",
}
SAYS_SHA256 = {
    "pillars.svg": "76d45484956748e14a7306e7eecfbfe691be03db9ab857ae285babb1f187c6e7",
}
MARKS = ("ring", "dot", "hook", "strike", "bead", "zero")

failed = []


def check(what, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + what + (f"  ({detail})" if detail and not ok else ""))
    if not ok:
        failed.append(what)


def images():
    for name in read.IMAGES:
        path = ROOT / "assets" / name
        try:
            got = read.read(path)
        except (read.Unreadable, OSError) as e:
            check(f"{name} can be read", False, str(e))
            continue
        if name in SAYS:
            check(f"{name} reads {SAYS[name]}", got == SAYS[name], f"it reads {got}")
        else:
            digest = hashlib.sha256(got.encode()).hexdigest()
            check(f"{name} reads what it has always read", digest == SAYS_SHA256[name], "its reading changed")
            svg = path.read_text(encoding="utf-8")
            desc = re.search(r"<desc[^>]*>(.*?)</desc>", svg, flags=re.S).group(1)
            check(f"{name} draws the signs its description names", write.describe(got) in desc)


def readme():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    footer = SAYS["footer.svg"].replace(" / ", " ").lower()
    check("README translates the footer as the footer reads", f"*{footer}.*" in text)
    check("README: 1337 is one bead, then three, three, and seven",
          "one bead, then three, three, and seven" in text
          and [beads(table.TABLE[d]) for d in "1337"] == [1, 3, 3, 7])
    check("README: dots come in twos", "Dots come in twos" in text and all(
        count(parts, "dot") in (0, 2) for parts in table.TABLE.values()))


def count(parts, role):
    return sum(1 for r, _, _ in parts if r == role)


def beads(parts):
    return count(parts, "bead")


def rules():
    for d in table.DIGITS:
        n, parts = int(d), table.TABLE[d]
        per_cord = table.cords(n)
        fine = (beads(parts) == n and sum(per_cord) == n and max(per_cord) <= 3
                and per_cord == per_cord[::-1] and count(parts, "beam") == 1)
        if n == 0:
            fine = fine and count(parts, "zero") == 1
        check(f"{d} hangs from a beam and carries {n} bead{'' if n == 1 else 's'}, at most three to a cord", fine)
    flat = [ch for ch in table.LETTERS if any(
        re.search(r"[Hh]", d) for _, w, d in table.TABLE[ch] if w == "bold")]
    check("no letter has a horizontal stroke, so the beam marks a number", not flat, " ".join(flat))
    check("beads on a cord do not touch", table.BEAD_STEP > 2 * table.BEAD_R)
    sample = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG / 0123456789 TIMES"
    check("what the writer writes, the reader reads", read.text(read.signs(write.svg(sample))) == sample)


def drawing(parts, cords=True):
    return sorted((w, d) for r, w, d in parts if cords or r != "cord")


def lost_marks():
    """For every sign, take away one mark and see what is left."""
    whole = {ch: drawing(p) for ch, p in table.TABLE.items()}
    cordless = {ch: drawing(p, cords=False) for ch, p in table.TABLE.items()}
    rows = {}
    for ch, parts in table.TABLE.items():
        for i, (role, _, _) in enumerate(parts):
            if role not in MARKS:
                continue
            left = parts[:i] + parts[i + 1:]
            exact = next((c for c, d in whole.items() if d == drawing(left)), None)
            loose = next((c for c, d in cordless.items() if d == drawing(left, cords=False)), None)
            rows.setdefault(role, {}).setdefault(ch, set()).add((exact, loose))
    print("\nWhat one lost mark does")
    silent_dot = False
    for role in MARKS:
        caught, becomes, nearly = [], [], []
        for ch, outcomes in rows.get(role, {}).items():
            exact = {e for e, _ in outcomes if e}
            loose = {l for _, l in outcomes if l} - exact
            if exact:
                becomes.append(f"{ch} reads as {'/'.join(sorted(exact))}")
            elif loose:
                nearly.append(f"{ch} as {'/'.join(sorted(loose))}")
            else:
                caught.append(ch)
        label = {"zero": "ring of 0"}.get(role, role)
        if caught:
            print(f"  {label:9} {' '.join(caught)}: what is left is not a sign")
        if becomes:
            print(f"  {label:9} {', '.join(becomes)}")
            silent_dot = silent_dot or role == "dot"
        if nearly:
            print(f"  {label:9} {', '.join(nearly)}: only a bare length of cord says a bead is missing")
    print()
    check("a lone dot is damage, not a letter", not silent_dot)


def main():
    images()
    readme()
    rules()
    lost_marks()
    print("\nall checks pass" if not failed else f"\n{len(failed)} failed: " + "; ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
