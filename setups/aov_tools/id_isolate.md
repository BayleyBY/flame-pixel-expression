# id_isolate

**What it does:** Grades only the region picked by a mask on Matte 1 (gain + per-channel tint).

**Use case:** Tweak a single object/region selected by an ID or mask pass.

**Inputs:** Front 1 = beauty, Matte 1 = mask

**Expects:** any (mask is data; grades in your working space)

**Variables:** `gain` (1.0), `tintR` (1.0), `tintG` (1.0), `tintB` (1.0)

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
