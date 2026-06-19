# depth_matte

**What it does:** Isolates a depth band `zMin..zMax` with soft edges into a matte.

**Use case:** Hold out a depth slice (foreground / midground / background).

**Inputs:** Matte 1 = depth

**Expects:** raw / data (no colour management)

**Variables:** `zMin` (0.2), `zMax` (0.6), `soft` (0.05)

## Notes

A **distance qualifier**: white inside the depth band `[zMin..zMax]`, black outside, with
soft edges. The depth-axis sibling of a luma or chroma key.

### Why use it
Pull a garbage matte by distance — isolate the midground, hold out everything past a wall,
grab a character standing at a known depth — without rotoing. Because it's just depth, it
ignores colour and texture entirely.

### Practical notes
- **Depth on Matte 1.** Defaults assume a normalised 0..1 depth (run `depth_normalize`
  first); for raw world-unit depth set `zMin`/`zMax`/`soft` to your scene's range.
- `soft` feathers both ends of the band — widen it to avoid a hard edge on a gradient.
- It's a qualifier (written to RGB **and** Matte) — combine with an object alpha via
  `matte_and` to get "this object *and* in this depth range".
