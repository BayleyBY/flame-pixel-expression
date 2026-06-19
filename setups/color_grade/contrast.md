# contrast

**What it does:** Scales values around a `pivot`; `contrast` >1 increases.

**Use case:** Add/reduce contrast about a chosen mid grey (0.18 scene-linear default).

**Inputs:** Front 1

**Expects:** scene-linear (pivot 0.18; use ~0.5 in display/log)

**Variables:** `contrast` (1.0), `pivot` (0.18)

## Notes

Scales values around a `pivot`: `pivot + (value - pivot) * contrast`. Tones above the pivot
go up, tones below go down, and the pivot itself stays put — so it stretches or compresses
the range without shifting the midpoint.

### The pivot is the whole game
The pivot is the tone that doesn't move. Everything hinges on putting it where your "middle"
actually is **in the current encoding**:
- **scene-linear** → `0.18` (18% middle grey), the default.
- **display / log / sRGB** → roughly `0.5`.

Pick the wrong pivot and contrast also shifts overall brightness (the image gets darker or
lighter as you add contrast), which usually isn't what you want.

### Practical notes
- `contrast` > 1 increases, < 1 flattens, 1.0 is unchanged.
- **No clamp** — strong contrast can drive values negative or super-white. Follow with
  `aov_clamp_negative` or a clamp if a downstream op can't take it.
- Do contrast *after* exposure/white-balance so the pivot sits at the right level.
