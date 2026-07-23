# voronoi_manhattan

**What it does:** Voronoi cells under the Manhattan (taxicab) metric — diamond/blocky cells. `scale`, `seed`, `jitter` as voronoi.

**Use case:** Circuit-board / pixel-crystal cellular texture, blocky shatter masks.

**Inputs:** none (generator)

**Expects:** any — generates data/values

**Variables:** `scale` (80), `seed` (0.0), `jitter` (1.0)

## Notes

`voronoi` with the **Manhattan (taxicab) metric** — distance is `|dx|+|dy|` instead of Euclidean
`length`, which turns the round-ish cells into **diamonds/blocks** with straight 45° walls. Reads
as circuit-board / pixel-crystal. Same `scale`/`seed`/`jitter` controls as `voronoi`; keyframe
`seed` to drift. Grayscale generator.
