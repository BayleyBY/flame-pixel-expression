# rays

**What it does:** Radial rays around Centre; `rays` sets the count, `rot` the rotation.

**Use case:** Sunbursts, star/optical flares, radial wipes.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `rays` (8), `rot` (0), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

A **radial sunburst** — `rays` spokes via `atan` around the node's **Centre**.

### Practical notes
- `rays` = number of spokes; `rot` = rotation in **radians**.
- Two colours `aR/aG/aB`→`bR/bG/bB` (default black→white), raw pattern on OutMatte.
- `rot` is a **static** angle — for a spinning version use `spin_rays`.
