# sdf_lattice

**What it does:** A tiled, anti-aliased rounded-square SDF: `spacing` px, `boxSize` half-extent, `corner` round, `soft` edge. Sharper/cleaner than a hard checker.

**Use case:** Perforation/pegboard/grille mattes, anti-aliased tile patterns.

**Inputs:** none (generator)

**Expects:** any — generates data/values

**Variables:** `spacing` (80.0), `boxSize` (22.0), `corner` (8.0), `soft` (2.0)

## Notes

Tiles a single **rounded-square SDF** across the frame with `mod`-space repetition, so every cell
is an anti-aliased rounded square — a cleaner, softer alternative to the hard-edged `checkerboard`.

- `spacing` cell pitch (px), `boxSize` the square's half-extent, `corner` the rounding radius,
  `soft` the AA edge width.
- Grayscale (RGB + Matte). Good for perforation/pegboard/grille mattes and tidy tiled patterns.
  Set `corner` ≈ `boxSize` for circles, 0 for sharp squares.
