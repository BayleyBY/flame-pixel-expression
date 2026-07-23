# noise_fbm

**What it does:** 3-octave fractal noise; `lacunarity`/`persistence` shape it, `seed` = pattern/drift.

**Use case:** Clouds, smoke/atmosphere masks, natural-looking break-up.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `scale` (80), `seed` (0.0), `lacunarity` (2.0), `persistence` (0.5)

## Notes

**Fractal noise** — three octaves of value noise summed (fractional Brownian motion). The
natural-looking one: clouds, smoke, terrain, weathering.

### The shaping controls
- `scale` = base feature size.
- `lacunarity` = how much **frequency** rises each octave (~2.0 doubles it) — adds finer
  detail.
- `persistence` = how much **amplitude** falls each octave (~0.5 halves it) — **lower =
  smoother/softer, higher = rougher/grittier**.
- `seed` = pattern + animation (keyframe to evolve).

### Practical notes
- This is the **heaviest expression in the library** (three inlined octaves) — it's verified
  loading in Flame, but it's the most likely place to feel a compile cost.
- Greyscale field on RGB, solid alpha; **tag Raw/Data**.

### Quick test
Any clip on **Front 1** → **cloudy fractal field** on load. `persistence` 0.8 → gritty,
0.3 → smooth; keyframe `seed` to evolve. (Heaviest expression in the library — a beat of
compile hesitation on load is normal.)
