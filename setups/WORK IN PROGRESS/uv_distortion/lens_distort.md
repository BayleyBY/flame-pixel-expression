# lens_distort

**What it does:** Radial barrel/pincushion ST map (k1, k2), aspect-corrected.

**Use case:** Add lens distortion to a clean render (feed an STMap node) to match a plate.

**Inputs:** none (generator → STMap)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

**Variables:** `k1` (0.1), `k2` (0.0)

## Node dependencies
**Pipeline:** **this node** → **STMap**

Outputs a 0..1 **ST/UV map** (`red`=U, `green`=V) — *coordinates*, not a warped image. On its own it looks like a red/green gradient and changes nothing. Wire its output into a downstream **STMap** node's map/UV input, and the plate you want warped into the STMap's source — the STMap does the re-sample (the pixel gather this node can't do). **Tag the map Raw/Data**; colour-managing a coordinate map corrupts the warp. Adds radial barrel (`k1<0`) / pincushion (`k1>0`) distortion; typical job is baking a plate's measured distortion onto a clean CG render.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Generates a **radial distortion ST map** (barrel / pincushion). Like everything in
`uv_distortion/`, it **does not warp the image itself** — `red = U, green = V`, and you feed
the result into an **STMap node** whose source is the plate you want distorted.

### Practical notes
- **`k1` is the main term:** `k1 < 0` = barrel (wide-angle bulge), `k1 > 0` = pincushion.
  `k2` is a higher-order term that mostly affects the far corners.
- Aspect-corrected (coords normalised by half-width), so distortion stays isotropic at any
  resolution.
- **Tag the output Raw/Data** and STMap it — colour-managing a coordinate map corrupts it.
- Typical job: **add** a plate's measured distortion onto a clean CG render so it matches.

### ST-map precision (live-Flame lesson, 2026-07-23)
- **Keep the map 32-bit float end-to-end.** UV coordinates need sub-pixel precision: at
  1920 wide, adjacent pixels differ by ~0.0005 in U — the entire resolution of a 16-bit
  half float near 0.5. A 16f (or integer) map costs up to a full pixel of positional error
  and the warp comes back "correct but soft". No resize/filter/colour management on the map.
- **The STMap's sampler is generic** (typically bilinear) — visibly softer than a Transform
  node's high-quality filters on plain scaling. Prefer Transform/Resize for pure affine
  moves; an ST map earns its keep for non-uniform warps, or when several UV operations are
  composed into ONE map so the footage is resampled only once.

### Quick test
Viewed directly it is just a red/green gradient — **correct; it outputs coordinates, not a
warp**. Sanity check alone: `k1` 0.0 → identical to the `stmap` setup's ramp. Real test:
feed it into the same downstream ST-map/UV-warp node you used to verify the uploaded
`stmap_generators` folder, with `uv_test_chart` as the source → `k1` −0.2 bulges the grid
(barrel), +0.2 pinches it (pincushion).
