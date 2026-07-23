# moire

**What it does:** Beat pattern of two near-identical line gratings (`freqA` vs `freqB`) — an intentional moiré.

**Use case:** Interference/aliasing FX, hypnotic op-art, screen/CRT artefacts.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `freqA` (0.08), `freqB` (0.085), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

An **intentional moiré**: lay two near-identical line gratings over each other and the tiny
frequency/angle mismatch beats into a slow, large-scale pattern — the same artefact you get
photographing a CRT or a striped shirt, here made on purpose.

### How it works
- `sin(x·freqA)` is grating A (vertical lines); `sin((x·0.9992 + y·0.04)·freqB)` is grating B
  rotated by a fixed small angle. **Multiplying** them produces the beat (their sum/difference
  frequencies); the product is remapped to 0..1.
- The two-colour vars eat 6 of 8 slots, so the two **frequencies** are the exposed knobs (the
  rotation is baked); the frequency mismatch is what drives the moiré anyway.

### Practical notes
- Keep `freqA` and `freqB` **close** (e.g. 0.08 vs 0.085) — the closer they are, the wider and
  slower the moiré bands.
- Nudge `freqA`/`freqB` by hundredths to "tune" the pattern; keyframe one for a living,
  breathing moiré.
- Two colours `aR/aG/aB`→`bR/bG/bB`; raw pattern on OutMatte. Uses: op-art, interference/aliasing
  FX, screen-artefact looks.
