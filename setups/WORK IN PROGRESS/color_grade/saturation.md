# saturation

**What it does:** Scales saturation around luminance; `sat` 0=greyscale, 1=normal, >1=boosted.

**Use case:** Quick saturation tweak or full desaturate.

**Inputs:** Front 1

**Expects:** scene-linear (Rec.709 luma weights)

**Variables:** `sat` (1.0)

## Notes

**Saturation grade** — `mix(luma, colour, sat)` per channel using Rec.709 luma. `sat` 0 =
greyscale, 1 = unchanged, > 1 = boosted (can clip), < 1 desaturates toward grey.

### Practical notes
- **Luma weights are Rec.709** — correct in scene-linear, approximate elsewhere.
- This is a flat, global push. For saturation that **protects already-vivid colours and
  skin**, use `vibrance`; for a single hue, `hsl_targeted`.

### Quick test
Loads neutral (`sat` 1.0). Fastest check: `sat` 0.0 → **full greyscale**; 2.0 →
cartoon-vivid.
