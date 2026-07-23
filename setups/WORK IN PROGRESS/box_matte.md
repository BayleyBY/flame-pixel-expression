# box_matte

**What it does:** Axis-aligned cube matte around the centre, half-size `boxSize`, soft edge `soft`.

**Use case:** Isolate a rectangular volume of a CG render by world position.

**Inputs:** Front 1 = P-world pass

**Expects:** raw / data (no colour management)

**Variables:** `cenR` (0), `cenG` (0), `cenB` (0), `boxSize` (1.0), `soft` (0.5)

## Node dependencies
**Pipeline:** P-world pass (Front 1) → **this node** → (matte to comp)

Reads a **world-position (P) pass on Front 1** (RGB encode XYZ). Set the centre/extent variables to the world point/size you want to isolate; without a P pass it produces nothing meaningful. Tip: test without a render by feeding the `stmap` node into Front 1.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

An **axis-aligned box (cube) matte** in world space — white inside a rectangular region,
soft-edged outside. The rectangular cousin of `pmatte_sphere`, and cheaper for boxy volumes.

### How it works
It's the **intersection of three per-axis slabs** (X, Y, Z each within `boxSize` of centre),
multiplied together — which is exactly why it's **axis-aligned only**: there's no rotation.

### Practical notes
- **Front 1 = P-world pass; `cenR/cenG/cenB` = box centre in world XYZ; `boxSize` = half-
  extent** (world units); `soft` = edge softness as a fraction of the extent.
- Read the P pass raw. Great for a world-space garbage matte (isolate a room, a vehicle's
  bounding volume, a slab of the set).
