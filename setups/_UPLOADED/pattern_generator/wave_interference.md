# wave_interference

**What it does:** Ripple-tank interference of two circular point sources (Centre + `srcX` offset); animate `phase` to make the ripples travel.

**Use case:** Caustics/ripple references, sonar-style interference, energy-field FX.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `srcX` (300.0), `phase` (animated), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

A **ripple tank**: two circular point sources dropped into still water, their wavefronts
crossing to make the classic interference lattice (bright where crests meet, dark where a crest
meets a trough).

### How it works
- Source **A** sits at the node **Centre**; source **B** is offset by `srcX` pixels on X. Each
  contributes `cos(k·distance − phase)` where `k = 2π/wavelength` (wavelength baked to 80 px in
  formula `k`), and the two are summed and remapped to 0..1.
- Only **two** sources — the node has no loops, so each source is written out by hand. With the
  two-colour vars eating 6 of 8 slots, only **two** own vars are exposed (`srcX` + `phase`);
  edit the `k` formula to change the ripple wavelength.

### Practical notes
- `srcX` = horizontal separation of the second source (set to 0 to collapse onto a single source
  = plain concentric rings; widen for a finer interference lattice).
- **`phase` is the keyframed clock** (0 → 4π over frames 1–100 = two full ripple cycles) — scrub
  to make the wavefronts travel outward.
- Two colours `aR/aG/aB`→`bR/bG/bB` (default black→white); raw field on OutMatte. Uses: caustic
  refs, energy fields, sonar interference.
