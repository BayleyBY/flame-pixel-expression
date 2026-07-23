# matte_and

**What it does:** Intersection of two mattes (`m1 * m2`).

**Use case:** Keep only where both mattes overlap.

**Inputs:** Matte 1 + Matte 2

**Expects:** any (data / value op)

_No variables._

## Notes

Intersection of two mattes (`m1 * m2`) — white only where **both** are white. Inputs on
Matte 1 and Matte 2.

### Quick test
Needs BOTH mattes: wire two overlapping soft shapes (e.g. two `radial_ramp` renders with
different Centres) into **Matte 1 + Matte 2** → white **only in the overlap**. With only
Matte 1 wired the output is ALL BLACK (`m2` reads 0) — wiring, not a bug.
