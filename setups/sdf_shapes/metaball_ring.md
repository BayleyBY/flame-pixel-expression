# metaball_ring

**What it does:** Six point sources on a ring around Centre, welded with a polynomial smooth-min (`k`) into one gooey blob ring; `ringRadius`/`blobRadius` size it, keyframe `spin` to rotate. RGB + Matte.

**Use case:** Rotating metaball rings, blob clusters, lava-lamp / loader animations, organic ring mattes.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `ringRadius` (200.0), `blobRadius` (90.0), `k` (80.0), `spin` (0.0)

## Notes

The **higher-count companion** to `smin_metaballs`: six blobs arranged on a ring around the node
**Centre** and welded with the same polynomial smooth-min into one gooey ring.

### Why six here but three there
Independent x/y for each blob costs 2 variables per blob; the node has only **8**, so
`smin_metaballs` caps at 3 hand-placed blobs. Here the positions are **derived** — blob *i* sits at
angle `i·60° + spin` on a circle of radius `ringRadius` — so the whole ring rides on just four
knobs (`ringRadius`, `blobRadius`, `k`, `spin`), leaving budget to spare. The count (6) is fixed at
build time: the node has no loops, so each blob's distance is inlined. The six distances are packed
into two `vec3` formulas (`da`,`db`) and smooth-min'd as two triads (`sa`,`sb`) then a final weld —
referencing the packed distances by swizzle keeps the nested `smin` from re-expanding.

### Controls
- `ringRadius` — radius of the ring the blobs sit on (px, from Centre).
- `blobRadius` — size of each blob; raise it (or `k`) until neighbours merge into a continuous ring.
- `k` — smooth-min blend radius: bigger = longer, gooier necks between blobs.
- **`spin`** — rotates the whole ring. **Keyframe it** (0 → 1 = one full turn) for a rotating
  metaball loop / loader animation.
- Result on RGB + Matte — an organic ring matte or displacement source. Move the node **Centre** to
  reposition the ring. For hand-placed blobs instead of a ring, use `smin_metaballs`.
