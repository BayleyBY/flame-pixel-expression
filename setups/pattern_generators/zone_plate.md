# zone_plate

**What it does:** `sin(r²)` Fresnel-ring test target around Centre (rings densen outward); `freq` is tiny because r² is large. Two-colour; matte = pattern.

**Use case:** Resolution/aliasing test chart, moiré reference, op-art texture.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `freq` (0.001), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

A **`sin(r²)` zone plate** (Fresnel/Newton's-rings target): rings that get **denser the further
out** you go — the classic resolution and aliasing test pattern, and excellent moiré bait.

### Why r² (not r)
`rings` uses `sin(dist)` — evenly spaced. Here the phase is `r²`, so ring frequency rises with
radius, sweeping through the whole frequency range in one image. That's what makes it reveal
sampling/aliasing artefacts (and beat into moiré against other grids or a screen).

### Controls
- `freq` — ring density. **Tiny** by design (default 0.001) because `r²` is large; nudge with
  Space+Drag.
- Centred on the node **Centre**; two-colour A→B like the other pattern generators, `matte` =
  raw pattern.
