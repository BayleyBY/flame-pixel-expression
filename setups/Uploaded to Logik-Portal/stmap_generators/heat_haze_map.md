# heat_haze_map

**What it does:** fbm-driven UV-offset ST map; `amp` strength, keyframe `seed` to shimmer.

**Use case:** Heat-haze / refraction wobble — feed an STMap node.

**Inputs:** none (generator → STMap)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

**Variables:** `scale` (120.0), `seed` (0.0), `lacunarity` (2.0), `persistence` (0.5), `amp` (0.03)

## Node dependencies
**Pipeline:** **this node** → **STMap**

Outputs a 0..1 **ST/UV map** (`red`=U, `green`=V) — *coordinates*, not a warped image. On its own it looks like a red/green gradient and changes nothing. Wire its output into a downstream **STMap** node's map/UV input, and the plate you want warped into the STMap's source — the STMap does the re-sample (the pixel gather this node can't do). **Tag the map Raw/Data**; colour-managing a coordinate map corrupts the warp. fbm-driven shimmer — **keyframe `seed`** to animate the wobble; `amp` sets strength.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

A **heat-haze / refraction ST map** — `red = U, green = V` feeding a downstream **STMap node**
(this node → STMap **map/UV input**, plate → STMap **source input**). Output tagged **Raw/Data**.

### What it does
Offsets each pixel's source UV by an **animated 3-octave fbm** field (the shared `_FBM_NOISE`
builder) times **`amp`**. X and Y use the same noise field sampled at different offsets, so they
wobble independently — the organic shimmer of hot air or water refraction.

### Controls
- **`seed`** — **keyframe this to animate the shimmer** (the node has no time variable; the seed
  offset into the noise field is how you get motion).
- **`amp`** = displacement strength (UV units; 0.03 default ≈ a few percent of the frame).
- **`scale`** = feature size, **`lacunarity`**/**`persistence`** shape the fbm octaves.

### ST-map precision (live-Flame lesson, 2026-07-23)
- **Keep the map 32-bit float end-to-end.** UV coordinates need sub-pixel precision: at
  1920 wide, adjacent pixels differ by ~0.0005 in U — the entire resolution of a 16-bit
  half float near 0.5. A 16f (or integer) map costs up to a full pixel of positional error
  and the warp comes back "correct but soft". No resize/filter/colour management on the map.
- **The STMap's sampler is generic** (typically bilinear) — visibly softer than a Transform
  node's high-quality filters on plain scaling. Prefer Transform/Resize for pure affine
  moves; an ST map earns its keep for non-uniform warps, or when several UV operations are
  composed into ONE map so the footage is resampled only once.
