# split_tone

**What it does:** Tints shadows toward `shadowHue` and highlights toward `highHue`, weighted by luma; `balance` slides the pivot.

**Use case:** Classic teal-shadow / warm-highlight (and similar) colour looks.

**Inputs:** Front 1

**Expects:** your working/display space (tonal + hue-based)

**Variables:** `shadowHue` (0.58), `highHue` (0.08), `shadowAmt` (0.1), `highAmt` (0.1), `balance` (0.0)

## Notes

Tints the **shadows** toward one colour and the **highlights** toward another — the
backbone of a graded "look" (the ubiquitous teal-shadow / warm-highlight being the obvious
one). It's a colour move keyed off *brightness*, which is exactly what RGB makes awkward
and tonal/HSV thinking makes easy.

### How it works
Pixel luma drives two weights: a shadow weight that's strong in the darks and a highlight
weight that's strong in the brights. Each region is nudged toward its tint colour — derived
from `shadowHue` / `highHue` at full saturation — *centred* so a neutral tint does nothing
and a hue pushes some channels up and others down (a tint, not a brightness change).
`balance` slides the luma pivot between the two regions.

### Controls
- `shadowHue` / `highHue` — 0..1 hue of each tint (red 0.0, orange ~0.07, yellow ~0.15,
  green 0.33, cyan 0.5, blue 0.66, magenta 0.83).
- `shadowAmt` / `highAmt` — strength of each tint (start small, ~0.1).
- `balance` — -0.5..0.5, shifts the shadow/highlight split point. Negative throws more of
  the image into "highlight", positive into "shadow".

### Why use it
It's the fastest way to put a cohesive colour personality on a plate: cool the shadows and
warm the highlights for the modern blockbuster look, or push complementary hues for a
stylised grade. Defaults are a gentle teal-blue shadow (`0.58`) / warm-orange highlight
(`0.08`).

### Practical notes
- **Keep amounts low.** 0.05–0.15 reads as a grade; higher reads as a colour cast.
- **Complementary hues** (≈0.5 apart on the wheel) give the strongest, most filmic
  separation — teal/orange is 0.5↔0.08, roughly opposite.
- **`balance` is your midtone protector** — slide it to keep the tint off the faces/midtones
  and concentrated in the deep shadows or bright highlights.
- Works in your working/display space; the look depends on where your blacks and whites
  sit, so set exposure/contrast first, tint second.
