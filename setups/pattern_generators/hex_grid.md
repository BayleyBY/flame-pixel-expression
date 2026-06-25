# hex_grid

**What it does:** True hexagonal (honeycomb) tiling: `hexSize` cell size, `lineW` border thickness, two-colour cell→border.

**Use case:** Honeycomb mattes/overlays, hex-cell bases for randomised fills, sci-fi shields.

**Inputs:** none (generator)

**Expects:** any — generates data/values

**Variables:** `hexSize` (60.0), `lineW` (0.06), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

A true **hexagonal (honeycomb) tiling**. It folds the plane onto a hex lattice by testing two
offset square grids and keeping whichever centre is nearer (the standard "Art of Code" hex trick),
then draws the cell border from the hex edge-distance.

- `hexSize` — hexagon size in px. `lineW` — border thickness (in hex units, ~0..0.2).
- Two-colour: A = cell fill, B = border. `matte` = the border mask.
- The square grids (`pattern_generators/`) had no hex option; this fills that gap. Per-cell IDs for
  randomised fills would need the cell centre (not exposed here) — this is the tiling/border look.
