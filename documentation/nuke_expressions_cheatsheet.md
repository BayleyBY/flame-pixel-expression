# Foundry Nuke Expressions — Cheat Sheet

A practical reference for Nuke's **Expression node** (per-channel pixel math) and
**linking/parameter expressions** (knob-to-knob math). Both share a C-like syntax
that also overlaps with TCL.

---

## 1. Fundamentals

### What's what
- **Expression node** — applies a C-like math formula to channel values. One field
  per channel: `r`, `g`, `b`, `a` (plus custom channels).
- **Linking / parameter expression** — any knob can pull its value from another knob
  or a formula. Add one by pressing `=` on a parameter, or right-click → *Add expression*.

### Coordinate systems
| Vars | Origin | Notes |
|------|--------|-------|
| `x`, `y` | bottom-left | Absolute pixel coordinates |
| `cx`, `cy` | image center | Normalized: `0,0` = center, `-1,0` = left edge, `1,0` = right edge. Resolution-independent. |

### References
- **Channels:** `r`, `g`, `b`, `a` (read the current pixel's value).
- **Sample a coordinate:** `r(x+1, y)` reads red at a neighboring pixel.
- **Other nodes' knobs:** `NodeName.knob` → e.g. `Blur1.size`.
- **Parent linking:** `parent.Transform1.rotate`.
- **Common globals:** `frame`, `width`, `height`, `input.width`, `root.format`.

---

## 2. Everyday expressions

### Alpha cleanup
```
a < 1 ? 0 : a        # Crunch alpha — anything below 1 becomes 0
a > 0 ? 1 : a        # Fill alpha   — anything above 0 becomes 1
4*(1-a)*a            # Alpha fringe — isolate edges (peaks at mid-tones)
```

### Fix NaN / Inf pixels (render cleanup)
```
isnan(r) ? 0 : r              # Replace bad pixel with a fixed value
isnan(r) ? r(x+1,y) : r       # Patch from a neighboring pixel
isnan(r)                      # Detect NaN  (use isinf() for infinities) — for QC
```

### ST / UV map generation (coordinates, no warp)
```
# Red channel:
(x + 0.5) / width
# Green channel:
(y + 0.5) / height
```

### Retime / re-speed an animation curve
```
curve((frame - firstFrame) * speed + firstFrame)
```

### Absolute value
```
abs(r)   abs(g)   abs(b)   abs(a)
```

---

## 3. Animation & linking

```
sin(frame)*100               # Oscillate
sin(frame/10)*100            # Slower oscillation

# Circular motion:
cos(frame/5)*100             # x knob
sin(frame/5)*100             # y knob   (swap sin/cos to reverse direction)

frame < 1010 ? 0 : 100       # Conditional value by frame
inrange(frame, 1010, 1015)   # True within an inclusive frame range
$gui                         # 1 in GUI, 0 on the farm — skip heavy work on render
random()                     # Random 0..1
random()*100                 # Scaled random
Blur_CONTROL.size*3          # Link a knob to another knob's value
```

---

## 4. Generators & utility setups
*(from Andrea Geremia's Expression Node collection)*

```
floor(y/size)%2                                   # Bricks / stripe pattern
fmod(x,offsetX)==0 ? (fmod(y,offsetY)==0 ? 1:0):0 # Point grid
random  /  random(frame)                          # Per-pixel / per-frame color

# Normal-pass relight (dot product of light dir and normal):
max((r*norm.r)+(g*norm.g)+(b*norm.b), 0)

# UV map:
(x+0.5)/width                # expr0
(y+0.5)/height              # expr1
```
Also in that collection: green/blue **despill** formulas, **DeepExpression** thickness
offsets (`deep.front` / `deep.back`).

---

## 5. TCL knob / text snippets
*(from gatimedia — used in Text nodes and knob fields, wrapped in `[ ]`)*

```
[value size]                         # Show a knob's value
[value red], [value green], [value blue]
[knob Blur15.size 200]               # Set a knob
[knob Blur13.size Blur_CONTROL.size*3]
[setkey this.size 34 2]              # Set keyframe: value 34 at frame 2
[value input.name]                   # Connected input node's name
[sample [node ColorWheel5] red 1075 378]  # Sample pixel color at coords
[layers this]   [channels this]   [knobs this]
[metadata]      [metadata input/timecode]
[date]          [value frame]
[set var1 25]   $var1                # Define / use a variable
[getenv NUKE_TEMP_DIR]   [array get env]
```

### Text formatting (Text node)
```
<center>text</center>
<b>text</b>
<font color=#582b00>text</font>
<p style="font-size:100px">&#129409;</p>   # Emoji by decimal code
```

---

## 6. Wave generators
*(from Cameron Carson — controllable via `waveLength`, `minVal`, `maxVal`, `offset`)*

Types available: Random, Noise, Sine, Triangle, Square, Sawtooth, Sawtooth
(Parabolic / Reversed / Exponential), Bounce, Blip, Sine Blip. Full formulas and a
ready-made Gizmo are on his site / Nukepedia (page is JS-rendered — visit directly).

---

## 7. Expression Node 101 — generators & P-mattes from scratch
*(walkthrough from the [Nukepedia tutorial](https://www.nukepedia.com/knowledge/general-tutorials/written-tutorials/expression-node-101/) — builds up from first principles)*

### 2D gradients & patterns
```
1                        # Solid: every pixel's red = 1
x / width                # Horizontal gradient (0..1, left→right)
y / height               # Vertical gradient (top→bottom)
1 - (y / height)         # Inverted vertical
(sin(x) + 1) / 2         # Sine lines, normalized to 0..1
(sin(x/4) + 1) / 2       # Wider lines (slow the input)
```

### Radial gradients & rings
```
sqrt(x*x + y*y)                       # Distance from origin (0,0)
(300 - sqrt(x*x + y*y)) / 300         # Inverted, normalized radial gradient
sin(sqrt(x*x + y*y))                  # Concentric rings
sin(sqrt(x*x + y*y) / 4)              # Wider ring spacing
sin(hypot(x-center.x, y-center.y) / size)   # Rings centered on a 'center' knob, 'size' slider
```

### Radial rays
```
atan(x-center.x, y-center.y)                       # Angle around a point (~ -1.24..1.24)
sin(atan(x-center.x, y-center.y))                  # Rays
sin(atan(x-center.x, y-center.y) * size)           # More rays ('size' = count)
sin((atan(x-center.x, y-center.y) + offset) * size)  # Rotate with 'offset'
```

### P-mattes (3D position pass: r=X, g=Y, b=Z)
```
sqrt(r*r + g*g + b*b)                 # 3D distance from origin
(1 - sqrt(r*r + g*g + b*b)) * a       # Basic spherical matte

# Offset center — define a variable 'dist' to keep it readable:
#   dist = sqrt((r-center.r)^2 + (g-center.g)^2 + (b-center.b)^2)
sqrt((r-center.r)*(r-center.r)+(g-center.g)*(g-center.g)+(b-center.b)*(b-center.b))
(1 - dist) * a                        # Spherical matte at 'center'
sin(dist) * a                         # 3D concentric rings
sin(dist * ringScale) * a             # Ring spacing control
sin(atan(r-center.r, b-center.b) * rays) * a   # 3D rays on the X-Z plane
```

### 3D noise & voxel/box effects
```
noise(r, g, b)                        # 3D noise driven by the P-pass

trunc(r)                              # Blocky/voxel: truncate decimals
trunc(r*scale)/scale                  # Adjustable block size ('scale' slider)

# Box matte from absolute value, clamped & smoothed per axis:
clamp(1 - abs(r)) * clamp(1 - abs(g)) * clamp(1 - abs(b))
smoothstep(start,end, clamp(1-abs(r))) * smoothstep(start,end, clamp(1-abs(g))) * smoothstep(start,end, clamp(1-abs(b)))
```

### Functions introduced in the tutorial
`sqrt` (distance) · `sin`/`cos` (oscillation) · `atan` (angle) · `hypot` (2D distance shorthand) ·
`noise` (3D noise) · `trunc` (truncate) · `clamp` (limit to range) · `smoothstep` (smooth interp) · `abs`.

> Advanced topics covered: **C44Matrix** for full 4×4 transforms on position passes,
> P-world → P-object (sticking mattes to moving geometry via a parented null + camera),
> and building **projections without plugins** (3×3 ColorMatrix for rotation + Add for
> translation + Expression for the perspective divide + STMap to apply), plus limiting
> projections to front-facing surfaces with normal·camera dot products.

---

## 8. Resources

### Official Foundry docs
- [Expression node reference](https://learn.foundry.com/nuke/content/reference_guide/color_nodes/expression.html) — channel math + function table
- [Expressions primer](https://learn.foundry.com/nuke/content/comp_environment/expressions/expressions.html)
- [Linking Expressions](https://learn.foundry.com/nuke/12.0/content/comp_environment/expressions/linking_expressions.html)
- [ParticleExpression](https://learn.foundry.com/nuke/content/reference_guide/particles_nodes/particleexpression.html)

### Community collections
- [Andrea Geremia – Expression Node collection](http://www.andreageremia.it/tutorial_expression_node.html) — richest copy-paste set
- [Andrea Geremia – Python/TCL tips](http://www.andreageremia.it/tutorial_python_tcl.html)
- [Marcel Pichert – Useful Nuke Expressions](https://www.marcelpichert.com/post/useful-nuke-expressions)
- [gatimedia – Expressions tutorial](https://www.gatimedia.co.uk/expressions) — broadest TCL snippet list
- [Cameron Carson – Nuke Wave Expressions](https://www.cameroncarson.com/nuke-wave-expressions)
- [Nukepedia – Expression Node 101](https://www.nukepedia.com/knowledge/general-tutorials/written-tutorials/expression-node-101/)
- [keheka – Useful Nuke Tools and Setups](https://www.keheka.com/useful-nuke-tools-and-setups/)
- [TCL expression reference (NDK)](https://www.nukepedia.com/reference/Tcl/group__tcl__expressions.html)
