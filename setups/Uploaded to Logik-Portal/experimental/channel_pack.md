# channel_pack

**What it does:** Packs FOUR single-channel signals: red = Matte 1, green = Matte 2, blue = Front 1 luma (Result), plus Front 2 luma on OutMatte.

**Use case:** Ferry four mattes/masks through a comp on the Result + OutMatte wire pair; unpack with channel_unpack.

**Inputs:** Matte 1 + Matte 2 + Front 1 + Front 2

**Expects:** any (the four packed signals are data — tag both outputs Raw/Data)

_No variables._

## Node dependencies
**Pipeline:** Matte 1 + Matte 2 + Front 1 + Front 2 → **this node** → `channel_unpack`

Ferries FOUR single-channel signals on the Result + OutMatte wire pair (red = Matte 1, green = Matte 2, blue = Front 1 luma; OutMatte = Front 2 luma — the Result socket is RGB-only, so channel 4 rides the OutMatte). Useless without its partner **`channel_unpack`** at the far end to recover them.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

A **4-into-1-node muxer**: stuff four unrelated single-channel signals into one node's outputs
so they ride a wire *pair* (Result + OutMatte) through a comp, then split them back out with
`channel_unpack` at the far end. Saves wiring and keeps related masks travelling together.

### The packing
- **red** = Matte 1, **green** = Matte 2, **blue** = Front 1 **luma** (Rec.709) — all on the
  **Result** output. **Channel 4** = Front 2 **luma**, on the **OutMatte** output.
- The lumas are used rather than raw channels so those slots work whether the Front is a
  colour plate (carries its brightness/key) or a grayscale mask; swap for `b1`/`b2` in
  `generate_setups.py` if you'd rather ferry a literal single channel.

### The topology (why 4 needs two wires)
The **Result socket is RGB — three channels** — so the fourth signal has to leave through the
**OutMatte** output: run BOTH wires to the far end (Result → `channel_unpack` Front 1,
OutMatte → its Matte 1). That second wire is no extra cost at the destination —
`channel_unpack`'s own OutMatte needs *something* on Matte 1 anyway, and now that wire
carries real data. Pack-side OutMatte always renders because Matte 1 is a packed input by
construction. (Same two-outputs-at-once trick as `dual_output_depth`.)

### How to pack four *mattes*
The node has only **two Matte sockets** (`m1`, `m2`), so signals 3 and 4 come in on the
Fronts. For a grayscale matte `r = g = b`, so its **luma equals the matte value** — recovered
exactly. Wiring: matte A → Matte 1, B → Matte 2, C → Front 1, D → Front 2. Only three to
ferry? Leave Front 2 unconnected — channels 1–3 are unchanged from the old 3-wide pack.

### Practical notes
- The packed channels are **data, not colour** — tag **both outputs** Raw/Data so colour
  management doesn't bend the values before you unpack them.
- Unpack partner: **`channel_unpack`** (`pick` 0–3 routes any packed channel to its OutMatte).
  Keep both ends in the same space/data tag.

### Quick test
Wire FOUR different greyscale clips/mattes: A → **Matte 1**, B → **Matte 2**, C → **Front 1**,
D → **Front 2**. The **Result** reads as a false-colour RGB (A in red, B in green, C's luma in
blue) and the **OutMatte** shows D's luma. Nothing on Front 2 → OutMatte reads black — that's
the empty 4th slot, not a bug. Confirm the round trip with `channel_unpack` (Result → its
Front 1, OutMatte → its Matte 1): `pick` 0/1/2/3 must reproduce A/B/C/D on its OutMatte.
