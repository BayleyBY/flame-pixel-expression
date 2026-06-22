# channel_unpack

**What it does:** Passes a packed RGB (from channel_pack) through unchanged and routes one channel to the Matte: `pick` 0/1/2 selects r1/g1/b1.

**Use case:** Recover a packed mask and send it to OutMatte at the destination; pairs with channel_pack.

**Inputs:** Front 1 (the packed RGB)

**Expects:** any (operates on the channels as data)

**Variables:** `pick` (0)

## Node dependencies
**Pipeline:** `channel_pack` output (Front 1) → **this node**

The other half of the pair: takes a **packed RGB** (from `channel_pack`) on Front 1 and routes one channel to OutMatte (`pick` = 0/1/2 selects r/g/b).

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

The **demuxer** for `channel_pack` (or any packed RGB). It passes the full RGB through
untouched and additionally **routes one chosen channel to the OutMatte**, so you can recover a
ferried mask and feed it straight to a downstream matte input.

### Picking the channel
`pick` selects which channel goes to the Matte: **0 = red, 1 = green, 2 = blue**. It's a
branchless `step`/`mix` select (no arrays in GLSL): `step(0.5, pick)` switches r→g, then
`step(1.5, pick)` switches that→b.

### Practical notes
- RGB out = RGB in, so this is non-destructive on the image; it only *derives* the Matte.
- **OutMatte only renders when Matte 1 is connected** — the Matte expression here reads Front 1,
  but Flame still requires Matte 1 wired for the OutMatte to appear. Connect anything (even the
  packed clip) to Matte 1.
- Pairs with **`channel_pack`**; keep the Raw/Data tag consistent across the pair.
