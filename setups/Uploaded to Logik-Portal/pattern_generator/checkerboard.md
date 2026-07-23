# checkerboard

**What it does:** Checker pattern with `size`-pixel squares.

**Use case:** UV/distortion checks, placeholder textures, alignment grids.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `size` (64), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

A **checkerboard** test pattern — `size`-pixel squares.

### Screen-space, not Centre-based
Unlike `radial_ramp`/`rings`/`rays`, this is anchored to the **image origin** (`x`/`y`), not
the Centre control — so it tiles the frame and doesn't move with Centre.

### Practical notes
- `size` = square size in pixels.
- Two colours `aR/aG/aB`→`bR/bG/bB` (default black→white); raw pattern on OutMatte. Classic
  uses: alignment/UV checks, transparency-style backgrounds, test patterns.
