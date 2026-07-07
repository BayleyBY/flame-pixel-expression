# voronoi_edges

**What it does:** Cellular crack network — the F2−F1 distance (nearest vs second-nearest feature) drawn as cell-wall lines. `scale`/`jitter`/`seed` as voronoi, `edgeW` crack width.

**Use case:** Cracked mud, shattered glass, dried-paint, cell membranes; crack/edge masks.

**Inputs:** none (generator)

**Expects:** any — generates data/values

**Variables:** `scale` (80), `seed` (0.0), `jitter` (1.0), `edgeW` (0.08)

## Notes

The **cell-wall / crack** complement to `voronoi`: instead of the cells, it draws the **borders**
between them. At each pixel it finds the nearest feature point (**F1**) and the second-nearest
(**F2**); the two are equal exactly on a cell boundary, so `F2 − F1` is ~0 there and large in cell
interiors. The output is `1 − smoothstep(0, edgeW, F2−F1)` — bright cracks on a dark field.

### How F2 is found without state
The node can't sort, so F2 uses a trick: take the 9-way min for F1, then take the min again over
the same 9 distances but with whichever one equals F1 **pushed up by 1000** (`d + step(d,f1)·1000`)
— leaving the second-smallest as the new min. F1 is referenced **by name**, so there's no
expression blow-up. (Verified correct over 100k random cases.)

### Controls
`scale` cell size, `seed` pattern (keyframe to drift), `jitter` 0=regular grid…1=random points,
`edgeW` crack thickness. Grayscale (RGB + Matte), like `voronoi`.
