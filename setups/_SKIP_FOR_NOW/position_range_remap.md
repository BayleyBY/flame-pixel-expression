# position_range_remap

**What it does:** Remaps a world/object P pass (Front 1) into 0..1 across a per-axis bbox `[min..max]`. Eats 6 vars (the bbox).

**Use case:** Drive a ramp/grade keyed to an object's extents from a position pass (e.g. gradient along a model's height).

**Inputs:** Front 1 (position/P pass)

**Expects:** raw / data (world/object position pass)

**Variables:** `minX` (-1.0), `maxX` (1.0), `minY` (-1.0), `maxY` (1.0), `minZ` (-1.0), `maxZ` (1.0)

## Node dependencies
**Pipeline:** world/object position (P) pass (Front 1) → **this node**

Reads a **world-position (P) pass on Front 1** (RGB encode XYZ). Set the centre/extent variables to the world point/size you want to isolate; without a P pass it produces nothing meaningful. Tip: test without a render by feeding the `stmap` node into Front 1.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Remaps a **world/object position (P) pass** into 0..1 across a bounding box, so a position pass can
drive a ramp keyed to where things are in space — e.g. a gradient up an object's height, or a
falloff across its depth.

- `minX/maxX`, `minY/maxY`, `minZ/maxZ` are the bbox in the pass's world units; each axis is
  remapped and clamped to 0..1 independently.
- This eats **6 of 8** variable slots (the bbox) — like the colour-var pattern, that's expected.
- Tip: read the P pass's values off a pixel to find the object's extents, then set the bbox.
  **Tag Raw/Data.**
