# halftone

**What it does:** Newspaper halftone: tiles the frame into `cell`-px cells (rotatable by `angle`) and draws a dot per cell whose size grows with that cell's luma.

**Use case:** Print/comic look, retro screen-print stylisation, animated dot-screen transitions.

**Inputs:** Front 1

**Expects:** display-referred / working image (luma-driven look)

**Variables:** `cell` (12), `angle` (0.4), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

The classic **newspaper / comic dot-screen**. The frame is tiled into a regular grid of
`cell`-pixel squares; in each cell a single dot is drawn whose radius grows with that
region's brightness — bright areas pack big overlapping dots (reads as light), dark areas
shrink to tiny dots (reads as dark). Output is two-colour, defaulting to black ink on white
paper.

### How it works
1. Pixel coordinates are rotated by `angle` (radians) so the dot grid can sit at the
   traditional ~15-45 degree screen angle instead of square-on.
2. `mod(coords, cell)` folds everything into one cell; the dot is the SDF of a circle whose
   radius is `0.5 * cell * sqrt(luma)` (the `sqrt` makes dot *area* roughly linear in luma,
   which is what print actually does).
3. A soft threshold of that SDF gives the inked pixel, then `_two_color` maps it from paper
   (`aR/aG/aB`, default black... wait — see below) to ink.

### Controls
- `cell` — dot pitch in pixels. Smaller = finer screen.
- `angle` — screen rotation in radians (~0.4 ≈ 23 deg is a good print angle).
- `aR/aG/aB` (ink) and `bR/bG/bB` (paper) — the two tones. Default is ink black / paper
  white; swap them or set a colour for duotone (e.g. ink = deep blue on cream paper).

### Recipes
- **Comic halftone:** `cell` 6-10, `angle` 0.4, leave colours black/white.
- **Pop-art duotone:** set ink to a saturated magenta and paper to pale yellow.
- **Animated reveal:** keyframe `cell` from large to 1 to dissolve the dot-screen into the
  full image.

### Notes
- Expects a **display-referred / working image** — it shades by Rec.709 luma, so feed it the
  graded look, not scene-linear, or the dots will skew toward the highlights.
