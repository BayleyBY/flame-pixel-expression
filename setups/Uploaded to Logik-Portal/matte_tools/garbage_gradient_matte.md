# garbage_gradient_matte

**What it does:** Generator: a rotated linear gradient through Centre — `angle` (radians) direction, `offset` slides the edge, `feather` softens it. Result on RGB + Matte.

**Use case:** Quick garbage matte — cut off a floor/ceiling/region without a roto shape.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `angle` (0.0), `offset` (0.0), `feather` (100.0)

## Notes

A **procedural garbage matte** — a soft linear gradient you position and rotate, no roto shape
needed. The transition is a line through the node **Centre**; `angle` (radians) sets its
direction, `offset` slides it along the normal, `feather` sets the softness. Result is written to
RGB **and** the Matte.

Great for the fast "cut off everything past this line" jobs — a floor, a ceiling, a wall edge —
or as a soft side-to-side wipe. Keyframe `offset`/`angle` to animate the cut. Combine with the
`matte_*` ops to carve more complex garbage regions.
