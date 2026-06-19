# aov_grade_add

**What it does:** Tints/exposes Front 2 (one pass) and adds it to Front 1 (the running sum).

**Use case:** Isolate a single AOV, grade it, and merge it back.

**Inputs:** Front 1 = sum, Front 2 = pass

**Expects:** scene-linear

**Variables:** `exposure` (1.0), `tintR` (1.0), `tintG` (1.0), `tintB` (1.0)

## Notes

The core **"isolate a pass, art-direct it, put it back"** move: `running_beauty + pass *
tint * exposure`. This is why you render in passes at all.

### How to wire it
- **Front 1 = the running beauty** (or another pass total), **Front 2 = the single pass** you
  want to tweak. Tint and expose Front 2, then add it back into Front 1.
- Chain one node per pass you want to touch; passes you don't touch can stay in the
  `aov_add` running sum.

### Practical notes
- **Scene-linear.** `exposure` scales the pass's intensity, `tintR/G/B` recolours it — e.g.
  warm just the bounce light, or knock the spec down a stop, with no re-render.
- Keeps Front 1's alpha.
