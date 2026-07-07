# truchet

**What it does:** Truchet tiles: each `tile`-px cell is hashed to one of two diagonal arc orientations; the quarter-circle arcs connect across edges into endless maze/circuit lines.

**Use case:** Procedural maze/circuit/pipe textures, generative backgrounds, motion-graphics fills.

**Inputs:** none (procedural; ignores Front)

**Expects:** any — generates data/values

**Variables:** `tile` (40), `lineW` (4.0), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

**Truchet tiling** — a venerable generative-art trick. Each square cell contains one of two
quarter-circle arc pairs, chosen at random; because the arcs always meet the cell edges at
the same points, adjacent tiles connect into one continuous, endless maze of curves. From a
two-state-per-cell hash you get organic-looking circuit / pipe / labyrinth patterns.

### How it works
The frame is divided into `tile`-pixel cells. Each cell is **hashed** (`_hash2` on the cell
index) to a 0/1 `flip` that mirrors the local coordinates, swapping the arc orientation. Two
quarter-circles (radius = half a cell, centred on opposite corners) are drawn as the
distance band `arc`; a soft threshold of width `lineW` inks them.

### Controls
- `tile` — cell size in pixels (the scale of the weave).
- `lineW` — arc stroke width in pixels.
- `aR..bB` — line and background colours (default white lines on black).

### Notes
- This is a **pure generator** — it ignores any Front input and produces the same pattern
  regardless of what's connected; expects nothing.
- Keyframe the **Centre** to scroll the weave, or `tile` to zoom it.
- Feed the matte into a displacement / edge node for a circuit-board or stained-glass look.
