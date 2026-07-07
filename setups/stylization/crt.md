# crt

**What it does:** CRT/VHS look: scanlines, an RGB phosphor-triad mask, a vignette, and an animated rolling bright bar (keyframe `roll`) multiplied over Front 1.

**Use case:** Retro-monitor / broadcast-glitch stylisation, in-screen TV inserts, music-video grunge.

**Inputs:** Front 1 (+ Matte 1 to pass alpha)

**Expects:** display-referred / working image (look applied multiplicatively)

**Variables:** `scanDepth` (0.3), `maskDepth` (0.3), `vignette` (0.4), `scanFreq` (1.5), `scale` (3.0), `roll` (animated)

## Notes

A stacked **CRT / VHS** stylisation applied multiplicatively over Front 1: horizontal
scanlines, an RGB **phosphor-triad** mask, a corner **vignette**, and a slow **rolling
bright bar** like a mis-synced analogue signal. Every piece is dialable so you can go from a
subtle "this is on a monitor" cue to full retro grunge.

### How it works
- **Scanlines** — `tone` darkens every other line via `sin(y * scanFreq)`, depth set by
  `scanDepth`.
- **Phosphor mask** — `floor(x / scale) mod 3` selects which of R/G/B stays bright in each
  column; the other two are knocked back by `maskDepth`, giving the characteristic
  colour-fringed vertical stripes. **`scale`** sets the stripe width in pixels (triad =
  `3 * scale` px) — raise it for a coarse, clearly-visible phosphor grid; `scale = 1` is the
  native 1-pixel-per-stripe look.
- **Vignette** — radial darkening from frame centre, strength `vignette`.
- **Rolling bar** — a soft bright band whose vertical position is the **keyframed** `roll`
  variable (0..1 = one full pass up the frame). Animate it for the drifting-hold-bar look.

### Controls
- `scanDepth` / `maskDepth` / `vignette` — 0..1 strength of each effect (set any to 0 to
  disable it).
- `scanFreq` — scanline pitch (higher = finer lines).
- `scale` — phosphor-stripe width in px (default 3). `1` = the original hairline mask; larger =
  chunkier, more obvious RGB stripes.
- `roll` — **keyframe this** 0->1 over your shot to make the bright bar crawl. Default is
  one pass over frames 1-100; rescale to taste.

### Notes
- Expects a **display-referred / working image** — the effect multiplies the existing pixel
  values, so it reads correctly on a graded/display look.
- Connect **Matte 1** if you want the alpha passed through (the RGB look ignores it).
- For maximum authenticity, follow with a slight horizontal blur + chromatic-aberration
  offset in a separate node (this node can't sample neighbours).
