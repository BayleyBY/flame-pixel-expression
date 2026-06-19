# hsl_targeted

**What it does:** Applies `dHue`/`dSat`/`dVal` only inside a hue band (`centerHue`, `bandWidth`, `soft`); the rest is untouched.

**Use case:** Per-colour grade — darken the blues, desaturate the greens, warm skin.

**Inputs:** Front 1

**Expects:** your working/display space (hue-based)

**Variables:** `centerHue` (0.33), `bandWidth` (0.08), `soft` (0.05), `dHue` (0.0), `dSat` (0.0), `dVal` (0.0)

## Notes

A **secondary colour correction in a single node** — it isolates one range of hues and
pushes only those pixels, leaving everything else untouched. No separate key, matte, or
qualifier node: the hue selection *is* the qualifier. This is the Lightroom/Resolve **HSL
panel** behaviour, or a Flame **secondary**, as one expression node you can keyframe.

### How it works
1. **Select** a soft slice of the colour wheel — a band centred on `centerHue`,
   `bandWidth` wide, with `soft` feathering the edges. Inside the band the weight is ~1,
   outside it is 0, and the `soft` zone ramps between them (so the grade blends instead of
   hard-clipping). The band **wraps around the wheel**, so a `centerHue` near 0.0 catches
   reds on both sides of the seam.
2. **Grade** the selected pixels along three independent axes:
   - `dHue` — rotate the hue (luma-preserving, like `hue_rotate`, so it won't change
     brightness)
   - `dSat` — scale saturation (`+` more vivid, `-` toward grey)
   - `dVal` — scale brightness (`+` lighter, `-` darker)

   Each channel is `mix(original, graded, bandWeight)`, so unselected colours pass through
   untouched.

### Why use it
"Change one colour without touching the rest" is miserable in RGB — "the greens" is a
tangled three-channel inequality. In hue space it's just *a position on the wheel ± a
width*. That's the whole reason this lives in `hsv_color/`.

### Hue reference
`centerHue` is 0..1 around the wheel: **red 0.0, orange ~0.07, yellow ~0.15, green 0.33,
cyan 0.5, blue 0.66, magenta 0.83.**

### Recipes
| Goal | `centerHue` | The move |
|------|-------------|----------|
| Calm a too-vivid green spill on foliage | 0.33 | `dSat` -0.4 |
| Make a daytime sky deeper blue | 0.6 | `dSat` +0.3, `dVal` -0.1 |
| Warm skin tones | 0.07 | `dHue` +0.01, `dSat` +0.1 |
| Turn a red car slightly orange | 0.0 | `dHue` +0.05 |
| Knock back a distracting yellow sign | 0.15 | `dSat` -0.5, `dVal` -0.2 |

### Practical notes
- **Tune the selection first, grade second.** Crank `dSat` to an extreme (`+2` or `-1`) so
  the affected region is obvious, adjust `bandWidth`/`soft` until *only* the colour you want
  is moving, then dial the deltas back to taste.
- **`soft` prevents banding** on gradients (skies, cheeks) — a hard band edge shows a seam.
- **Relationship to neighbours:** `color_replace` is the `dHue`-only special case aimed at a
  target hue; `chroma_key` / `sat_matte` *output a matte* for a band instead of grading it
  inline. Use those when a downstream node needs the selection; use `hsl_targeted` when you
  just want the corrected pixels out the other side.
