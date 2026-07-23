# polar_to_cartesian

**What it does:** Polar/rectangular ST map around Centre; `twist` rotates, `zoom` scales radius.

**Use case:** Tiny-planet, mirror-ball and 360 reframes — feed an STMap node.

**Inputs:** none (generator → STMap)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

**Variables:** `twist` (0.0), `zoom` (1.0)

## Node dependencies
**Pipeline:** **this node** → **STMap**

Outputs a 0..1 **ST/UV map** (`red`=U, `green`=V) — *coordinates*, not a warped image. On its own it looks like a red/green gradient and changes nothing. Wire its output into a downstream **STMap** node's map/UV input, and the plate you want warped into the STMap's source — the STMap does the re-sample (the pixel gather this node can't do). **Tag the map Raw/Data**; colour-managing a coordinate map corrupts the warp. Polar/rectangular remap — tiny-planet, mirror-ball, 360 reframe (`twist` rotates, `zoom` scales the radius).

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

A **polar-coordinate ST map**. It does **not** warp the image itself — `red = U, green = V`,
and you feed the result into a downstream **STMap node** (or an **Action ST-map / GMIC ST**)
whose source is the plate you want remapped. Output is tagged **Raw/Data**.

### Required downstream wiring
1. This node → **STMap node**, plugged into the STMap's **map / UV input**.
2. The plate to remap → the STMap's **front / source input**.
3. The STMap resamples the source at each pixel's `(U,V)` = `(red, green)` here.

### What it does
For every output pixel it computes a **source UV from (angle, radius)** measured around the
node **Centre** (drag Centre to set the pole). `red` carries the normalised angle (0..1 around
the circle), `green` the normalised radius. The result is the classic **tiny-planet /
mirror-ball / 360-reframe** unwrap-rewrap.

### Controls
- **`twist`** rotates the angular axis (radians) — spins the planet.
- **`zoom`** scales the radius — `>1` pulls the horizon in, `<1` pushes it out.
- Aspect-corrected (Y normalised by height/width) so the circle stays round at any res.

### ST-map precision (live-Flame lesson, 2026-07-23)
- **Keep the map 32-bit float end-to-end.** UV coordinates need sub-pixel precision: at
  1920 wide, adjacent pixels differ by ~0.0005 in U — the entire resolution of a 16-bit
  half float near 0.5. A 16f (or integer) map costs up to a full pixel of positional error
  and the warp comes back "correct but soft". No resize/filter/colour management on the map.
- **The STMap's sampler is generic** (typically bilinear) — visibly softer than a Transform
  node's high-quality filters on plain scaling. Prefer Transform/Resize for pure affine
  moves; an ST map earns its keep for non-uniform warps, or when several UV operations are
  composed into ONE map so the footage is resampled only once.
