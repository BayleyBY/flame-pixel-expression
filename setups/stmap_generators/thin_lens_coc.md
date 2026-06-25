# thin_lens_coc

**What it does:** Physically-based circle-of-confusion from depth on Matte 1 via the thin-lens equation (`focalLen`, `fStop`, `focusDist`); near/far blur asymmetrically and far CoC saturates. Output feeds a Defocus.

**Use case:** Drive a downstream variable-blur/Defocus with real lens DoF — proper foreground/background falloff instead of the symmetric `coc_from_depth` ramp.

**Inputs:** Matte 1 (depth pass)

**Expects:** depth raw in (Matte 1); outputs a 0..maxBlur circle-of-confusion map (Raw/Data)

**Variables:** `focalLen` (0.05), `fStop` (2.8), `focusDist` (5.0), `blurScale` (1000.0), `maxBlur` (1.0)

## Node dependencies
**Pipeline:** depth pass (Matte 1) → **this node** → variable-blur / Defocus

Emits a per-pixel **blur amount** (0..1), not a blurred image — the node can't gather neighbours. Feed it into a downstream **variable-blur / Defocus** node as its blur-amount (matte) input, with the plate on that node's front. Output is data — tag it Raw/Data. A **physical** circle-of-confusion from the depth pass on Matte 1 via the thin-lens equation (`focalLen`, `fStop`, `focusDist`) — unlike `coc_from_depth`'s symmetric ramp, foreground and background blur differently and far CoC saturates. Set `blurScale`/`maxBlur` to map the physical CoC onto your Defocus node's amount range.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

**A real lens blur can't happen in this node** — defocus is a *gather* (each output pixel mixes a
disc of its neighbours, shaped by the aperture), and this node only ever sees the **current
pixel**. So the honest, useful job here is to compute the **circle-of-confusion (CoC)** — the
per-pixel blur *radius* — and hand it to a downstream **Defocus / variable-blur** that does the
actual gather. This is the same split as `coc_from_depth`, but with a **physically correct**
model instead of a linear ramp.

### The model
From the thin-lens equation, CoC diameter ∝ `(f²/N) · |S2 − S1| / (S2 · (S1 − f))`, where
`f` = `focalLen`, `N` = `fStop`, `S1` = `focusDist`, and `S2` = the **depth on Matte 1**. Two
behaviours fall out of this that a linear ramp (`coc_from_depth`) gets wrong:
- **Asymmetry** — for the same metric distance from focus, the **background blurs more than the
  foreground**. The `S2` in the denominator is what does it.
- **Far-CoC ceiling** — as depth → ∞ the CoC approaches a constant (`f²/(N·(S1−f))`), so distant
  objects don't blur infinitely. Foreground CoC, by contrast, keeps growing as `S2` → 0.

### Controls & units
- `focalLen`, `focusDist`, and the **depth pass must share units**. If depth is in metres, use a
  metre focal length (50 mm → `0.05`). The *relative* DoF look is unit-stable; absolute scale is
  set by `blurScale`.
- `fStop` — aperture. Lower = shallower DoF = more blur (CoC ∝ 1/N).
- `blurScale` — maps the physical CoC onto your Defocus node's pixel-amount range.
- `maxBlur` — clamps the output (stops a near-camera pixel from asking for an enormous kernel).

### Wiring (required)
**depth → Matte 1 → this node → Defocus's blur-amount input**, plate on the Defocus front.
Output is data — **tag it Raw/Data**. Keyframe `focusDist` to rack focus.

### When to use which
`coc_from_depth` = quick, symmetric, art-directed. **`thin_lens_coc` = physically plausible lens
DoF** when you want the background/foreground asymmetry and far falloff to read as a real lens.
