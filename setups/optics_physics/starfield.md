# starfield

**What it does:** Procedural stars: space is tiled into `cellSize` cells, each hashed to place one star above `threshold`; animate `twinkle` to pulse them.

**Use case:** Star backgrounds, sparkle/glint fields, sci-fi skies.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `cellSize` (40.0), `twinkle` (animated), `threshold` (0.92), `brightness` (1.0)

## Notes

A **procedural starfield** — no plotting, no loop. Space is tiled into `cellSize` cells; each
cell is hashed once (`_hash2`) and may hold a single star. Because the hash is deterministic per
cell, the field is stable when you scrub (only the twinkle moves).

### How it works
- `h = _hash2(floor(pixel / cellSize))` — a per-cell random vec2. `h.y` gates whether the cell
  has a star (`smoothstep(threshold, 1.0, h.y)` — raise `threshold` for fewer, brighter stars);
  `h.x` seeds its twinkle phase and a faint warm/cool tint.
- `d` is the distance from the pixel to the star's sub-cell position; a `smoothstep` makes a
  small round dot.

### Practical notes
- `cellSize` = average star spacing (px); `threshold` (0..1) = density (higher = sparser);
  `brightness` scales them all.
- **`twinkle` is the keyframed clock** (0 → 1 over frames 1–100 = one twinkle cycle); each star
  pulses on its own `h.x` phase so they don't blink in unison.
- One star per cell by construction — drop `cellSize` for a denser sky. RGB carries a subtle
  hash tint; OutMatte is the clean star mask (good for glow/comp).
