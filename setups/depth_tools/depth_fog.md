# depth_fog

**What it does:** Blends beauty toward a fog colour with distance.

**Use case:** Atmospheric haze / aerial perspective.

**Inputs:** Front 1 = beauty, Matte 1 = depth

**Expects:** depth raw; beauty scene-linear

**Variables:** `near` (0.0), `far` (1.0), `fogR` (0.7), `fogG` (0.8), `fogB` (0.9)

## Node dependencies
**Pipeline:** beauty (Front 1) + depth pass (Matte 1) → **this node**

Reads the **Z/depth pass on Matte 1** (the library convention — `m1`). Raw Z is in scene units, so set the normalising range to your near/far. No depth on Matte 1 = no useful result (input wiring is never saved in the setup file — re-wire it in Batch every time). Also needs the **beauty on Front 1** — it tints by depth.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

**Atmospheric perspective** — blends the beauty toward a fog colour as things get farther
away, the cheap way to add depth and air to a CG render or matte painting.

### Practical notes
- **Front 1 = beauty, Matte 1 = depth.** `near`/`far` set where the fog starts and where it
  fully saturates; `fogR/G/B` is the haze colour (default a cool blue-grey).
- **Work in scene-linear** for plausible falloff, and put `fogR/G/B` in that same space.
- Unlike `depth_fade`, this keeps alpha intact (`matte = m1`) — it tints, it doesn't dissolve.
- Keyframe `near`/`far` (or the fog colour) for rolling mist or a clearing-fog reveal.
