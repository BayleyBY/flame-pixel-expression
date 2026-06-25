# point_grid

**What it does:** Dot-lattice generator: `spacing` px between dots, `dotR` radius, two-colour A→B (like checkerboard). matte = dot mask.

**Use case:** Alignment/registration grids, perforation/polka mattes, screentone base.

**Inputs:** none (generator)

**Expects:** any — generates data/values

**Variables:** `spacing` (64.0), `dotR` (6.0), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

A **dot-lattice generator** — regularly spaced dots, the dot complement to `checkerboard` and
`bricks`. Built on the shared two-colour convention.

### Controls
- `spacing` — pixels between dot centres.
- `dotR` — dot radius (px). Anti-aliasing is a fixed 1px `smoothstep`.
- Colour **A** (`aR/aG/aB`, default black = background) → colour **B** (`bR/bG/bB`, default
  white = dots). `matte` carries the raw dot mask.

### Uses
Alignment/registration grids, perforation or polka-dot mattes, a screentone/halftone base, or a
particle-seed mask. Keyframe `spacing` to pulse the lattice.
