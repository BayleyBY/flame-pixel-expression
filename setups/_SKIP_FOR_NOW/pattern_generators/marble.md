# marble

**What it does:** Turbulence-distorted vein bands (`freq` spacing, `turb` distortion) — Perlin's classic marble. Default colours pale-stone/dark-vein; two-colour.

**Use case:** Marble/stone texture, veined organic looks, paint-swirl bases.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `freq` (0.05), `turb` (6.0), `aR` (0.85), `aG` (0.85), `aB` (0.83), `bR` (0.15), `bG` (0.15), `bB` (0.18)

## Notes

Procedural **marble** (Perlin's classic recipe): straight vein bands along X, displaced by
value-noise **turbulence** so they swirl and fold like stone.

- `freq` — vein spacing. `turb` — swirl amount (this is what makes it marble rather than stripes).
- Default colours are pale-stone → dark-vein; two-colour, so dial any stone palette. Rotate the
  whole look by feeding it through a transform upstream, or pair with `cosine_palette`.
