"""Read the signs out of an image, back into text.

    python3 signs/read.py                    every image on the profile
    python3 signs/read.py assets/footer.svg  one image

A sign is recognised only if it is drawn exactly as the table draws it. That is
deliberate: a sign redrawn by hand, or damaged, is reported instead of guessed.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import table  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMAGES = ["header.svg", "nodes.svg", "pillars.svg", "glyphs.svg", "footer.svg"]
# The profile leaves this one for the reader. The key is enough.
UNTRANSLATED = {"pillars.svg"}

SIGN = re.compile(r'<g(?: id="[^"]+")? transform="translate\((-?[\d.]+) 0\)">((?:<path [^>]*/>)+)</g>')


class Unreadable(ValueError):
    pass


def signs(svg):
    """The signs of an image in drawing order, as [(x, character)]."""
    out = []
    for m in SIGN.finditer(svg):
        x, drawn = float(m.group(1)), m.group(2)
        if drawn not in table.BY_MARKUP:
            raise Unreadable(f"a sign at x={table.fmt(x)} is not in the table: {drawn[:90]}")
        out.append((x, table.BY_MARKUP[drawn]))
    return out


def text(seq):
    """Signs to text. A step wider than one advance is a new word; a step backwards is a new line."""
    out, prev = "", None
    for x, ch in seq:
        _, _, inset = table.NUMBER_CELL if ch in table.DIGITS else table.LETTER_CELL
        start = x - inset
        if prev is not None:
            prev_start, prev_ch = prev
            _, advance, _ = table.NUMBER_CELL if prev_ch in table.DIGITS else table.LETTER_CELL
            step = start - prev_start
            if step < 0:
                out += " / "
            elif step > advance + 0.01:
                out += " "
        out += ch
        prev = (start, ch)
    return out


def read(path):
    return text(signs(pathlib.Path(path).read_text(encoding="utf-8")))


def main(argv):
    reveal = "--reveal" in argv
    paths = [a for a in argv if not a.startswith("--")] or [str(ROOT / "assets" / n) for n in IMAGES]
    status = 0
    for p in paths:
        label = pathlib.Path(p).name
        try:
            got = read(p)
        except (Unreadable, OSError) as e:
            print(f"{label}: {e}")
            status = 1
            continue
        if label in UNTRANSLATED and not reveal:
            print(f"{label}: left untranslated on the profile. The key is enough. (--reveal reads it here.)")
        else:
            print(f"{label}: {got}")
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
