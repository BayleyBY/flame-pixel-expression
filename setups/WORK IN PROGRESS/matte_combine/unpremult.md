# unpremult

**What it does:** Divides RGB by the matte (guards 0).

**Use case:** Unpremultiply before colour-correcting an edge.

**Inputs:** Front 1 + Matte 1

**Expects:** any (data / value op)

_No variables._

## Notes

Divides RGB by the matte, guarding 0 (where `m1 = 0`, RGB passes through). Run **before**
colour-correcting an edge so the soft alpha doesn't darken it; re-`premult` after. Inverse of
`premult`.

### Quick test
Best tested as a round-trip: `premult` → `unpremult` with the same soft matte on both →
restores the original (check with `difference_matte`, gain up — black means exact). Alone
on solid alpha: no change, correct. (Where `m1` = 0 it passes through by the divide guard.)
