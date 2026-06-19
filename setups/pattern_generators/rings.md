# rings

**What it does:** Concentric sine rings around Centre, spacing set by `freq`.

**Use case:** Test/alignment patterns, ripple textures, radial guides.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `freq` (0.05), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

**Concentric rings** (`sin` of distance) around the node's **Centre**.

### Practical notes
- `freq` sets ring spacing — it's **small** (0.05 default), so hold **Space + Drag** for
  hundredths when tuning.
- Two colours: `aR/aG/aB` (pattern 0) → `bR/bG/bB` (pattern 1), default black→white; OutMatte
  carries the raw pattern. (See `radial_ramp` notes.)
- For rings that **expand over time**, use `pulse_rings` instead.
