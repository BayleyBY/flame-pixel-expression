# Pixel Expression — Save File Format (`.pixel_expression_node`)

Originally reverse-engineered from `pixelexpression1.pixel_expression_node` (kept in this
folder as the old worked example; Flame 2027.1, Version `21.020000`), then **updated for the
PR245 node change** (2026-07-07) against fresh Flame saves (`color_blindness_pr245`,
`alpha_fringe_pr245`, `radial_ramp_animated_pr245` — PR-test files since deleted; recover
from git history at commit `9b056db` if ever needed). The file is a
**single-line XML** document. A sibling `<name>.pixel_expression_node.p` is just a proxy
thumbnail for the media browser — ignore it when authoring.

> **⚠️ PR245 changed the `<State>` structure** (same `<Version>` string, so it fails
> *silently*). The three changes, all captured below: (1) four new `<…Declarations>` blocks
> after the channel expressions; (2) variables moved from 8 flat `Variable0..7`/`VariableName0..7`
> slots to a single name-keyed `<Variables>` list; (3) static channels dropped
> `<Size>`/`<KeyVersion>`/`<KFrames>`. Also: Centre now defaults to the image middle, and both
> `centre`/`center` spellings are recognised.

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

### Channel expressions (verbatim GLSL strings) + declaration blocks
```
<RedExpression>…</RedExpression>
<GreenExpression>…</GreenExpression>
<BlueExpression>…</BlueExpression>
<MatteExpression>…</MatteExpression>
<RedDeclarations></RedDeclarations>       <!-- NEW (PR245): per-channel locals from the -->
<GreenDeclarations></GreenDeclarations>   <!-- multi-line Expression Editor. Emitted empty -->
<BlueDeclarations></BlueDeclarations>     <!-- when unused; the tags are mandatory. -->
<MatteDeclarations></MatteDeclarations>
```

### Custom variables — the `<Variables>` list (NEW PR245 structure)
Variables are no longer 8 flat `VariableName0..7` + `Variable0..7` slots. They're a single
`<Variables>` container with one `<Variable>` per **defined** variable, keyed by name. The
block is **omitted entirely** when a setup has no variables. Still capped at 8 by the UI.

```xml
<Variables>
  <Variable index="0" name="type">        <!-- name is the identifier used in expressions -->
    <Channel Name="scene/<NODE>/type">    <!-- path uses the NAME now, not variableN -->
      <Uncollapsed/>                      <!-- untouched-at-default: Extrap+Value omitted -->
    </Channel>
  </Variable>
  <Variable index="1" name="amount">
    <Channel Name="scene/<NODE>/amount">
      <Extrap>constant</Extrap>
      <Value>1</Value>                    <!-- static: lean form, no Size/KeyVersion/KFrames -->
      <Uncollapsed/>
    </Channel>
  </Variable>
</Variables>
```

### Channels: static (lean) vs animated
`centre.x`/`centre.y` (`<CentreX>`/`<CentreY>`) and each variable use the same channel form.
- **Static (PR245 lean form):** just `<Extrap>constant</Extrap><Value>V</Value><Uncollapsed/>`
  — no `<Size>`/`<KeyVersion>`/`<KFrames>`. A channel left untouched at its default may omit
  `<Extrap>`+`<Value>` too (only `<Uncollapsed/>`); writing them explicitly is safe.
- **Animated:** unchanged from the old format — `<Size>N</Size><KeyVersion>2</KeyVersion>` plus a
  `<KFrames>` block of N `<Key>` entries (`<Frame>`,`<Value>`, R/LHandle, `<CurveMode>hermite`,
  `<CurveOrder>linear`). `Size` must equal the `<Key>` count. (Handle `dX` is cosmetic under
  linear order — the generator's `33` is fine; Flame may write other values.)
```xml
<Channel Name="scene/<NODE>/radius">
  <Extrap>constant</Extrap><Value>133.999939</Value>
  <Size>2</Size><KeyVersion>2</KeyVersion>
  <KFrames>
    <Key Index="0"><Frame>1</Frame><Value>133.999939</Value>
      <RHandle_dX>83</RHandle_dX><RHandle_dY>0</RHandle_dY>
      <LHandle_dX>-83</LHandle_dX><LHandle_dY>0</LHandle_dY>
      <CurveMode>hermite</CurveMode><CurveOrder>linear</CurveOrder></Key>
    <Key Index="1"> … Frame 250 … </Key>
  </KFrames>
  <Uncollapsed/>
</Channel>
```

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
   clip is connected to Matte 1**, regardless of what the expression references. The OutMatte
   clip output is tagged as **Matte** (PR245).
8. **PR245 centre change (confirmed in Flame):** with `centre=(0,0)`, a `radial_ramp` glow renders
   at the **image middle** (not the top-left corner as before) and a pixel-scale radius stays
   pixel-accurate — so `x`/`y` and `x - centre.x` distance math are unchanged; only the centre's
   default position moved to the middle. No expression edits were needed across the library. Both
   `centre` and `center` spellings resolve.
9. **PR245 was a *silent* break** because `<Version>` did **not** change (still `21.020000`) — the
   only signal was setups failing to load. Diagnosis method (repeatable): save a fresh setup from
   the updated node, then diff its XML skeleton (tags/attrs, ignoring text) against a known-good
   file to isolate added/removed/renamed tags.

---

## Authoring a new setup from scratch (do NOT hand-author — use `tools/generate_setups.py`)
The generator is the single source of truth; these steps describe what it emits. For reference,
the new-format `<State>` order is: **expressions → 4 `*Declarations` → `<Variables>` (if any) →
`CentreX`/`CentreY` → `FormulaName/Expression/Type 0..3`**.
1. Edit `NAME` (and the filename to match) + `FrameBounds`.
2. Set the four `*Expression` strings; emit the four `*Declarations` empty.
3. Emit a `<Variables>` list — one `<Variable index="N" name="…">` per variable (omit the block
   if none); each holds a `<Channel Name="scene/<NODE>/<name>">` (lean static or keyframed).
4. Set `FormulaName/Expression/Type 0..3` (still 4 fixed slots).
5. Fix every `Channel Name="scene/<NODE>/…"` to the node name.
6. Save as `<NAME>.pixel_expression_node`; Flame regenerates the `.p` proxy on load.
