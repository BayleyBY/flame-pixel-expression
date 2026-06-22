# depth_grade

**What it does:** Multiplies beauty by a gain that ramps with distance (near→far).

**Use case:** Darken or lift by distance without introducing a fog colour.

**Inputs:** Front 1 = beauty, Matte 1 = depth

**Expects:** depth raw; beauty scene-linear

**Variables:** `near` (0.0), `far` (1.0), `gainNear` (1.0), `gainFar` (0.3)

## Node dependencies
**Pipeline:** beauty (Front 1) + depth pass (Matte 1) → **this node**

Reads the **Z/depth pass on Matte 1** (the library convention — `m1`). Raw Z is in scene units, so set the normalising range to your near/far. No depth on Matte 1 = no useful result (input wiring is never saved in the setup file — re-wire it in Batch every time). Also needs the **beauty on Front 1**.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Multiplies the beauty by a gain that **ramps with distance** (`gainNear` → `gainFar`) — adds
density/falloff with depth without introducing a colour, the way `depth_fog` does.

### depth_grade vs depth_fog
Use `depth_grade` to **darken or lift** with distance (atmospheric density, a light that
falls off into the deep); use `depth_fog` when you want far pixels to take on a **colour**.

### Practical notes
- **Front 1 = beauty, Matte 1 = depth.** `near`/`far` set the ramp range; `gainNear`/
  `gainFar` are the multipliers at each end (default lifts near, darkens far).
- A multiply, so keep it in **scene-linear** for predictable results.
