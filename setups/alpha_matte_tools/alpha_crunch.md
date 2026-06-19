# alpha_crunch

**What it does:** Sets matte pixels below `thresh` to 0, passing the rest through.

**Use case:** Harden a soft or dirty matte and drop low-value noise to fully transparent.

**Inputs:** Matte 1

**Expects:** any (data / value op)

**Variables:** `thresh` (1.0)

## Notes

A **hard floor on the matte**: any alpha below `thresh` drops to 0; the rest keeps its value.
RGB passes through untouched (it only rewrites alpha).

### The default keeps only solids
With `thresh` 1.0, *everything below fully-opaque* goes to 0 — so only pixels that were
exactly 1.0 survive. That's a "core / solids only" crunch: it strips semi-transparent edges,
spill, and soft fringe. **Lower `thresh`** to keep more of the partial alpha.

### Practical notes
- Matte on **Matte 1**. Use before a hard composite to kill a noisy/feathered edge, or to
  pull a clean core out of a soft matte. Pair with `fill_alpha` (its rough inverse) and
  `matte_grade` to reshape density.
