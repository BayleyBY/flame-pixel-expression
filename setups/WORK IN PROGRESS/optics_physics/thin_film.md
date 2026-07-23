# thin_film

**What it does:** Thin-film interference iridescence: a soap-bubble/oil-slick rainbow whose hue tracks an interference phase that grows with radius and `thickness`; animate `shift` to roll the colours.

**Use case:** Iridescent oil-slick/soap-bubble looks, holographic foil, fuel-rainbow sheens.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `thickness` (1.0), `scale` (0.004), `shift` (animated)

## Notes

**Thin-film interference** — the rainbow you see on a soap bubble, an oil slick, or a fuel
sheen. The light reflecting off the top and bottom of a thin film interferes; the colour that
survives depends on the film's optical thickness, so as thickness changes across the frame the
hue cycles through the spectrum. Here the optical path is faked as a function of **radius**
(DIST) so the bands ring out from the **Centre**.

### How it works
- `phase = dist * scale * thickness + shift`. `fract(phase)` rolls 0→1 repeatedly, and
  `_hue2rgb()` turns that 0..1 into a fully-saturated spectral colour — so each unit of phase
  is one full pass through the rainbow.
- RGB is the spectral colour; **OutMatte is the band intensity** `(sin(phase·2π)+1)/2`, handy
  as a mask to comp the iridescence over something.

### Practical notes
- `scale` sets how tightly the bands ring (try 0.001–0.02); `thickness` multiplies it, so it's
  a second, more "physical" knob (thicker film = more, finer rings).
- **`shift` is the keyframed clock** (0 → 1 over frames 1–100 = one full rainbow cycle) — scrub
  to roll the colours outward. Edit the two keys for speed/length; reverse them to roll inward.
- Tag it Raw/Data-ish — it's a generated look, not scene-linear light. Screen/add it over a
  surface for an oil-slick comp.

### Quick test
Any clip on **Front 1** → **rainbow interference rings from Centre immediately**. Scrub
frames 1–100: the colours roll outward (`shift` is keyframed). Band intensity rides
OutMatte (Matte 1 wired).
