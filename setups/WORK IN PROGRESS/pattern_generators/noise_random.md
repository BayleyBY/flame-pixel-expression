# noise_random

**What it does:** Per-pixel hash (white) noise, with a different seed per channel.

**Use case:** Grain, dither, random seeding — the GLSL stand-in for Nuke's random().

**Inputs:** none

**Expects:** any — generates data/values

_No variables._

## Notes

**Per-pixel white noise** — a fixed hash of `x`/`y`, the GLSL stand-in for Nuke's `random()`.
The **only** generator here without the two-colour blend: each of R/G/B gets an independent
noise channel, alpha solid.

### Static by design
It's a pure function of pixel position, so it's the **same every frame** and has **no `seed`
or animation**. For noise that evolves over a shot — or that you can shape (scale, octaves,
cells) — use the `noise/` folder (`noise_value`, `noise_fbm`, `voronoi`), where keyframing
`seed` drives the motion.

### Practical notes
- Uses: grain, dither, a random source to drive a dissolve/threshold. Tag it Raw/Data.

### Quick test
Any clip on **Front 1** → **per-pixel colour static** (R/G/B are independent hashes). It is
IDENTICAL every frame by design — for animated noise use `noise/` with a keyframed `seed`.
