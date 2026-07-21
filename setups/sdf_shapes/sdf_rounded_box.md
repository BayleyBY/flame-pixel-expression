# sdf_rounded_box

**What it does:** Rounded rectangle (`corner`); `hollow` 0..1 cuts out the middle.

**Use case:** Soft-cornered framing masks and outlines.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `bx` (200), `by` (120), `corner` (40), `hollow` (0.0), `soft` (2.0)

## Notes

A **rounded rectangle** (SDF) with a `corner` radius — and a hollow that stays correctly
rounded. Centred on **Centre**.

### Why the hole is a second box (the clever bit)
When `hollow` > 0 the interior cut-out is a **second rounded box**, not an inward SDF offset.
An inward offset would **sharpen** the inner corners (the radius shrinks as you move in);
subtracting a matched rounded box keeps the inner corners round — so a rounded frame looks
right at any `hollow` amount. The inner corner radius (`cin`) grows with the hole and caps at
`corner`, so a just-opened hole is small and capsule-ish, and by the time it's corner-sized
its rounding **matches the exterior**. This is why its formulas (`wall`, `cin`, `d`, `d2`)
differ from the other shapes' simple `_HOLLOW`.

### Practical notes
- `bx`/`by` = **half-extents**; `corner` = corner radius (px); `hollow` 0 = solid → frame;
  `soft` = edge feather. Ideal for UI panels, soft-cornered mattes and outlines.
