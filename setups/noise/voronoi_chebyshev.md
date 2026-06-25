# voronoi_chebyshev

**What it does:** Voronoi cells under the Chebyshev (chessboard) metric — square cells. `scale`, `seed`, `jitter` as voronoi.

**Use case:** Faceted/chunky crystal cells, tiled square-cell texture.

**Inputs:** none (generator)

**Expects:** any — generates data/values

**Variables:** `scale` (80), `seed` (0.0), `jitter` (1.0)

## Notes

`voronoi` with the **Chebyshev (chessboard) metric** — distance is `max(|dx|,|dy|)`, giving
**axis-aligned square cells**. A faceted, chunky-crystal look distinct from the round Euclidean
cells and the diamond Manhattan ones. Same controls as `voronoi`. Grayscale generator.
