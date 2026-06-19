# screen_merge

**What it does:** Screens Front 2 onto Front 1; `gain` scales the added pass.

**Use case:** Add glow/bloom/light passes without hard clipping.

**Inputs:** Front 1 + Front 2

**Expects:** scene-linear, or display-referred for a Photoshop-style screen

**Variables:** `gain` (1.0)

## Notes

**Screens** a glow/bloom pass onto the beauty — `1 - (1-base)(1-over)` — the standard way to
add light-emitting passes without the harsh clipping of a plain add.

### Practical notes
- **Front 1 = beauty, Front 2 = the glow/bloom/emission pass.** `gain` scales the pass on
  the way in.
- Screen is a **display-referred** operator (it assumes 0..1), so it reads naturally on
  display-referred images; on scene-linear it still combines but behaves more like a soft
  add. Choose your space to taste — see the **Expects** line.
- Run `aov_clamp_negative` on the glow pass first if it carries negatives.
