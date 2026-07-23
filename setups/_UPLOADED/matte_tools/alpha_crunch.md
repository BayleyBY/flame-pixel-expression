# alpha_crunch

**What it does:** Sets matte pixels below `thresh` to 0, passing the rest through.

**Use case:** Harden a soft or dirty matte and drop low-value noise to fully transparent.

**Inputs:** Matte 1

**Expects:** any (data / value op)

**Variables:** `thresh` (0.1)

## Notes

A **hard floor on the matte**: any alpha below `thresh` drops to 0; the rest keeps its value.
RGB passes through untouched (it only rewrites alpha).

### The default crushes the noise floor
With `thresh` 0.1, faint low-level alpha (grain lift, compression haze, stray speckle) drops
to 0 while real edges and solids pass through. **Raise `thresh`** to bite deeper — all the
way to 1.0 for a "core / solids only" crunch that keeps just the fully-opaque pixels and
strips every semi-transparent edge.

### Practical notes
- Matte on **Matte 1**. Use before a hard composite to kill a noisy/feathered edge, or to
  pull a clean core out of a soft matte. Pair with `fill_alpha` (its rough inverse) and
  `matte_grade` to reshape density.
