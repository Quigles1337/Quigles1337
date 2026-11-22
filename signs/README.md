# The script

The signs on this profile are a script: a way of writing English. It is not a language, and it hides nothing, because the key is public. This folder is its one definition. The images in `assets/` are drawn from it and checked against it.

## The rules

- Every sign hangs from a line. Each word hangs from its own.
- A letter is a shape and an ending. The shape picks the row, the ending picks the column, and the 26 letters fill the grid in order.

|  | none | ring | dot | hook | strike |
| :-- | :-: | :-: | :-: | :-: | :-: |
| **stem** | A | B | C | D | E |
| **twin** | F | G | H | I | J |
| **vee** | K | L | M | N | O |
| **bowl** | P | Q | R | S | T |
| **fork** | U | V | W | X | Y |
| **slant** | Z | | | | |

- An ending attaches wherever the shape ends, so a shape with two ends carries it twice. The strike is the exception: one stroke across the whole shape.
- Dots come in twos. A shape with one end carries the pair beneath it.
- A number hangs from a beam, which no letter has. It is counted, not named: beads on up to three cords, never more than three to a cord. Zero is a hollow ring.

## Use it

```
python3 signs/check.py                                  # every inscription reads what the profile says
python3 signs/read.py assets/footer.svg                 # image to text
python3 signs/write.py "many minds / one main branch"   # text to image
```

Python 3, nothing to install. `table.py` is the definition; the other three only read it.

## What one lost mark does

`check.py` takes one mark away from every sign and looks at what is left.

| Mark lost | What is left |
| :-- | :-- |
| A dot | Never a letter. C, H, M, R and W all fail to read. |
| A ring or hook, from a shape that carries two | Fails to read: G, V, I and X. |
| A ring or hook, from a shape that carries one | The bare shape: B, L, Q, D, N and S read as A, K or P. |
| The strike | The bare shape: E, J, O, T and Y read as A, F, K, P and U. |
| A bead | 1, 2, 5 and 8 fail to read. 3, 4, 6, 7 and 9 can lose the lowest bead of the middle cord and show the next number down, with only a bare length of cord to give it away. |

A lost dot is always caught. Eleven letters still turn into another letter when one stroke goes missing. The check catches those too, but only because it knows what each image is supposed to say.
