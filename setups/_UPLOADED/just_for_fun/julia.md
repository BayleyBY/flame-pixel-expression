# julia

**What it does:** Escape-time Julia set; constant `cRe`/`cIm` picks the shape (keyframe to morph), `gain`/`gamma` shape the bands. Grayscale.

**Use case:** Animated organic fractal element; morphing background or matte.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `zoom` (400.0), `cRe` (-0.8), `cIm` (0.156), `gain` (1.0), `gamma` (1.0)

## Notes

The **Julia** companion to `mandelbrot`: same 8-iteration escape-time engine, but `z`
**starts at the pixel** and `c` is a **constant** you control with `cRe`/`cIm`. Sweeping
that constant morphs the whole shape — which is the fun part.

### The morph (keyframe `cRe`/`cIm`)
`cRe`/`cIm` is a point in the complex plane; each value gives a different Julia set.
**Keyframe them** to animate a continuously-morphing fractal. Good values to try:
| `cRe` | `cIm` | Look |
|-------|-------|------|
| -0.8 | 0.156 | default — connected, dragon-ish |
| -0.4 | 0.6 | spiral arms |
| 0.285 | 0.01 | dense, near-circular |
| -0.70176 | -0.3842 | classic "rabbit" |
| -0.835 | -0.2321 | lightning / dendrite |

Animate a small loop (e.g. `cRe` -0.8→-0.7→-0.8 over 100 frames) for a breathing morph.

### Same shallow caveat
Like `mandelbrot`, this is **8 total iterations** (the 4-formula chain expands ~8x per
inlined step, so deeper is impractical). Interiors read solid; edges band. It's a
texture/animation tool, not a deep renderer.

### Output (`gain` / `gamma`)
**Grayscale** — the escape value written to RGB **and** Matte (via `_solid`). As in
`mandelbrot`, `gamma` curves the bands (`>1` darkens mids / crisper, `<1` lifts / more glow)
and `gain` scales brightness after; both default `1.0`, order `clamp(pow(escape, gamma) *
gain, 0, 1)`. Tint downstream or mask off the Matte. Pan/zoom via node **Centre** + `zoom`.
