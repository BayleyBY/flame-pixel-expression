# sdf_circle

**What it does:** Anti-aliased circle matte around Centre.

**Use case:** Round garbage mattes, spotlights, vignette shapes.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `radius` (200), `soft` (2.0)

## Notes

An **anti-aliased disc matte** built from a signed distance field, centred on the node's
**Centre** control. The simplest SDF primitive.

### Conventions shared across `sdf_shapes/`
- The shape sits at **Centre** (the node's Centre X/Y), *not* the image origin — set Centre to
  position it. No input needed (it's a generator).
- Sizes are in **pixels**; `soft` = edge width in pixels (anti-aliasing / feather).
- Written to **RGB and Matte**, so it's usable straight as a matte (Result or OutMatte).

### Practical notes
- `radius` = disc radius. For a circular **outline** instead of a filled disc, use `sdf_ring`.
