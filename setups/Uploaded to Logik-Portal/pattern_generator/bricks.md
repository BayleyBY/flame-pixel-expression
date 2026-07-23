# bricks

**What it does:** Offset brick pattern (`bw`×`bh`), alternate rows shifted half a brick.

**Use case:** Procedural wall/tile texture or a test grid.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `bw` (128), `bh` (64), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

An **offset brick / masonry** pattern — rows of `bw`×`bh` bricks with every other row shifted
half a brick (the `row` formula does the offset).

### Practical notes
- `bw`/`bh` = brick **full** width/height in pixels. Screen-space (anchored to `x`/`y`, not
  Centre).
- Two colours `aR/aG/aB`→`bR/bG/bB` (default black→white); raw pattern on OutMatte.
- Uses: wall/tile mattes, a base mask to drive displacement or per-brick breakup.
