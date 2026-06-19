# Pixel Expression — Feature Showcase Setup

Purpose: a single setup that **touches every feature** of the Pixel Expression node, so
that when you Save it the resulting file reveals how each part is serialized. It's a
front1↔front2 blend with a Gaussian vignette, saturation + gamma control, and a
ring × ray pattern on the matte output.

Enter everything below, set the inputs, keyframe the two animated variables, then Save.

---

## 1. Input connections
| Socket | Connect | Why (what it exercises) |
|--------|---------|-------------------------|
| **Front 1** | any RGB clip | required; `r1 g1 b1` |
| **Front 2** | a different RGB clip | `r2 g2 b2` (blend source) |
| **Constraint** | a B&W shape clip | region-limit input (not referenced by name) |
| **Matte 1** | a greyscale clip | `m1` |
| **Matte 2** | a different greyscale clip | `m2` |

Outputs to verify after: **Result** (from R/G/B) and **OutMatte** (from Matte field).

---

## 2. Centre
- **Centre X** = `960`   **Centre Y** = `540`  (i.e. center of a 1920×1080 clip)
- **Show Icon** = ON  (so the on-screen manipulator appears — confirms it drives `centre.x/centre.y`)

---

## 3. Custom variables (all 8)
| # | Variable Name | Value | Used for |
|---|---------------|-------|----------|
| 1 | `mixAmt`   | 0.5   | front1↔front2 + matte1↔matte2 blend |
| 2 | `radius`   | 600.0 | vignette falloff radius (pixels) |
| 3 | `ringFreq` | 0.05  | ring frequency (use Space+Drag for hundredths) |
| 4 | `rays`     | 8.0   | number of rays |
| 5 | `rot`      | 0.0   | ray rotation in turns — **animate this** |
| 6 | `gamma`    | 2.2   | output gamma |
| 7 | `sat`      | 1.2   | saturation |
| 8 | `t`        | 0.0   | animation phase — **animate this** |

> Tip: `ringFreq` and `mixAmt`/`sat` sit in the 0–1ish range where tenths-stepping is
> too coarse — use **Space + Drag** for hundredths, or scale inside the expression.

---

## 4. Custom formulas (one of each type — all 4)
Define in this order (later formulas reference earlier ones + built-ins/vars only):

| # | Type | Name | Formula Text |
|---|------|------|--------------|
| 1 | float | `dist`  | `length(vec2(x - centre.x, y - centre.y))` |
| 2 | vec2  | `uvN`   | `vec2(x / width, y / height)` |
| 3 | vec3  | `lumaW` | `vec3(0.2126, 0.7152, 0.0722)` |
| 4 | vec4  | `vign`  | `vec4(uvN.x, uvN.y, dist / radius, pow(E, -dist * dist / (radius * radius)))` |

`vign` packs: `.x/.y` = uv gradient, `.z` = normalized distance, `.w` = Gaussian vignette.

> **Reserved names:** Flame injects its own variables into the compiled GLSL, so custom
> names can't collide with them or with GLSL keywords. `uv` fails with a "redefinition"
> error — hence `uvN`. Avoid `uv`, `color`, `pos`, `coord`, `texture`, `gl_*`; suffix if unsure.

> If the node **does** allow inputs (`r1`,`m1`…) inside formulas, you could move the
> blend into a formula too — the save file will tell us. For now formulas stay
> input-free (only built-ins, vars, and other formulas) to be safe.

---

## 5. Channel expressions

**Red Channel:**
```glsl
pow(clamp(mix(dot(vec3(mix(r1,r2,mixAmt), mix(g1,g2,mixAmt), mix(b1,b2,mixAmt)), lumaW), mix(r1,r2,mixAmt), sat) * (vign.w * (0.5 + 0.5 * vign.y)), 0.0, 1.0), 1.0 / gamma)
```

**Green Channel:**
```glsl
pow(clamp(mix(dot(vec3(mix(r1,r2,mixAmt), mix(g1,g2,mixAmt), mix(b1,b2,mixAmt)), lumaW), mix(g1,g2,mixAmt), sat) * (vign.w * (0.5 + 0.5 * vign.y)), 0.0, 1.0), 1.0 / gamma)
```

**Blue Channel:**
```glsl
pow(clamp(mix(dot(vec3(mix(r1,r2,mixAmt), mix(g1,g2,mixAmt), mix(b1,b2,mixAmt)), lumaW), mix(b1,b2,mixAmt), sat) * (vign.w * (0.5 + 0.5 * vign.y)), 0.0, 1.0), 1.0 / gamma)
```

**Matte Channel:**
```glsl
clamp(((sin(dist * ringFreq + t) + 1.0) / 2.0) * ((sin((atan(y - centre.y, x - centre.x) + rot * PI) * rays) + 1.0) / 2.0) * mix(m1, m2, mixAmt), 0.0, 1.0)
```

What each channel does: blend Front 1 ↔ Front 2, desaturate/saturate toward luma
(`sat`), multiply by the Gaussian vignette with a vertical gradient, then apply gamma.
The matte multiplies a concentric-ring wave by a radial-ray wave by the blended mattes.

---

## 6. Animation (reveals keyable variable channels)
In the Animation editor, set keyframes so the save file records animated channels:
- `t`  : frame 1 → `0.0`,  frame 100 → `6.28`  (one full ring cycle, 2·PI)
- `rot`: frame 1 → `0.0`,  frame 100 → `1.0`   (one full ray rotation, in turns)

---

## 7. Feature coverage checklist
- [x] Inputs: `r1 g1 b1`, `r2 g2 b2`, `m1`, `m2`, Constraint socket
- [x] Built-ins: `E`, `PI`, `centre.x`, `centre.y`, `width`, `height`, `x`, `y`
- [x] All 8 custom variables (incl. 2 animated)
- [x] All 4 formula types: float / vec2 / vec3 / vec4
- [x] Formula→formula references (`vign` uses `uv`, `dist`)
- [x] All 4 channel fields: Red, Green, Blue, Matte
- [x] Both outputs: Result + OutMatte
- [x] Centre X/Y + Show Icon manipulator
- [x] GLSL features: swizzles, `mix`, `dot`, `pow`, `clamp`, `sin`, `atan`, `length`, ternary-free

---

## 8. After you Save
Drop the saved setup file next to these notes. From it I can map:
how channel expressions, custom variable names/values/animation, formula
types+text, centre values, and input wiring are stored — then we can author setups
as files directly instead of typing them into the UI.
