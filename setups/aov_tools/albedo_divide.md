# albedo_divide

**What it does:** Beauty ÷ albedo → lighting (guards divide-by-zero).

**Use case:** Extract the lighting/shadow pass to regrade independently.

**Inputs:** Front 1 = beauty, Front 2 = albedo

**Expects:** scene-linear

_No variables._

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
