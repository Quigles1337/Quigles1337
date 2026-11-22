"""Write text in the script.

    python3 signs/write.py "many minds / one main branch" > inscription.svg
    python3 signs/write.py --describe "many minds"

Letters A to Z and digits 0 to 9. A space starts a new word, which hangs from its
own line; " / " starts a new row. Prints one standalone SVG, rows centred.
--describe prints the signs in words instead, for an image's <desc>.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import table  # noqa: E402

GOLD = "#E3B862"
ROW_PITCH = 72 / 0.92  # distance between rows, as the profile's two-row inscriptions set it


def clean(text):
    rows = [r.split() for r in text.upper().split("/")]
    rows = [r for r in rows if r]
    bad = sorted({ch for r in rows for w in r for ch in w if ch not in table.TABLE})
    if bad:
        raise ValueError("no sign for: " + " ".join(bad))
    return rows


def row(words):
    """One row of words in sign units: (markup of lines and signs, width)."""
    cursor, lines, drawn = 0, [], []
    for i, word in enumerate(words):
        if i:
            cursor += table.WORD_GAP
        start = cursor
        for ch in word:
            _, advance, inset = table.NUMBER_CELL if ch in table.DIGITS else table.LETTER_CELL
            drawn.append(f'<g transform="translate({table.fmt(cursor + inset)} 0)">{table.markup(table.TABLE[ch])}</g>')
            cursor += advance
        lines.append(f'<path d="M{table.fmt(start - table.LINE_OVERHANG)} 0H{table.fmt(cursor + table.LINE_OVERHANG)}"/>')
    return "".join(lines) + "".join(drawn), cursor


def group(words, x, y, scale, color=GOLD):
    """One row as the group the profile's images use, placed at (x, y)."""
    inner, width = row(words)
    return (f'<g transform="translate({table.fmt(x)} {table.fmt(y)}) scale({table.fmt(scale)})" fill="none" '
            f'stroke="currentColor" stroke-width="{table.fmt(table.STROKE)}" stroke-linecap="round" '
            f'stroke-linejoin="round" color="{color}">{inner}</g>'), width


def describe(text):
    """The signs in words, as the profile's images describe themselves: words by semicolons, signs by commas."""
    return "; ".join(", ".join(table.name(ch) for ch in w) for r in clean(text) for w in r) + "."


def svg(text, scale=1.0, color=GOLD, margin=24):
    rows = clean(text)
    widths = [row(r)[1] for r in rows]
    width = max(widths) * scale + 2 * margin
    height = (len(rows) - 1) * ROW_PITCH * scale + 50 * scale + 2 * margin
    body = ""
    for i, (r, w) in enumerate(zip(rows, widths)):
        x = (width - w * scale) / 2
        y = margin + table.STROKE * scale + i * ROW_PITCH * scale
        body += group(r, x, y, scale, color)[0]
    w, h = table.fmt(width), table.fmt(height)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-labelledby="t d"><title id="t">An inscription in the script</title>'
            f'<desc id="d">Its signs, left to right: {describe(text)}</desc>{body}</svg>')


def main(argv):
    flags = [a for a in argv if a.startswith("--")]
    words = [a for a in argv if not a.startswith("--")]
    if not words:
        print(__doc__.strip())
        return 2
    try:
        print(describe(" ".join(words)) if "--describe" in flags else svg(" ".join(words)))
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
