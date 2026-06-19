# depth_posterize

**What it does:** Quantises depth into `steps` flat bands.

**Use case:** Card-style depth separation or stylised depth.

**Inputs:** Matte 1 = depth

**Expects:** raw / data (no colour management)

**Variables:** `steps` (8)

## Notes

Quantises depth into `steps` flat bands — turns a smooth Z pass into discrete **"cards"**.

### Why use it
Cheap 2.5D separation: each band is a constant depth you can pull with `depth_matte` and
treat as its own layer (parallax, per-card grades, a stepped/stylised look). Also handy to
preview how many depth slices a shot really needs.

### Practical notes
- **Depth on Matte 1.** `steps` = number of bands.
- Pair with `depth_matte` (set `zMin`/`zMax` to one band) to extract a single card.
