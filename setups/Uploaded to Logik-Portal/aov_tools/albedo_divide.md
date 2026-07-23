# albedo_divide

**What it does:** Beauty ÷ albedo → lighting (guards divide-by-zero).

**Use case:** Extract the lighting/shadow pass to regrade independently.

**Inputs:** Front 1 = beauty, Front 2 = albedo

**Expects:** scene-linear

_No variables._

## Node dependencies
**Pipeline:** beauty (Front 1) + albedo (Front 2) → **this node**

Consumes specific **render AOVs/passes** delivered by your renderer or extracted from EXR layers upstream (a Read/MUX/Channel node). The passes are data/light — keep them in the right space (linear for light math) and wire each to the input named below. De-lights: beauty ÷ albedo → lighting.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Divides the beauty by its **albedo** to recover the **lighting alone** (illumination,
de-textured). Half of the de-light / re-light pair with `albedo_multiply`.

### Why use it
Working on the lighting without the texture in the way: **denoise** or **grade** or **regrain**
the smooth lighting, then multiply the albedo back in with `albedo_multiply`. Also the way to
swap a texture — divide out the old albedo, multiply in a new one.

### Practical notes
- **Front 1 = beauty, Front 2 = albedo.** Output is beauty ÷ albedo per channel.
- **Divide-by-zero is guarded** — pixels where albedo is 0 come out black (there's no
  lighting info to recover there).
- Keep everything **scene-linear**.
