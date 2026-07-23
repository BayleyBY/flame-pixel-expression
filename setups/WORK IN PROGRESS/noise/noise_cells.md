# noise_cells

**What it does:** Flat random value per `cellSize`-pixel cell; `seed` picks/drifts the pattern.

**Use case:** Blocky random masks, mosaic seeds.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `cellSize` (64), `seed` (0.0)

## Notes

**Blocky per-cell random** — one flat random value per `cellSize`-pixel cell, no
interpolation. The cheapest noise here and the only hard-edged one.

### Animating it (the `seed` trick)
The node has **no frame/time variable**, so you animate procedural patterns by **keyframing
`seed`** — it offsets the sampling into the noise field, reshuffling the cells. Keyframe it to
make the pattern evolve/flicker over a shot.

### Practical notes
- `cellSize` = cell size in pixels; `seed` = pattern / animation.
- Output is a greyscale field on **RGB with solid alpha** (`matte = 1.0`) — it's data, not a
  matte. Shuffle a channel to alpha downstream if you need it as a mask, and **tag it
  Raw/Data**.
- Uses: mosaic/blocky randomness, glitch, per-cell breakup, stepped dissolves.

### Quick test
Any clip on **Front 1** (resolution only) → **flat random grey blocks, 64 px** on load. No
image at all usually means Front 1 isn't wired. Keyframe `seed` and the cells reshuffle
every frame.
