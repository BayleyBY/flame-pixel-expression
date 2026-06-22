# crypto_pick_4rank

**What it does:** Extracts a matte for object hash `id` across two crypto layers (4 ranks).

**Use case:** Pull a Cryptomatte selection with cleaner anti-aliased edges.

**Inputs:** Front 1 + Matte 1 + Front 2 + Matte 2

**Expects:** raw / data (no colour management)

**Variables:** `id` (0.0), `tol` (1e-05)

## Node dependencies
**Pipeline:** crypto ranks (Front 1 + Matte 1, Front 2 + Matte 2) → **this node**

Needs **two Cryptomatte rank pairs** extracted upstream — value/coverage on Front 1/Matte 1 and Front 2/Matte 2 — for a cleaner edge across four ranks.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Same object-hash pick as `crypto_pick_2rank`, but reads **two** Cryptomatte layers (4 ranks)
and sums their coverage — for clean anti-aliased and overlapping edges.

### Setup
- **Front 1 / Matte 1 = layer A** `(hash0, cov0, hash1)` + `cov1`; **Front 2 / Matte 2 =
  layer B** `(hash2, cov2, hash3)` + `cov3` (two Shuffles).
- `id` and `tol` work exactly as in the 2-rank version.

### When to use it over 2-rank
Reach for 4-rank when a 2-rank pull **fringes**: fine hair, heavy motion blur, or
semi-transparent edges where a single pixel's coverage is split across more than two objects.
More ranks = more of that partial coverage recovered.

### Practical notes
- **Read the crypto passes raw** — no resize/filter/colour management (see `crypto_pick_2rank`;
  same hard requirement, doubly so across two layers).
- Output goes straight into `id_isolate` or any matte input.
