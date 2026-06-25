# holdout_matte

**What it does:** `clamp(m1 - m1·m2·amount, 0, 1)` — matte A (Matte 1) held out by occluder B (Matte 2). Multiplicative, vs `matte_subtract`'s straight m1−m2.

**Use case:** Subtract an occluder's coverage from a layer's matte in a layered-render comp.

**Inputs:** Matte 1 (A) + Matte 2 (B)

**Expects:** any (data / value op)

**Variables:** `amount` (1.0)

## Notes

The **holdout** op for layered renders: matte **A** (Matte 1) minus where occluder **B**
(Matte 2) covers it — `clamp(A − A·B·amount, 0, 1)`. `amount` scales how strongly B holds A out.

### vs `matte_subtract`
`matte_subtract` is a straight `A − B`. This is **multiplicative** (`A − A·B`): it only removes A
where A *itself* has coverage, so A's soft edges survive against B instead of being eaten by a
flat subtraction. That's the behaviour you want when compositing one render element in front of
another. Result on RGB + Matte.
