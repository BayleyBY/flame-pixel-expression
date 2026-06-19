# sdf_polygon

**What it does:** Regular n-gon (`sides`, `radius`, `rot`); `hollow` 0..1 cuts out the middle.

**Use case:** Polygonal masks/outlines (hexagons, triangles), stylised shapes.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `radius` (200), `sides` (6), `rot` (0.0), `hollow` (0.0), `soft` (2.0)

## Notes

A **regular n-gon matte** (SDF) — triangles, hexagons, etc. — centred on **Centre**, with the
shared hollow control.

### Controls
- `sides` = number of sides (3 = triangle, 5 = pentagon, 6 = hexagon…).
- `radius` = circumradius (centre to vertex), in pixels.
- `rot` = rotation in **radians** (so a full turn is `2*PI`).
- `hollow` 0 = solid → cuts an inward hole (frame/outline); `soft` = edge feather.

### Practical notes
- Built from the polar SDF (`r`, `a`, `d` formulas), so edges stay crisp at any size.
- Uses: polygonal masks and outlines, stylised shapes, aperture/iris mattes.
