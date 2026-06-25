# linear_to_cineon

**What it does:** Linear → Kodak Cineon/DPX log (inverse of `cineon_to_linear`). Same `blackPt`/`whitePt`/`gammaC` controls.

**Use case:** Re-encode to Cineon log for a film-log delivery or to round-trip a DPX pipeline.

**Inputs:** Front 1 (scene-linear)

**Expects:** scene-linear in → Cineon/DPX log out

**Variables:** `blackPt` (95.0), `whitePt` (685.0), `gammaC` (0.6)

## Notes

The inverse of `cineon_to_linear` — **scene-linear → Kodak Cineon/DPX log**. Use the **same**
`blackPt` / `whitePt` / `gammaC` as the decode so the round-trip is exact. GLSL has no `log10`,
so it's computed as `log()·0.4342944819`; the argument is `max()`-guarded against ≤0.

Use it to re-encode for a DPX/film-log delivery, or as the closing half of a
`cineon_to_linear` … `linear_to_cineon` bracket. **Expects** scene-linear in, Cineon-log out.
