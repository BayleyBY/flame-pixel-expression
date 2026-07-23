# radial_ramp

**What it does:** Radial gradient from Centre: white in the middle to black at `radius`, edge shaped by `softness`.

**Use case:** Vignettes, falloff masks, soft round mattes, light pools.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `radius` (600), `softness` (1.0), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

A **radial gradient / vignette** centred on the node's **Centre** control — white at the
centre falling to black at `radius`.

### Two colours (shared across the tonal generators)
The pattern is a 0..1 mask blended `mix(A, B, pattern)` per channel: **colour A** `aR/aG/aB`
(default black, where the pattern = 0) → **colour B** `bR/bG/bB` (default white, where it = 1).
Defaults reproduce the original greyscale; set all three of a colour equal for a
luminance-only look. **OutMatte carries the raw 0..1 pattern**, regardless of the colours.
(Colour fields step in tenths — hold **Space + Drag** for finer values.)

### Practical notes
- `radius` = falloff radius in px; `softness` 0 = hard-edged circle, 1 = smooth falloff all
  the way from centre. **Centre** positions it.
- The go-to for vignettes, spotlight masks, and soft radial holdouts.
