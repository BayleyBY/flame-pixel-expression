# clip_highlighter

**What it does:** Marks pixels over `ceiling` red and under `floorVal` blue (solid, `tint` opacity); in-range passes through. matte = union of clip masks.

**Use case:** At-a-glance over/under-exposure QC with hard thresholds — the solid-marker companion to `exposure_zebra`.

**Inputs:** Front 1

**Expects:** any (thresholds are on raw channel values — set `ceiling`/`floorVal` to your range)

**Variables:** `ceiling` (1.0), `floorVal` (0.0), `tint` (1.0)

## Notes

Solid over/under-exposure markers: any channel ≥ `ceiling` is marked **red**, any channel ≤
`floorVal` is marked **blue**, in-range passes through; `tint` sets marker opacity and `matte` is
the union of the two clip masks.

### vs `exposure_zebra`
`exposure_zebra` draws **animated diagonal stripes** on clipped areas (a moving camera-zebra look).
This paints **solid** colour with artist-set `ceiling`/`floorVal` thresholds — easier to read as a
still and to use as an actual clip *mask*. Two takes on the same QC; pick by preference.
