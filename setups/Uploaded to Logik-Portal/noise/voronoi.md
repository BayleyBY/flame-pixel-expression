# voronoi

**What it does:** Nearest feature-point distance; `jitter` 0=grid..1=random, `seed` = pattern/drift.

**Use case:** Cellular/organic patterns, scales, cracked textures.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `scale` (80), `seed` (0.0), `jitter` (1.0)

## Notes

**Cellular (Voronoi) noise** — distance to the nearest feature point in the surrounding 3×3
cells. Gives cells, scales, cracks, stained-glass and caustic-like looks.

### Controls
- `scale` = cell size in pixels.
- `jitter` = how far feature points wander from a regular grid: **0 = perfectly regular
  lattice, 1 = fully random** cells. Dial it for ordered-vs-organic.
- `seed` = pattern + animation (keyframe to evolve — points drift, cells reshape).

### Practical notes
- Output is the distance field (dark at cell centres, bright at borders); greyscale on RGB
  with solid alpha — **tag Raw/Data**.
- Threshold or `smoothstep` it for hard cell edges, or use it raw as a bumpy displacement.
