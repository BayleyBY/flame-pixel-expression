# channel_pack

**What it does:** Packs three single-channel signals into one RGB: red = Matte 1, green = Matte 2, blue = Front 1 luma; matte = 1.

**Use case:** Ferry three mattes/masks down a single connection through a comp; unpack later with channel_unpack.

**Inputs:** Matte 1 + Matte 2 + Front 1

**Expects:** any (the three packed signals are data — tag the output Raw/Data)

_No variables._

## Node dependencies
**Pipeline:** Matte 1 + Matte 2 + Front 1 → **this node** → `channel_unpack`

Ferries three single-channel signals down **one** RGB connection (red = Matte 1, green = Matte 2, blue = Front 1 luma). Useless without its partner **`channel_unpack`** at the far end to recover them.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

A **3-into-1 muxer**: stuff three unrelated single-channel signals into one RGB so they ride a
single connection through a comp, then split them back out with `channel_unpack` at the far
end. Saves wiring and keeps related masks travelling together.

### The packing
- **red** = Matte 1, **green** = Matte 2, **blue** = Front 1 **luma** (Rec.709). Matte = 1.
- Blue is luma rather than a raw channel so the third slot can carry a brightness/key signal;
  swap it for `b1` in `generate_setups.py` if you'd rather ferry a literal blue channel.

### Why blue is a luma, and how to pack three *mattes*
The node has only **two Matte sockets** (`m1`, `m2`) — there is no third Matte input — so the
third packed signal **must come from a Front input**. Blue reads **Front 1's luma** so that slot
works whether Front 1 is a colour plate (carries its brightness/key) or a grayscale mask.
- **Yes, you can pack three mattes:** feed your third matte into **Front 1**. For a grayscale
  matte `r1 = g1 = b1`, so its **luma equals the matte value** — `channel_unpack` recovers it
  exactly. No change needed; the wiring is just `m1`, `m2`, and the third matte on **Front 1**.
- Only switch blue to a raw channel (`r1`/`b1`) if your third signal lives in a **single channel
  of a colour** Front 1 (where luma would blend it with the other two channels).

### Practical notes
- The packed channels are **data, not colour** — tag the output **Raw/Data** so colour
  management doesn't bend the values before you unpack them.
- Unpack partner: **`channel_unpack`** (route any packed channel to a Matte). Keep both ends in
  the same space/data tag.
