# hue_rotate

**What it does:** Luma-preserving hue rotation; `hue` 0..1 = full turn.

**Use case:** Shift colours without changing brightness.

**Inputs:** Front 1

**Expects:** any (operates on the RGB values as given)

**Variables:** `hue` (0.0)

## Notes

**Global hue rotation** — spins every colour around the wheel by a fixed amount; `hue` 0..1 =
one full turn, positive values rotating red → green → blue. Uses a luma-preserving rotation
matrix (Rec.709 weights, no HSV decode), so **brightness is unchanged**.

### Practical notes
- Affects the **whole image** equally. To rotate only one colour band, use `color_replace`
  (hue→hue) or `hsl_targeted` (band + sat/value).
- Keyframe `hue` for a cycling-colour effect.
