# premult

**What it does:** Multiplies RGB by the matte (Matte 1).

**Use case:** Premultiply before operations that expect premult footage.

**Inputs:** Front 1 + Matte 1

**Expects:** any (data / value op)

_No variables._

## Notes

Multiplies RGB by the matte (`r1 * m1`). Run **before** ops that expect premultiplied
footage. Inverse of `unpremult`.

### Quick test
On solid-alpha footage NOTHING changes (`m1` = 1 everywhere) — correct. Wire a soft matte
(`radial_ramp` render) into **Matte 1** → **RGB fades to black outside the shape** with the
matte's soft rolloff.
