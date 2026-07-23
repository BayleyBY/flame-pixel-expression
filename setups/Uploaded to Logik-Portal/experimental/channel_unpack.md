# channel_unpack

**What it does:** Passes a packed RGB (from channel_pack) through unchanged and routes one channel to the Matte: `pick` 0/1/2/3 selects r1/g1/b1/m1.

**Use case:** Recover a packed mask and send it to OutMatte at the destination; pairs with channel_pack.

**Inputs:** Front 1 (the packed RGB) + Matte 1 (the ferried 4th channel)

**Expects:** any (operates on the channels as data)

**Variables:** `pick` (0)

## Node dependencies
**Pipeline:** `channel_pack` Result (Front 1) + its OutMatte (Matte 1) → **this node**

The other half of the pair: takes the **packed RGB** on Front 1 and the ferried fourth channel on Matte 1, and routes one to OutMatte (`pick` = 0/1/2/3 selects r/g/b/m1).

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

The **demuxer** for `channel_pack` (or any packed RGB). It passes the full RGB through
untouched and additionally **routes one chosen channel to the OutMatte**, so you can recover a
ferried mask and feed it straight to a downstream matte input.

### Wiring
`channel_pack`'s **Result → Front 1** (channels 1–3) and its **OutMatte → Matte 1**
(channel 4). Both wires matter: Matte 1 carries the ferried fourth signal AND satisfies the
node's OutMatte-needs-Matte-1 rule in one go.

### Picking the channel
`pick` selects which channel goes to the Matte: **0 = red, 1 = green, 2 = blue, 3 = the
Matte 1 input** (the pack's fourth channel). It's a branchless `step`/`mix` select (no arrays
in GLSL): `step(0.5, pick)` switches r→g, `step(1.5, pick)` switches that→b, and
`step(2.5, pick)` switches that→m1.

### Practical notes
- RGB out = RGB in, so this is non-destructive on the image; it only *derives* the Matte.
- Ferrying only three channels (no Front 2 on the pack)? Wire the packed clip itself to
  Matte 1 as before — `pick` 3 then just reads that clip's matte.
- Pairs with **`channel_pack`**; keep the Raw/Data tag consistent across the pair.

### Quick test
Feed `channel_pack`'s **Result → Front 1** and its **OutMatte → Matte 1** (that wire is the
ferried 4th channel AND what makes this node's OutMatte render). RGB passes through
untouched; step `pick` through 0 → 1 → 2 → 3 and watch OutMatte flip between the four packed
signals (3 = the Matte 1 input). With `pick` 3 and nothing on Matte 1 the matte reads
black — wire the 4th channel (or any clip) in.
