# chromatic_aberration_map

**What it does:** Radial per-channel ST map (red channel's UV) + blue = offset magnitude; `amount`.

**Use case:** Lens chromatic aberration / defringe — feed an STMap node (see Notes).

**Inputs:** none (generator → STMap)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

**Variables:** `amount` (0.02)

## Node dependencies
**Pipeline:** **this node** → **STMap** (per channel)

Outputs the **red** channel's ST/UV in `red`/`green` and the **radial-offset magnitude** in `blue` — one ST map can't carry three different per-channel UVs. Two downstream options: (1) **per-channel STMap** — generate the map three times (red as-is; a green variant with `amount`=0; a blue variant with `-amount`), STMap each colour channel of the plate, recombine; or (2) feed `blue` into a **defringe** node as its strength map (simpler, approximate). Tag Raw/Data.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

A **chromatic-aberration ST map** — `red = U, green = V` for a downstream **STMap node**. Output
tagged **Raw/Data**.

### The one-map limitation (read this)
A single ST map can only carry **one** source UV, but chromatic aberration needs the R/G/B
channels sampled at **different** radii. Two clean ways to wire it:

1. **Per-channel (most accurate):** this map carries the **red channel's** distorted UV (scaled
   by `1 + amount`). Build **green** with `amount = 0` (identity) and **blue** with `-amount`,
   STMap each colour channel of the plate separately, then recombine — R sampled wide, B sampled
   tight. Since the green map is the identity you can skip its STMap and take green straight
   from the plate: two maps, two STMaps. **Warping the whole plate with just this one map does
   nothing chromatic — all channels move together and it reads as a slight uniform zoom.**
   The recombine can be two tiny Pixel Expression nodes (the node has two Front inputs):
   - Node A — Front 1 = red-warp, Front 2 = plate: `red = r1`, `green = g2`, `blue = 0.0`
   - Node B — Front 1 = node A, Front 2 = blue-warp: `red = r1`, `green = g1`, `blue = b2`
2. **Magnitude-driven defringe (simplest):** ignore the per-channel UVs and use the **blue
   channel** here, which carries the **radial offset magnitude** (`length(n) * amount`). Feed
   that as the strength/mask input of a downstream **defringe / lateral-CA** node so it fringes
   strongest at the edges and zero at the optical centre.

### Controls
- **`amount`** = radial divergence (0.02 default). Use **Centre** as the optical centre.

### ST-map precision (live-Flame lesson, 2026-07-23)
- **Keep the map 32-bit float end-to-end.** UV coordinates need sub-pixel precision: at
  1920 wide, adjacent pixels differ by ~0.0005 in U — the entire resolution of a 16-bit
  half float near 0.5. A 16f (or integer) map costs up to a full pixel of positional error
  and the warp comes back "correct but soft". No resize/filter/colour management on the map.
- **The STMap's sampler is generic** (typically bilinear) — visibly softer than a Transform
  node's high-quality filters on plain scaling. Prefer Transform/Resize for pure affine
  moves; an ST map earns its keep for non-uniform warps, or when several UV operations are
  composed into ONE map so the footage is resampled only once.
