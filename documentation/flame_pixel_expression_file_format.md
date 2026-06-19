# Pixel Expression — Save File Format (`.pixel_expression_node`)

Reverse-engineered from `pixelexpression1.pixel_expression_node` (kept in this folder as a
worked example; Flame 2027.1, Version `21.020000`). The file is a **single-line XML**
document. A sibling
`<name>.pixel_expression_node.p` is just a proxy thumbnail for the media browser —
ignore it when authoring.

> **Inputs are NOT stored here.** Front 1/2, Constraint, Matte 1/2 wiring lives in the
> Batch/BFX setup, not in this node file. This file only holds the node's internal state.

---

## Top-level structure
```
<Setup>
  <Base> … node metadata … </Base>
  <State> … expressions, variables, formulas … </State>
</Setup>
```

### `<Base>` (metadata — safe to copy verbatim, edit NAME + FrameBounds)
| Tag | Example | Meaning |
|-----|---------|---------|
| `Version` | `21.020000` | file format version |
| `NAME` | `pixelexpression1` | node name (matches filename) |
| `Note` | (empty) | user note |
| `Expanded` / `ScrollBar` | `False` / `0` | UI state |
| `Frames` / `Current_Time` | `0` / `1` | timeline state |
| `Input_DataType` | `4` | input bit depth/type |
| `ClampMode` | `0` | output clamp mode |
| `AdapDegrad` / `ReadOnly` / `UsedAsTransition` | `False` | flags |
| `NoMediaHandling` | `1` | media handling |
| `FrameBounds` | `W="1920" H="1080" X="0" Y="0" SX="16" SY="9"` | resolution + aspect (SX:SY) |

---

## `<State>`

### Channel expressions (verbatim GLSL strings)
```
<RedExpression>…</RedExpression>
<GreenExpression>…</GreenExpression>
<BlueExpression>…</BlueExpression>
<MatteExpression>…</MatteExpression>
```

### Custom variable NAMES (the 8 slots)
```
<VariableName0>mixAmt</VariableName0> … <VariableName7>t</VariableName7>
```

### Custom variable VALUES = animated channels
Each variable's value is a full animation channel: `<Variable0>` … `<Variable7>`.
`centre.x` / `centre.y` use the same channel structure as `<CentreX>` / `<CentreY>`.

```xml
<Variable0>
  <Channel Name="scene/<NODE>/variable0">
    <Extrap>constant</Extrap>      <!-- extrapolation outside keys -->
    <Value>1.10000682</Value>      <!-- current evaluated value -->
    <Size>2</Size>                 <!-- number of keyframes -->
    <KeyVersion>2</KeyVersion>
    <KFrames>
      <Key Index="0">
        <Frame>1</Frame>
        <Value>1.10000682</Value>
        <RHandle_dX>33</RHandle_dX><RHandle_dY>0</RHandle_dY>
        <LHandle_dX>-33</LHandle_dX><LHandle_dY>0</LHandle_dY>
        <CurveMode>hermite</CurveMode>
        <CurveOrder>linear</CurveOrder>
      </Key>
      <Key Index="1"> … Frame 100 … </Key>
    </KFrames>
    <Uncollapsed/>
  </Channel>
</Variable0>
```
- `Channel Name` path is `scene/<NODE>/variableN` (and `…/centre/x`, `…/centre/y`).
- `Size` must equal the number of `<Key>` entries.
- A **static** (un-keyed) value: `Size=0` with an empty `<KFrames></KFrames>` and the
  constant in `<Value>`. Confirmed to load with no keyframe set. (An animated value uses
  `Size=N` with N `<Key>` entries.)

### Custom formulas (the 4 slots)
```
<FormulaName0>dist</FormulaName0>
<FormulaExpression0>length(vec2(x - centre.x, y - centre.y))</FormulaExpression0>
<FormulaType0>0</FormulaType0>
…
<FormulaType3>3</FormulaType3>
```
**`FormulaType` mapping:** `0`=float · `1`=vec2 · `2`=vec3 · `3`=vec4.

---

## Key findings

1. **`uv` is a built-in injected variable** (a `vec2`, normalized texture coords ~0–1).
   That's why naming a formula `uv` threw "redefinition" — and why the saved `vign`
   formula references `uv.x`/`uv.y` and still compiles. **Our `uvN` formula is therefore
   redundant** — `uv` already provides `vec2(x/width, y/height)`. Use the built-in `uv`
   directly and free up that formula slot.
2. **Variable values are raw UI floats** (tenths-stepping), not pre-scaled. In the save,
   e.g. `ringFreq` came out as `-13.45` — scale inside the expression if you need 0–1.
3. **No input wiring** in the file (see note up top).
4. **No `ShowIcon` tag** appears — likely defaults / stored elsewhere.
5. Everything is **one line** — when hand-authoring, keep it single-line (or test whether
   Flame tolerates pretty-printed whitespace before relying on it).
6. **Expressions must be XML-escaped.** Comparison operators (`<`, `>`, `<=`, `>=`) have
   to be written as `&lt;` / `&gt;` (and `&` as `&amp;`). A raw `<` makes the file
   silently fail to load with **no error message** — the parser reads it as a stray tag.
   Confirmed: empty unused variable/formula slots load fine and clear correctly.
7. **The Matte expression can read Front inputs** (`r1`,`g1`,`b1`,`r2`…), not just
   `m1`/`m2` — confirmed by a test setup. But the **OutMatte output only renders when a
   clip is connected to Matte 1**, regardless of what the expression references.

---

## Authoring a new setup from scratch
1. Copy this file as a template.
2. Edit `NAME` (and the filename to match) + `FrameBounds`.
3. Replace the four `*Expression` strings.
4. Set `VariableName0..7` and each `Variable0..7` channel (value + keys).
5. Set `FormulaName/Expression/Type 0..3`.
6. Fix every `Channel Name="scene/<NODE>/…"` to the new node name.
7. Save as `<NAME>.pixel_expression_node`; Flame regenerates the `.p` proxy on load.
