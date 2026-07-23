# id_isolate

**What it does:** Grades only the region picked by a mask on Matte 1 (gain + per-channel tint).

**Use case:** Tweak a single object/region selected by an ID or mask pass.

**Inputs:** Front 1 = beauty, Matte 1 = mask

**Expects:** any (mask is data; grades in your working space)

**Variables:** `gain` (1.0), `tintR` (1.0), `tintG` (1.0), `tintB` (1.0)

## Node dependencies
**Pipeline:** beauty (Front 1) + ID mask (Matte 1) → **this node**

Consumes specific **render AOVs/passes** delivered by your renderer or extracted from EXR layers upstream (a Read/MUX/Channel node). The passes are data/light — keep them in the right space (linear for light math) and wire each to the input named below. The **ID/matte pass goes on Matte 1** to isolate a region of the beauty.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Grades **only the region picked by an ID/mask pass**, leaving everything outside untouched —
`mix(beauty, beauty * tint * gain, mask)`. A masked secondary driven by a render pass instead
of a key.

### How to wire it
- **Front 1 = beauty, Matte 1 = the mask** (an object-ID matte, a Cryptomatte coverage from
  `crypto_pick_*`, or any 0..1 selection).
- Inside the mask the pixels are tinted/exposed; outside, they pass through bit-for-bit.

### Practical notes
- `gain` + `tintR/G/B` are the grade applied inside the mask.
- Feed it the output of `crypto_pick_2rank`/`4rank` to grade a single object with no roto.

### Quick test
Beauty on **Front 1**, ANY high-contrast clip or matte on **Matte 1** (a `radial_ramp`
render works). Set `tintR` 2.0, `tintG` 0.3, `tintB` 0.3 → **the masked region turns hot
red**, everything else passes through untouched. With nothing on Matte 1 the mask reads 0
and the node outputs the beauty bit-for-bit — the classic "it does nothing" trap.
