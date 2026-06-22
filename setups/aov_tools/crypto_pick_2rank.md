# crypto_pick_2rank

**What it does:** Extracts a matte for object hash `id` from one Cryptomatte layer (2 ranks).

**Use case:** Pull a Cryptomatte selection on simpler/harder edges.

**Inputs:** Front 1 + Matte 1 (one crypto layer)

**Expects:** raw / data (no colour management)

**Variables:** `id` (0.0), `tol` (1e-05)

## Node dependencies
**Pipeline:** crypto value (Front 1) + crypto coverage (Matte 1) → **this node**

Needs **Cryptomatte rank layers** extracted upstream (a Cryptomatte/Channel node): the rank's value on Front 1, its coverage on Matte 1. It picks the object hash `id` from those ranks — no extracted ranks, no matte.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Extracts a coverage **matte for one object** from a single Cryptomatte layer (2 ranks), by
matching its `id` hash. The no-roto way to pull any object the renderer tagged.

### Setup (important)
- **Shuffle the crypto layer** so Front 1 = `(hash0, coverage0, hash1)` and Matte 1 =
  `coverage1`. The expression reads those exact slots.
- **`id`** = the object's float32 hash from the Cryptomatte **manifest** (the metadata
  list of name→hash). `tol` = relative match tolerance (leave tiny).
- **The crypto pass MUST be read raw** — no resize, no filtering, no colour management.
  Cryptomatte stores object hashes *as pixel values*; any resample or grade corrupts them and
  the matte falls apart. This is the #1 cause of a broken crypto pull.

### Practical notes
- 2 ranks is enough for solid objects; switch to **`crypto_pick_4rank`** when edges fringe
  (hair, motion blur, semi-transparency need more coverage ranks).
- Feed the result into `id_isolate` (or any matte input) to grade that object.
