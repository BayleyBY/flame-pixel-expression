# Nuke → Flame Pixel Expression — Translation Guide

Translating the best examples from Nuke's Expression node into Autodesk Flame's
**Pixel Expression** node (2027.1+). The big difference: Flame uses **GLSL**, not
Nuke's C-like expression language. Most generators port cleanly; a few Nuke tricks
have no GLSL equivalent (noted below).

---

## 0. Key differences (read first)

| Concept | Nuke | Flame Pixel Expression (GLSL) |
|---------|------|-------------------------------|
| Current pixel RGB | `r` `g` `b` | `r1` `g1` `b1` (Front 1) — or `front1.r` etc. |
| Alpha | `a` | `m1` (Matte 1), edited in the **Matte** field |
| Second input | (extra input) | `r2` `g2` `b2` / `m2` (Front 2 / Matte 2) |
| Pixel coords | `x` `y` | `x` `y` |
| Size | `width` `height` | `width` `height` |
| Centered coords | `cx` `cy` | none — use `centre.x` / `centre.y` or `x - width/2.0` |
| Custom knobs (size, rays…) | user knobs | the **8 custom variables** + **4 custom formulas** |
| Time | `frame` | **none** — animate a custom variable in the Animation editor |
| Constants | `pi` | `PI`, `E` (built-in) |

**GLSL gotchas that will bite you:**
- **Strongly typed.** Write float literals with a decimal: `1.0`, `4.0`, `x/2.0`
  (not `1`, `x/2`). Mixing `int`/`float` fails to compile.
- **`clamp` needs min & max:** `clamp(v, 0.0, 1.0)` (Nuke's 1-arg `clamp(v)` = 0..1).
- **`fmod` → `mod`**, **`hypot(a,b)` → `length(vec2(a,b))`**, **`trunc` is fine**.
- **`atan` arg order is `atan(y, x)`** (same as Nuke's 2-arg form).
- **No `noise()` / `random()`** you can rely on — use the hashes in §6.
- **No neighbor sampling** (`r(x+1,y)`): each input is read only at the current pixel.
- Numeric fields step in tenths. For 0..1 values, either divide by 100 in the
  expression or use **Space + Drag** for hundredths.

---

## 1. Alpha cleanup → Matte field
Nuke operated on `a`; in Flame put these in the **Matte Channel Expression** using `m1`.
```glsl
m1 < 1.0 ? 0.0 : m1        // Crunch alpha
m1 > 0.0 ? 1.0 : m1        // Fill alpha
4.0 * (1.0 - m1) * m1      // Alpha fringe (edge isolation)
```

## 2. Fix NaN / Inf
```glsl
isnan(r1) ? 0.0 : r1       // Replace NaN with a fixed value (per channel)
isinf(r1) ? 0.0 : r1       // Replace Inf
```
> Nuke's "patch from a neighbor" (`isnan(r) ? r(x+1,y) : r`) has **no equivalent** —
> Flame reads only the current pixel. Use a Front 2 input as the patch source instead:
> `isnan(r1) ? r2 : r1`.

## 3. ST / UV map
```glsl
(x + 0.5) / width          // Red channel
(y + 0.5) / height         // Green channel
```

## 4. Absolute value
```glsl
abs(r1)   abs(g1)   abs(b1)
```

---

## 5. Generators (2D)
These port directly — they're pure pixel math. Use a custom variable for any
former Nuke knob, and `centre.x/centre.y` for the center point.

### Gradients & lines
```glsl
x / width                       // Horizontal gradient
y / height                      // Vertical gradient
1.0 - (y / height)              // Inverted vertical
(sin(x) + 1.0) / 2.0            // Sine lines (0..1)
(sin(x / 4.0) + 1.0) / 2.0      // Wider lines
```

### Radial gradients & rings
```glsl
length(vec2(x - centre.x, y - centre.y))                 // Distance from centre
(rad - length(vec2(x-centre.x, y-centre.y))) / rad       // Normalized radial ('rad' var)
sin(length(vec2(x-centre.x, y-centre.y)))                // Concentric rings
sin(length(vec2(x-centre.x, y-centre.y)) / size)         // Ring spacing ('size' var)
```

### Radial rays
```glsl
sin(atan(y - centre.y, x - centre.x) * rays)                 // Rays ('rays' var = count)
sin((atan(y - centre.y, x - centre.x) + offset) * rays)     // Rotated ('offset' var)
```

---

## 6. Noise & random (custom formulas)
GLSL's built-in `noise()` is unreliable in Flame's context — define a hash instead.
Create a **custom formula** (Type: float) named `rand`:
```glsl
// Formula 'rand' (float):
fract(sin(dot(vec2(x, y), vec2(12.9898, 78.233))) * 43758.5453)
```
Then use `rand` in any channel field. For value-noise, build from a hashed grid, or
drive a pattern with an animated custom variable `t` (see §8).

---

## 7. P-mattes (3D position pass in Front 1 RGB)
Front 1 carries a P-world pass: `r1`=X, `g1`=Y, `b1`=Z. Output to the **Matte** field
(it can still read `r1/g1/b1`). For the 3D center, use three custom variables
`cenR / cenG / cenB`; for ring/ray controls use `ringScale` / `rays`.

Define a **custom formula** (Type: float) named `dist`:
```glsl
// Formula 'dist' (float):
length(vec3(r1 - cenR, g1 - cenG, b1 - cenB))
```
Then, in the Matte field:
```glsl
(1.0 - dist) * m1                       // Spherical matte at centre
sin(dist * ringScale) * m1              // 3D concentric rings
sin(atan(b1 - cenB, r1 - cenR) * rays) * m1   // 3D rays on the X-Z plane
```

### Voxel / blocky
```glsl
trunc(r1 * scale) / scale               // Stepped values ('scale' var)
```

### Box matte (clamped & smoothed per axis)
```glsl
clamp(1.0 - abs(r1), 0.0, 1.0) * clamp(1.0 - abs(g1), 0.0, 1.0) * clamp(1.0 - abs(b1), 0.0, 1.0)

// Soft edges ('start'/'end' vars):
smoothstep(start, end, clamp(1.0 - abs(r1), 0.0, 1.0)) *
smoothstep(start, end, clamp(1.0 - abs(g1), 0.0, 1.0)) *
smoothstep(start, end, clamp(1.0 - abs(b1), 0.0, 1.0))
```

---

## 8. Animation (no `frame` variable)
Nuke's `sin(frame)` relies on a global time. Flame has none — instead create a custom
variable (e.g. `t`), then **animate it in the Animation editor** (all numeric fields
are keyable). Drive patterns with it:
```glsl
sin(x / 4.0 + t)                                   // Scrolling lines
sin(length(vec2(x-centre.x, y-centre.y)) - t)      // Expanding rings (pulse)
sin((atan(y-centre.y, x-centre.x) + t) * rays)     // Rotating rays
```
> Nuke's transform-knob animations (e.g. circular motion via `cos/sin(frame)`) don't
> map here — Pixel Expression outputs **pixel color**, not transform values. Express
> the motion as a pattern over `x/y` driven by `t` instead.

---

## 9. Quick reference — function name mapping
| Nuke | Flame GLSL |
|------|-----------|
| `fmod(a,b)` | `mod(a,b)` |
| `hypot(a,b)` | `length(vec2(a,b))` |
| `clamp(v)` | `clamp(v, 0.0, 1.0)` |
| `trunc(v)` | `trunc(v)` |
| `pow(a,b)` | `pow(a,b)` |
| `atan(y,x)` | `atan(y,x)` |
| `random()` | hash (see §6) |
| `noise(...)` | hash / custom (see §6) |
| `pi` | `PI` |
| `frame` | animated custom variable |
