# triangle_tiling

**What it does:** Three `fract` line families 60° apart form a triangular/rhombille op-art grid. `triSize` cell size, `lineW` thickness; two-colour.

**Use case:** Isometric/op-art tiling, triangular grid overlays, faux-3D rhombille texture.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `triSize` (60.0), `lineW` (0.08), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

Three `fract` line families **60° apart** overlaid to make a **triangular / rhombille** grid — the
op-art "isometric" tessellation. `triSize` sets the cell size, `lineW` the line thickness;
two-colour (A = ground, B = lines). Distinct from `checkerboard`/`bricks`/`truchet` (square or
tile based) — this is the triangular lattice.
