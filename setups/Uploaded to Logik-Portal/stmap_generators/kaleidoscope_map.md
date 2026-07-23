# kaleidoscope_map

**What it does:** Mirror-folds angular space into `segments` wedges around Centre; `rot` spins it.

**Use case:** Kaleidoscope / mirror-symmetry looks — feed an STMap node.

**Inputs:** none (generator → STMap)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

**Variables:** `segments` (6.0), `rot` (0.0)

## Node dependencies
**Pipeline:** **this node** → **STMap**

Outputs a 0..1 **ST/UV map** (`red`=U, `green`=V) — *coordinates*, not a warped image. On its own it looks like a red/green gradient and changes nothing. Wire its output into a downstream **STMap** node's map/UV input, and the plate you want warped into the STMap's source — the STMap does the re-sample (the pixel gather this node can't do). **Tag the map Raw/Data**; colour-managing a coordinate map corrupts the warp. Mirror-folds angular space into `segments` wedges around Centre; `rot` spins it.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

A **kaleidoscope ST map** — `red = U, green = V` feeding a downstream **STMap node** (this node
into the STMap's **map/UV input**, the plate into its **source input**). Output tagged
**Raw/Data**.

### What it does
Mirror-folds angular space into **`segments`** wedges around the node **Centre**, then
reconstructs a source UV from the folded angle + original radius. The STMap then samples your
plate through that folded coordinate field, giving the mirror-symmetry kaleidoscope look.

### Controls
- **`segments`** = number of mirrored wedges (6 default).
- **`rot`** = rotation of the fold (radians) — spin it for an animated kaleidoscope.
- Drag **Centre** to move the pivot. Keyframe `rot` for motion.

### ST-map precision (live-Flame lesson, 2026-07-23)
- **Keep the map 32-bit float end-to-end.** UV coordinates need sub-pixel precision: at
  1920 wide, adjacent pixels differ by ~0.0005 in U — the entire resolution of a 16-bit
  half float near 0.5. A 16f (or integer) map costs up to a full pixel of positional error
  and the warp comes back "correct but soft". No resize/filter/colour management on the map.
- **The STMap's sampler is generic** (typically bilinear) — visibly softer than a Transform
  node's high-quality filters on plain scaling. Prefer Transform/Resize for pure affine
  moves; an ST map earns its keep for non-uniform warps, or when several UV operations are
  composed into ONE map so the footage is resampled only once.
