# sdf_ring

**What it does:** Annulus (ring) matte; `radius` and `thickness`.

**Use case:** Circular outlines, target/HUD shapes, halos.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `radius` (200), `thickness` (20), `soft` (2.0)

## Notes

An **annulus (ring) matte** — the outline primitive of the SDF set. Centred on **Centre**.

### Practical notes
- `radius` = ring radius (to the centre of the band); `thickness` = half the band width, so
  the ring spans `radius ± thickness`. `soft` = edge feather.
- Use for circular outlines, target/HUD reticles, halos. For a filled disc use `sdf_circle`.
