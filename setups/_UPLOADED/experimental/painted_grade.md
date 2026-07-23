# painted_grade

**What it does:** Grades Front 1 using a PAINTED Front 2 control map: r2 = local exposure, g2 = local hue shift, b2 = local saturation (0.5 = neutral on each).

**Use case:** Paint a soft control map (in Paint/roto/another Pixel Expression) to drive exposure/hue/sat that vary across the frame from one node — no tracked mattes.

**Inputs:** Front 1 (image) + Front 2 (control map); Matte 1 optional (passes through)

**Expects:** Front 1 in your grading/scene-linear space; Front 2 is a 0..1 data control map

**Variables:** `expRange` (2.0), `hueRange` (1.0), `satRange` (1.0)

## Node dependencies
**Pipeline:** image (Front 1) + painted control map (Front 2) → **this node**

The grade is driven by a **painted control map on Front 2**: `r2` = local exposure, `g2` = local hue, `b2` = local saturation (flat 0.5 grey = neutral). The upstream 'node' is wherever you paint/generate that map — Paint, a roto fill, a ramp, or another generator.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

A grade whose **parameters are painted, not global**. The usual grade node has one exposure,
one hue, one saturation for the whole frame; here those three knobs live in **Front 2** and
can differ at every pixel. It's a hand-authored control surface — a *spatially-varying* grade
from a single node, with no tracked mattes or stacked secondaries.

### Paint the control map
Build Front 2 in Paint, roto, a ramp, or another Pixel Expression. Each channel is a
**0..1 control, 0.5 = neutral**:
- **red (r2)** → local **exposure**: 0.5 = no change, >0.5 brightens, <0.5 darkens (`exp2`,
  so it's symmetric in stops). `expRange` sets the stops at the 0/1 extremes.
- **green (g2)** → local **hue shift**: 0.5 = no rotation; the rotation is luma-preserving
  (same matrix as `hue_rotate`), so it won't change brightness. `hueRange` = full turns at the
  extremes.
- **blue (b2)** → local **saturation**: 0.5 = no change, 1.0 = more vivid, 0.0 = toward grey
  (mix around Rec.709 luma). `satRange` scales the push.

A **flat 0.5 grey** Front 2 (or no paint) leaves the image untouched — defaults are neutral.

### Order of operations
Exposure first (linear multiply), then saturation, then the hue rotation on the result
(formula `pr`). Work in **scene-linear** so the exposure stops are photometric.

### Recipes
- **Localised relight:** paint a soft white blob on r2 over a face to lift just that area.
- **Selective desaturation:** paint b2 dark over a distracting background to grey it down while
  the hero stays saturated.
- **Animated reveal:** keyframe / animate the painted map upstream to sweep a grade across the
  frame.
