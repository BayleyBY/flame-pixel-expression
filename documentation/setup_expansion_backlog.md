# Setup expansion backlog

Curated ideas for new Pixel Expression setups, beyond the current 112. Every item is
**strictly current-pixel** (no neighbour gather), fits **8 scalars + 4 vec formulas**, and is
**not** a duplicate of an existing setup. Graded by value-vs-effort into tiers. "Gap" = the hole
in the current library it fills.

Source: synthesized from two research threads (constraint-fit GLSL effects; per-pixel VFX/AOV
ops) + the Nuke-collection cheatsheet, 2026-06-25.

Status legend: ☐ not started · ▶ in progress · ☑ done (in generator + Flame-compile-checked)

---

## Tier 1 — build first (high value, low effort, no constraint risk)

Mappers and pure-builtin utilities that upgrade every scalar field already in the library.

- ☑ **cosine_palette** — map any scalar (luma / depth on m1 / a pattern) to an IQ cosine
  gradient (heatmap, thermal LUT, false-colour regrade). `col = a + b*cos(2π*(c*t+d))` with
  a/b/c/d baked as vec3 **literals** (don't spend var slots). Inputs: any. Expects: any/data.
  Gap: no scalar→colour mapper exists.
- ☑ **false_color_exposure** — ARRI/RED-style exposure monitoring; luma into IRE bands
  (purple→green-18%→red-clip). `_LUMA` then a cascade of `step`/`mix` into ~6–7 bands.
  Inputs: Front1. Expects: scene-linear. Gap: zebra is a stripe only, no false-colour ramp.
- ☑ **contour_lines** — topographic iso-lines from any scalar (luma/depth/height); map look,
  depth inspector. `f=fract(v*N); line=smoothstep(0,w,f)*smoothstep(0,w,1-f)` (fixed `w`, no
  fwidth). Inputs: any. Expects: any. Gap: no contour/iso extractor.
- ☑ **uv_test_chart** — combined UV/lens calibration chart: UV colour ramp + grid + crosshair
  + rings, to check an STMap/lens. `vec3(uv,.5)` + `step(.98,fract(uv*N))` grid + centre cross.
  Inputs: none. Expects: data. Gap: only bare gradients exist.
- ☑ **st_uv_map_inspector** (was stmap_qc_overlay) — QC an ST/UV map: tint where UV leaves 0..1, mark the 0.5 seam,
  checker from UV values. `oob=step(1.,max(r1,g1))+step(r1*g1,0.)`; checker
  `mod(floor(r1*N)+floor(g1*N),2)`. Inputs: Front1=STmap. Expects: data.
  Depends: pairs with the ST-map generators. Gap: nothing QCs them.
- ☑ **lens_vignette** — physically-flavoured cos⁴ vignette / natural lens darkening.
  `v=pow(cos(atan(r/f)),4.)` or `pow(1-k*r*r,p)`, multiply Front. Inputs: Front1.
  Expects: scene-linear. Gap: only a radial *ramp* exists, not an optical vignette.
- ☑ **point_grid** — dot/point lattice generator (classic Nuke `fmod(x,ox)==0 &&
  fmod(y,oy)==0`). `step` near grid intersections, AA via `smoothstep`. Inputs: none.
  Expects: any. Gap: have checker/bricks, no dot grid.
- ☑ **zone_plate** — Newton's-rings / `sin(r²)` test target, denser outward, moiré bait.
  `0.5+0.5*sin(k*dot(p,p))`. Inputs: none. Expects: any. Gap: rings are linear-spaced (r),
  not r².

---

## Tier 2 — strong comp tools (low risk, clear use)

_Built 2026-06-25: 16 setups (log curves as directional pairs like srgb). 137 total, 0 errors, 0 GLSL errors; log-curve round-trips numerically verified._

### Colour science / log curves (encode↔decode pairs, like srgb↔linear)
- ☑ **cineon_log ↔ linear** — film-log curve (Nuke Log2Lin); direction toggle. Guard `pow` of
  negatives. Inputs: Front1. Expects: any (defines the transform).
- ☑ **logc_to_linear** (ARRI LogC) and ☑ **acescct ↔ linear** — piecewise: linear toe below a
  breakpoint, log above. Separate setups (different constants). The two log encodings artists
  hit most after Cineon.
- ☑ **saturation_by_luma** — desat shadows *or* highlights selectively:
  `satAmt=mix(satLo,satHi,smoothstep(lo,hi,L))`. Reuses `_LUMA`. Expects: scene-linear.
- ☑ **highlight_desaturate** — collapse chroma toward white above a threshold; fixes electric
  CG speculars / over-sat skies. Expects: scene-linear.
- ☑ **hue_preserving_clip** — clamp to a ceiling by scaling all channels equally (no per-channel
  hue twist). Note in docs how it differs from `gamut_clip`. Expects: any.

### Matte math (no gather)
- ☑ **garbage_gradient_matte** — positioned/rotated linear gradient card to cut a region without
  roto: `d=(x-cx)cosθ+(y-cy)sinθ; smoothstep(-w,w,d)`. Also gives the missing **linear/axial
  angled gradient** generator. Inputs: none. Expects: data.
- ☑ **holdout_matte** — `clamp(m1 - m1*m2*amount,0,1)`, multiplicative "subtract the occluder".
  Distinguish from `matte_subtract`. Inputs: Matte1, Matte2. Expects: data.
- ☑ **matte_screen_multiply** — soft optical combine `mix(a*b, a+b-a*b, mode)`; softer cousin of
  the min/max and/or. Inputs: Matte1, Matte2. Expects: data.
- ☑ **matte_falloff_ramp** — feather an already-soft matte via `smoothstep(lo,hi,m1)`. Caveat:
  remaps existing partial-coverage, can't create new edge width (no blur). Inputs: Matte1.

### QC / diagnostics
- ☑ **negative_pixel_highlighter** — *flags* sub-zero pixels loudly (companion to
  `aov_clamp_negative`, which fixes them). Inputs: Front1. Expects: scene-linear.
- ☑ **clip_highlighter** — per-channel over-white / under-black markers (solid, threshold-driven;
  distinct from the zebra stripe). Inputs: Front1. Expects: any.
- ☑ **zone_system_posterize** — quantize luma into 11 photographic zones, optional Zone-V tint;
  exposure-distribution QC + a look. Inputs: Front1. Expects: scene-linear.

---

## Tier 3 — technical-pass (AOV) tools

_Built 2026-06-25: Tier 3 = 5 AOV/technical-pass tools; Tier 4 = 13 setups (voronoi_metric_variants → `voronoi_manhattan`+`voronoi_chebyshev`; wood_marble → `wood_grain`+`marble`; waves → `wave_bounce`/`wave_blip`/`wave_parabolic`). voronoi_edges F1/F2 trick + smooth-min numerically verified. 155 total, 0 errors, 0 GLSL errors._

- ☑ **motion_vector_visualize** — 2D velocity pass (R=u,G=v) → hue=direction, value=magnitude.
  Reuses `_hue2rgb`. Inputs: Front1. Expects: raw-data.
- ☑ **motion_vector_normalize** — pack/unpack signed vectors to 0..1; encode↔decode pair.
  Res-dependent — document. Inputs: Front1. Expects: raw-data.
- ☑ **normal_renormalize** — unit-length a normal pass after resize/lerp + optional green flip
  (OpenGL↔DirectX). Epsilon-guard the divide. Inputs: Front1. Expects: raw-data.
- ☑ **normal_to_facing** — facing/rim ratio from a *view-space* normal pass (you only have
  facing-from-P via `fresnel_facing`). Valid for view-space normals only. Inputs: Front1.
- ☑ **position_range_remap** — remap world/object P-pass into a 0..1 bbox to drive a ramp keyed
  to object extents. Eats 6 vars (min/max XYZ). Inputs: Front1. Expects: raw-data.

---

## Tier 4 — pattern/texture gap-fillers (reuse existing machinery)

- ☑ **voronoi_edges** — F2−F1 crack/cell-wall network (cracked mud, shattered glass). Reuses
  voronoi loop, +1 var for second minimum. Compile-check early (heaviest GLSL family).
- ☑ **voronoi_metric_variants** — swap `length` for Manhattan/Chebyshev → blocky/diamond cells.
  Nearly free as a metric flag.
- ☑ **hex_grid** — true honeycomb tiling + per-cell hash (only square grids exist).
- ☑ **sdf_lattice** — `mod`-space tiling of one SDF → AA polka/perforation mattes (anti-aliased,
  unlike hard-edge checker/bricks).
- ☑ **smin_metaballs** — gooey blob merges of 2–4 fixed centres via polynomial `smin`; organic
  alpha matte. Animate one centre by scalar.
- ☑ **wood_marble** — Perlin `sin(p+noise*turb)` grain/veins; pairs with cosine_palette.
- ☑ **triangle_rhombille_tiling** — triangle / iso-cube op-art tiling (distinct from
  truchet/checker).
- ☑ **log_polar_spiral** — droste/log-spiral coords; `twist` scalar animates rotation. Guard
  `log(max(r,1e-4))`.
- ☑ **bounce / blip / parabolic waves** — Cameron Carson wave types not yet built (have
  sine/tri/square/saw). Phase = keyframed scalar.

---

## Deferred / flagged

- **Apollonian / inversive-fold texture** and **single-pass domain-warp** — fit only under ~4–6
  unrolled steps; exactly the load-risk class CLAUDE.md flags. Compile-check early if attempted.
- **Chromatic-aberration fringe overlay** — real CA needs a gather (already covered by
  `chromatic_aberration_map` STMap). A per-pixel version is only a stylised radial tint. Skippable.

### Captured during Live-Flame eval
- ☐ **digital_counter alphabet / alphanumeric** (the 7-seg setup, formerly `seven_segment`) — extend the SDF seven-segment approach to letters.
  Plain 7-seg can fake a crude A–F (hex) + some letters, but full A–Z really wants a **14- or
  16-segment** ("starburst") layout. Risk: 14/16 bars = a much bigger unrolled truth table than
  the 7-bar digit, which is *already the longest expression in the library* — likely needs a
  packed per-character bitmask decoded with arithmetic (no arrays/loops in-node). Compile-check
  early; may hit the expression-length ceiling. (Requested 2026-06-25 right after seven_segment
  passed its load test.)

### Overlap notes (call out in each setup's Notes so they don't read as dupes)
hue_preserving_clip vs `gamut_clip` · holdout vs `matte_subtract` · matte_screen_multiply vs
`matte_and/or` · negative_highlighter vs `aov_clamp_negative` · clip_highlighter vs
`exposure_zebra`.

---

## Lens blur (investigated 2026-06-25)
A *true* lens blur/defocus is a gather (sample many neighbours) and is **impossible** in this
node (single current-pixel only). The node's role in a defocus pipeline is to **generate the
control map** that a downstream Flame **Defocus / variable-blur** node consumes — same pattern as
the existing `coc_from_depth` / `depth_dof_mask`. **Outcome: built as `thin_lens_coc`** (stmap_generators) — a physically-based thin-lens
CoC map (asymmetric near/far, far-CoC ceiling) that feeds a downstream Defocus. A true gather
blur remains impossible in-node. ☑ done.
