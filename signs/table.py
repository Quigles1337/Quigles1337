"""The sign table: the one definition of the script drawn across this profile.

Every sign hangs from a line. A letter is a shape and an ending: the shape picks
the row of the grid, the ending picks the column, and the 26 letters fill the grid
in alphabetical order. A number hangs from a beam and is counted in beads.

It is a script, a way of writing English. It is not a language and it hides
nothing: the key is public. The images in assets/ are drawn from this table, and
check.py reads them back against it.
"""

SHAPES = ("stem", "twin", "vee", "bowl", "fork", "slant")
ENDINGS = ("none", "ring", "dot", "hook", "strike")
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"

# ----------------------------------------------------------------- drawing
# Units are the sign's own. The line a sign hangs from is y = 0 and y grows
# downward. A letter sits in a box 40 wide, a number in a box 30 wide.

STROKE = 3.4  # every stroke, round caps and joins
CORD = 1.8    # the hairline a bead hangs on

BODY = {
    "stem": "M20 0V30",
    "twin": "M12 0V24M28 0V24",
    "vee": "M8 0L20 28L32 0",
    "bowl": "M9 0C9 15 14 23 20 23S31 15 31 0",
    "fork": "M20 0V13M20 13L10 29M20 13L30 29",
    "slant": "M10 0L30 28",
}
# Where each shape ends. An ending attaches here; a shape with two ends carries it twice.
ENDS = {
    "stem": [(20, 30)],
    "twin": [(12, 24), (28, 24)],
    "vee": [(20, 28)],
    "bowl": [(20, 23)],
    "fork": [(10, 29), (30, 29)],
}
# The strike is one stroke across the whole shape.
STRIKE = {
    "stem": "M13 18L27 9",
    "twin": "M6 18L34 7",
    "vee": "M10 17L30 8",
    "bowl": "M5 14L35 5",
    "fork": "M10 23L30 16",
}
RING_R, RING_DROP = 4.6, 4.8
# Dots come in twos. A shape with one end carries the pair side by side beneath it;
# a shape with two ends carries one dot under each.
DOT_R, DOT_DROP, DOT_SPREAD = 3.0, 9.5, 5.5

# A number hangs from a beam. Beads are counted on up to three cords, never more
# than three to a cord. Zero is a hollow ring.
BEAM_Y = 8
BEAM = "M15 0V8M3 8H27"
CORD_X = (5, 15, 25)
BEAD_R, BEAD_Y, BEAD_STEP = 3.2, 16.2, 8.6
ZERO_Y = 19.4

# Layout along the line: (box width, advance, inset of the box within its advance).
LETTER_CELL = (40, 46, 3)
NUMBER_CELL = (30, 34, 2)
WORD_GAP = 26     # extra advance between words; each word hangs from its own line
LINE_OVERHANG = 6  # how far the line runs past the first and last sign of a word


def fmt(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def circle(cx, cy, r):
    return (f"M{fmt(cx - r)} {fmt(cy)}a{fmt(r)} {fmt(r)} 0 1 0 {fmt(2 * r)} 0"
            f"a{fmt(r)} {fmt(r)} 0 1 0 {fmt(-2 * r)} 0")


def hook(x, y, side):
    if side < 0:
        return f"M{fmt(x)} {fmt(y)}c0 5 -3 8 -8 8s-3 -2 -4 -5"
    return f"M{fmt(x)} {fmt(y)}c0 5 3 8 8 8s3 -2 4 -5"


def place(letter):
    """A letter's place in the grid: (shape, ending)."""
    i = LETTERS.index(letter)
    return SHAPES[i // 5], ENDINGS[i % 5]


def cords(n):
    """How the beads of a number sit on the three cords: (left, middle, right).

    Threes fill all three cords evenly. One spare bead goes to the middle cord,
    two spare beads go to the outer cords, so every number is symmetric.
    """
    q, r = divmod(n, 3)
    return {0: (q, q, q), 1: (q, q + 1, q), 2: (q + 1, q, q + 1)}[r]


def sign(ch):
    """One sign as a list of parts: (role, weight, path).

    role   body | ring | dot | hook | strike | beam | zero | cord | bead
    weight bold (stroked at STROKE) | thin (stroked at CORD) | fill
    """
    if ch in DIGITS:
        n = int(ch)
        if n == 0:
            return [("beam", "bold", BEAM),
                    ("zero", "bold", circle(15, ZERO_Y, RING_R)),
                    ("cord", "thin", f"M15 {fmt(BEAM_Y)}V{fmt(ZERO_Y - RING_R)}")]
        parts, hung, beads = [("beam", "bold", BEAM)], [], []
        for x, k in zip(CORD_X, cords(n)):
            if not k:
                continue
            ys = [BEAD_Y + BEAD_STEP * i for i in range(k)]
            hung.append(("cord", "thin", f"M{fmt(x)} {fmt(BEAM_Y)}V{fmt(ys[-1])}"))
            beads += [("bead", "fill", circle(x, y, BEAD_R)) for y in ys]
        return parts + hung + beads

    shape, ending = place(ch)
    parts = [("body", "bold", BODY[shape])]
    if ending == "none":
        return parts
    ends = ENDS[shape]
    if ending == "ring":
        return parts + [("ring", "bold", circle(x, y + RING_DROP, RING_R)) for x, y in ends]
    if ending == "hook":
        sides = (+1,) if len(ends) == 1 else (-1, +1)
        return parts + [("hook", "bold", hook(x, y, s)) for (x, y), s in zip(ends, sides)]
    if ending == "strike":
        return parts + [("strike", "bold", STRIKE[shape])]
    if len(ends) == 1:
        (x, y), = ends
        at = [(x - DOT_SPREAD, y + DOT_DROP), (x + DOT_SPREAD, y + DOT_DROP)]
    else:
        at = [(x, y + DOT_DROP) for x, y in ends]
    return parts + [("dot", "fill", circle(x, y, DOT_R)) for x, y in at]


def markup(parts):
    """The SVG a sign is drawn with: consecutive parts of one weight share a path."""
    out, run, weight = [], "", None

    def flush():
        if weight == "bold":
            out.append(f'<path d="{run}"/>')
        elif weight == "thin":
            out.append(f'<path d="{run}" stroke-width="{fmt(CORD)}"/>')
        elif weight == "fill":
            out.append(f'<path d="{run}" fill="currentColor" stroke="none"/>')

    for _, w, d in parts:
        if w != weight:
            flush()
            run, weight = "", w
        run += d
    flush()
    return "".join(out)


TABLE = {ch: sign(ch) for ch in LETTERS + DIGITS}
BY_MARKUP = {markup(parts): ch for ch, parts in TABLE.items()}
assert len(BY_MARKUP) == 36, "two signs are drawn alike"


def name(ch):
    """A sign in words, as the images' own descriptions name it."""
    if ch in DIGITS:
        n = int(ch)
        return "beam with ring" if n == 0 else f"beam with {n} bead{'s' if n > 1 else ''}"
    shape, ending = place(ch)
    return shape if ending == "none" else f"{shape} with {ending}"
