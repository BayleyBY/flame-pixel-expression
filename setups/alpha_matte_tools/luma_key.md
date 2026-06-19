# luma_key

**What it does:** Soft key on luminance between `lo` and `hi`; result on Result and OutMatte.

**Use case:** Pull a quick matte from brightness (skies, highlights, blacks) without a full keyer.

**Inputs:** Front 1

**Expects:** scene-linear (Rec.709 luma weights); approximate elsewhere

**Variables:** `lo` (0.3), `hi` (0.7)

## Notes

A **soft luminance key**: `smoothstep(lo, hi, luma)` on Rec.709 luma, written to **RGB and
the Matte** (so you see the key on Result and get OutMatte at once).

### Controls
- `lo` = the luma where the key starts (black point), `hi` = where it reaches full (white
  point). The gap between them is the softness — widen for a gentle ramp, narrow for a hard
  key. Invert by swapping `lo` and `hi`.

### Practical notes
- **Luma weights are Rec.709** — exact in scene-linear; in a display/log space it's an
  approximation (still useful, just not photometric).
- Quick pulls: skies/highlights (high `lo`/`hi`), shadows (low, inverted), a self-matte for a
  glow or a brightness-driven grade.
