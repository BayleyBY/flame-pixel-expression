# difference_matte

**What it does:** Matte from the colour difference between Front 1 and a clean plate (Front 2), scaled by `gain`.

**Use case:** Isolate what changed between a shot and its clean plate (added objects, motion).

**Inputs:** Front 1 + Front 2

**Expects:** any (most even in scene-linear)

**Variables:** `gain` (5.0)

## Node dependencies
**Pipeline:** shot (Front 1) + aligned clean plate (Front 2) → **this node** → (matte to comp)

Keys what *changed* between the shot (Front 1) and a **clean plate** (Front 2) — so it needs that aligned clean plate wired upstream. `gain` scales the difference.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

A **difference key against a clean plate**: the RGB distance between Front 1 and Front 2,
scaled by `gain` and clamped — white where the two images differ, black where they match.
Written to RGB and the Matte.

### Setup
- **Front 1 = the shot, Front 2 = a locked-off clean plate** of the same scene without the
  element. They must be **registered** (same camera, alignment) — it compares pixel-for-pixel.
- `gain` boosts sensitivity (default 5.0); raise it to catch subtle differences, lower it to
  reject noise.

### Practical notes
- **Most even in scene-linear.** It's sensitive to grain, exposure flicker and lighting
  change between shot and plate — **denoise / match levels first**, then soften the result
  with `matte_grade`.
- Great as a *starting* garbage matte to combine with a real key, rarely a final key alone.
