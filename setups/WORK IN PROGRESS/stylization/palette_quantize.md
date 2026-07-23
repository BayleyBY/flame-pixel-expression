# palette_quantize

**What it does:** Snaps Front 1 to `levels` tonal steps and tints the result between two palette anchor colours (default 4-tone; set the colours for a Game-Boy green ramp).

**Use case:** Limited-palette / pixel-art stylisation, duotone posterise, retro console look.

**Inputs:** Front 1

**Expects:** display-referred / working image (luma-driven look)

**Variables:** `levels` (4.0), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

**Limited-palette posterise.** Front 1 is reduced to `levels` discrete tonal steps and the
result is re-coloured between two palette anchors — the budget-friendly route to a
pixel-art / retro-console look without needing a full per-colour palette match (which would
blow the 8-variable cap three times over).

### How it works
The Rec.709 luma is quantized: `min(floor(luma * levels), levels - 1) / (levels - 1)` snaps
it to `levels` evenly-spaced values spanning 0..1 (the `min` pins full white — and anything
clipped above it — to the top step instead of overshooting past colour B). That stepped
value `q` then drives `_two_color`, so each tone lands on a `mix` between colour A (darkest)
and colour B (lightest). Pick the two endpoints and the intermediate steps fall on the ramp
between them.

### Controls
- `levels` — number of tones (4 = the classic 4-shade console look; 2 = hard duotone).
- `aR/aG/aB` (dark) and `bR/bG/bB` (light) — the palette endpoints.

### Recipes
- **Game-Boy green:** `levels` 4, A = dark green (≈0.06, 0.22, 0.06), B = pale green
  (≈0.61, 0.74, 0.06).
- **Sepia duotone:** `levels` 2-3, A = deep brown, B = cream.

### Notes
- Expects a **display-referred / working image** — it snaps by display luma, so grade
  first, quantize last.
- This is the tonal-ramp approach; for a *hue*-based limited palette, qualify with
  `chroma_key` / `hsl_targeted` upstream and quantize the regions separately.

### Quick test
⚠ **Re-verify the 2026-07-21 fix:** feed a plate with blown highlights (or gain one up ×4)
→ the brightest areas must land EXACTLY on colour B (default white), never brighter (the
old bug overshot past B). Normal load: instant 4-tone posterize of any clip.
