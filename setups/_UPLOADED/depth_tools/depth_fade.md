# depth_fade

**What it does:** Fades colour and alpha to nothing with distance.

**Use case:** Dissolve distant elements; depth-based vignette.

**Inputs:** Front 1 = beauty, Matte 1 = depth

**Expects:** depth raw; beauty scene-linear

**Variables:** `near` (0.0), `far` (1.0)

## Node dependencies
**Pipeline:** beauty (Front 1) + depth pass (Matte 1) → **this node**

Reads the **Z/depth pass on Matte 1** (the library convention — `m1`). Raw Z is in scene units, so set the normalising range to your near/far. No depth on Matte 1 = no useful result (input wiring is never saved in the setup file — re-wire it in Batch every time). Also needs the **beauty on Front 1**.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Fades the beauty's **colour and alpha together** to nothing with distance — a premultiplied
depth dissolve, so distant pixels genuinely disappear rather than just darken.

### depth_fade vs depth_fog
`depth_fog` pushes far pixels toward a colour but keeps them opaque; `depth_fade` takes them
to transparent. Use fade when the element needs to **vanish into** whatever's behind it
(dissolve a far crowd, taper a particle sim); use fog for haze/air.

### Practical notes
- **Front 1 = beauty, Matte 1 = depth.** `near`/`far` set the fade range.
- Because alpha fades too, the result composites correctly over a background — drop it
  straight into the comp.
