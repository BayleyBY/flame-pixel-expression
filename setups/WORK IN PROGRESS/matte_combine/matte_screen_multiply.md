# matte_screen_multiply

**What it does:** Soft optical combine of two mattes: `mode` 1 = screen (a+b−ab, union), 0 = multiply (ab, intersection); blends between. Softer than `matte_or`/`matte_and`.

**Use case:** Optical-feel union/intersection of two mattes where min/max read too hard.

**Inputs:** Matte 1 + Matte 2

**Expects:** any (data / value op)

**Variables:** `mode` (1.0)

## Notes

A **soft optical combine** of two mattes. `mode` 1 = **screen** (`A+B−AB`, an optical *union*),
`mode` 0 = **multiply** (`A·B`, an *intersection*); values between blend the two.

### vs `matte_or` / `matte_and`
Those use `max` / `min` — geometrically hard unions/intersections with a visible crease where the
two mattes meet. Screen/multiply roll the overlap together smoothly, which usually reads better
for soft mattes and density build-up. Pick `matte_or`/`and` for crisp set logic, this for an
optical feel. Result on RGB + Matte.

### Quick test
Two overlapping soft shapes on **Matte 1 + Matte 2**: `mode` 1 (screen) → a smooth union
with no hard crease in the overlap; `mode` 0 → their intersection. Toggle 1 ↔ 0 and the
combine visibly flips. Only Matte 1 wired: screen ≈ pass-through, multiply → black.
