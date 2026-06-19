# depth_fade

**What it does:** Fades colour and alpha to nothing with distance.

**Use case:** Dissolve distant elements; depth-based vignette.

**Inputs:** Front 1 = beauty, Matte 1 = depth

**Expects:** depth raw; beauty scene-linear

**Variables:** `near` (0.0), `far` (1.0)

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
