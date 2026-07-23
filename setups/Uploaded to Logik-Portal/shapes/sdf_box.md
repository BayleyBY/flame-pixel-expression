# sdf_box

**What it does:** Anti-aliased rectangle matte (`bx`×`by`); `hollow` 0..1 cuts out the middle.

**Use case:** Rectangular holdouts, framing masks, rectangular outlines.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `bx` (200), `by` (120), `hollow` (0.0), `soft` (2.0)

## Notes

An **anti-aliased rectangle matte** (SDF), centred on **Centre**, with a hollow control that
turns it into a frame.

### bx / by are HALF-extents
`bx` and `by` are the **half-width and half-height** (distance from centre to edge), so the
box is `2*bx` × `2*by` pixels. Easy to mistake for full size.

### The `hollow` control
`hollow` 0 = solid; as it rises toward 1 it **cuts a growing hole out of the middle while the
outer edge stays fixed** — so you get a rectangular frame/border whose thickness shrinks
inward as `hollow` increases. (Shared `_HOLLOW` mechanism across the SDF shapes.)

### Practical notes
- `soft` feathers the edge. Uses: framing masks, holdouts, rectangular outlines.
