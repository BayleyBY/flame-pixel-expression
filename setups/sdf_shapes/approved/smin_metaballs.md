# smin_metaballs

**What it does:** Three point sources merged with a polynomial smooth-min (`k` = blend radius) into one gooey blob field; centres are offsets from Centre. Result on RGB + Matte.

**Use case:** Organic blobby alpha mattes, lava-lamp/metaball shapes, soft union bases.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `c1x` (-150.0), `c1y` (0.0), `c2x` (150.0), `c2y` (0.0), `c3x` (0.0), `c3y` (150.0), `radius` (120.0), `k` (90.0)

## Notes

Three circular point sources blended with a **polynomial smooth-minimum** (`smin`) so they don't
just overlap — they **weld** into one organic surface with smooth necks between them (the classic
metaball look). `k` is the blend radius: bigger `k` = longer, gooier necks.

- Centres `c1/c2/c3 (x,y)` are offsets from the node **Centre**; `radius` is the shared blob size.
- **Animate** one centre (keyframe `c2x`, say) to make the blobs flow and merge — that's where the
  smooth-min earns its keep.
- Result on RGB + Matte — an organic alpha matte or a displacement source. `smin` is verified to
  weld below `min` and never exceed it.
