# wood_grain

**What it does:** Concentric rings around Centre warped by value-noise turbulence (`freq` spacing, `turb` distortion). Default colours brown/tan; two-colour.

**Use case:** Procedural wood texture, tree-ring patterns, organic concentric distortion.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `freq` (0.02), `turb` (4.0), `aR` (0.25), `aG` (0.13), `aB` (0.05), `bR` (0.55), `bG` (0.35), `bB` (0.18)

## Notes

Procedural **wood**: concentric growth rings around the node Centre, warped by value-noise
**turbulence** so they wander like real grain instead of perfect circles.

- `freq` — ring spacing (higher = tighter rings). `turb` — how much the noise distorts them
  (0 = clean circles, high = knotty).
- Default colours are brown→tan; it's a two-colour generator, so set `aR/aG/aB`→`bR/bG/bB` for any
  wood tone (or match all three for grayscale). Pair with `cosine_palette` for richer grading.

### Quick test
Any clip on **Front 1** → **brown/tan wandering growth rings immediately**. `turb` 0 →
perfect circles; higher = knottier.
