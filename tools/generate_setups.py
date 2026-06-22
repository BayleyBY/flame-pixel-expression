#!/usr/bin/env python3
"""Generate Flame Pixel Expression setup files (.pixel_expression_node).

Reverse-engineered from a real Flame 2027.1 save. Each setup is single-line XML:
  <Setup><Base>..metadata..</Base><State>..expressions/vars/formulas..</State></Setup>

Slots are fixed by the UI: 8 custom variables, 4 custom formulas. Unused slots are
emitted empty. Static values (incl. Centre, default 0,0) are written with NO keyframes;
only (frame, value) lists produce animation keys.
FormulaType: 0=float, 1=vec2, 2=vec3, 3=vec4.
"""
import os

# Repo root is the parent of this script's folder (tools/); setups live in <repo>/setups/.
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "setups")
W, H, SX, SY = 1920, 1080, 16, 9


def xml_escape(s):
    """Escape XML-significant chars. GLSL comparison operators (< > <= >=) MUST be
    escaped or the parser treats them as tags and the file silently fails to load."""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _keyframe(index, frame, value):
    return (
        f'<Key Index="{index}"><Frame>{frame}</Frame><Value>{value}</Value>'
        f'<RHandle_dX>33</RHandle_dX><RHandle_dY>0</RHandle_dY>'
        f'<LHandle_dX>-33</LHandle_dX><LHandle_dY>0</LHandle_dY>'
        f'<CurveMode>hermite</CurveMode><CurveOrder>linear</CurveOrder></Key>'
    )


def channel(path, value):
    """Animation channel. `value` is either a scalar (static — NO keyframes, just a
    constant value) or a list of (frame, value) pairs (animated, linear interpolation)."""
    if isinstance(value, (list, tuple)) and value and isinstance(value[0], (list, tuple)):
        keys = list(value)
        current = keys[0][1]
    else:
        keys = []
        current = value
    kf = "".join(_keyframe(i, f, v) for i, (f, v) in enumerate(keys))
    return (
        f'<Channel Name="{path}"><Extrap>constant</Extrap><Value>{current}</Value>'
        f'<Size>{len(keys)}</Size><KeyVersion>2</KeyVersion><KFrames>{kf}</KFrames>'
        f'<Uncollapsed/></Channel>'
    )


def build(name, red, green, blue, matte,
          variables=None, formulas=None, centre=(0, 0), category=""):
    """variables: list of (name, value), up to 8. formulas: list of (name, expr, type), up to 4."""
    variables = (variables or [])[:8]
    formulas = (formulas or [])[:4]

    # Pad to fixed slot counts.
    var_names = [v[0] for v in variables] + [""] * (8 - len(variables))
    var_vals = [v[1] for v in variables] + [0] * (8 - len(variables))
    forms = list(formulas) + [("", "", 0)] * (4 - len(formulas))

    base = (
        f'<Setup><Base><Version>21.020000</Version><NAME>{name}</NAME><Note></Note>'
        f'<Expanded>False</Expanded><ScrollBar>0</ScrollBar><Frames>0</Frames>'
        f'<Current_Time>1</Current_Time><Input_DataType>4</Input_DataType>'
        f'<ClampMode>0</ClampMode><AdapDegrad>False</AdapDegrad><ReadOnly>False</ReadOnly>'
        f'<NoMediaHandling>1</NoMediaHandling><UsedAsTransition>False</UsedAsTransition>'
        f'<FrameBounds W="{W}" H="{H}" X="0" Y="0" SX="{SX}" SY="{SY}"/></Base>'
    )

    exprs = (
        f'<RedExpression>{xml_escape(red)}</RedExpression>'
        f'<GreenExpression>{xml_escape(green)}</GreenExpression>'
        f'<BlueExpression>{xml_escape(blue)}</BlueExpression>'
        f'<MatteExpression>{xml_escape(matte)}</MatteExpression>'
    )

    names_xml = "".join(f'<VariableName{i}>{xml_escape(var_names[i])}</VariableName{i}>' for i in range(8))

    centre_xml = (
        f'<CentreX>{channel(f"scene/{name}/centre/x", centre[0])}</CentreX>'
        f'<CentreY>{channel(f"scene/{name}/centre/y", centre[1])}</CentreY>'
    )

    vars_xml = "".join(
        f'<Variable{i}>{channel(f"scene/{name}/variable{i}", var_vals[i])}</Variable{i}>'
        for i in range(8)
    )

    forms_xml = "".join(
        f'<FormulaName{i}>{xml_escape(forms[i][0])}</FormulaName{i}>'
        f'<FormulaExpression{i}>{xml_escape(forms[i][1])}</FormulaExpression{i}>'
        f'<FormulaType{i}>{forms[i][2]}</FormulaType{i}>'
        for i in range(4)
    )

    xml = f'{base}<State>{exprs}{names_xml}{centre_xml}{vars_xml}{forms_xml}</State></Setup>'

    out_dir = os.path.join(OUT_DIR, category) if category else OUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{name}.pixel_expression_node")
    with open(path, "w") as f:
        f.write(xml)
    print("wrote", os.path.relpath(path, OUT_DIR))


DIST = ("dist", "length(vec2(x - centre.x, y - centre.y))", 0)        # float
DIST3 = ("dist", "length(vec3(r1 - cenR, g1 - cenG, b1 - cenB))", 0)  # float

# Animated 't' (in cycles). Keyframe a variable by giving it a list of (frame, value)
# pairs instead of a scalar; the channel interpolates linearly between them.
ANIM_T2 = [(1, 0.0), (100, 2.0)]   # two cycles over frames 1-100
ANIM_T1 = [(1, 0.0), (100, 1.0)]   # one cycle / full rotation

# --- Procedural-noise expression builders ------------------------------------
# No user-defined functions are available in the node, so noise is inlined. These
# return GLSL strings; parentheses balance by construction.
_NHASH = "vec2(12.9898, 78.233)"
# Pattern offset into the noise field. Changing 'seed' gives a different pattern;
# KEYFRAME 'seed' to drift/evolve the noise over time (it's no longer a static frame).
_SEEDOFF = "vec2(seed, seed * 1.3)"


def _h_ifw(dx, dy):
    """One hash corner using the declared formula i (cell) — for noise_value."""
    return f"fract(sin(dot(i + vec2({dx}, {dy}), {_NHASH})) * 43758.5453)"


# noise_value channel body: bilinear value noise (formulas i, w), shaped by 'gain'.
_VALUE_NOISE = (
    f"mix(mix({_h_ifw('0.0', '0.0')}, {_h_ifw('1.0', '0.0')}, w.x), "
    f"mix({_h_ifw('0.0', '1.0')}, {_h_ifw('1.0', '1.0')}, w.x), w.y)"
)
_VALUE_NOISE_GAINED = f"clamp(({_VALUE_NOISE} - 0.5) * gain + 0.5, 0.0, 1.0)"

# flat per-cell random (no interpolation), with seed offset.
_CELLS_NOISE = (f"fract(sin(dot(floor(vec2(x, y) / cellSize + {_SEEDOFF}), "
                "vec2(12.9898, 78.233))) * 43758.5453)")


def _vnoise_at(pexpr):
    """Self-contained value-noise float expression at vec2 `pexpr` (no formula refs)."""
    i = f"floor({pexpr})"
    f = f"fract({pexpr})"
    w = f"({f} * {f} * (3.0 - 2.0 * {f}))"

    def h(dx, dy):
        return f"fract(sin(dot({i} + vec2({dx}, {dy}), {_NHASH})) * 43758.5453)"

    return (f"mix(mix({h('0.0', '0.0')}, {h('1.0', '0.0')}, {w}.x), "
            f"mix({h('0.0', '1.0')}, {h('1.0', '1.0')}, {w}.x), {w}.y)")


# fbm: 3 octaves; 'lacunarity' = freq step, 'persistence' = amplitude falloff, seed offset.
_FBM_BASE = f"(vec2(x, y) / scale + {_SEEDOFF})"
_FBM_FREQ = ["1.0", "lacunarity", "lacunarity * lacunarity"]
_FBM_AMP = ["1.0", "persistence", "persistence * persistence"]
_FBM_NOISE = ("(" + " + ".join(
    f"{_FBM_AMP[k]} * ({_vnoise_at(f'{_FBM_BASE} * {_FBM_FREQ[k]}')})" for k in range(3)
) + ") / (1.0 + persistence + persistence * persistence)")


def _hash2(c):
    return (f"fract(sin(vec2(dot({c}, vec2(127.1, 311.7)), "
            f"dot({c}, vec2(269.5, 183.3)))) * 43758.5453)")


# voronoi: min distance to feature points in the 3x3 neighbourhood (formulas i, f).
# 'jitter' 0=regular grid .. 1=fully random cell points.
def _voronoi_body():
    terms = []
    for ox in ("-1.0", "0.0", "1.0"):
        for oy in ("-1.0", "0.0", "1.0"):
            off = f"vec2({ox}, {oy})"
            terms.append(f"length({off} + jitter * {_hash2(f'i + {off}')} - f)")
    expr = terms[0]
    for t in terms[1:]:
        expr = f"min({expr}, {t})"
    return expr


_VORONOI = _voronoi_body()

# rgb<->hsv helper formulas (Hocevar, branchless). p=vec4, q=vec4.
HSV_P = ("p", "mix(vec4(b1, g1, -1.0, 0.6666667), vec4(g1, b1, 0.0, -0.3333333), step(b1, g1))", 3)
HSV_Q = ("q", "mix(vec4(p.x, p.y, p.w, r1), vec4(r1, p.y, p.z, p.x), step(p.x, r1))", 3)
_HUE = "abs(q.z + (q.w - q.y) / (6.0 * (q.x - min(q.w, q.y)) + 0.0001))"
_SAT = "(q.x - min(q.w, q.y)) / (q.x + 0.0001)"

# Rec.709 luma — used to hold brightness fixed while chroma is pushed (mix toward it to
# desaturate, past it to saturate).
_LUMA = "dot(vec3(r1, g1, b1), vec3(0.2126, 0.7152, 0.0722))"

# Luma-preserving hue-rotation matrix rows (rotate by formulas c=cos(theta), s=sin(theta)).
_HROT_R = "r1 * (0.299 + 0.701 * c + 0.168 * s) + g1 * (0.587 - 0.587 * c + 0.330 * s) + b1 * (0.114 - 0.114 * c - 0.497 * s)"
_HROT_G = "r1 * (0.299 - 0.299 * c - 0.328 * s) + g1 * (0.587 + 0.413 * c + 0.035 * s) + b1 * (0.114 - 0.114 * c + 0.292 * s)"
_HROT_B = "r1 * (0.299 - 0.300 * c + 1.250 * s) + g1 * (0.587 - 0.588 * c - 1.050 * s) + b1 * (0.114 + 0.886 * c - 0.203 * s)"


def _hue_band(hue_expr, center, halfwidth, soft):
    """0..1 weight that is 1 when hue == center and rolls to 0 at +/-(halfwidth+soft).
    Wrap-around safe (the fract/0.5 trick handles the hue seam)."""
    return (f"(1.0 - smoothstep({halfwidth}, {halfwidth} + {soft}, "
            f"abs(fract(({hue_expr}) - {center} + 0.5) - 0.5)))")


def _hue2rgb(hue):
    """Fully-saturated, full-value RGB for a hue (0..1) — a pure tint colour."""
    return f"clamp(abs(fract({hue} + vec3(1.0, 0.6666667, 0.3333333)) * 6.0 - 3.0) - 1.0, 0.0, 1.0)"


def _HOLLOW(extent):
    """SDF shape fill (formula d) with a `hollow` 0..1 cut-out of the middle. The outer
    edge stays fixed; the hole grows as hollow->1. `extent` = the shape's interior depth."""
    return (f"smoothstep(-soft, soft, d + (1.0 - hollow) * ({extent} + soft)) "
            f"- smoothstep(-soft, soft, d)")


# Two-colour pattern: a 0..1 pattern mask becomes mix(colour A, colour B). Defaults
# black->white so the look is unchanged; set aR/aG/aB and bR/bG/bB for colour (or
# match all three of each for a luminance-only result). Matte = the raw pattern mask.
_COLVARS = [("aR", 0.0), ("aG", 0.0), ("aB", 0.0), ("bR", 1.0), ("bG", 1.0), ("bB", 1.0)]


def _two_color(pattern):
    return {"red": f"mix(aR, bR, {pattern})", "green": f"mix(aG, bG, {pattern})",
            "blue": f"mix(aB, bB, {pattern})", "matte": pattern}


def _solid(expr):
    """Matte-generating setup: write the same 0..1 result to RGB *and* the Matte field."""
    return {"red": expr, "green": expr, "blue": expr, "matte": expr}


# --- Escape-time fractals ----------------------------------------------------
# The node has no reassignable state, so the ONLY way to iterate z is the 4-formula
# chain: formula0 does K inlined steps from the seed, formula1 references formula0 BY
# NAME and does K more, etc. A vec3 carries state: .xy = z (complex), .z = smooth escape
# accumulator. Each step adds step(dot(z,z), bailout) — 1.0 while still inside the bailout
# radius, 0.0 once escaped — so summing across all iterations gives a 0..count "how long it
# survived" value we normalise to 0..1. Deliberately shallow (K*4 iterations): interiors
# read solid, edges band — experimental, not a deep-zoom renderer.
# K is small on purpose: a complex square references z several times, so inlining a step
# expands the string by ~8x. K=2 keeps each formula ~3.7KB (well under the 8KB budget);
# K=3 would blow past 33KB. 8 total iterations is the practical ceiling here.
_FRAC_K = 2                      # iterations per formula slot
_FRAC_FORMULAS = 4               # formula slots used by the chain
_FRAC_TOTAL = _FRAC_K * _FRAC_FORMULAS   # 8 — the accum normaliser
# Pixel mapped to the complex plane relative to the node Centre, scaled by `zoom`.
_FRAC_PIX = "vec2((x - centre.x) / zoom, (y - centre.y) / zoom)"


def _fractal_step(prev, c, abs_z=False):
    """One escape-time iteration as a vec3 expression. `prev` is a vec3 expr (.xy=z,
    .z=accum); `c` is a vec2 expr (the added constant). step() adds 1 while |z|^2<bailout.
    With abs_z (burning_ship) the components fold to abs before squaring."""
    zx = f"abs(({prev}).x)" if abs_z else f"({prev}).x"
    zy = f"abs(({prev}).y)" if abs_z else f"({prev}).y"
    # complex square of (zx,zy) then + c
    nzx = f"({zx}) * ({zx}) - ({zy}) * ({zy}) + ({c}).x"
    nzy = f"2.0 * ({zx}) * ({zy}) + ({c}).y"
    accum = f"({prev}).z + step(dot(({prev}).xy, ({prev}).xy), 4.0)"
    return f"vec3({nzx}, {nzy}, {accum})"


def _fractal_chain(start, c, abs_z=False):
    """Build the 4 formula entries (name, expr, TYPE=2 vec3) for the escape-time chain.
    `start` = vec3 seed expr (.xy=z0, .z=0); `c` = vec2 constant expr. f0 does K steps from
    the seed; f1..f3 each reference the previous formula by name and do K more."""
    forms = []
    prev = start
    for slot in range(_FRAC_FORMULAS):
        expr = prev
        for _ in range(_FRAC_K):
            expr = _fractal_step(expr, c, abs_z)
        name = f"z{slot}"
        forms.append((name, expr, 2))
        prev = name   # next slot references this formula by name (one cheap token)
    return forms


# Smooth 0..1 escape value from the final formula's accumulator (z3.z), normalised by the
# total iteration count. 0 = never escaped (interior), 1 = escaped immediately (far outside).
_FRAC_RAW = f"clamp(z3.z / {float(_FRAC_TOTAL)}, 0.0, 1.0)"
# Shaped output: `gamma` curves the bands (contrast; >1 darkens mids, <1 lifts them), then
# `gain` scales brightness. Both default 1.0 per setup, so the default look is the raw value.
_FRAC_ESCAPE = f"clamp(pow({_FRAC_RAW}, gamma) * gain, 0.0, 1.0)"


# --- Stylization helpers -----------------------------------------------------
# Rec.709 luma of Front 1, clamped to 0..1 (the source tone these looks shade by).
_LUMA01 = f"clamp({_LUMA}, 0.0, 1.0)"


def _seg_eq(n):
    """1.0 when the (rounded) `digit` variable equals integer n, else 0.0. `digit` may be
    fractional from keyframing, so it's rounded with floor(digit + 0.5)."""
    return f"(step({n - 0.5}, floor(digit + 0.5)) * step(floor(digit + 0.5), {n + 0.5}))"


def _seg_bar(cx, cy, hx, hy):
    """0..1 fill of one 7-segment bar: a box centred at (cx,cy) with half-extents (hx,hy)
    in digit-local space (formula `p`). 1 inside, 0 outside, soft 0.04 edge."""
    d = (f"length(max(abs(p - vec2({cx}, {cy})) - vec2({hx}, {hy}), 0.0)) "
         f"+ min(max(abs(p.x - ({cx})) - {hx}, abs(p.y - ({cy})) - {hy}), 0.0)")
    return f"(1.0 - smoothstep(-0.02, 0.02, {d}))"


# 7-segment truth table as on-sets per segment a..g (which digits light each bar).
_SEG_ON = {
    "a": [0, 2, 3, 5, 6, 7, 8, 9], "b": [0, 1, 2, 3, 4, 7, 8, 9],
    "c": [0, 1, 3, 4, 5, 6, 7, 8, 9], "d": [0, 2, 3, 5, 6, 8, 9],
    "e": [0, 2, 6, 8], "f": [0, 4, 5, 6, 8, 9], "g": [2, 3, 4, 5, 6, 8, 9],
}
# Bar geometry in digit-local space: (centre x, centre y, half-w, half-h). `t`=stroke half-
# width (var thick), `hw`/`hh`=bar half-lengths. y up: a=top, g=middle, d=bottom.
_SEG_GEO = {
    "a": ("0.0", "1.0", "hw", "thick"), "b": ("hw", "0.5", "thick", "hh"),
    "c": ("hw", "-0.5", "thick", "hh"), "d": ("0.0", "-1.0", "hw", "thick"),
    "e": ("-hw", "-0.5", "thick", "hh"), "f": ("-hw", "0.5", "thick", "hh"),
    "g": ("0.0", "0.0", "hw", "thick"),
}


def _seven_seg_expr():
    """Union of the lit bars: max over segments of (lit ? fill : 0)."""
    terms = []
    for s in "abcdefg":
        on = " + ".join(_seg_eq(n) for n in _SEG_ON[s])
        cx, cy, hx, hy = _SEG_GEO[s]
        terms.append(f"({on}) * {_seg_bar(cx, cy, hx, hy)}")
    expr = terms[0]
    for t in terms[1:]:
        expr = f"max({expr}, {t})"
    return expr


# Per-pixel stylizations of Front 1 (no neighbour gather). Appended to SETUPS below.
_STYLIZATION = [
    # Halftone dots — rotate coords by `angle`, tile into `cell`-px cells, draw a dot
    # whose radius tracks the cell luma. Formula `lp` = rotated coords; `dot` = cell-local
    # distance-to-centre minus the luma-driven radius. Two-colour (paper -> ink).
    dict(name="halftone",
         **_two_color("smoothstep(-1.5, 1.5, dot)"),
         variables=[("cell", 12), ("angle", 0.4)] + _COLVARS,
         formulas=[("lp", "vec2(cos(angle) * (x - centre.x) - sin(angle) * (y - centre.y), sin(angle) * (x - centre.x) + cos(angle) * (y - centre.y))", 1),
                   ("dot", f"length(mod(lp, cell) - cell * 0.5) - cell * 0.5 * sqrt({_LUMA01})", 0)]),

    # Ordered 4x4 Bayer dithering — `bv` is the dispersed threshold (0..1) built by index
    # math (NO loop): interleave the low 2 bits of int(x),int(y). Luma is posterized to
    # `levels` steps with the per-pixel threshold dithered in. Classic 1-bit / GameBoy look.
    dict(name="bayer_dither",
         **_two_color("floor(luma * (levels - 1.0) + bv) / max(levels - 1.0, 1.0)"),
         variables=[("levels", 2.0)] + _COLVARS,
         formulas=[("px", "vec2(mod(floor(x), 4.0), mod(floor(y), 4.0))", 1),
                   ("bv", "(mod(px.x, 2.0) * 8.0 + mod(px.y, 2.0) * 4.0 + floor(px.x / 2.0) * 2.0 + floor(px.y / 2.0) + 0.5) / 16.0", 0),
                   ("luma", _LUMA01, 0)]),

    # Pen crosshatch — 4 line sets (0/45/90/135 deg) switch on as luma drops through 4 even
    # thresholds (darker = more directions = denser shading). `hatch` = product of the
    # active line masks (1=paper); output ink-on-paper. `spacing` px, `lineW` 0..1 weight.
    dict(name="crosshatch",
         **_two_color("1.0 - hatch"),
         variables=[("spacing", 8), ("lineW", 0.5)] + _COLVARS,
         formulas=[("lum", _LUMA01, 0),
                   ("hatch",
                    "(lum > 0.8 ? 1.0 : smoothstep(0.0, lineW, abs(sin(PI * y / spacing)))) * "
                    "(lum > 0.6 ? 1.0 : smoothstep(0.0, lineW, abs(sin(PI * (x + y) * 0.7071 / spacing)))) * "
                    "(lum > 0.4 ? 1.0 : smoothstep(0.0, lineW, abs(sin(PI * x / spacing)))) * "
                    "(lum > 0.2 ? 1.0 : smoothstep(0.0, lineW, abs(sin(PI * (x - y) * 0.7071 / spacing))))", 0)]),

    # CRT / VHS look — multiply Front 1 by a scanline darkening (function of y), an RGB
    # phosphor-triad mask (x mod 3 picks the bright channel), a radial vignette, and an
    # animated rolling bright bar (KEYFRAME `roll` 0..1 to crawl it up the frame).
    # `scanDepth`/`maskDepth`/`vignette` 0..1 dial each effect; `scanFreq` = scanline pitch.
    dict(name="crt",
         red="r1 * tone * (1.0 - maskDepth * (1.0 - step(mod(floor(x), 3.0), 0.5)))",
         green="g1 * tone * (1.0 - maskDepth * (1.0 - step(abs(mod(floor(x), 3.0) - 1.0), 0.5)))",
         blue="b1 * tone * (1.0 - maskDepth * (1.0 - step(2.5, mod(floor(x), 3.0) + 1.0)))",
         matte="m1",
         variables=[("scanDepth", 0.3), ("maskDepth", 0.3), ("vignette", 0.4),
                    ("scanFreq", 1.5), ("roll", ANIM_T1)],
         formulas=[("vig", "1.0 - vignette * smoothstep(0.4 * height, 0.75 * height, length(vec2(x - width * 0.5, y - height * 0.5)))", 0),
                   ("bar", "1.0 + 0.4 * smoothstep(0.85, 1.0, cos((y / height - roll) * 2.0 * PI))", 0),
                   ("tone", "vig * bar * (1.0 - scanDepth * (0.5 + 0.5 * sin(y * scanFreq)))", 0)]),

    # Truchet tiles — per `tile`-px cell, hash the cell (_hash2) to pick one of two diagonal
    # arc orientations; draw two quarter-circle arcs of width `lineW` centred on opposite
    # corners so they connect across edges into endless maze/circuit lines. `tp` = cell-
    # local coords (0..1), `flip` = the hashed orientation, `arc` = px distance to the arcs.
    dict(name="truchet",
         **_two_color("1.0 - smoothstep(lineW - 1.5, lineW + 1.5, arc)"),
         variables=[("tile", 40), ("lineW", 4.0)] + _COLVARS,
         formulas=[("tp", "mod(vec2(x, y), tile) / tile", 1),
                   ("flip", f"step(0.5, {_hash2('floor(vec2(x, y) / tile)')}.x)", 0),
                   ("arc",
                    "min("
                    "abs(length(mix(tp, vec2(1.0 - tp.x, tp.y), flip)) - 0.5), "
                    "abs(length(mix(tp, vec2(1.0 - tp.x, tp.y), flip) - vec2(1.0, 1.0)) - 0.5)) * tile", 0)]),

    # Palette quantize — snap Front 1 to `levels` tonal steps (a clean, budget-friendly
    # stand-in for an N-colour palette), then tint the result between two palette anchors
    # via _two_color driven by the quantized luma. Default 4-tone; set the A/B colours to a
    # dark/light green for the classic Game-Boy palette.
    dict(name="palette_quantize",
         red="mix(aR, bR, q)", green="mix(aG, bG, q)", blue="mix(aB, bB, q)", matte="q",
         variables=[("levels", 4.0)] + _COLVARS,
         formulas=[("q", f"floor({_LUMA01} * levels) / max(levels - 1.0, 1.0)", 0)]),

    # Seven-segment digit — one SDF 7-segment digit burned into the frame with NO text node.
    # `digit` 0..9 (KEYFRAME it for a frame counter) lights bars via an arithmetic truth
    # table; `seg` = union of the lit bars. Drawn at Centre; `digScale` px = vertical half-
    # size; `thick` = stroke half-width; `hw`/`hh` = bar half-lengths. Two-colour (bg->lit).
    dict(name="seven_segment",
         red="mix(0.0, lit, seg)", green="mix(0.05, lit, seg)", blue="mix(0.0, lit, seg)",
         matte="seg",
         variables=[("digit", 0.0), ("digScale", 150), ("thick", 0.1),
                    ("hw", 0.42), ("hh", 0.42), ("lit", 1.0)],
         formulas=[("p", "vec2(x - centre.x, y - centre.y) / digScale", 1),
                   ("seg", _seven_seg_expr(), 0)]),
]

SETUPS = [
    # ST / UV map — feed a warp; red=u, green=v.
    dict(name="stmap",
         red="(x + 0.5) / width", green="(y + 0.5) / height",
         blue="0.0", matte="1.0"),

    # Radial ramp / vignette — white centre to black at 'radius'.
    # 'softness' 0..1: 0 = hard circle, 1 = full smooth falloff from centre.
    dict(name="radial_ramp",
         **_two_color("1.0 - smoothstep(radius * (1.0 - softness), radius, dist)"),
         variables=[("radius", 600), ("softness", 1.0)] + _COLVARS, formulas=[DIST]),

    # Concentric rings — 'freq' controls spacing (use Space+Drag for hundredths).
    dict(name="rings",
         **_two_color("(sin(dist * freq) + 1.0) / 2.0"),
         variables=[("freq", 0.05)] + _COLVARS, formulas=[DIST]),

    # Radial rays — 'rays' = count, 'rot' = rotation (radians).
    dict(name="rays",
         **_two_color("(sin((atan(y - centre.y, x - centre.x) + rot) * rays) + 1.0) / 2.0"),
         variables=[("rays", 8), ("rot", 0)] + _COLVARS),

    # Green despill — 'spill' 0..1 blends from none to full despill.
    dict(name="despill_green",
         red="r1",
         green="mix(g1, min(g1, (r1 + b1) / 2.0), spill)",
         blue="b1", matte="m1",
         variables=[("spill", 1.0)]),

    # P-matte sphere — Front 1 = P-world pass (r=X,g=Y,b=Z). Output as RGB matte.
    dict(name="pmatte_sphere",
         red="clamp(1.0 - dist / prad, 0.0, 1.0)",
         green="clamp(1.0 - dist / prad, 0.0, 1.0)",
         blue="clamp(1.0 - dist / prad, 0.0, 1.0)",
         matte="clamp(1.0 - dist / prad, 0.0, 1.0)",
         variables=[("cenR", 0), ("cenG", 0), ("cenB", 0), ("prad", 1.0)],
         formulas=[DIST3]),

    # NaN / Inf cleanup — replace bad pixels with 0 (swap 0.0 for r2/g2/b2 to patch from Front 2).
    dict(name="nan_cleanup",
         red="isnan(r1) || isinf(r1) ? 0.0 : r1",
         green="isnan(g1) || isinf(g1) ? 0.0 : g1",
         blue="isnan(b1) || isinf(b1) ? 0.0 : b1",
         matte="m1"),

    # Alpha crunch — matte below 'thresh' -> 0 (RGB passthrough).
    dict(name="alpha_crunch",
         red="r1", green="g1", blue="b1",
         matte="m1 < thresh ? 0.0 : m1",
         variables=[("thresh", 1.0)]),

    # --- Wave 2 -------------------------------------------------------------

    # Fill alpha — any matte above 0 -> 1 (RGB passthrough).
    dict(name="fill_alpha",
         red="r1", green="g1", blue="b1",
         matte="m1 > 0.0 ? 1.0 : m1"),

    # Alpha fringe — isolate matte edges (peaks at 0.5).
    dict(name="alpha_fringe",
         red="r1", green="g1", blue="b1",
         matte="4.0 * (1.0 - m1) * m1"),

    # Saturation — 'sat' 0=greyscale, 1=normal, >1=boosted.
    dict(name="saturation",
         red="mix(dot(vec3(r1, g1, b1), vec3(0.2126, 0.7152, 0.0722)), r1, sat)",
         green="mix(dot(vec3(r1, g1, b1), vec3(0.2126, 0.7152, 0.0722)), g1, sat)",
         blue="mix(dot(vec3(r1, g1, b1), vec3(0.2126, 0.7152, 0.0722)), b1, sat)",
         matte="m1", variables=[("sat", 1.0)]),

    # Luma key — soft key between 'lo' and 'hi' luminance; on Result AND OutMatte.
    dict(name="luma_key",
         red="smoothstep(lo, hi, dot(vec3(r1, g1, b1), vec3(0.2126, 0.7152, 0.0722)))",
         green="smoothstep(lo, hi, dot(vec3(r1, g1, b1), vec3(0.2126, 0.7152, 0.0722)))",
         blue="smoothstep(lo, hi, dot(vec3(r1, g1, b1), vec3(0.2126, 0.7152, 0.0722)))",
         matte="smoothstep(lo, hi, dot(vec3(r1, g1, b1), vec3(0.2126, 0.7152, 0.0722)))",
         variables=[("lo", 0.3), ("hi", 0.7)]),

    # Difference matte — Front 1 vs Front 2 (clean plate); 'gain' scales the result.
    dict(name="difference_matte",
         red="clamp(length(vec3(r1 - r2, g1 - g2, b1 - b2)) * gain, 0.0, 1.0)",
         green="clamp(length(vec3(r1 - r2, g1 - g2, b1 - b2)) * gain, 0.0, 1.0)",
         blue="clamp(length(vec3(r1 - r2, g1 - g2, b1 - b2)) * gain, 0.0, 1.0)",
         matte="clamp(length(vec3(r1 - r2, g1 - g2, b1 - b2)) * gain, 0.0, 1.0)",
         variables=[("gain", 5.0)]),

    # Voxelize / posterize — quantize colour to 'scale' steps.
    dict(name="voxelize",
         red="floor(r1 * scale) / scale",
         green="floor(g1 * scale) / scale",
         blue="floor(b1 * scale) / scale",
         matte="m1", variables=[("scale", 10.0)]),

    # Normal relight — Front 1 = normal pass (-1..1); 'l*' = light direction.
    dict(name="normal_relight",
         red="max(dot(normalize(vec3(r1, g1, b1)), normalize(vec3(lx, ly, lz))), 0.0)",
         green="max(dot(normalize(vec3(r1, g1, b1)), normalize(vec3(lx, ly, lz))), 0.0)",
         blue="max(dot(normalize(vec3(r1, g1, b1)), normalize(vec3(lx, ly, lz))), 0.0)",
         matte="m1", variables=[("lx", 0.0), ("ly", 0.0), ("lz", 1.0)]),

    # Checkerboard — 'size' = square size in pixels.
    dict(name="checkerboard",
         **_two_color("mod(floor(x / size) + floor(y / size), 2.0)"),
         variables=[("size", 64)] + _COLVARS),

    # Bricks — 'bw'/'bh' brick width/height; alternate rows offset by half a brick.
    dict(name="bricks",
         **_two_color("mod(floor((x + mod(row, 2.0) * bw * 0.5) / bw) + row, 2.0)"),
         variables=[("bw", 128), ("bh", 64)] + _COLVARS,
         formulas=[("row", "floor(y / bh)", 0)]),

    # Random value noise — per-pixel hash (replaces Nuke random()).
    dict(name="noise_random",
         red="fract(sin(dot(vec2(x, y), vec2(12.9898, 78.233))) * 43758.5453)",
         green="fract(sin(dot(vec2(x, y), vec2(39.346, 11.135))) * 43758.5453)",
         blue="fract(sin(dot(vec2(x, y), vec2(73.156, 52.235))) * 43758.5453)",
         matte="1.0"),

    # P-matte rings — 3D concentric rings around the centre point.
    dict(name="pmatte_rings",
         red="(sin(dist * ringScale) + 1.0) / 2.0",
         green="(sin(dist * ringScale) + 1.0) / 2.0",
         blue="(sin(dist * ringScale) + 1.0) / 2.0",
         matte="(sin(dist * ringScale) + 1.0) / 2.0",
         variables=[("cenR", 0), ("cenG", 0), ("cenB", 0), ("ringScale", 10.0)],
         formulas=[DIST3]),

    # P-matte rays — 3D rays on the X-Z plane; 'rays' = count.
    dict(name="pmatte_rays",
         red="(sin(atan(b1 - cenB, r1 - cenR) * rays) + 1.0) / 2.0",
         green="(sin(atan(b1 - cenB, r1 - cenR) * rays) + 1.0) / 2.0",
         blue="(sin(atan(b1 - cenB, r1 - cenR) * rays) + 1.0) / 2.0",
         matte="(sin(atan(b1 - cenB, r1 - cenR) * rays) + 1.0) / 2.0",
         variables=[("cenR", 0), ("cenB", 0), ("rays", 8)]),

    # Box P-matte — axis-aligned cube around centre; 'boxSize' half-extent, 'soft' edge.
    dict(name="box_matte",
         red="(1.0 - smoothstep(boxSize * (1.0 - soft), boxSize, abs(r1 - cenR))) * (1.0 - smoothstep(boxSize * (1.0 - soft), boxSize, abs(g1 - cenG))) * (1.0 - smoothstep(boxSize * (1.0 - soft), boxSize, abs(b1 - cenB)))",
         green="(1.0 - smoothstep(boxSize * (1.0 - soft), boxSize, abs(r1 - cenR))) * (1.0 - smoothstep(boxSize * (1.0 - soft), boxSize, abs(g1 - cenG))) * (1.0 - smoothstep(boxSize * (1.0 - soft), boxSize, abs(b1 - cenB)))",
         blue="(1.0 - smoothstep(boxSize * (1.0 - soft), boxSize, abs(r1 - cenR))) * (1.0 - smoothstep(boxSize * (1.0 - soft), boxSize, abs(g1 - cenG))) * (1.0 - smoothstep(boxSize * (1.0 - soft), boxSize, abs(b1 - cenB)))",
         matte="(1.0 - smoothstep(boxSize * (1.0 - soft), boxSize, abs(r1 - cenR))) * (1.0 - smoothstep(boxSize * (1.0 - soft), boxSize, abs(g1 - cenG))) * (1.0 - smoothstep(boxSize * (1.0 - soft), boxSize, abs(b1 - cenB)))",
         variables=[("cenR", 0), ("cenG", 0), ("cenB", 0), ("boxSize", 1.0), ("soft", 0.5)]),

    # --- Wave 3: animated generators (keyframed 't') ------------------------
    # All scroll horizontally as 't' advances. 'wavelength' = period in pixels.
    # Scrub frames 1-100 to see motion.

    # Sine wave — smooth scrolling bands.
    dict(name="wave_sine",
         **_two_color("(sin((x / wavelength + t) * 2.0 * PI) + 1.0) / 2.0"),
         variables=[("wavelength", 200), ("t", ANIM_T2)] + _COLVARS),

    # Triangle wave — linear up/down ramp.
    dict(name="wave_triangle",
         **_two_color("abs(2.0 * fract(x / wavelength + t) - 1.0)"),
         variables=[("wavelength", 200), ("t", ANIM_T2)] + _COLVARS),

    # Square wave — hard on/off stripes.
    dict(name="wave_square",
         **_two_color("step(0.5, fract(x / wavelength + t))"),
         variables=[("wavelength", 200), ("t", ANIM_T2)] + _COLVARS),

    # Sawtooth wave — repeating 0->1 ramp.
    dict(name="wave_sawtooth",
         **_two_color("fract(x / wavelength + t)"),
         variables=[("wavelength", 200), ("t", ANIM_T2)] + _COLVARS),

    # Pulse rings — concentric rings expanding from Centre over time.
    dict(name="pulse_rings",
         **_two_color("(sin(dist / wavelength * 2.0 * PI - t * 2.0 * PI) + 1.0) / 2.0"),
         variables=[("wavelength", 100), ("t", ANIM_T2)] + _COLVARS, formulas=[DIST]),

    # Spin rays — radial rays rotating around Centre; 't' 0->1 = one full turn.
    dict(name="spin_rays",
         **_two_color("(sin((atan(y - centre.y, x - centre.x) + t * 2.0 * PI) * rays) + 1.0) / 2.0"),
         variables=[("rays", 8), ("t", ANIM_T1)] + _COLVARS),

    # --- Depth toolkit -----------------------------------------------------
    # Convention: DEPTH always arrives on Matte 1 (m1). Defaults assume depth
    # normalised to 0..1 (near=0, far=1); for raw world-unit depth, set near/far/
    # thresholds to your scene range. If closer = larger in your pass, swap near/far.

    # Normalize depth — remap raw depth to a viewable 0..1. Connect depth to Matte 1;
    # view OutMatte (or also wire depth to Front 1 to see it on Result).
    dict(name="depth_normalize",
         red="clamp((m1 - near) / (far - near), 0.0, 1.0)",
         green="clamp((m1 - near) / (far - near), 0.0, 1.0)",
         blue="clamp((m1 - near) / (far - near), 0.0, 1.0)",
         matte="clamp((m1 - near) / (far - near), 0.0, 1.0)",
         variables=[("near", 0.0), ("far", 1.0)]),

    # Depth matte — isolate a depth band [zMin..zMax] with 'soft' edges. Depth on Matte 1.
    dict(name="depth_matte",
         red="smoothstep(zMin - soft, zMin, m1) * (1.0 - smoothstep(zMax, zMax + soft, m1))",
         green="smoothstep(zMin - soft, zMin, m1) * (1.0 - smoothstep(zMax, zMax + soft, m1))",
         blue="smoothstep(zMin - soft, zMin, m1) * (1.0 - smoothstep(zMax, zMax + soft, m1))",
         matte="smoothstep(zMin - soft, zMin, m1) * (1.0 - smoothstep(zMax, zMax + soft, m1))",
         variables=[("zMin", 0.2), ("zMax", 0.6), ("soft", 0.05)]),

    # Depth fog / atmosphere — blend beauty toward fog colour with distance.
    # Front 1 = beauty, Matte 1 = depth.
    dict(name="depth_fog",
         red="mix(r1, fogR, smoothstep(near, far, m1))",
         green="mix(g1, fogG, smoothstep(near, far, m1))",
         blue="mix(b1, fogB, smoothstep(near, far, m1))",
         matte="m1",
         variables=[("near", 0.0), ("far", 1.0),
                    ("fogR", 0.7), ("fogG", 0.8), ("fogB", 0.9)]),

    # Depth fade — fade beauty (colour AND alpha) to nothing with distance.
    # Front 1 = beauty, Matte 1 = depth.
    dict(name="depth_fade",
         red="r1 * (1.0 - smoothstep(near, far, m1))",
         green="g1 * (1.0 - smoothstep(near, far, m1))",
         blue="b1 * (1.0 - smoothstep(near, far, m1))",
         matte="m1 * (1.0 - smoothstep(near, far, m1))",
         variables=[("near", 0.0), ("far", 1.0)]),

    # Depth mix — composite Front 1 (near) over Front 2 (far) at 'zThresh', 'soft' edge.
    # Front 1 = plate A, Front 2 = plate B, Matte 1 = depth.
    dict(name="depth_mix",
         red="mix(r1, r2, smoothstep(zThresh - soft, zThresh + soft, m1))",
         green="mix(g1, g2, smoothstep(zThresh - soft, zThresh + soft, m1))",
         blue="mix(b1, b2, smoothstep(zThresh - soft, zThresh + soft, m1))",
         matte="m1",
         variables=[("zThresh", 0.5), ("soft", 0.05)]),

    # DOF mask — 0 at the 'focus' plane, ramping to 1 over 'range'. Feed this to a
    # Defocus node's blur-amount input. Depth on Matte 1.
    dict(name="depth_dof_mask",
         red="clamp(abs(m1 - focus) / range, 0.0, 1.0)",
         green="clamp(abs(m1 - focus) / range, 0.0, 1.0)",
         blue="clamp(abs(m1 - focus) / range, 0.0, 1.0)",
         matte="clamp(abs(m1 - focus) / range, 0.0, 1.0)",
         variables=[("focus", 0.5), ("range", 0.2)]),

    # Depth contours — topographic iso-lines every 'spacing' in depth. Depth on Matte 1.
    dict(name="depth_contours",
         red="1.0 - smoothstep(0.0, lineWidth, min(fract(m1 / spacing), 1.0 - fract(m1 / spacing)))",
         green="1.0 - smoothstep(0.0, lineWidth, min(fract(m1 / spacing), 1.0 - fract(m1 / spacing)))",
         blue="1.0 - smoothstep(0.0, lineWidth, min(fract(m1 / spacing), 1.0 - fract(m1 / spacing)))",
         matte="1.0 - smoothstep(0.0, lineWidth, min(fract(m1 / spacing), 1.0 - fract(m1 / spacing)))",
         variables=[("spacing", 0.1), ("lineWidth", 0.05)]),

    # Depth posterize — quantize depth into 'steps' flat bands (cards / stylised). Matte 1.
    dict(name="depth_posterize",
         red="floor(m1 * steps) / steps",
         green="floor(m1 * steps) / steps",
         blue="floor(m1 * steps) / steps",
         matte="floor(m1 * steps) / steps",
         variables=[("steps", 8)]),

    # Depth grade — multiply beauty by a gain that ramps with distance (near->far).
    # Front 1 = beauty, Matte 1 = depth.
    dict(name="depth_grade",
         red="r1 * mix(gainNear, gainFar, smoothstep(near, far, m1))",
         green="g1 * mix(gainNear, gainFar, smoothstep(near, far, m1))",
         blue="b1 * mix(gainNear, gainFar, smoothstep(near, far, m1))",
         matte="m1",
         variables=[("near", 0.0), ("far", 1.0), ("gainNear", 1.0), ("gainFar", 0.3)]),

    # --- AOV compositing ---------------------------------------------------
    # Only 2 RGB inputs, so these do pairwise pass math; CHAIN nodes to rebuild a
    # full beauty (out -> next node's Front 1 = running sum). Light passes keep
    # Front 1's alpha (matte = m1).

    # AOV add — sum two light passes with per-pass gain (diffuse + specular, etc.).
    dict(name="aov_add",
         red="r1 * gainA + r2 * gainB",
         green="g1 * gainA + g2 * gainB",
         blue="b1 * gainA + b2 * gainB",
         matte="m1",
         variables=[("gainA", 1.0), ("gainB", 1.0)]),

    # AOV grade + add — Front 1 = running beauty, Front 2 = one pass; tint/expose that
    # pass, then add it back. The core "isolate an AOV, grade it, recombine" move.
    dict(name="aov_grade_add",
         red="r1 + r2 * tintR * exposure",
         green="g1 + g2 * tintG * exposure",
         blue="b1 + b2 * tintB * exposure",
         matte="m1",
         variables=[("exposure", 1.0), ("tintR", 1.0), ("tintG", 1.0), ("tintB", 1.0)]),

    # AO multiply — multiply beauty by an AO pass (Matte 1); 'amount' blends it in,
    # 'aoGamma' shapes it. Front 1 = beauty, Matte 1 = AO.
    dict(name="ao_multiply",
         red="r1 * mix(1.0, pow(clamp(m1, 0.0, 1.0), aoGamma), amount)",
         green="g1 * mix(1.0, pow(clamp(m1, 0.0, 1.0), aoGamma), amount)",
         blue="b1 * mix(1.0, pow(clamp(m1, 0.0, 1.0), aoGamma), amount)",
         matte="m1",
         variables=[("amount", 1.0), ("aoGamma", 1.0)]),

    # Albedo divide — extract lighting from a beauty by dividing out albedo.
    # Front 1 = beauty, Front 2 = albedo. (Guards divide-by-zero.)
    dict(name="albedo_divide",
         red="r2 > 0.0 ? r1 / r2 : 0.0",
         green="g2 > 0.0 ? g1 / g2 : 0.0",
         blue="b2 > 0.0 ? b1 / b2 : 0.0",
         matte="m1"),

    # Albedo multiply (relight) — recombine a graded albedo with a lighting pass.
    # Front 1 = albedo, Front 2 = lighting.
    dict(name="albedo_multiply",
         red="r1 * r2", green="g1 * g2", blue="b1 * b2", matte="m1"),

    # AOV clamp negative — remove sub-zero values renderers sometimes emit. Front 1.
    dict(name="aov_clamp_negative",
         red="max(r1, 0.0)", green="max(g1, 0.0)", blue="max(b1, 0.0)", matte="m1"),

    # Screen merge — screen Front 2 (glow/bloom pass) onto Front 1; 'gain' scales it.
    dict(name="screen_merge",
         red="1.0 - (1.0 - r1) * (1.0 - clamp(r2 * gain, 0.0, 1.0))",
         green="1.0 - (1.0 - g1) * (1.0 - clamp(g2 * gain, 0.0, 1.0))",
         blue="1.0 - (1.0 - b1) * (1.0 - clamp(b2 * gain, 0.0, 1.0))",
         matte="m1", variables=[("gain", 1.0)]),

    # ID isolate — grade only the region picked by an ID/mask pass on Matte 1.
    # Front 1 = beauty, Matte 1 = mask. Outside the mask passes through untouched.
    dict(name="id_isolate",
         red="mix(r1, r1 * tintR * gain, clamp(m1, 0.0, 1.0))",
         green="mix(g1, g1 * tintG * gain, clamp(m1, 0.0, 1.0))",
         blue="mix(b1, b1 * tintB * gain, clamp(m1, 0.0, 1.0))",
         matte="m1",
         variables=[("gain", 1.0), ("tintR", 1.0), ("tintG", 1.0), ("tintB", 1.0)]),

    # Fresnel / facing ratio — rim matte from a camera-space normal pass (Front 1, -1..1).
    # b1 = normal.z (1 facing camera, 0 grazing); 'power' shapes the falloff.
    dict(name="fresnel_facing",
         red="pow(1.0 - clamp(b1, 0.0, 1.0), power)",
         green="pow(1.0 - clamp(b1, 0.0, 1.0), power)",
         blue="pow(1.0 - clamp(b1, 0.0, 1.0), power)",
         matte="pow(1.0 - clamp(b1, 0.0, 1.0), power)",
         variables=[("power", 2.0)]),

    # Cryptomatte ID picker (2 ranks) — extract a matte for object hash 'id'.
    # Shuffle one crypto layer so Front 1 = (hash0, cov0, hash1) and Matte 1 = cov1.
    # 'id' = the object's float32 hash from the manifest; 'tol' = relative match tolerance.
    # Crypto pass MUST be read raw/unfiltered (no resize, no colour management).
    dict(name="crypto_pick_2rank",
         red="clamp((abs(r1 - id) <= abs(id) * tol ? g1 : 0.0) + (abs(b1 - id) <= abs(id) * tol ? m1 : 0.0), 0.0, 1.0)",
         green="clamp((abs(r1 - id) <= abs(id) * tol ? g1 : 0.0) + (abs(b1 - id) <= abs(id) * tol ? m1 : 0.0), 0.0, 1.0)",
         blue="clamp((abs(r1 - id) <= abs(id) * tol ? g1 : 0.0) + (abs(b1 - id) <= abs(id) * tol ? m1 : 0.0), 0.0, 1.0)",
         matte="clamp((abs(r1 - id) <= abs(id) * tol ? g1 : 0.0) + (abs(b1 - id) <= abs(id) * tol ? m1 : 0.0), 0.0, 1.0)",
         variables=[("id", 0.0), ("tol", 0.00001)]),

    # Cryptomatte ID picker (4 ranks) — two crypto layers for cleaner AA edges.
    # Front 1 = (hash0, cov0, hash1), Matte 1 = cov1; Front 2 = (hash2, cov2, hash3),
    # Matte 2 = cov3. Sums coverage across all 4 ranks matching 'id'.
    dict(name="crypto_pick_4rank",
         red="clamp((abs(r1 - id) <= abs(id) * tol ? g1 : 0.0) + (abs(b1 - id) <= abs(id) * tol ? m1 : 0.0) + (abs(r2 - id) <= abs(id) * tol ? g2 : 0.0) + (abs(b2 - id) <= abs(id) * tol ? m2 : 0.0), 0.0, 1.0)",
         green="clamp((abs(r1 - id) <= abs(id) * tol ? g1 : 0.0) + (abs(b1 - id) <= abs(id) * tol ? m1 : 0.0) + (abs(r2 - id) <= abs(id) * tol ? g2 : 0.0) + (abs(b2 - id) <= abs(id) * tol ? m2 : 0.0), 0.0, 1.0)",
         blue="clamp((abs(r1 - id) <= abs(id) * tol ? g1 : 0.0) + (abs(b1 - id) <= abs(id) * tol ? m1 : 0.0) + (abs(r2 - id) <= abs(id) * tol ? g2 : 0.0) + (abs(b2 - id) <= abs(id) * tol ? m2 : 0.0), 0.0, 1.0)",
         matte="clamp((abs(r1 - id) <= abs(id) * tol ? g1 : 0.0) + (abs(b1 - id) <= abs(id) * tol ? m1 : 0.0) + (abs(r2 - id) <= abs(id) * tol ? g2 : 0.0) + (abs(b2 - id) <= abs(id) * tol ? m2 : 0.0), 0.0, 1.0)",
         variables=[("id", 0.0), ("tol", 0.00001)]),

    # --- UV / lens distortion ----------------------------------------------
    # All generate 0..1 ST/UV maps (red=U, green=V) to feed an STMap node.
    # nx/ny are centred coords normalised by half-WIDTH (so distortion is isotropic
    # at any aspect ratio); green re-applies the width/height ratio on the way out.

    # Lens distort — radial barrel/pincushion (k1, k2). k1>0 pincushion, k1<0 barrel.
    dict(name="lens_distort",
         red="0.5 + nx * f * 0.5",
         green="0.5 + ny * f * 0.5 * (width / height)",
         blue="0.0", matte="1.0",
         variables=[("k1", 0.1), ("k2", 0.0)],
         formulas=[("nx", "(x + 0.5 - width / 2.0) / (width / 2.0)", 0),
                   ("ny", "(y + 0.5 - height / 2.0) / (width / 2.0)", 0),
                   ("f", "1.0 + k1 * (nx * nx + ny * ny) + k2 * (nx * nx + ny * ny) * (nx * nx + ny * ny)", 0)]),

    # Lens undistort — approximate inverse of the same radial model (divides instead).
    dict(name="lens_undistort",
         red="0.5 + nx * f * 0.5",
         green="0.5 + ny * f * 0.5 * (width / height)",
         blue="0.0", matte="1.0",
         variables=[("k1", 0.1), ("k2", 0.0)],
         formulas=[("nx", "(x + 0.5 - width / 2.0) / (width / 2.0)", 0),
                   ("ny", "(y + 0.5 - height / 2.0) / (width / 2.0)", 0),
                   ("f", "1.0 / (1.0 + k1 * (nx * nx + ny * ny) + k2 * (nx * nx + ny * ny) * (nx * nx + ny * ny))", 0)]),

    # Anamorphic unsqueeze — stretch horizontally by 'squeeze' (2.0 = 2x anamorphic).
    dict(name="anamorphic_unsqueeze",
         red="0.5 + ((x + 0.5) / width - 0.5) / squeeze",
         green="(y + 0.5) / height",
         blue="0.0", matte="1.0",
         variables=[("squeeze", 2.0)]),

    # UV transform — zoom/pan a source via STMap. 'zoom' >1 zooms in; pan in UV units.
    dict(name="uv_transform",
         red="0.5 + ((x + 0.5) / width - 0.5) / zoom - panX",
         green="0.5 + ((y + 0.5) / height - 0.5) / zoom - panY",
         blue="0.0", matte="1.0",
         variables=[("zoom", 1.0), ("panX", 0.0), ("panY", 0.0)]),

    # --- Colour-space & grade ----------------------------------------------

    # Exposure — multiply by 2^stops. Front 1.
    dict(name="exposure",
         red="r1 * pow(2.0, stops)", green="g1 * pow(2.0, stops)",
         blue="b1 * pow(2.0, stops)", matte="m1",
         variables=[("stops", 0.0)]),

    # Contrast — scale around a 'pivot' (scene-linear 0.18 by default). Front 1.
    dict(name="contrast",
         red="(r1 - pivot) * contrast + pivot",
         green="(g1 - pivot) * contrast + pivot",
         blue="(b1 - pivot) * contrast + pivot",
         matte="m1", variables=[("contrast", 1.0), ("pivot", 0.18)]),

    # Lift / gamma / gain — master tonal grade. Front 1.
    dict(name="lift_gamma_gain",
         red="pow(max(r1 * gain + lift, 0.0), 1.0 / gamma)",
         green="pow(max(g1 * gain + lift, 0.0), 1.0 / gamma)",
         blue="pow(max(b1 * gain + lift, 0.0), 1.0 / gamma)",
         matte="m1", variables=[("lift", 0.0), ("gamma", 1.0), ("gain", 1.0)]),

    # White balance — per-channel gain to neutralise a colour cast. Front 1.
    dict(name="white_balance",
         red="r1 * gainR", green="g1 * gainG", blue="b1 * gainB", matte="m1",
         variables=[("gainR", 1.0), ("gainG", 1.0), ("gainB", 1.0)]),

    # sRGB -> linear (exact piecewise). Front 1.
    dict(name="srgb_to_linear",
         red="r1 <= 0.04045 ? r1 / 12.92 : pow((r1 + 0.055) / 1.055, 2.4)",
         green="g1 <= 0.04045 ? g1 / 12.92 : pow((g1 + 0.055) / 1.055, 2.4)",
         blue="b1 <= 0.04045 ? b1 / 12.92 : pow((b1 + 0.055) / 1.055, 2.4)",
         matte="m1"),

    # linear -> sRGB (exact piecewise). Front 1.
    dict(name="linear_to_srgb",
         red="r1 <= 0.0031308 ? r1 * 12.92 : 1.055 * pow(r1, 1.0 / 2.4) - 0.055",
         green="g1 <= 0.0031308 ? g1 * 12.92 : 1.055 * pow(g1, 1.0 / 2.4) - 0.055",
         blue="b1 <= 0.0031308 ? b1 * 12.92 : 1.055 * pow(b1, 1.0 / 2.4) - 0.055",
         matte="m1"),

    # --- Procedural noise --------------------------------------------------
    # Generators driven by x/y. No user functions in the node, so noise is inlined.

    # Flat per-cell random — blocky value per `cellSize`-pixel cell. Keyframe `seed` to evolve.
    dict(name="noise_cells",
         red=_CELLS_NOISE, green=_CELLS_NOISE, blue=_CELLS_NOISE, matte="1.0",
         variables=[("cellSize", 64), ("seed", 0.0)]),

    # Smooth value noise — `scale` = feature size, `gain` = contrast, `seed` = pattern/drift.
    dict(name="noise_value",
         red=_VALUE_NOISE_GAINED, green=_VALUE_NOISE_GAINED, blue=_VALUE_NOISE_GAINED, matte="1.0",
         variables=[("scale", 80), ("seed", 0.0), ("gain", 1.0)],
         formulas=[("p", f"vec2(x, y) / scale + {_SEEDOFF}", 1), ("i", "floor(p)", 1),
                   ("f", "fract(p)", 1), ("w", "f * f * (3.0 - 2.0 * f)", 1)]),

    # fbm — 3 octaves; `lacunarity`/`persistence` shape it, `seed` = pattern/drift. Inlined, large.
    dict(name="noise_fbm",
         red=_FBM_NOISE, green=_FBM_NOISE, blue=_FBM_NOISE, matte="1.0",
         variables=[("scale", 80), ("seed", 0.0), ("lacunarity", 2.0), ("persistence", 0.5)]),

    # Voronoi — nearest feature-point distance; `jitter` 0=grid..1=random, `seed` = pattern/drift.
    dict(name="voronoi",
         red=_VORONOI, green=_VORONOI, blue=_VORONOI, matte="1.0",
         variables=[("scale", 80), ("seed", 0.0), ("jitter", 1.0)],
         formulas=[("p", f"vec2(x, y) / scale + {_SEEDOFF}", 1), ("i", "floor(p)", 1),
                   ("f", "fract(p)", 1)]),

    # --- SDF shape generators ----------------------------------------------
    # Anti-aliased mattes around Centre; size in px, `soft` = edge width in px.

    dict(name="sdf_circle",
         red="1.0 - smoothstep(-soft, soft, d)", green="1.0 - smoothstep(-soft, soft, d)",
         blue="1.0 - smoothstep(-soft, soft, d)", matte="1.0 - smoothstep(-soft, soft, d)",
         variables=[("radius", 200), ("soft", 2.0)],
         formulas=[("d", "length(vec2(x - centre.x, y - centre.y)) - radius", 0)]),

    # `hollow` 0=solid .. ->1 cuts a growing hole in the middle (outer edge stays put).
    dict(name="sdf_box",
         red=_HOLLOW("min(bx, by)"), green=_HOLLOW("min(bx, by)"),
         blue=_HOLLOW("min(bx, by)"), matte=_HOLLOW("min(bx, by)"),
         variables=[("bx", 200), ("by", 120), ("hollow", 0.0), ("soft", 2.0)],
         formulas=[("d", "length(max(abs(vec2(x - centre.x, y - centre.y)) - vec2(bx, by), 0.0)) + min(max(abs(x - centre.x) - bx, abs(y - centre.y) - by), 0.0)", 0)]),

    # Hole is a SECOND rounded box with the SAME corner radius (not an inward offset),
    # so the interior rounding matches the exterior at any `hollow` amount.
    dict(name="sdf_rounded_box",
         red="smoothstep(-soft, soft, d2) - smoothstep(-soft, soft, d)",
         green="smoothstep(-soft, soft, d2) - smoothstep(-soft, soft, d)",
         blue="smoothstep(-soft, soft, d2) - smoothstep(-soft, soft, d)",
         matte="smoothstep(-soft, soft, d2) - smoothstep(-soft, soft, d)",
         variables=[("bx", 200), ("by", 120), ("corner", 40), ("hollow", 0.0), ("soft", 2.0)],
         formulas=[("wall", "(1.0 - hollow) * min(bx, by)", 0),
                   ("d", "length(max(abs(vec2(x - centre.x, y - centre.y)) - vec2(bx - corner, by - corner), 0.0)) + min(max(abs(x - centre.x) - (bx - corner), abs(y - centre.y) - (by - corner)), 0.0) - corner", 0),
                   ("d2", "length(max(abs(vec2(x - centre.x, y - centre.y)) - vec2(bx - wall - corner, by - wall - corner), 0.0)) + min(max(abs(x - centre.x) - (bx - wall - corner), abs(y - centre.y) - (by - wall - corner)), 0.0) - corner", 0)]),

    dict(name="sdf_ring",
         red="1.0 - smoothstep(-soft, soft, d)", green="1.0 - smoothstep(-soft, soft, d)",
         blue="1.0 - smoothstep(-soft, soft, d)", matte="1.0 - smoothstep(-soft, soft, d)",
         variables=[("radius", 200), ("thickness", 20), ("soft", 2.0)],
         formulas=[("d", "abs(length(vec2(x - centre.x, y - centre.y)) - radius) - thickness", 0)]),

    dict(name="sdf_polygon",
         red=_HOLLOW("radius"), green=_HOLLOW("radius"),
         blue=_HOLLOW("radius"), matte=_HOLLOW("radius"),
         variables=[("radius", 200), ("sides", 6), ("rot", 0.0), ("hollow", 0.0), ("soft", 2.0)],
         formulas=[("r", "length(vec2(x - centre.x, y - centre.y))", 0),
                   ("a", "atan(y - centre.y, x - centre.x) + rot", 0),
                   ("d", "r - radius * cos(PI / sides) / cos(mod(a, 2.0 * PI / sides) - PI / sides)", 0)]),

    # --- HSV / chroma colour -----------------------------------------------

    # RGB -> HSV (H,S,V on R,G,B). Front 1.
    dict(name="rgb_to_hsv",
         red=_HUE, green=_SAT, blue="q.x", matte="m1",
         formulas=[HSV_P, HSV_Q]),

    # HSV -> RGB (Front 1 holds H,S,V). Front 1.
    dict(name="hsv_to_rgb",
         red="b1 * mix(1.0, clamp(pp.x - 1.0, 0.0, 1.0), g1)",
         green="b1 * mix(1.0, clamp(pp.y - 1.0, 0.0, 1.0), g1)",
         blue="b1 * mix(1.0, clamp(pp.z - 1.0, 0.0, 1.0), g1)",
         matte="m1",
         formulas=[("pp", "abs(fract(vec3(r1) + vec3(1.0, 0.6666667, 0.3333333)) * 6.0 - 3.0)", 2)]),

    # Hue rotate — luma-preserving rotation matrix; `hue` 0..1 = full turn. Front 1.
    dict(name="hue_rotate",
         red=_HROT_R, green=_HROT_G, blue=_HROT_B,
         matte="m1", variables=[("hue", 0.0)],
         formulas=[("c", "cos(hue * 2.0 * PI)", 0), ("s", "sin(hue * 2.0 * PI)", 0)]),

    # Chroma key — matte from hue distance to `keyHue` (+ min `satMin`). Front 1.
    dict(name="chroma_key",
         **_solid(f"{_hue_band(_HUE, 'keyHue', 'tol', 'soft')} * smoothstep(satMin, satMin + 0.05, ({_SAT}))"),
         variables=[("keyHue", 0.33), ("tol", 0.05), ("soft", 0.05), ("satMin", 0.15)],
         formulas=[HSV_P, HSV_Q]),

    # Colour replace — shift hues near `srcHue` toward `dstHue` (rest untouched). Front 1.
    dict(name="color_replace",
         red=f"mix(r1, {_HROT_R}, {_hue_band(_HUE, 'srcHue', 'tol', 'soft')})",
         green=f"mix(g1, {_HROT_G}, {_hue_band(_HUE, 'srcHue', 'tol', 'soft')})",
         blue=f"mix(b1, {_HROT_B}, {_hue_band(_HUE, 'srcHue', 'tol', 'soft')})",
         matte="m1",
         variables=[("srcHue", 0.33), ("dstHue", 0.0), ("tol", 0.06), ("soft", 0.05)],
         formulas=[HSV_P, HSV_Q,
                   ("c", "cos((dstHue - srcHue) * 2.0 * PI)", 0),
                   ("s", "sin((dstHue - srcHue) * 2.0 * PI)", 0)]),

    # Vibrance — saturation that pushes low-sat pixels more than already-vivid ones
    # (`vibrance`), plus a master `saturation`; `skinProtect` spares the skin-hue band.
    # Front 1.
    dict(name="vibrance",
         red="mix(Y, r1, f)", green="mix(Y, g1, f)", blue="mix(Y, b1, f)", matte="m1",
         variables=[("vibrance", 0.0), ("saturation", 1.0), ("skinProtect", 0.0)],
         formulas=[HSV_P, HSV_Q, ("Y", _LUMA, 0),
                   ("f", f"1.0 + (vibrance * (1.0 - {_SAT}) + (saturation - 1.0)) "
                         f"* (1.0 - skinProtect * {_hue_band(_HUE, '0.07', '0.06', '0.06')})", 0)]),

    # HSL targeted — apply dHue/dSat/dVal ONLY inside a hue band (`centerHue`, `width`,
    # `soft`); everything outside is untouched. The Lightroom HSL panel in one node. Front 1.
    dict(name="hsl_targeted",
         red=f"mix(r1, (1.0 + dVal) * mix({_LUMA}, {_HROT_R}, 1.0 + dSat), {_hue_band(_HUE, 'centerHue', 'bandWidth', 'soft')})",
         green=f"mix(g1, (1.0 + dVal) * mix({_LUMA}, {_HROT_G}, 1.0 + dSat), {_hue_band(_HUE, 'centerHue', 'bandWidth', 'soft')})",
         blue=f"mix(b1, (1.0 + dVal) * mix({_LUMA}, {_HROT_B}, 1.0 + dSat), {_hue_band(_HUE, 'centerHue', 'bandWidth', 'soft')})",
         matte="m1",
         variables=[("centerHue", 0.33), ("bandWidth", 0.08), ("soft", 0.05),
                    ("dHue", 0.0), ("dSat", 0.0), ("dVal", 0.0)],
         formulas=[HSV_P, HSV_Q, ("c", "cos(dHue * 2.0 * PI)", 0), ("s", "sin(dHue * 2.0 * PI)", 0)]),

    # Split tone — tint shadows toward `shadowHue`, highlights toward `highHue`, weighted
    # by luma; `balance` (-0.5..0.5) slides the shadow/highlight pivot. Front 1.
    dict(name="split_tone",
         red="r1 + sw * (shTint.r - 0.5) + hw * (hiTint.r - 0.5)",
         green="g1 + sw * (shTint.g - 0.5) + hw * (hiTint.g - 0.5)",
         blue="b1 + sw * (shTint.b - 0.5) + hw * (hiTint.b - 0.5)",
         matte="m1",
         variables=[("shadowHue", 0.58), ("highHue", 0.08),
                    ("shadowAmt", 0.1), ("highAmt", 0.1), ("balance", 0.0)],
         formulas=[("sw", f"shadowAmt * (1.0 - smoothstep(0.0, 0.5 + balance, {_LUMA}))", 0),
                   ("hw", f"highAmt * smoothstep(0.5 + balance, 1.0, {_LUMA})", 0),
                   ("shTint", _hue2rgb("shadowHue"), 2),
                   ("hiTint", _hue2rgb("highHue"), 2)]),

    # Saturation matte — qualifier from the saturation window [`satLow`,`satHigh`] gated by
    # a `valMin` brightness floor; isolates vivid vs neutral regions. Front 1.
    dict(name="sat_matte",
         **_solid(f"smoothstep(satLow, satLow + soft, {_SAT}) "
                  f"* (1.0 - smoothstep(satHigh, satHigh + soft, {_SAT})) "
                  f"* smoothstep(valMin, valMin + soft, q.x)"),
         variables=[("satLow", 0.15), ("satHigh", 1.0), ("soft", 0.05), ("valMin", 0.0)],
         formulas=[HSV_P, HSV_Q]),

    # --- Matte combine & premult -------------------------------------------

    dict(name="premult",
         red="r1 * m1", green="g1 * m1", blue="b1 * m1", matte="m1"),
    dict(name="unpremult",
         red="m1 > 0.0 ? r1 / m1 : r1", green="m1 > 0.0 ? g1 / m1 : g1",
         blue="m1 > 0.0 ? b1 / m1 : b1", matte="m1"),
    dict(name="matte_and",
         red="m1 * m2", green="m1 * m2", blue="m1 * m2", matte="m1 * m2"),
    dict(name="matte_or",
         red="max(m1, m2)", green="max(m1, m2)", blue="max(m1, m2)", matte="max(m1, m2)"),
    dict(name="matte_subtract",
         red="clamp(m1 - m2, 0.0, 1.0)", green="clamp(m1 - m2, 0.0, 1.0)",
         blue="clamp(m1 - m2, 0.0, 1.0)", matte="clamp(m1 - m2, 0.0, 1.0)"),
    dict(name="matte_xor",
         red="clamp(m1 + m2 - 2.0 * m1 * m2, 0.0, 1.0)", green="clamp(m1 + m2 - 2.0 * m1 * m2, 0.0, 1.0)",
         blue="clamp(m1 + m2 - 2.0 * m1 * m2, 0.0, 1.0)", matte="clamp(m1 + m2 - 2.0 * m1 * m2, 0.0, 1.0)"),
    dict(name="matte_invert",
         red="1.0 - m1", green="1.0 - m1", blue="1.0 - m1", matte="1.0 - m1"),
    dict(name="matte_grade",
         red="clamp(pow(clamp(m1, 0.0, 1.0), gamma) * gain, 0.0, 1.0)",
         green="clamp(pow(clamp(m1, 0.0, 1.0), gamma) * gain, 0.0, 1.0)",
         blue="clamp(pow(clamp(m1, 0.0, 1.0), gamma) * gain, 0.0, 1.0)",
         matte="clamp(pow(clamp(m1, 0.0, 1.0), gamma) * gain, 0.0, 1.0)",
         variables=[("gamma", 1.0), ("gain", 1.0)]),

    # --- Escape-time fractals ----------------------------------------------
    # All three share _fractal_chain (4 vec3 formulas z0..z3, 8 total iterations) and read
    # the smooth escape value _FRAC_ESCAPE off z3.z. Pan/zoom via node Centre + `zoom`.

    # Mandelbrot — c = pixel, z0 = (cRe,cIm). cRe/cIm seed the iteration (default 0,0 = the
    # classic set); KEYFRAME them to morph, mirroring Julia's constant. Grayscale via _solid.
    dict(name="mandelbrot",
         **_solid(_FRAC_ESCAPE),
         variables=[("zoom", 400.0), ("cRe", 0.0), ("cIm", 0.0),
                    ("gain", 1.0), ("gamma", 1.0)],
         formulas=_fractal_chain("vec3(cRe, cIm, 0.0)", _FRAC_PIX)),

    # Julia — z0 = pixel, c = constant (cRe,cIm). KEYFRAME cRe/cIm to morph. Grayscale.
    dict(name="julia",
         **_solid(_FRAC_ESCAPE),
         variables=[("zoom", 400.0), ("cRe", -0.8), ("cIm", 0.156),
                    ("gain", 1.0), ("gamma", 1.0)],
         formulas=_fractal_chain(f"vec3({_FRAC_PIX}, 0.0)", "vec2(cRe, cIm)")),

    # Burning Ship — like Mandelbrot but fold z to abs() before each square (abs_z=True).
    # cRe/cIm seed z0 (default 0,0 = classic); KEYFRAME to morph. Grayscale via _solid.
    dict(name="burning_ship",
         **_solid(_FRAC_ESCAPE),
         variables=[("zoom", 400.0), ("cRe", 0.0), ("cIm", 0.0),
                    ("gain", 1.0), ("gamma", 1.0)],
         formulas=_fractal_chain("vec3(cRe, cIm, 0.0)", _FRAC_PIX, abs_z=True)),

    # --- ST-map generators (feed a downstream STMap node) ------------------

    # Polar<->cartesian remap. Source U follows the angle around Centre, source V the
    # normalised radius. 'twist' rotates the angular axis, 'zoom' scales the radius.
    # Aspect-corrected so the mapping stays circular at any resolution.
    dict(name="polar_to_cartesian",
         red="fract((atan(ny, nx) + twist) / (2.0 * PI) + 1.0)",
         green="clamp(length(vec2(nx, ny)) / zoom, 0.0, 1.0)",
         blue="0.0", matte="1.0",
         variables=[("twist", 0.0), ("zoom", 1.0)],
         formulas=[("nx", "((x + 0.5) / width - 0.5 - centre.x / width) * 2.0", 0),
                   ("ny", "((y + 0.5) / height - 0.5 - centre.y / height) * 2.0 * (height / width)", 0)]),

    # Kaleidoscope fold — mirror-fold angular space into 'segments' wedges around Centre.
    # Source UV is reconstructed from the folded angle + original radius, back to 0..1.
    dict(name="kaleidoscope_map",
         red="0.5 + cos(fa) * rad",
         green="0.5 + sin(fa) * rad * (width / height)",
         blue="0.0", matte="1.0",
         variables=[("segments", 6.0), ("rot", 0.0)],
         formulas=[("nx", "((x + 0.5) / width - 0.5 - centre.x / width)", 0),
                   ("ny", "((y + 0.5) / height - 0.5 - centre.y / height) * (height / width)", 0),
                   ("rad", "length(vec2(nx, ny))", 0),
                   ("fa", "abs(mod(atan(ny, nx) + rot, 2.0 * PI / segments) - PI / segments)", 0)]),

    # Lens distort/undistort ST map with anamorphic squeeze. Radial polynomial (k1, k2)
    # around Centre; 'squeeze' scales X for anamorphic. Negate k1/k2 to invert (undistort).
    dict(name="lens_distort_map",
         red="0.5 + centre.x / width + nx * f / squeeze * 0.5",
         green="0.5 + centre.y / height + ny * f * 0.5 * (width / height)",
         blue="0.0", matte="1.0",
         variables=[("k1", 0.1), ("k2", 0.0), ("squeeze", 1.0)],
         formulas=[("nx", "((x + 0.5) / width - 0.5 - centre.x / width) * 2.0", 0),
                   ("ny", "((y + 0.5) / height - 0.5 - centre.y / height) * 2.0 * (height / width)", 0),
                   ("r2v", "nx * nx + ny * ny", 0),
                   ("f", "1.0 + k1 * r2v + k2 * r2v * r2v", 0)]),

    # Glitch-block ST map — quantise UV into 'blockSize'-pixel blocks, hash each block to a
    # random offset, scale by 'corruption' (0..1, KEYFRAME to trigger). seed reshuffles.
    dict(name="glitch_block_map",
         red="(x + 0.5) / width + (off.x - 0.5) * corruption * 0.2",
         green="(y + 0.5) / height + (off.y - 0.5) * corruption * 0.05",
         blue="0.0", matte="1.0",
         variables=[("blockSize", 64.0), ("corruption", 0.0), ("seed", 0.0)],
         formulas=[("blk", "floor(vec2(x, y) / blockSize) + seed", 1),
                   ("off", _hash2("blk"), 1)]),

    # Heat-haze ST map — UV offset from animated 3-octave fbm * 'amp'. KEYFRAME 'seed' to
    # shimmer. Same fbm field shifted on each axis so X/Y wobble independently.
    dict(name="heat_haze_map",
         red="(x + 0.5) / width + (nA - 0.5) * amp",
         green="(y + 0.5) / height + (nB - 0.5) * amp",
         blue="0.0", matte="1.0",
         variables=[("scale", 120.0), ("seed", 0.0),
                    ("lacunarity", 2.0), ("persistence", 0.5), ("amp", 0.03)],
         formulas=[("nA", _FBM_NOISE, 0),
                   ("nB", _vnoise_at("(vec2(x, y) / scale + vec2(seed + 5.2, seed * 1.3 + 1.7))"), 0)]),

    # Circle-of-confusion from depth (NOT a UV map). Depth on Matte 1. Per-pixel blur
    # radius 0..1 = distance from focusDepth, normalised by focusRange, scaled by maxBlur.
    dict(name="coc_from_depth",
         red="clamp(abs(m1 - focusDepth) / focusRange, 0.0, 1.0) * maxBlur",
         green="clamp(abs(m1 - focusDepth) / focusRange, 0.0, 1.0) * maxBlur",
         blue="clamp(abs(m1 - focusDepth) / focusRange, 0.0, 1.0) * maxBlur",
         matte="clamp(abs(m1 - focusDepth) / focusRange, 0.0, 1.0) * maxBlur",
         variables=[("focusDepth", 5.0), ("focusRange", 5.0), ("maxBlur", 1.0)]),

    # Chromatic-aberration ST map — radial scale that diverges per channel from Centre.
    # Carries the RED channel's distorted source UV (apply per-channel, see Notes); blue
    # holds the radial-offset magnitude for a downstream defringe.
    dict(name="chromatic_aberration_map",
         red="0.5 + centre.x / width + nx * (1.0 + amount) * 0.5",
         green="0.5 + centre.y / height + ny * (1.0 + amount) * 0.5 * (width / height)",
         blue="length(vec2(nx, ny)) * amount",
         matte="1.0",
         variables=[("amount", 0.02)],
         formulas=[("nx", "((x + 0.5) / width - 0.5 - centre.x / width) * 2.0", 0),
                   ("ny", "((y + 0.5) / height - 0.5 - centre.y / height) * 2.0 * (height / width)", 0)]),

    # === control_surfaces — Front 2 / Matte 2 as a painted control map ===

    # Painted grade — Front 2 is a PAINTED control map: r2 = local exposure,
    # g2 = local hue shift, b2 = local saturation (all 0.5 = neutral). Exposure
    # multiplies in linear; sat mixes toward luma; hue uses the luma-preserving
    # rotation matrix on the exposed/saturated RGB (formula `pr`), angle from g2.
    # Defaults map a flat 0.5 control map to no change. Matte passes m1 through.
    dict(name="painted_grade",
         red="pr.x * (0.299 + 0.701 * c + 0.168 * s) + pr.y * (0.587 - 0.587 * c + 0.330 * s) + pr.z * (0.114 - 0.114 * c - 0.497 * s)",
         green="pr.x * (0.299 - 0.299 * c - 0.328 * s) + pr.y * (0.587 + 0.413 * c + 0.035 * s) + pr.z * (0.114 - 0.114 * c + 0.292 * s)",
         blue="pr.x * (0.299 - 0.300 * c + 1.250 * s) + pr.y * (0.587 - 0.588 * c - 1.050 * s) + pr.z * (0.114 + 0.886 * c - 0.203 * s)",
         matte="m1",
         variables=[("expRange", 2.0), ("hueRange", 1.0), ("satRange", 1.0)],
         formulas=[
             ("c", "cos((g2 - 0.5) * hueRange * 2.0 * PI)", 0),
             ("s", "sin((g2 - 0.5) * hueRange * 2.0 * PI)", 0),
             # exposure (linear multiply, r2 about 0.5) then saturation (b2 about 0.5).
             ("ex", "exp2((r2 - 0.5) * 2.0 * expRange)", 0),
             ("pr", "mix(vec3(dot(vec3(r1, g1, b1) * ex, vec3(0.2126, 0.7152, 0.0722))), "
                    "vec3(r1, g1, b1) * ex, 1.0 + (b2 - 0.5) * 2.0 * satRange)", 2),
         ]),

    # Channel pack — ferry three single-channel signals down ONE connection:
    # red = Matte 1, green = Matte 2, blue = Front 1 luma. Unpack with channel_unpack.
    dict(name="channel_pack",
         red="m1", green="m2", blue=_LUMA, matte="1.0"),

    # Channel unpack — expose a packed RGB (from channel_pack) on Front 1 and route
    # one channel to the Matte. `pick` 0/1/2 selects r1/g1/b1 for the OutMatte; RGB
    # passes through unchanged. Selection via step (no arrays).
    dict(name="channel_unpack",
         red="r1", green="g1", blue="b1",
         matte="mix(mix(r1, g1, step(0.5, pick)), b1, step(1.5, pick))",
         variables=[("pick", 0)]),

    # Dual-output depth — ONE node, TWO products: RGB is a depth-tinted grade of the
    # beauty (Front 1), while the Matte INDEPENDENTLY keys a depth slab from Matte 1
    # (m1). matte = smoothstep(near, far, m1). OutMatte needs Matte 1 connected.
    dict(name="dual_output_depth",
         red="mix(r1, r1 * tintR, smoothstep(near, far, m1) * strength)",
         green="mix(g1, g1 * tintG, smoothstep(near, far, m1) * strength)",
         blue="mix(b1, b1 * tintB, smoothstep(near, far, m1) * strength)",
         matte="smoothstep(near, far, m1)",
         variables=[("near", 0.0), ("far", 1.0), ("strength", 0.0),
                    ("tintR", 0.6), ("tintG", 0.8), ("tintB", 1.4)]),

    # --- Wave 4: optics / physics generators -------------------------------
    # Analytic physics around the Centre. Animate the keyframed var noted on each
    # (no time builtin) — scrub frames 1-100. Use DIST for radius, atan() for angle.

    # Thin-film interference — soap-bubble / oil-slick iridescence. The interference
    # 'phase' grows with radius (DIST) and 'thickness'; fract(phase) picks a spectral
    # hue via _hue2rgb. Keyframe 'shift' to roll the rainbow. Matte = ring intensity.
    dict(name="thin_film",
         red=f"({_hue2rgb('fract(phase)')}).r",
         green=f"({_hue2rgb('fract(phase)')}).g",
         blue=f"({_hue2rgb('fract(phase)')}).b",
         matte="(sin(phase * 2.0 * PI) + 1.0) / 2.0",
         variables=[("thickness", 1.0), ("scale", 0.004), ("shift", [(1, 0.0), (100, 1.0)])],
         formulas=[DIST, ("phase", "dist * scale * thickness + shift", 0)]),

    # Wave interference — ripple-tank from two circular point sources. Source A sits at
    # Centre, source B at offset 'srcX' (px, on X). Each contributes cos(k*distance -
    # phase); KEYFRAME 'phase' to animate the ripples. Two own vars (two-colour eats 6):
    # 'srcX' + animated 'phase'; wavelength/amp baked into formula 'k'. Field 0..1.
    dict(name="wave_interference",
         **_two_color("clamp((cos(dA * k - phase) + cos(dB * k - phase)) * 0.25 + 0.5, 0.0, 1.0)"),
         variables=[("srcX", 300.0), ("phase", [(1, 0.0), (100, 12.566)])] + _COLVARS,
         formulas=[("dA", "length(vec2(x - centre.x, y - centre.y))", 0),
                   ("dB", "length(vec2(x - centre.x - srcX, y - centre.y))", 0),
                   ("k", "2.0 * PI / 80.0", 0)]),

    # Moire — two line gratings at slightly different frequency; their beat is the moire.
    # gA is axis-aligned, gB rotated by a fixed small angle. Two own vars (two-colour eats
    # 6): freqA + freqB — keep them CLOSE for wide, slow beats. Product -> 0..1 pattern.
    dict(name="moire",
         **_two_color("(sin(x * freqA) * sin((x * 0.9992 + y * 0.04) * freqB) + 1.0) / 2.0"),
         variables=[("freqA", 0.08), ("freqB", 0.085)] + _COLVARS),

    # Starfield — tile space into 'cellSize' cells, hash each cell (_hash2) to place one
    # star with random brightness; KEYFRAME 'twinkle' to make them pulse (each cell's
    # hash sets its phase). Stars above 'threshold' only; faint hash tint on RGB.
    dict(name="starfield",
         red="star * (0.7 + 0.3 * h.x)",
         green="star",
         blue="star * (0.7 + 0.3 * h.y)",
         matte="star",
         variables=[("cellSize", 40.0), ("twinkle", [(1, 0.0), (100, 1.0)]),
                    ("threshold", 0.92), ("brightness", 1.0)],
         formulas=[("h", _hash2("floor(vec2(x, y) / cellSize)"), 1),
                   ("d", "length(fract(vec2(x, y) / cellSize) - h)", 0),
                   ("star", "smoothstep(threshold, 1.0, h.y) * (1.0 - smoothstep(0.0, 0.12, d)) "
                            "* brightness * (0.4 + 0.6 * (0.5 + 0.5 * sin((twinkle + h.x) * 2.0 * PI)))", 0)]),

    # Radar sweep — a rotating sweep line around Centre. 'sweep' (KEYFRAME 0->2*PI) is the
    # line angle; brightness decays exponentially BEHIND it (afterglow) by angular gap,
    # plus faint range rings from DIST. 'glow' default phosphor green.
    dict(name="radar_sweep",
         red="sweepLevel * glowR + rings",
         green="sweepLevel * glowG + rings",
         blue="sweepLevel * glowB + rings",
         matte="clamp(sweepLevel + rings, 0.0, 1.0)",
         variables=[("sweep", [(1, 0.0), (100, 6.283)]), ("decay", 3.0), ("ringFreq", 0.02),
                    ("glowR", 0.1), ("glowG", 1.0), ("glowB", 0.3)],
         formulas=[("gap", "mod(sweep - atan(y - centre.y, x - centre.x), 2.0 * PI)", 0),
                   ("sweepLevel", "exp(-gap * decay)", 0),
                   ("rings", "0.12 * (0.5 + 0.5 * sin(length(vec2(x - centre.x, y - centre.y)) * ringFreq))", 0)]),


    # --- Diagnostics -------------------------------------------------------
    # Colour-blindness sim — Machado 2009 severity-1.0 matrices. 'type' 0=protan,
    # 1=deutan, 2=tritan selected by step() weights w (no arrays/loops); 'amount'
    # blends sim vs original. Output = 3 dot products per channel against w.
    dict(name="color_blindness",
         red="mix(r1, dot(vec3(simP.x, simD.x, simT.x), w), amount)",
         green="mix(g1, dot(vec3(simP.y, simD.y, simT.y), w), amount)",
         blue="mix(b1, dot(vec3(simP.z, simD.z, simT.z), w), amount)",
         matte="m1",
         variables=[("type", 0), ("amount", 1.0)],
         formulas=[
             ("w", "vec3(1.0 - step(0.5, type), step(0.5, type) - step(1.5, type), step(1.5, type))", 2),
             ("simP", "vec3("
                      "0.152286 * r1 + 1.052583 * g1 - 0.204868 * b1, "
                      "0.114503 * r1 + 0.786281 * g1 + 0.099216 * b1, "
                      "-0.003882 * r1 - 0.048116 * g1 + 1.051998 * b1)", 2),
             ("simD", "vec3("
                      "0.367322 * r1 + 0.860646 * g1 - 0.227968 * b1, "
                      "0.280085 * r1 + 0.672501 * g1 + 0.047413 * b1, "
                      "-0.011820 * r1 + 0.042940 * g1 + 0.968881 * b1)", 2),
             ("simT", "vec3("
                      "1.255528 * r1 - 0.076749 * g1 - 0.178779 * b1, "
                      "-0.078411 * r1 + 0.930809 * g1 + 0.147602 * b1, "
                      "0.004733 * r1 + 0.691367 * g1 + 0.303900 * b1)", 2),
         ]),

    # Exposure zebra — diagonal stripes over clipped pixels. Clip detected on the
    # per-channel max: max(r,g,b) >= hi shows red stripes, <= lo shows blue stripes;
    # mid passes through. Stripes = sign of sin((x+y)*freq + phase); keyframe 'phase'
    # to crawl. matte flags the clipped region.
    dict(name="exposure_zebra",
         red="over > 0.5 ? mix(r1, 1.0, stripe) : r1",
         green="(over > 0.5 || under > 0.5) ? mix(g1, 0.0, stripe) : g1",
         blue="under > 0.5 ? mix(b1, 1.0, stripe) : b1",
         matte="max(over, under)",
         variables=[("hi", 1.0), ("lo", 0.0), ("freq", 0.15), ("phase", 0.0)],
         formulas=[
             ("chmax", "max(max(r1, g1), b1)", 0),
             ("over", "step(hi, chmax)", 0),
             ("under", "step(chmax, lo)", 0),
             ("stripe", "step(0.0, sin((x + y) * freq + phase))", 0),
         ]),

    # Gamut clip — flag illegal pixels. Any channel < 0 (negative light) tinted
    # magenta (1,0,1); any channel > 'ceiling' tinted yellow (1,1,0); in-range passes
    # through (negative wins over over-ceiling). 'tint' 0..1 blends the warning colour
    # over the pixel. matte = the out-of-gamut mask (union of negative OR over-ceiling).
    dict(name="gamut_clip",
         red="neg > 0.5 ? mix(r1, 1.0, tint) : (over > 0.5 ? mix(r1, 1.0, tint) : r1)",
         green="neg > 0.5 ? mix(g1, 0.0, tint) : (over > 0.5 ? mix(g1, 1.0, tint) : g1)",
         blue="neg > 0.5 ? mix(b1, 1.0, tint) : (over > 0.5 ? mix(b1, 0.0, tint) : b1)",
         matte="max(neg, over)",
         variables=[("ceiling", 1.0), ("tint", 1.0)],
         formulas=[
             ("neg", "1.0 - step(0.0, min(min(r1, g1), b1))", 0),
             ("over", "step(ceiling, max(max(r1, g1), b1))", 0),
         ]),
] + _STYLIZATION

# Organise outputs into subfolders by use.
CATEGORY = {
    # Alpha / matte tools
    "alpha_crunch": "alpha_matte_tools",
    "fill_alpha": "alpha_matte_tools",
    "alpha_fringe": "alpha_matte_tools",
    "luma_key": "alpha_matte_tools",
    "difference_matte": "alpha_matte_tools",
    # Pattern generators
    "radial_ramp": "pattern_generators",
    "rings": "pattern_generators",
    "rays": "pattern_generators",
    "checkerboard": "pattern_generators",
    "bricks": "pattern_generators",
    "noise_random": "pattern_generators",
    # Colour / grade
    "despill_green": "color_grade",
    "saturation": "color_grade",
    "voxelize": "color_grade",
    "exposure": "color_grade",
    "contrast": "color_grade",
    "lift_gamma_gain": "color_grade",
    "white_balance": "color_grade",
    "srgb_to_linear": "color_grade",
    "linear_to_srgb": "color_grade",
    # UV / lens distortion
    "lens_distort": "uv_distortion",
    "lens_undistort": "uv_distortion",
    "anamorphic_unsqueeze": "uv_distortion",
    "uv_transform": "uv_distortion",
    # 3D position-pass tools
    "pmatte_sphere": "3d_position_tools",
    "pmatte_rings": "3d_position_tools",
    "pmatte_rays": "3d_position_tools",
    "box_matte": "3d_position_tools",
    "normal_relight": "3d_position_tools",
    "fresnel_facing": "3d_position_tools",
    # Animated generators (keyframed 't')
    "wave_sine": "animated_generators",
    "wave_triangle": "animated_generators",
    "wave_square": "animated_generators",
    "wave_sawtooth": "animated_generators",
    "pulse_rings": "animated_generators",
    "spin_rays": "animated_generators",
    # Depth toolkit
    "depth_normalize": "depth_tools",
    "depth_matte": "depth_tools",
    "depth_fog": "depth_tools",
    "depth_fade": "depth_tools",
    "depth_mix": "depth_tools",
    "depth_dof_mask": "depth_tools",
    "depth_contours": "depth_tools",
    "depth_posterize": "depth_tools",
    "depth_grade": "depth_tools",
    # AOV compositing
    "aov_add": "aov_tools",
    "aov_grade_add": "aov_tools",
    "ao_multiply": "aov_tools",
    "albedo_divide": "aov_tools",
    "albedo_multiply": "aov_tools",
    "aov_clamp_negative": "aov_tools",
    "screen_merge": "aov_tools",
    "id_isolate": "aov_tools",
    "crypto_pick_2rank": "aov_tools",
    "crypto_pick_4rank": "aov_tools",
    # Procedural noise
    "noise_cells": "noise", "noise_value": "noise",
    "noise_fbm": "noise", "voronoi": "noise",
    # SDF shapes
    "sdf_circle": "sdf_shapes", "sdf_box": "sdf_shapes",
    "sdf_rounded_box": "sdf_shapes", "sdf_ring": "sdf_shapes",
    "sdf_polygon": "sdf_shapes",
    # HSV / chroma
    "rgb_to_hsv": "hsv_color", "hsv_to_rgb": "hsv_color", "hue_rotate": "hsv_color",
    "chroma_key": "hsv_color", "color_replace": "hsv_color",
    "vibrance": "hsv_color", "hsl_targeted": "hsv_color", "split_tone": "hsv_color",
    "sat_matte": "hsv_color",
    # Matte combine & premult
    "premult": "matte_combine", "unpremult": "matte_combine",
    "matte_and": "matte_combine", "matte_or": "matte_combine",
    "matte_subtract": "matte_combine", "matte_xor": "matte_combine",
    "matte_invert": "matte_combine", "matte_grade": "matte_combine",
    # Utility / technical
    "stmap": "utility",
    "nan_cleanup": "utility",
    # Escape-time fractals
    "mandelbrot": "fractals",
    "julia": "fractals",
    "burning_ship": "fractals",
    # ST-map generators (feed a downstream STMap node)
    "polar_to_cartesian": "stmap_generators",
    "kaleidoscope_map": "stmap_generators",
    "lens_distort_map": "stmap_generators",
    "glitch_block_map": "stmap_generators",
    "heat_haze_map": "stmap_generators",
    "coc_from_depth": "stmap_generators",
    "chromatic_aberration_map": "stmap_generators",
    # Control surfaces (Front 2 / Matte 2 as a painted control map)
    "painted_grade": "control_surfaces",
    "channel_pack": "control_surfaces",
    "channel_unpack": "control_surfaces",
    "dual_output_depth": "control_surfaces",
    # Stylization (per-pixel looks)
    "halftone": "stylization",
    "bayer_dither": "stylization",
    "crosshatch": "stylization",
    "crt": "stylization",
    "truchet": "stylization",
    "palette_quantize": "stylization",
    "seven_segment": "stylization",
    # Optics / physics generators
    "thin_film": "optics_physics",
    "wave_interference": "optics_physics",
    "moire": "optics_physics",
    "starfield": "optics_physics",
    "radar_sweep": "optics_physics",
    # Diagnostics
    "color_blindness": "diagnostics",
    "exposure_zebra": "diagnostics",
    "gamut_clip": "diagnostics",
}

# Per-setup documentation: what it does + when to use it + inputs.
DOCS = {
    # alpha_matte_tools
    "alpha_crunch": ("Sets matte pixels below `thresh` to 0, passing the rest through.",
                     "Harden a soft or dirty matte and drop low-value noise to fully transparent.",
                     "Matte 1"),
    "fill_alpha": ("Sets any matte pixel above 0 to 1 (fully opaque).",
                   "Solidify a matte so semi-transparent areas become solid; fill key holes.",
                   "Matte 1"),
    "alpha_fringe": ("Outputs `4*(1-a)*a`, which peaks at mid-grey matte values.",
                     "Isolate a matte's soft transition zone for edge work (despill, edge blur, light wrap).",
                     "Matte 1"),
    "luma_key": ("Soft key on luminance between `lo` and `hi`; result on Result and OutMatte.",
                 "Pull a quick matte from brightness (skies, highlights, blacks) without a full keyer.",
                 "Front 1"),
    "difference_matte": ("Matte from the colour difference between Front 1 and a clean plate (Front 2), scaled by `gain`.",
                         "Isolate what changed between a shot and its clean plate (added objects, motion).",
                         "Front 1 + Front 2"),
    # pattern_generators
    "radial_ramp": ("Radial gradient from Centre: white in the middle to black at `radius`, edge shaped by `softness`.",
                    "Vignettes, falloff masks, soft round mattes, light pools.",
                    "none (uses Centre)"),
    "rings": ("Concentric sine rings around Centre, spacing set by `freq`.",
              "Test/alignment patterns, ripple textures, radial guides.",
              "none (uses Centre)"),
    "rays": ("Radial rays around Centre; `rays` sets the count, `rot` the rotation.",
             "Sunbursts, star/optical flares, radial wipes.",
             "none (uses Centre)"),
    "checkerboard": ("Checker pattern with `size`-pixel squares.",
                     "UV/distortion checks, placeholder textures, alignment grids.",
                     "none"),
    "bricks": ("Offset brick pattern (`bw`×`bh`), alternate rows shifted half a brick.",
               "Procedural wall/tile texture or a test grid.",
               "none"),
    "noise_random": ("Per-pixel hash (white) noise, with a different seed per channel.",
                     "Grain, dither, random seeding — the GLSL stand-in for Nuke's random().",
                     "none"),
    # animated_generators
    "wave_sine": ("Horizontal scrolling sine bands; `wavelength` is the period, animated `t` drives motion.",
                  "Animated stripes, scanning/sweep effects, a smooth modulation source.",
                  "none"),
    "wave_triangle": ("Scrolling triangle wave (linear up/down ramp); `wavelength` period, animated `t`.",
                      "Linear sweeps and sharper-than-sine modulation.",
                      "none"),
    "wave_square": ("Scrolling hard on/off stripes; `wavelength` period, animated `t`.",
                    "Strobe/blink patterns, hard barcode-style wipes.",
                    "none"),
    "wave_sawtooth": ("Scrolling repeating 0→1 ramp; `wavelength` period, animated `t`.",
                      "Scrolling gradients, phase ramps, scan lines.",
                      "none"),
    "pulse_rings": ("Concentric rings expanding from Centre over time (animated `t`).",
                    "Sonar/radar pulses, shockwaves, ripple triggers.",
                    "none (uses Centre)"),
    "spin_rays": ("Radial rays rotating around Centre; animated `t` 0→1 is one full turn.",
                  "Rotating sunburst, radar sweep, hypnotic wheels.",
                  "none (uses Centre)"),
    # color_grade
    "despill_green": ("Reduces green where it exceeds the red/blue average; `spill` 0→1 sets strength.",
                      "Remove green-screen spill from a foreground.",
                      "Front 1"),
    "saturation": ("Scales saturation around luminance; `sat` 0=greyscale, 1=normal, >1=boosted.",
                   "Quick saturation tweak or full desaturate.",
                   "Front 1"),
    "voxelize": ("Quantises colour to `scale` steps per channel.",
                 "Posterise/banding look, colour reduction, stylise.",
                 "Front 1"),
    # 3d_position_tools
    "pmatte_sphere": ("Spherical matte in 3D position space around (cenR,cenG,cenB), radius `prad`.",
                      "Isolate a region of a CG render by world position for a local grade.",
                      "Front 1 = P-world pass"),
    "pmatte_rings": ("Concentric 3D shells around the centre point, spacing `ringScale`.",
                     "Position-based ring patterns or masks on CG geometry.",
                     "Front 1 = P-world pass"),
    "pmatte_rays": ("Radial rays on the X-Z plane around (cenR,cenB), `rays` count.",
                    "Position-based radial mask (e.g. ground fan patterns).",
                    "Front 1 = P-world pass"),
    "box_matte": ("Axis-aligned cube matte around the centre, half-size `boxSize`, soft edge `soft`.",
                  "Isolate a rectangular volume of a CG render by world position.",
                  "Front 1 = P-world pass"),
    "normal_relight": ("Lambert lighting from a normal pass and a light direction (lx,ly,lz).",
                       "Add or preview a CG light in comp without re-rendering.",
                       "Front 1 = normal pass"),
    "fresnel_facing": ("Rim/facing matte from a camera-space normal pass; `power` shapes the falloff.",
                       "Rim light, edge wear, fresnel reflections, atmosphere holdouts.",
                       "Front 1 = normal pass"),
    # depth_tools
    "depth_normalize": ("Remaps depth `near..far` to a viewable 0..1.",
                        "Make a raw Z-pass viewable and prep it for the other depth tools.",
                        "Matte 1 = depth"),
    "depth_matte": ("Isolates a depth band `zMin..zMax` with soft edges into a matte.",
                    "Hold out a depth slice (foreground / midground / background).",
                    "Matte 1 = depth"),
    "depth_fog": ("Blends beauty toward a fog colour with distance.",
                  "Atmospheric haze / aerial perspective.",
                  "Front 1 = beauty, Matte 1 = depth"),
    "depth_fade": ("Fades colour and alpha to nothing with distance.",
                   "Dissolve distant elements; depth-based vignette.",
                   "Front 1 = beauty, Matte 1 = depth"),
    "depth_mix": ("Composites Front 1 (near) over Front 2 (far) at a depth threshold.",
                  "Insert an element at a given depth, or swap plates by distance.",
                  "Front 1 + Front 2 + Matte 1 = depth"),
    "depth_dof_mask": ("0 at the `focus` plane, ramping to 1 over `range`.",
                       "Drive a Defocus node's blur amount for depth of field.",
                       "Matte 1 = depth"),
    "depth_contours": ("Topographic iso-depth lines every `spacing`.",
                       "Visualise depth structure; tech/HUD look; holdout lines.",
                       "Matte 1 = depth"),
    "depth_posterize": ("Quantises depth into `steps` flat bands.",
                        "Card-style depth separation or stylised depth.",
                        "Matte 1 = depth"),
    "depth_grade": ("Multiplies beauty by a gain that ramps with distance (near→far).",
                    "Darken or lift by distance without introducing a fog colour.",
                    "Front 1 = beauty, Matte 1 = depth"),
    # aov_tools
    "aov_add": ("Sums two passes with per-pass gain.",
                "Beauty rebuild — add diffuse+specular etc.; chain nodes for more passes.",
                "Front 1 + Front 2"),
    "aov_grade_add": ("Tints/exposes Front 2 (one pass) and adds it to Front 1 (the running sum).",
                      "Isolate a single AOV, grade it, and merge it back.",
                      "Front 1 = sum, Front 2 = pass"),
    "ao_multiply": ("Multiplies beauty by an AO pass; `amount` blends it in, `aoGamma` shapes it.",
                    "Apply ambient occlusion in comp with control.",
                    "Front 1 = beauty, Matte 1 = AO"),
    "albedo_divide": ("Beauty ÷ albedo → lighting (guards divide-by-zero).",
                      "Extract the lighting/shadow pass to regrade independently.",
                      "Front 1 = beauty, Front 2 = albedo"),
    "albedo_multiply": ("Albedo × lighting → beauty.",
                        "Recombine after grading albedo/texture separately (relight).",
                        "Front 1 = albedo, Front 2 = lighting"),
    "aov_clamp_negative": ("Clamps sub-zero pixels to 0 per channel.",
                           "Clean negative values some renderers emit before further math.",
                           "Front 1"),
    "screen_merge": ("Screens Front 2 onto Front 1; `gain` scales the added pass.",
                     "Add glow/bloom/light passes without hard clipping.",
                     "Front 1 + Front 2"),
    "id_isolate": ("Grades only the region picked by a mask on Matte 1 (gain + per-channel tint).",
                   "Tweak a single object/region selected by an ID or mask pass.",
                   "Front 1 = beauty, Matte 1 = mask"),
    "crypto_pick_2rank": ("Extracts a matte for object hash `id` from one Cryptomatte layer (2 ranks).",
                          "Pull a Cryptomatte selection on simpler/harder edges.",
                          "Front 1 + Matte 1 (one crypto layer)"),
    "crypto_pick_4rank": ("Extracts a matte for object hash `id` across two crypto layers (4 ranks).",
                          "Pull a Cryptomatte selection with cleaner anti-aliased edges.",
                          "Front 1 + Matte 1 + Front 2 + Matte 2"),
    # utility
    "stmap": ("Generates an ST/UV map (red = U, green = V).",
              "Feed an STMap node for warps/distortion, or bake screen UVs.",
              "none (generator)"),
    "nan_cleanup": ("Replaces NaN/Inf pixels with 0 per channel.",
                    "Fix corrupt render pixels that break downstream math or filters.",
                    "Front 1 (optionally Front 2 as patch source)"),
    # noise  (keyframe `seed` to evolve any of these over time)
    "noise_cells": ("Flat random value per `cellSize`-pixel cell; `seed` picks/drifts the pattern.",
                    "Blocky random masks, mosaic seeds.", "none"),
    "noise_value": ("Smooth value noise; `scale` = feature size, `gain` = contrast, `seed` = pattern/drift.",
                    "Organic break-up masks, soft procedural texture, displacement source.",
                    "none"),
    "noise_fbm": ("3-octave fractal noise; `lacunarity`/`persistence` shape it, `seed` = pattern/drift.",
                  "Clouds, smoke/atmosphere masks, natural-looking break-up.", "none"),
    "voronoi": ("Nearest feature-point distance; `jitter` 0=grid..1=random, `seed` = pattern/drift.",
                "Cellular/organic patterns, scales, cracked textures.", "none"),
    # sdf_shapes
    "sdf_circle": ("Anti-aliased circle matte around Centre.",
                   "Round garbage mattes, spotlights, vignette shapes.", "none (uses Centre)"),
    "sdf_box": ("Anti-aliased rectangle matte (`bx`×`by`); `hollow` 0..1 cuts out the middle.",
                "Rectangular holdouts, framing masks, rectangular outlines.", "none (uses Centre)"),
    "sdf_rounded_box": ("Rounded rectangle (`corner`); `hollow` 0..1 cuts out the middle.",
                        "Soft-cornered framing masks and outlines.", "none (uses Centre)"),
    "sdf_ring": ("Annulus (ring) matte; `radius` and `thickness`.",
                 "Circular outlines, target/HUD shapes, halos.", "none (uses Centre)"),
    "sdf_polygon": ("Regular n-gon (`sides`, `radius`, `rot`); `hollow` 0..1 cuts out the middle.",
                    "Polygonal masks/outlines (hexagons, triangles), stylised shapes.",
                    "none (uses Centre)"),
    # hsv_color
    "rgb_to_hsv": ("Converts RGB to HSV (H,S,V on R,G,B).",
                   "Inspect or feed hue/sat/value into other tools.", "Front 1"),
    "hsv_to_rgb": ("Converts HSV (on Front 1 RGB) back to RGB.",
                   "Reconstruct colour after manipulating HSV channels.", "Front 1 = HSV"),
    "hue_rotate": ("Luma-preserving hue rotation; `hue` 0..1 = full turn.",
                   "Shift colours without changing brightness.", "Front 1"),
    "chroma_key": ("Matte from hue distance to `keyHue` with a `satMin` floor.",
                   "Quick chroma key by colour (greens, blues, skin).", "Front 1"),
    "color_replace": ("Shifts hues near `srcHue` toward `dstHue`, leaving the rest.",
                      "Recolour one object/colour while protecting everything else.",
                      "Front 1"),
    "vibrance": ("Smart saturation — `vibrance` lifts low-sat pixels more than vivid ones, "
                 "`saturation` is a master scale, `skinProtect` spares skin hues.",
                 "Add punch without clipping already-saturated colours or wrecking skin.",
                 "Front 1"),
    "hsl_targeted": ("Applies `dHue`/`dSat`/`dVal` only inside a hue band (`centerHue`, "
                     "`bandWidth`, `soft`); the rest is untouched.",
                     "Per-colour grade — darken the blues, desaturate the greens, warm skin.",
                     "Front 1"),
    "split_tone": ("Tints shadows toward `shadowHue` and highlights toward `highHue`, "
                   "weighted by luma; `balance` slides the pivot.",
                   "Classic teal-shadow / warm-highlight (and similar) colour looks.",
                   "Front 1"),
    "sat_matte": ("Matte from a saturation window [`satLow`,`satHigh`] gated by a `valMin` "
                  "brightness floor.",
                  "Qualifier that isolates vivid vs neutral regions to drive a downstream grade.",
                  "Front 1"),
    # matte_combine
    "premult": ("Multiplies RGB by the matte (Matte 1).",
                "Premultiply before operations that expect premult footage.",
                "Front 1 + Matte 1"),
    "unpremult": ("Divides RGB by the matte (guards 0).",
                  "Unpremultiply before colour-correcting an edge.", "Front 1 + Matte 1"),
    "matte_and": ("Intersection of two mattes (`m1 * m2`).",
                  "Keep only where both mattes overlap.", "Matte 1 + Matte 2"),
    "matte_or": ("Union of two mattes (`max`).",
                 "Combine two mattes into one.", "Matte 1 + Matte 2"),
    "matte_subtract": ("Matte 1 minus Matte 2 (clamped).",
                       "Cut one matte out of another (holdouts).", "Matte 1 + Matte 2"),
    "matte_xor": ("Exclusive-or of two mattes.",
                  "Keep only the non-overlapping parts.", "Matte 1 + Matte 2"),
    "matte_invert": ("Inverts the matte (`1 - m1`).",
                     "Flip a matte's inside/outside.", "Matte 1"),
    "matte_grade": ("Gamma + gain on the matte (clamped).",
                    "Tighten or spread a matte's edge/density.", "Matte 1"),
    # uv_distortion
    "lens_distort": ("Radial barrel/pincushion ST map (k1, k2), aspect-corrected.",
                     "Add lens distortion to a clean render (feed an STMap node) to match a plate.",
                     "none (generator → STMap)"),
    "lens_undistort": ("Approximate inverse of the radial model — removes lens distortion.",
                       "Flatten a distorted plate before tracking/paint, then re-distort after.",
                       "none (generator → STMap)"),
    "anamorphic_unsqueeze": ("Horizontal stretch ST map; `squeeze` = anamorphic factor (2.0 = 2x).",
                             "Unsqueeze anamorphic footage to its correct aspect.",
                             "none (generator → STMap)"),
    "uv_transform": ("Zoom/pan ST map; `zoom` >1 zooms in, `panX/panY` shift in UV units.",
                     "Reposition/scale a source through an STMap without a Transform.",
                     "none (generator → STMap)"),
    # color_grade (additions)
    "exposure": ("Multiplies by 2^`stops`.",
                 "Exposure adjustment in photographic stops.",
                 "Front 1"),
    "contrast": ("Scales values around a `pivot`; `contrast` >1 increases.",
                 "Add/reduce contrast about a chosen mid grey (0.18 scene-linear default).",
                 "Front 1"),
    "lift_gamma_gain": ("Master tonal grade: `gain` (mult), `lift` (offset), then `gamma`.",
                        "Primary grade of shadows/mids/highlights.",
                        "Front 1"),
    "white_balance": ("Per-channel gain (`gainR/G/B`).",
                      "Neutralise a colour cast or warm/cool the image.",
                      "Front 1"),
    "srgb_to_linear": ("Exact piecewise sRGB → linear decode.",
                       "Linearise sRGB-encoded footage before doing light-linear math.",
                       "Front 1"),
    "linear_to_srgb": ("Exact piecewise linear → sRGB encode.",
                       "Re-encode to sRGB for display/output after linear work.",
                       "Front 1"),
    # fractals  (8-iteration escape-time; pan/zoom via node Centre + `zoom`)
    "mandelbrot": ("Escape-time Mandelbrot set; `cRe`/`cIm` seed z0 (keyframe to morph), `gain`/`gamma` shape the bands. Grayscale.",
                   "Procedural fractal texture/matte; abstract background or displacement source.",
                   "none"),
    "julia": ("Escape-time Julia set; constant `cRe`/`cIm` picks the shape (keyframe to morph), `gain`/`gamma` shape the bands. Grayscale.",
              "Animated organic fractal element; morphing background or matte.",
              "none"),
    "burning_ship": ("Burning Ship fractal (abs-folded squaring); `cRe`/`cIm` seed z0 (keyframe to morph), `gain`/`gamma` shape the bands. Grayscale.",
                     "Sharp, ship-like procedural fractal texture/matte.",
                     "none"),
    # stmap_generators
    "polar_to_cartesian": ("Polar/rectangular ST map around Centre; `twist` rotates, `zoom` scales radius.",
                           "Tiny-planet, mirror-ball and 360 reframes — feed an STMap node.",
                           "none (generator → STMap)"),
    "kaleidoscope_map": ("Mirror-folds angular space into `segments` wedges around Centre; `rot` spins it.",
                         "Kaleidoscope / mirror-symmetry looks — feed an STMap node.",
                         "none (generator → STMap)"),
    "lens_distort_map": ("Radial barrel/pincushion ST map (`k1`,`k2`) with anamorphic `squeeze` around Centre.",
                         "Add or (negate k1/k2 to) remove lens distortion — feed an STMap node.",
                         "none (generator → STMap)"),
    "glitch_block_map": ("Block-shuffle ST map; hashes `blockSize` blocks and offsets them by `corruption`.",
                         "Datamosh / block-glitch — keyframe `corruption` to trigger, feed an STMap node.",
                         "none (generator → STMap)"),
    "heat_haze_map": ("fbm-driven UV-offset ST map; `amp` strength, keyframe `seed` to shimmer.",
                      "Heat-haze / refraction wobble — feed an STMap node.",
                      "none (generator → STMap)"),
    "coc_from_depth": ("Per-pixel circle-of-confusion radius (0..1) from depth on Matte 1; `focusDepth/Range`, `maxBlur`.",
                       "Drive a variable-blur/Defocus node's blur-amount map for depth-of-field.",
                       "Matte 1 (depth)"),
    "chromatic_aberration_map": ("Radial per-channel ST map (red channel's UV) + blue = offset magnitude; `amount`.",
                                 "Lens chromatic aberration / defringe — feed an STMap node (see Notes).",
                                 "none (generator → STMap)"),
    # control_surfaces
    "painted_grade": ("Grades Front 1 using a PAINTED Front 2 control map: r2 = local exposure, "
                      "g2 = local hue shift, b2 = local saturation (0.5 = neutral on each).",
                      "Paint a soft control map (in Paint/roto/another Pixel Expression) to drive "
                      "exposure/hue/sat that vary across the frame from one node — no tracked mattes.",
                      "Front 1 (image) + Front 2 (control map); Matte 1 optional (passes through)"),
    "channel_pack": ("Packs three single-channel signals into one RGB: red = Matte 1, green = Matte 2, "
                     "blue = Front 1 luma; matte = 1.",
                     "Ferry three mattes/masks down a single connection through a comp; unpack later with channel_unpack.",
                     "Matte 1 + Matte 2 + Front 1"),
    "channel_unpack": ("Passes a packed RGB (from channel_pack) through unchanged and routes one channel "
                       "to the Matte: `pick` 0/1/2 selects r1/g1/b1.",
                       "Recover a packed mask and send it to OutMatte at the destination; pairs with channel_pack.",
                       "Front 1 (the packed RGB)"),
    "dual_output_depth": ("ONE node, TWO products: RGB is a depth-tinted grade of the beauty (Front 1) while "
                          "the Matte independently keys a depth slab via smoothstep(near, far, m1).",
                          "Tint the beauty by depth AND export a depth-slab matte from the same node — e.g. an "
                          "atmosphere look plus a holdout for the mid-ground.",
                          "Front 1 (beauty) + Matte 1 (depth)"),
    # stylization
    "halftone": ("Newspaper halftone: tiles the frame into `cell`-px cells (rotatable by `angle`) and draws a dot per cell whose size grows with that cell's luma.",
                 "Print/comic look, retro screen-print stylisation, animated dot-screen transitions.",
                 "Front 1"),
    "bayer_dither": ("Ordered 4x4 Bayer dithering: posterizes Front 1's luma to `levels` steps with a dispersed-dot threshold matrix for that crunchy retro 1-bit look.",
                     "Game-Boy / EGA / e-ink stylisation, retro UI, stippled gradients without banding.",
                     "Front 1"),
    "crosshatch": ("Pen crosshatch: 0/45/90/135-degree line sets switch on as luma darkens through four thresholds (darker = more hatch directions).",
                   "Ink-illustration / engraving look, sketch stylisation, comic shading.",
                   "Front 1"),
    "crt": ("CRT/VHS look: scanlines, an RGB phosphor-triad mask, a vignette, and an animated rolling bright bar (keyframe `roll`) multiplied over Front 1.",
            "Retro-monitor / broadcast-glitch stylisation, in-screen TV inserts, music-video grunge.",
            "Front 1 (+ Matte 1 to pass alpha)"),
    "truchet": ("Truchet tiles: each `tile`-px cell is hashed to one of two diagonal arc orientations; the quarter-circle arcs connect across edges into endless maze/circuit lines.",
                "Procedural maze/circuit/pipe textures, generative backgrounds, motion-graphics fills.",
                "none (procedural; ignores Front)"),
    "palette_quantize": ("Snaps Front 1 to `levels` tonal steps and tints the result between two palette anchor colours (default 4-tone; set the colours for a Game-Boy green ramp).",
                         "Limited-palette / pixel-art stylisation, duotone posterise, retro console look.",
                         "Front 1"),
    "seven_segment": ("Burns one SDF 7-segment digit (value `digit` 0..9) into the frame at Centre — no text node. Keyframe `digit` for a frame counter.",
                      "On-screen counters/timers/HUD numerals, retro display overlays, datamosh captions.",
                      "none (generator; composite over your plate)"),
    # optics_physics
    "thin_film": ("Thin-film interference iridescence: a soap-bubble/oil-slick rainbow whose hue tracks an interference phase that grows with radius and `thickness`; animate `shift` to roll the colours.",
                  "Iridescent oil-slick/soap-bubble looks, holographic foil, fuel-rainbow sheens.",
                  "none (uses Centre)"),
    "wave_interference": ("Ripple-tank interference of two circular point sources (Centre + `srcX` offset); animate `phase` to make the ripples travel.",
                          "Caustics/ripple references, sonar-style interference, energy-field FX.",
                          "none (uses Centre)"),
    "moire": ("Beat pattern of two near-identical line gratings (`freqA` vs `freqB`) — an intentional moiré.",
              "Interference/aliasing FX, hypnotic op-art, screen/CRT artefacts.",
              "none"),
    "starfield": ("Procedural stars: space is tiled into `cellSize` cells, each hashed to place one star above `threshold`; animate `twinkle` to pulse them.",
                  "Star backgrounds, sparkle/glint fields, sci-fi skies.",
                  "none"),
    "radar_sweep": ("Rotating radar/oscilloscope sweep around Centre with an exponential afterglow trailing behind the line, plus faint range rings; animate `sweep` 0→2π.",
                    "Radar/sonar HUDs, sci-fi scanner overlays, oscilloscope looks.",
                    "none (uses Centre)"),
    # diagnostics
    "color_blindness": ("Simulates colour-vision deficiency on Front 1 (Machado 2009 severity-1.0 matrix). `type` 0=protan / 1=deutan / 2=tritan; `amount` blends sim vs original.",
                        "Check that comp/graphics read for colour-blind viewers (accessibility QC).",
                        "Front 1 (+ Matte 1 to pass alpha)"),
    "exposure_zebra": ("Overlays animated diagonal stripes on clipped pixels: per-channel max >= `hi` shows red stripes, <= `lo` shows blue stripes; mid passes through. Keyframe `phase` to crawl the stripes.",
                       "Spot blown highlights and crushed blacks at a glance, like a camera zebra.",
                       "Front 1 (+ Matte 1 to render OutMatte)"),
    "gamut_clip": ("Flags illegal pixels: any channel < 0 tinted magenta, any channel > `ceiling` tinted yellow; in-range passes through. `tint` sets warning opacity.",
                   "Catch negative light and over-range values produced by grades, transforms or matrices.",
                   "Front 1 (+ Matte 1 to render OutMatte)"),
}


# Expected incoming colour space per setup. The node does no colour management itself —
# this is the space the pixel values should be in for the math to be correct.
_LINEAR = "scene-linear"
_RAW = "raw / data (no colour management)"
_ANY = "any (data / value op)"
_GEN = "any — generates data/values"
_STMAP = "any input; outputs an ST/UV map — tag output Raw/Data"

EXPECTS = {
    # alpha_matte_tools
    "alpha_crunch": _ANY, "fill_alpha": _ANY, "alpha_fringe": _ANY,
    "luma_key": "scene-linear (Rec.709 luma weights); approximate elsewhere",
    "difference_matte": "any (most even in scene-linear)",
    # pattern_generators
    "radial_ramp": _GEN, "rings": _GEN, "rays": _GEN,
    "checkerboard": _GEN, "bricks": _GEN, "noise_random": _GEN,
    # animated_generators
    "wave_sine": _GEN, "wave_triangle": _GEN, "wave_square": _GEN,
    "wave_sawtooth": _GEN, "pulse_rings": _GEN, "spin_rays": _GEN,
    # color_grade
    "despill_green": "your working space (keep consistent)",
    "saturation": "scene-linear (Rec.709 luma weights)",
    "voxelize": _ANY,
    "exposure": _LINEAR,
    "contrast": "scene-linear (pivot 0.18; use ~0.5 in display/log)",
    "lift_gamma_gain": "scene-linear, or your grading space",
    "white_balance": _LINEAR,
    "srgb_to_linear": "sRGB-encoded 0–1 in → linear out",
    "linear_to_srgb": "linear in → sRGB-encoded out",
    # 3d_position_tools
    "pmatte_sphere": _RAW, "pmatte_rings": _RAW, "pmatte_rays": _RAW, "box_matte": _RAW,
    "normal_relight": "raw normal pass in; output is scene-linear light",
    "fresnel_facing": _RAW,
    # depth_tools
    "depth_normalize": _RAW, "depth_matte": _RAW, "depth_dof_mask": _RAW,
    "depth_contours": _RAW, "depth_posterize": _RAW,
    "depth_fog": "depth raw; beauty scene-linear",
    "depth_fade": "depth raw; beauty scene-linear",
    "depth_mix": "depth raw; plates in matching space",
    "depth_grade": "depth raw; beauty scene-linear",
    # aov_tools
    "aov_add": _LINEAR, "aov_grade_add": _LINEAR,
    "ao_multiply": "scene-linear (AO on Matte 1 is data)",
    "albedo_divide": _LINEAR, "albedo_multiply": _LINEAR,
    "aov_clamp_negative": _ANY,
    "screen_merge": "scene-linear, or display-referred for a Photoshop-style screen",
    "id_isolate": "any (mask is data; grades in your working space)",
    "crypto_pick_2rank": _RAW, "crypto_pick_4rank": _RAW,
    # uv_distortion
    "lens_distort": _STMAP, "lens_undistort": _STMAP,
    "anamorphic_unsqueeze": _STMAP, "uv_transform": _STMAP,
    # noise
    "noise_cells": _GEN, "noise_value": _GEN, "noise_fbm": _GEN, "voronoi": _GEN,
    # sdf_shapes
    "sdf_circle": _GEN, "sdf_box": _GEN, "sdf_rounded_box": _GEN,
    "sdf_ring": _GEN, "sdf_polygon": _GEN,
    # hsv_color
    "rgb_to_hsv": "any (operates on the RGB values as given)",
    "hsv_to_rgb": "HSV data in → RGB out",
    "hue_rotate": "any (operates on the RGB values as given)",
    "chroma_key": "your working/display space (hue-based)",
    "color_replace": "your working/display space (hue-based)",
    "vibrance": "your working/display space (saturation-based)",
    "hsl_targeted": "your working/display space (hue-based)",
    "split_tone": "your working/display space (tonal + hue-based)",
    "sat_matte": "your working/display space (saturation-based)",
    # matte_combine
    "premult": _ANY, "unpremult": _ANY, "matte_and": _ANY, "matte_or": _ANY,
    "matte_subtract": _ANY, "matte_xor": _ANY, "matte_invert": _ANY, "matte_grade": _ANY,
    # utility
    "stmap": _STMAP, "nan_cleanup": _ANY,
    # fractals
    "mandelbrot": _GEN, "julia": _GEN, "burning_ship": _GEN,
    # stmap_generators
    "polar_to_cartesian": _STMAP, "kaleidoscope_map": _STMAP,
    "lens_distort_map": _STMAP, "glitch_block_map": _STMAP,
    "heat_haze_map": _STMAP, "chromatic_aberration_map": _STMAP,
    "coc_from_depth": "depth raw in; outputs a 0..1 blur-amount map (Raw/Data)",
    # control_surfaces
    "painted_grade": "Front 1 in your grading/scene-linear space; Front 2 is a 0..1 data control map",
    "channel_pack": "any (the three packed signals are data — tag the output Raw/Data)",
    "channel_unpack": "any (operates on the channels as data)",
    "dual_output_depth": "depth raw on Matte 1; beauty in your working/scene-linear space",
    # stylization
    "halftone": "display-referred / working image (luma-driven look)",
    "bayer_dither": "display-referred / working image (luma-driven look)",
    "crosshatch": "display-referred / working image (luma-driven look)",
    "crt": "display-referred / working image (look applied multiplicatively)",
    "truchet": _GEN,
    "palette_quantize": "display-referred / working image (luma-driven look)",
    "seven_segment": _GEN,
    # optics_physics
    "thin_film": _GEN, "wave_interference": _GEN, "moire": _GEN,
    "starfield": _GEN, "radar_sweep": _GEN,
    # diagnostics
    "color_blindness": "display-referred sRGB-ish (the Machado 2009 matrices are fit for sRGB display values)",
    "exposure_zebra": "scene-linear / your working space (clip thresholds hi=1.0, lo=0.0 assume normalised values)",
    "gamut_clip": "scene-linear / your working space (negative + over-ceiling detection on raw channel values)",
}


# Optional long-form notes appended to a setup's .md under a "## Notes" heading. Use for
# tools whose value isn't obvious from the one-line Use case (workflow, recipes, gotchas).
NOTES = {
    "hsl_targeted": """
## Notes

A **secondary colour correction in a single node** — it isolates one range of hues and
pushes only those pixels, leaving everything else untouched. No separate key, matte, or
qualifier node: the hue selection *is* the qualifier. This is the Lightroom/Resolve **HSL
panel** behaviour, or a Flame **secondary**, as one expression node you can keyframe.

### How it works
1. **Select** a soft slice of the colour wheel — a band centred on `centerHue`,
   `bandWidth` wide, with `soft` feathering the edges. Inside the band the weight is ~1,
   outside it is 0, and the `soft` zone ramps between them (so the grade blends instead of
   hard-clipping). The band **wraps around the wheel**, so a `centerHue` near 0.0 catches
   reds on both sides of the seam.
2. **Grade** the selected pixels along three independent axes:
   - `dHue` — rotate the hue (luma-preserving, like `hue_rotate`, so it won't change
     brightness)
   - `dSat` — scale saturation (`+` more vivid, `-` toward grey)
   - `dVal` — scale brightness (`+` lighter, `-` darker)

   Each channel is `mix(original, graded, bandWeight)`, so unselected colours pass through
   untouched.

### Why use it
"Change one colour without touching the rest" is miserable in RGB — "the greens" is a
tangled three-channel inequality. In hue space it's just *a position on the wheel ± a
width*. That's the whole reason this lives in `hsv_color/`.

### Hue reference
`centerHue` is 0..1 around the wheel: **red 0.0, orange ~0.07, yellow ~0.15, green 0.33,
cyan 0.5, blue 0.66, magenta 0.83.**

### Recipes
| Goal | `centerHue` | The move |
|------|-------------|----------|
| Calm a too-vivid green spill on foliage | 0.33 | `dSat` -0.4 |
| Make a daytime sky deeper blue | 0.6 | `dSat` +0.3, `dVal` -0.1 |
| Warm skin tones | 0.07 | `dHue` +0.01, `dSat` +0.1 |
| Turn a red car slightly orange | 0.0 | `dHue` +0.05 |
| Knock back a distracting yellow sign | 0.15 | `dSat` -0.5, `dVal` -0.2 |

### Practical notes
- **Tune the selection first, grade second.** Crank `dSat` to an extreme (`+2` or `-1`) so
  the affected region is obvious, adjust `bandWidth`/`soft` until *only* the colour you want
  is moving, then dial the deltas back to taste.
- **`soft` prevents banding** on gradients (skies, cheeks) — a hard band edge shows a seam.
- **Relationship to neighbours:** `color_replace` is the `dHue`-only special case aimed at a
  target hue; `chroma_key` / `sat_matte` *output a matte* for a band instead of grading it
  inline. Use those when a downstream node needs the selection; use `hsl_targeted` when you
  just want the corrected pixels out the other side.
""",
    "vibrance": """
## Notes

A **smarter saturation** than a flat multiply. A plain saturation control pushes every
pixel equally, so the colours that were already vivid clip and posterize first while the
muted ones still look flat. `vibrance` measures each pixel's current saturation and lifts
the *low*-saturation pixels more than the already-vivid ones — you get punch in the dull
areas without blowing out the colours that were fine.

### How it works
The boost factor is `1 + vibrance * (1 - S)`, where `S` is the pixel's HSV saturation. So
a grey-ish pixel (`S` near 0) gets the full lift, a saturated pixel (`S` near 1) is barely
touched. That result is then scaled by a master `saturation`, and the whole move is faded
out near skin hues by `skinProtect`. Every channel is `mix(luma, original, factor)`, so
brightness is held fixed — only chroma moves.

### Controls
- `vibrance` — the smart lift (0 = off). Positive adds, negative pulls dull colours toward
  grey while sparing vivid ones.
- `saturation` — a plain master multiply on top (1.0 = unchanged), if you also want a
  flat push.
- `skinProtect` — 0..1, how strongly to spare the skin-hue band (~orange) so faces don't go
  radioactive when you push everything else.

### Why use it
The classic problem: a shot needs more life, but cranking saturation makes the red jacket
or the green sign clip and band before the rest catches up. Vibrance fills in the muted
mid-saturation colours and leaves the already-saturated ones alone — the standard
"give it some pop without it looking cartoonish" move.

### Practical notes
- **Lead with `vibrance`, not `saturation`** for natural results; reach for `saturation`
  only when you genuinely want an even push across the whole frame.
- **Turn on `skinProtect`** whenever there are people in frame and you're pushing hard.
- Negative `vibrance` is a gentle, vivid-preserving **de**-saturation — handy for calming a
  busy background without flattening its few strong colours.
""",
    "split_tone": """
## Notes

Tints the **shadows** toward one colour and the **highlights** toward another — the
backbone of a graded "look" (the ubiquitous teal-shadow / warm-highlight being the obvious
one). It's a colour move keyed off *brightness*, which is exactly what RGB makes awkward
and tonal/HSV thinking makes easy.

### How it works
Pixel luma drives two weights: a shadow weight that's strong in the darks and a highlight
weight that's strong in the brights. Each region is nudged toward its tint colour — derived
from `shadowHue` / `highHue` at full saturation — *centred* so a neutral tint does nothing
and a hue pushes some channels up and others down (a tint, not a brightness change).
`balance` slides the luma pivot between the two regions.

### Controls
- `shadowHue` / `highHue` — 0..1 hue of each tint (red 0.0, orange ~0.07, yellow ~0.15,
  green 0.33, cyan 0.5, blue 0.66, magenta 0.83).
- `shadowAmt` / `highAmt` — strength of each tint (start small, ~0.1).
- `balance` — -0.5..0.5, shifts the shadow/highlight split point. Negative throws more of
  the image into "highlight", positive into "shadow".

### Why use it
It's the fastest way to put a cohesive colour personality on a plate: cool the shadows and
warm the highlights for the modern blockbuster look, or push complementary hues for a
stylised grade. Defaults are a gentle teal-blue shadow (`0.58`) / warm-orange highlight
(`0.08`).

### Practical notes
- **Keep amounts low.** 0.05–0.15 reads as a grade; higher reads as a colour cast.
- **Complementary hues** (≈0.5 apart on the wheel) give the strongest, most filmic
  separation — teal/orange is 0.5↔0.08, roughly opposite.
- **`balance` is your midtone protector** — slide it to keep the tint off the faces/midtones
  and concentrated in the deep shadows or bright highlights.
- Works in your working/display space; the look depends on where your blacks and whites
  sit, so set exposure/contrast first, tint second.
""",
    "sat_matte": """
## Notes

A **qualifier**, not a grade: it outputs a matte that is white where a pixel's saturation
falls inside a window and black elsewhere, so you can isolate *vivid* vs *neutral* regions
and drive a downstream correction with the result. It's the saturation-axis sibling of
`chroma_key` (which qualifies by hue).

### How it works
The matte is `inside(S, satLow..satHigh)` with soft edges, multiplied by a `valMin`
brightness floor so dark, noisy, near-black pixels don't sneak in. The result is written to
RGB **and** the Matte field, so you can use Result or OutMatte downstream.

### Controls
- `satLow` / `satHigh` — the saturation window to keep (default `0.15..1.0` = "anything
  reasonably colourful").
- `soft` — feathers both edges of the window so the matte isn't binary.
- `valMin` — brightness floor; raise it to reject dark regions whose hue/sat is unreliable.

### Why use it
Lots of fixes want "only the colourful bits" or "only the greys": pull a mask of the
saturated product on a neutral set, protect already-vivid areas from a global saturation
push, find blown-out neon to tame, or isolate the desaturated background to grade
separately. Because it's saturation-based it catches colour the way a hue key can't — it
doesn't care *which* colour, only *how* colourful.

### Practical notes
- **Invert it** (feed through `matte_invert`, or swap the window) to select the *neutral*
  regions instead of the vivid ones.
- **Combine with hue** — chain after `chroma_key` via `matte_and` to get "this hue *and*
  this saturation", a much tighter selection than either alone.
- Raise `valMin` first if a noisy shadow area is leaking into the matte.
""",
    "exposure": """
## Notes

Multiplies the image by `2^stops` — a single **photographic exposure** control. One stop is
a doubling (or halving) of light: `stops` +1 is twice as bright, -1 is half, +2 is 4x.

### Why stops (not a raw multiply)
Stops match how a DP and a lighting TD think, and they're perceptually even — every step is
the same *ratio*, so +1 looks like the same size move whether you're lifting a dark plate or
trimming a bright one. A plain "gain 1.7" carries no such intuition.

### Practical notes
- **Scene-linear only.** A clean `2^stops` multiply is only physically meaningful on linear
  light. On log/display-encoded pixels it'll crush or smear the tonal range — linearise
  first (`srgb_to_linear` or a Colour Mgmt node) and re-encode after.
- **Order:** exposure is a multiply, so it commutes with other gains but *not* with offsets
  or gamma — set exposure before `contrast` / `lift_gamma_gain` so the pivot math sees the
  intended levels.
- Keyframe `stops` for a quick exposure ramp (a light coming up, an iris pull).
""",
    "contrast": """
## Notes

Scales values around a `pivot`: `pivot + (value - pivot) * contrast`. Tones above the pivot
go up, tones below go down, and the pivot itself stays put — so it stretches or compresses
the range without shifting the midpoint.

### The pivot is the whole game
The pivot is the tone that doesn't move. Everything hinges on putting it where your "middle"
actually is **in the current encoding**:
- **scene-linear** → `0.18` (18% middle grey), the default.
- **display / log / sRGB** → roughly `0.5`.

Pick the wrong pivot and contrast also shifts overall brightness (the image gets darker or
lighter as you add contrast), which usually isn't what you want.

### Practical notes
- `contrast` > 1 increases, < 1 flattens, 1.0 is unchanged.
- **No clamp** — strong contrast can drive values negative or super-white. Follow with
  `aov_clamp_negative` or a clamp if a downstream op can't take it.
- Do contrast *after* exposure/white-balance so the pivot sits at the right level.
""",
    "lift_gamma_gain": """
## Notes

The **primary tonal grade**: one control each for highlights, shadows, and midtones. The
order baked in is `pow(value * gain + lift, 1/gamma)`.

### What each knob does
- **`gain`** — a multiply; its effect grows with brightness, so it pivots on black and
  mostly moves the **highlights** (white point).
- **`lift`** — an add; a constant push that's most visible in the **shadows** (black point),
  fading out toward the highlights.
- **`gamma`** — a power curve that bends the **midtones** while leaving 0 and 1 roughly
  anchored — brightening or darkening the mids without crushing or clipping the ends.

### Practical notes
- **Workflow:** set `gain` for the highlights, `lift` for the shadows, then `gamma` to taste
  on the mids — that's the order the math applies and the order that converges fastest.
- This is a luma-style master grade on all three channels equally; for a colour cast use
  `white_balance`, for a single-hue fix use `hsl_targeted`.
- Defaults (`lift` 0, `gamma` 1, `gain` 1) are a no-op, so it's safe to drop in and dial.
""",
    "white_balance": """
## Notes

A per-channel gain (`gainR` / `gainG` / `gainB`) — the simplest **colour-cast neutraliser**.
Multiplying each channel independently slides the image warm/cool/green/magenta.

### How to balance
Find something that *should* be neutral grey/white in the shot, read its RGB, and set the
gains to equalise the channels (raise the low channels or lower the high ones until R = G =
B on that sample). A common convention is to leave green at 1.0 and trim red/blue around it.

### Practical notes
- **Scene-linear** for a physically correct white balance — a channel multiply models a
  lighting/sensor gain, which is a linear operation. On display-encoded pixels it still
  *works* as a look but won't match a real temperature shift.
- It's a global cast fix; it can't correct a cast that only affects one tonal range — reach
  for `lift_gamma_gain` (per-range) or `hsl_targeted` (per-hue) for that.
- Three independent multiplies, no clamp — same downstream caution as the other grades.
""",
    "srgb_to_linear": """
## Notes

Exact piecewise **sRGB → linear decode**. The node does no colour management itself, so this
is the manual "linearise before light math" step.

### When you need it
All the physically-meaningful operations in this library — `exposure`, `white_balance`,
`aov_*` light-pass math, `normal_relight`, fog/depth blends — assume **scene-linear** input.
If your footage is sRGB-encoded (most 8-bit/display sources), decode it first or those ops
will give wrong results (crushed shadows, off colours).

### Practical notes
- **Pair it with `linear_to_srgb`**: decode → do your linear work → re-encode for
  display/output. They're exact inverses, so a decode/encode round-trip with nothing between
  is a no-op.
- This is the *exact* piecewise sRGB curve (linear toe + 2.4 gamma segment), not the 2.2
  approximation — match it on the encode side.
- Only for sRGB-encoded sources. Don't run it on data passes (P, normals, depth, ST maps,
  Cryptomatte) — those are already linear/raw and must stay untouched.
""",
    "linear_to_srgb": """
## Notes

Exact piecewise **linear → sRGB encode** — the re-encode half of the pair. Run it *after*
your linear work to put pixels back into a display-referred sRGB space for viewing or output.

### Practical notes
- **Pair with `srgb_to_linear`**: decode → linear ops → encode. The two are exact inverses,
  so the round-trip is lossless when nothing happens in between.
- Encode as the **last** step — anything after it (more grades, light math) would be
  operating on display-encoded values and misbehave.
- Exact piecewise sRGB, not a 2.2 gamma approximation; use the matching decode upstream.
- Data passes (P, normals, depth, ST maps, crypto) are linear/raw by definition — never
  sRGB-encode them.
""",
    "depth_normalize": """
## Notes

Remaps a raw depth pass into a viewable, standardised **0..1** range — the front door to
the rest of the depth toolkit.

### Why run it first
Render depth (Z) usually arrives in **world units** (0 to hundreds/thousands), not 0..1. The
other depth tools default to a 0..1 range, so normalising once up front lets all their
defaults (`zMin` 0.2, `focus` 0.5, …) make sense. Set `near`/`far` to your scene's nearest
and farthest depth and the result becomes a clean 0 (near) → 1 (far) ramp.

### Practical notes
- **Depth arrives on Matte 1 (`m1`)** — the convention for every depth setup here. Wire your
  Z pass to Matte 1; view OutMatte. Also wire it to Front 1 if you want it on Result too.
- **If closer = larger** in your pass (some renderers invert Z), swap `near` and `far`.
- Depth is **raw/data** — never colour-manage it (no sRGB, no grade) before these nodes.
""",
    "depth_matte": """
## Notes

A **distance qualifier**: white inside the depth band `[zMin..zMax]`, black outside, with
soft edges. The depth-axis sibling of a luma or chroma key.

### Why use it
Pull a garbage matte by distance — isolate the midground, hold out everything past a wall,
grab a character standing at a known depth — without rotoing. Because it's just depth, it
ignores colour and texture entirely.

### Practical notes
- **Depth on Matte 1.** Defaults assume a normalised 0..1 depth (run `depth_normalize`
  first); for raw world-unit depth set `zMin`/`zMax`/`soft` to your scene's range.
- `soft` feathers both ends of the band — widen it to avoid a hard edge on a gradient.
- It's a qualifier (written to RGB **and** Matte) — combine with an object alpha via
  `matte_and` to get "this object *and* in this depth range".
""",
    "depth_fog": """
## Notes

**Atmospheric perspective** — blends the beauty toward a fog colour as things get farther
away, the cheap way to add depth and air to a CG render or matte painting.

### Practical notes
- **Front 1 = beauty, Matte 1 = depth.** `near`/`far` set where the fog starts and where it
  fully saturates; `fogR/G/B` is the haze colour (default a cool blue-grey).
- **Work in scene-linear** for plausible falloff, and put `fogR/G/B` in that same space.
- Unlike `depth_fade`, this keeps alpha intact (`matte = m1`) — it tints, it doesn't dissolve.
- Keyframe `near`/`far` (or the fog colour) for rolling mist or a clearing-fog reveal.
""",
    "depth_fade": """
## Notes

Fades the beauty's **colour and alpha together** to nothing with distance — a premultiplied
depth dissolve, so distant pixels genuinely disappear rather than just darken.

### depth_fade vs depth_fog
`depth_fog` pushes far pixels toward a colour but keeps them opaque; `depth_fade` takes them
to transparent. Use fade when the element needs to **vanish into** whatever's behind it
(dissolve a far crowd, taper a particle sim); use fog for haze/air.

### Practical notes
- **Front 1 = beauty, Matte 1 = depth.** `near`/`far` set the fade range.
- Because alpha fades too, the result composites correctly over a background — drop it
  straight into the comp.
""",
    "depth_mix": """
## Notes

Composites **Front 1 (near) over Front 2 (far)** using depth as the switch — a poor-man's
deep comp for slotting one element between two layers by distance.

### Practical notes
- **Front 1 = near plate, Front 2 = far plate, Matte 1 = depth.** `zThresh` is the crossover
  depth; `soft` is the blend width across it.
- The two plates must be **aligned/registered** — this picks per-pixel between them, it
  doesn't transform anything.
- For more than two layers, chain: this node's Result becomes the next `depth_mix`'s Front 1.
""",
    "depth_dof_mask": """
## Notes

Builds a **blur-amount mask** for depth of field: 0 at the `focus` plane, ramping to 1 as
depth departs focus in either direction. It does *not* blur — it drives a blur.

### How to wire it
Feed the **output into the blur-amount / defocus input of a Defocus node**, not into an
image input. The node reads this mask per pixel to decide how much to defocus there.

### Practical notes
- **Depth on Matte 1.** `focus` = the depth that stays sharp; `range` = how quickly things
  defocus away from it (smaller = shallower DOF).
- Symmetric — objects nearer *and* farther than focus both blur, as a real lens does.
- Keyframe `focus` for a rack-focus pull.
""",
    "depth_contours": """
## Notes

Draws **topographic iso-depth lines** — a bright line every `spacing` in depth — over the
pass. Mostly a **diagnostic / look** tool: it makes the shape of a depth pass legible at a
glance, and doubles as a stylised contour effect.

### Practical notes
- **Depth on Matte 1.** `spacing` and `lineWidth` are in **depth units**, so normalise first
  (`depth_normalize`) or the lines bunch up / vanish at world-unit scales.
- Reduce `lineWidth` for fine lines; increase `spacing` for fewer of them.
""",
    "depth_posterize": """
## Notes

Quantises depth into `steps` flat bands — turns a smooth Z pass into discrete **"cards"**.

### Why use it
Cheap 2.5D separation: each band is a constant depth you can pull with `depth_matte` and
treat as its own layer (parallax, per-card grades, a stepped/stylised look). Also handy to
preview how many depth slices a shot really needs.

### Practical notes
- **Depth on Matte 1.** `steps` = number of bands.
- Pair with `depth_matte` (set `zMin`/`zMax` to one band) to extract a single card.
""",
    "depth_grade": """
## Notes

Multiplies the beauty by a gain that **ramps with distance** (`gainNear` → `gainFar`) — adds
density/falloff with depth without introducing a colour, the way `depth_fog` does.

### depth_grade vs depth_fog
Use `depth_grade` to **darken or lift** with distance (atmospheric density, a light that
falls off into the deep); use `depth_fog` when you want far pixels to take on a **colour**.

### Practical notes
- **Front 1 = beauty, Matte 1 = depth.** `near`/`far` set the ramp range; `gainNear`/
  `gainFar` are the multipliers at each end (default lifts near, darkens far).
- A multiply, so keep it in **scene-linear** for predictable results.
""",
    "aov_add": """
## Notes

Sums two light/AOV passes with a per-pass gain — `pass1 * gainA + pass2 * gainB`. The atom
of **render-pass recombination**: in linear, a beauty *is* the sum of its light components
(diffuse + specular + GI + …).

### The chaining workflow
The node only has two RGB inputs, so to rebuild a full beauty from many passes you **chain**:
this node's Result becomes the next node's Front 1 (a running sum), Front 2 is the next pass.

### Practical notes
- **Must be scene-linear** — additive pass math is only correct on linear light.
- `gainA`/`gainB` let you **rebalance** as you recombine: kill the specular, push the GI,
  etc., without re-rendering.
- Keeps Front 1's alpha (`matte = m1`).
""",
    "aov_grade_add": """
## Notes

The core **"isolate a pass, art-direct it, put it back"** move: `running_beauty + pass *
tint * exposure`. This is why you render in passes at all.

### How to wire it
- **Front 1 = the running beauty** (or another pass total), **Front 2 = the single pass** you
  want to tweak. Tint and expose Front 2, then add it back into Front 1.
- Chain one node per pass you want to touch; passes you don't touch can stay in the
  `aov_add` running sum.

### Practical notes
- **Scene-linear.** `exposure` scales the pass's intensity, `tintR/G/B` recolours it — e.g.
  warm just the bounce light, or knock the spec down a stop, with no re-render.
- Keeps Front 1's alpha.
""",
    "ao_multiply": """
## Notes

Multiplies the beauty by an **ambient-occlusion** pass, with controls to dial it in:
`amount` blends from off (1.0) to full AO, `aoGamma` shapes the contact-shadow falloff.

### Practical notes
- **Front 1 = beauty, Matte 1 = AO.** (AO rides on Matte 1, like depth.)
- `amount` 0..1 is the "how dirty" knob — 0 disables it, 1 is full multiply.
- `aoGamma` < 1 **deepens** the contact shadows, > 1 **lightens** them.
- Multiply belongs in **scene-linear**; the AO pass itself is data (0..1 occlusion).
""",
    "albedo_divide": """
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
""",
    "albedo_multiply": """
## Notes

Multiplies a (possibly graded) **albedo** by a **lighting** pass — the recombine/relight half
of the pair with `albedo_divide`: `albedo * lighting`.

### The de-light / re-light loop
`albedo_divide` to pull lighting → grade/denoise/repaint the albedo or the lighting
independently → `albedo_multiply` to put them back together. Lets you treat texture and
illumination as separate, art-directable layers.

### Practical notes
- **Front 1 = albedo, Front 2 = lighting.**
- Both inputs **scene-linear**; the product is your reconstructed (or re-lit) beauty.
""",
    "aov_clamp_negative": """
## Notes

Floors every channel at 0 — strips the **sub-zero values** renderers sometimes emit
(negative lobes from filtering/sharpening, stray specular, OpenEXR round-trips).

### Why it matters
Tiny negatives are invisible until an operation chokes on them: `pow`/log encodes go NaN,
`screen_merge` and other multiplicative comps misbehave, glows pick up dark fringes. This is
a cheap **safety pass** to drop in before any of those.

### Practical notes
- No controls — `max(channel, 0)` per channel; keeps alpha (`matte = m1`).
- Put it **before** `screen_merge`, a log/sRGB encode, or a glow extraction.
""",
    "screen_merge": """
## Notes

**Screens** a glow/bloom pass onto the beauty — `1 - (1-base)(1-over)` — the standard way to
add light-emitting passes without the harsh clipping of a plain add.

### Practical notes
- **Front 1 = beauty, Front 2 = the glow/bloom/emission pass.** `gain` scales the pass on
  the way in.
- Screen is a **display-referred** operator (it assumes 0..1), so it reads naturally on
  display-referred images; on scene-linear it still combines but behaves more like a soft
  add. Choose your space to taste — see the **Expects** line.
- Run `aov_clamp_negative` on the glow pass first if it carries negatives.
""",
    "id_isolate": """
## Notes

Grades **only the region picked by an ID/mask pass**, leaving everything outside untouched —
`mix(beauty, beauty * tint * gain, mask)`. A masked secondary driven by a render pass instead
of a key.

### How to wire it
- **Front 1 = beauty, Matte 1 = the mask** (an object-ID matte, a Cryptomatte coverage from
  `crypto_pick_*`, or any 0..1 selection).
- Inside the mask the pixels are tinted/exposed; outside, they pass through bit-for-bit.

### Practical notes
- `gain` + `tintR/G/B` are the grade applied inside the mask.
- Feed it the output of `crypto_pick_2rank`/`4rank` to grade a single object with no roto.
""",
    "crypto_pick_2rank": """
## Notes

Extracts a coverage **matte for one object** from a single Cryptomatte layer (2 ranks), by
matching its `id` hash. The no-roto way to pull any object the renderer tagged.

### Setup (important)
- **Shuffle the crypto layer** so Front 1 = `(hash0, coverage0, hash1)` and Matte 1 =
  `coverage1`. The expression reads those exact slots.
- **`id`** = the object's float32 hash from the Cryptomatte **manifest** (the metadata
  list of name→hash). `tol` = relative match tolerance (leave tiny).
- **The crypto pass MUST be read raw** — no resize, no filtering, no colour management.
  Cryptomatte stores object hashes *as pixel values*; any resample or grade corrupts them and
  the matte falls apart. This is the #1 cause of a broken crypto pull.

### Practical notes
- 2 ranks is enough for solid objects; switch to **`crypto_pick_4rank`** when edges fringe
  (hair, motion blur, semi-transparency need more coverage ranks).
- Feed the result into `id_isolate` (or any matte input) to grade that object.
""",
    "crypto_pick_4rank": """
## Notes

Same object-hash pick as `crypto_pick_2rank`, but reads **two** Cryptomatte layers (4 ranks)
and sums their coverage — for clean anti-aliased and overlapping edges.

### Setup
- **Front 1 / Matte 1 = layer A** `(hash0, cov0, hash1)` + `cov1`; **Front 2 / Matte 2 =
  layer B** `(hash2, cov2, hash3)` + `cov3` (two Shuffles).
- `id` and `tol` work exactly as in the 2-rank version.

### When to use it over 2-rank
Reach for 4-rank when a 2-rank pull **fringes**: fine hair, heavy motion blur, or
semi-transparent edges where a single pixel's coverage is split across more than two objects.
More ranks = more of that partial coverage recovered.

### Practical notes
- **Read the crypto passes raw** — no resize/filter/colour management (see `crypto_pick_2rank`;
  same hard requirement, doubly so across two layers).
- Output goes straight into `id_isolate` or any matte input.
""",
    "pmatte_sphere": """
## Notes

A soft **spherical matte anchored in 3D world space** — white at a world point, falling off
to black over a world-unit radius. Because it keys off a position (P) pass, the matte sticks
to the geometry through camera moves and never aliases.

### Setup
- **Front 1 = the P-world pass** (`r = X, g = Y, b = Z` world position per pixel).
- `cenR/cenG/cenB` = the **world XYZ of the sphere centre**. To find it, sample the P pass at
  the spot you want to target and read the values. `prad` = radius in world units.

### Practical notes
- **Read the P pass raw** — no colour management, no premult; the values *are* coordinates.
- Output is a soft 0..1 ball (written to RGB **and** Matte) — drive a local grade/light with
  it, or `matte_and` it with an object alpha.
- Keyframe `cenR/G/B` to fly the region of influence through the scene.
""",
    "pmatte_rings": """
## Notes

Concentric **3D rings** (a sine of world distance) radiating from a world point — like
`pmatte_sphere`, but a repeating ripple instead of a single falloff.

### Practical notes
- **Front 1 = P-world pass; `cenR/cenG/cenB` = centre in world XYZ** (read from the P pass).
- `ringScale` sets the ring frequency (higher = tighter rings).
- World-anchored, so the rings cling to the geometry — handy for **shockwaves / ripples /
  energy pulses** emanating from a point. Keyframe `cenR/G/B` or `ringScale` to animate.
- Read the P pass raw.
""",
    "pmatte_rays": """
## Notes

A radial **fan of rays on the ground (X–Z) plane**, centred on a world point. It uses only
world X (`r1`) and Z (`b1`), so it's a top-down pattern — think a sunburst on the floor.

### Practical notes
- **Front 1 = P-world pass; `cenR`/`cenB` = centre X/Z in world units.** (Y is ignored — the
  pattern is constant up the vertical axis.)
- `rays` = number of spokes.
- Read the P pass raw. For rays in a different plane, you'd need a pass with the relevant two
  axes on red/blue.
""",
    "box_matte": """
## Notes

An **axis-aligned box (cube) matte** in world space — white inside a rectangular region,
soft-edged outside. The rectangular cousin of `pmatte_sphere`, and cheaper for boxy volumes.

### How it works
It's the **intersection of three per-axis slabs** (X, Y, Z each within `boxSize` of centre),
multiplied together — which is exactly why it's **axis-aligned only**: there's no rotation.

### Practical notes
- **Front 1 = P-world pass; `cenR/cenG/cenB` = box centre in world XYZ; `boxSize` = half-
  extent** (world units); `soft` = edge softness as a fraction of the extent.
- Read the P pass raw. Great for a world-space garbage matte (isolate a room, a vehicle's
  bounding volume, a slab of the set).
""",
    "normal_relight": """
## Notes

A **Lambert (N·L) relight** from a normal pass — add or re-aim a light in comp, no re-render.
For each pixel it dots the surface normal with a light direction and clamps to 0.

### Setup
- **Front 1 = the normal pass**, components in **-1..1** (the node re-normalizes, so a
  slightly off pass is fine).
- `lx/ly/lz` = the light **direction** vector (it's normalized too; magnitude doesn't matter,
  only direction).

### Practical notes
- Output is the **diffuse term** (0..1). Multiply it onto an albedo, tint it, or add it as an
  extra light pass via `aov_grade_add` — its own RGB is a grey lighting map.
- **Normal space matters:** use a consistent space (world or camera). World-space normals give
  a light fixed in the scene; camera-space normals give a light fixed to the camera.
- Raw/data pass in; the **lit output is scene-linear** light.
""",
    "fresnel_facing": """
## Notes

A **rim / facing-ratio matte** from a **camera-space** normal pass: bright where surfaces
turn away from camera (grazing angles), dark where they face it. The comp-side fresnel.

### How it works
It reads `b1` = the normal's **Z** (camera-space): 1 = facing camera, 0 = edge-on. The matte
is `(1 - Nz) ^ power`, so it peaks at the silhouette. `power` sharpens or softens the falloff.

### Practical notes
- **Camera-space normals are required** — world-space normals won't produce a view-dependent
  rim (the whole point is that it follows the camera).
- Uses for the matte: **rim light, edge wear/dirt, fresnel reflections, atmosphere on
  silhouettes.** Written to RGB **and** Matte.
- Raw/data pass in.
""",
    "lens_distort": """
## Notes

Generates a **radial distortion ST map** (barrel / pincushion). Like everything in
`uv_distortion/`, it **does not warp the image itself** — `red = U, green = V`, and you feed
the result into an **STMap node** whose source is the plate you want distorted.

### Practical notes
- **`k1` is the main term:** `k1 < 0` = barrel (wide-angle bulge), `k1 > 0` = pincushion.
  `k2` is a higher-order term that mostly affects the far corners.
- Aspect-corrected (coords normalised by half-width), so distortion stays isotropic at any
  resolution.
- **Tag the output Raw/Data** and STMap it — colour-managing a coordinate map corrupts it.
- Typical job: **add** a plate's measured distortion onto a clean CG render so it matches.
""",
    "lens_undistort": """
## Notes

The **approximate inverse** of `lens_distort` — same radial polynomial, but it divides where
distort multiplies. Outputs an ST map to feed an STMap node.

### The undistort → work → redistort workflow
Flatten a distorted plate (so straight lines are straight) → **track / paint / roto / add CG**
on the undistorted plate → re-apply the distortion with `lens_distort` using the **same
`k1`/`k2`** so the result drops back onto the original.

### Practical notes
- It's an **approximation** (a true inverse of the polynomial has no closed form), so a
  distort→undistort round-trip won't be pixel-exact — fine for most work, but match `k1`/`k2`
  carefully and check edges on a grid.
- **Tag the output Raw/Data** and STMap it.
""",
    "anamorphic_unsqueeze": """
## Notes

A horizontal-stretch **ST map** to un-squeeze anamorphic footage back to its true aspect.
Outputs `red = U, green = V`; feed it to an STMap node.

### Practical notes
- **`squeeze` = the anamorphic factor** (2.0 = a 2x squeeze, the classic anamorphic). Only the
  horizontal axis is scaled; vertical passes through.
- **Tag the output Raw/Data** and STMap it onto the squeezed plate.
- Reframe/refit after, since the unsqueeze changes the working width.
""",
    "uv_transform": """
## Notes

A zoom / pan **ST map** — repositions a source through an STMap node instead of a Transform.
Outputs `red = U, green = V`.

### Why do it as an ST map
When your pipeline is already STMap-based (lens work, warps), folding a reposition into the
same map keeps everything to a **single resample** and a single coordinate space, rather than
stacking a separate Transform.

### Practical notes
- **`zoom` > 1 zooms in**, < 1 out (centred). `panX`/`panY` shift in **UV units** (0..1 across
  the frame), so 0.1 = a tenth of the width/height.
- **Tag the output Raw/Data** and STMap it onto the source.
""",
    "noise_cells": """
## Notes

**Blocky per-cell random** — one flat random value per `cellSize`-pixel cell, no
interpolation. The cheapest noise here and the only hard-edged one.

### Animating it (the `seed` trick)
The node has **no frame/time variable**, so you animate procedural patterns by **keyframing
`seed`** — it offsets the sampling into the noise field, reshuffling the cells. Keyframe it to
make the pattern evolve/flicker over a shot.

### Practical notes
- `cellSize` = cell size in pixels; `seed` = pattern / animation.
- Output is a greyscale field on **RGB with solid alpha** (`matte = 1.0`) — it's data, not a
  matte. Shuffle a channel to alpha downstream if you need it as a mask, and **tag it
  Raw/Data**.
- Uses: mosaic/blocky randomness, glitch, per-cell breakup, stepped dissolves.
""",
    "noise_value": """
## Notes

**Smooth value noise** — a single octave of interpolated lattice noise. The soft, organic
counterpart to `noise_cells`.

### Controls
- `scale` = feature size in pixels (bigger = larger blobs).
- `gain` = contrast on the result.
- `seed` = pattern selection **and** animation — keyframe it to drift/evolve (no time
  variable exists in the node).

### Practical notes
- One octave, so it's smooth but plain — reach for `noise_fbm` when you want fractal detail.
- Greyscale field on RGB, solid alpha; **tag Raw/Data**. Good base for displacement,
  soft masks, and subtle breakup.
""",
    "noise_fbm": """
## Notes

**Fractal noise** — three octaves of value noise summed (fractional Brownian motion). The
natural-looking one: clouds, smoke, terrain, weathering.

### The shaping controls
- `scale` = base feature size.
- `lacunarity` = how much **frequency** rises each octave (~2.0 doubles it) — adds finer
  detail.
- `persistence` = how much **amplitude** falls each octave (~0.5 halves it) — **lower =
  smoother/softer, higher = rougher/grittier**.
- `seed` = pattern + animation (keyframe to evolve).

### Practical notes
- This is the **heaviest expression in the library** (three inlined octaves) — it's verified
  loading in Flame, but it's the most likely place to feel a compile cost.
- Greyscale field on RGB, solid alpha; **tag Raw/Data**.
""",
    "voronoi": """
## Notes

**Cellular (Voronoi) noise** — distance to the nearest feature point in the surrounding 3×3
cells. Gives cells, scales, cracks, stained-glass and caustic-like looks.

### Controls
- `scale` = cell size in pixels.
- `jitter` = how far feature points wander from a regular grid: **0 = perfectly regular
  lattice, 1 = fully random** cells. Dial it for ordered-vs-organic.
- `seed` = pattern + animation (keyframe to evolve — points drift, cells reshape).

### Practical notes
- Output is the distance field (dark at cell centres, bright at borders); greyscale on RGB
  with solid alpha — **tag Raw/Data**.
- Threshold or `smoothstep` it for hard cell edges, or use it raw as a bumpy displacement.
""",
    "sdf_circle": """
## Notes

An **anti-aliased disc matte** built from a signed distance field, centred on the node's
**Centre** control. The simplest SDF primitive.

### Conventions shared across `sdf_shapes/`
- The shape sits at **Centre** (the node's Centre X/Y), *not* the image origin — set Centre to
  position it. No input needed (it's a generator).
- Sizes are in **pixels**; `soft` = edge width in pixels (anti-aliasing / feather).
- Written to **RGB and Matte**, so it's usable straight as a matte (Result or OutMatte).

### Practical notes
- `radius` = disc radius. For a circular **outline** instead of a filled disc, use `sdf_ring`.
""",
    "sdf_box": """
## Notes

An **anti-aliased rectangle matte** (SDF), centred on **Centre**, with a hollow control that
turns it into a frame.

### bx / by are HALF-extents
`bx` and `by` are the **half-width and half-height** (distance from centre to edge), so the
box is `2*bx` × `2*by` pixels. Easy to mistake for full size.

### The `hollow` control
`hollow` 0 = solid; as it rises toward 1 it **cuts a growing hole out of the middle while the
outer edge stays fixed** — so you get a rectangular frame/border whose thickness shrinks
inward as `hollow` increases. (Shared `_HOLLOW` mechanism across the SDF shapes.)

### Practical notes
- `soft` feathers the edge. Uses: framing masks, holdouts, rectangular outlines.
""",
    "sdf_rounded_box": """
## Notes

A **rounded rectangle** (SDF) with a `corner` radius — and a hollow that stays correctly
rounded. Centred on **Centre**.

### Why the hole is a second box (the clever bit)
When `hollow` > 0 the interior cut-out is a **second rounded box with the *same* `corner`
radius**, not an inward SDF offset. An inward offset would **sharpen** the inner corners
(the radius shrinks as you move in); subtracting a matched rounded box keeps the inner corners
as round as the outer ones — so a rounded frame looks right at any `hollow` amount. This is
why its formulas (`wall`, `d`, `d2`) differ from the other shapes' simple `_HOLLOW`.

### Practical notes
- `bx`/`by` = **half-extents**; `corner` = corner radius (px); `hollow` 0 = solid → frame;
  `soft` = edge feather. Ideal for UI panels, soft-cornered mattes and outlines.
""",
    "sdf_ring": """
## Notes

An **annulus (ring) matte** — the outline primitive of the SDF set. Centred on **Centre**.

### Practical notes
- `radius` = ring radius (to the centre of the band); `thickness` = half the band width, so
  the ring spans `radius ± thickness`. `soft` = edge feather.
- Use for circular outlines, target/HUD reticles, halos. For a filled disc use `sdf_circle`.
""",
    "sdf_polygon": """
## Notes

A **regular n-gon matte** (SDF) — triangles, hexagons, etc. — centred on **Centre**, with the
shared hollow control.

### Controls
- `sides` = number of sides (3 = triangle, 5 = pentagon, 6 = hexagon…).
- `radius` = circumradius (centre to vertex), in pixels.
- `rot` = rotation in **radians** (so a full turn is `2*PI`).
- `hollow` 0 = solid → cuts an inward hole (frame/outline); `soft` = edge feather.

### Practical notes
- Built from the polar SDF (`r`, `a`, `d` formulas), so edges stay crisp at any size.
- Uses: polygonal masks and outlines, stylised shapes, aperture/iris mattes.
""",
    "radial_ramp": """
## Notes

A **radial gradient / vignette** centred on the node's **Centre** control — white at the
centre falling to black at `radius`.

### Two colours (shared across the tonal generators)
The pattern is a 0..1 mask blended `mix(A, B, pattern)` per channel: **colour A** `aR/aG/aB`
(default black, where the pattern = 0) → **colour B** `bR/bG/bB` (default white, where it = 1).
Defaults reproduce the original greyscale; set all three of a colour equal for a
luminance-only look. **OutMatte carries the raw 0..1 pattern**, regardless of the colours.
(Colour fields step in tenths — hold **Space + Drag** for finer values.)

### Practical notes
- `radius` = falloff radius in px; `softness` 0 = hard-edged circle, 1 = smooth falloff all
  the way from centre. **Centre** positions it.
- The go-to for vignettes, spotlight masks, and soft radial holdouts.
""",
    "rings": """
## Notes

**Concentric rings** (`sin` of distance) around the node's **Centre**.

### Practical notes
- `freq` sets ring spacing — it's **small** (0.05 default), so hold **Space + Drag** for
  hundredths when tuning.
- Two colours: `aR/aG/aB` (pattern 0) → `bR/bG/bB` (pattern 1), default black→white; OutMatte
  carries the raw pattern. (See `radial_ramp` notes.)
- For rings that **expand over time**, use `pulse_rings` instead.
""",
    "rays": """
## Notes

A **radial sunburst** — `rays` spokes via `atan` around the node's **Centre**.

### Practical notes
- `rays` = number of spokes; `rot` = rotation in **radians**.
- Two colours `aR/aG/aB`→`bR/bG/bB` (default black→white), raw pattern on OutMatte.
- `rot` is a **static** angle — for a spinning version use `spin_rays`.
""",
    "checkerboard": """
## Notes

A **checkerboard** test pattern — `size`-pixel squares.

### Screen-space, not Centre-based
Unlike `radial_ramp`/`rings`/`rays`, this is anchored to the **image origin** (`x`/`y`), not
the Centre control — so it tiles the frame and doesn't move with Centre.

### Practical notes
- `size` = square size in pixels.
- Two colours `aR/aG/aB`→`bR/bG/bB` (default black→white); raw pattern on OutMatte. Classic
  uses: alignment/UV checks, transparency-style backgrounds, test patterns.
""",
    "bricks": """
## Notes

An **offset brick / masonry** pattern — rows of `bw`×`bh` bricks with every other row shifted
half a brick (the `row` formula does the offset).

### Practical notes
- `bw`/`bh` = brick **full** width/height in pixels. Screen-space (anchored to `x`/`y`, not
  Centre).
- Two colours `aR/aG/aB`→`bR/bG/bB` (default black→white); raw pattern on OutMatte.
- Uses: wall/tile mattes, a base mask to drive displacement or per-brick breakup.
""",
    "noise_random": """
## Notes

**Per-pixel white noise** — a fixed hash of `x`/`y`, the GLSL stand-in for Nuke's `random()`.
The **only** generator here without the two-colour blend: each of R/G/B gets an independent
noise channel, alpha solid.

### Static by design
It's a pure function of pixel position, so it's the **same every frame** and has **no `seed`
or animation**. For noise that evolves over a shot — or that you can shape (scale, octaves,
cells) — use the `noise/` folder (`noise_value`, `noise_fbm`, `voronoi`), where keyframing
`seed` drives the motion.

### Practical notes
- Uses: grain, dither, a random source to drive a dissolve/threshold. Tag it Raw/Data.
""",
    "wave_sine": """
## Notes

Smooth **scrolling sine bands**. Part of `animated_generators/` — motion comes from a
keyframed `t`.

### How the animation works (shared across this folder)
The node has **no time/frame variable**, so `t` is a **keyframed variable** that acts as the
clock. It ships as a 2-key channel (frame 1 → 0, frame 100 → end); **scrub frames 1–100** to
see it move. Edit those two keys to change **speed** (steeper) or **length** (move the end
frame). Here `t` runs 0 → 2 = two full cycles over the range.

### Practical notes
- `wavelength` = band period in pixels.
- Two colours `aR/aG/aB`→`bR/bG/bB` (default black→white); raw pattern on OutMatte.
""",
    "wave_triangle": """
## Notes

A **scrolling triangle wave** — a linear up/down ramp instead of a sine, so the gradient is
straight-sided with sharp peaks and troughs.

### Practical notes
- `wavelength` = period (px); `t` is the keyframed clock (0 → 2 over frames 1–100; edit the
  keys for speed/length — see `wave_sine`).
- Two colours `aR/aG/aB`→`bR/bG/bB`; raw pattern on OutMatte.
""",
    "wave_square": """
## Notes

**Scrolling square stripes** — a hard on/off step at the half-cycle, so it's binary (no
gradient).

### Practical notes
- `wavelength` = stripe period (px); `t` is the keyframed clock (0 → 2 over frames 1–100;
  edit keys for speed/length — see `wave_sine`).
- Two colours `aR/aG/aB`→`bR/bG/bB`; raw pattern on OutMatte. Uses: shutters, barcodes,
  hard-edged wipes, blink patterns.
""",
    "wave_sawtooth": """
## Notes

A **scrolling sawtooth** — a repeating 0 → 1 ramp that snaps back. Great as a **phase/sweep
driver** (a value that cycles linearly) as well as a visible ramp.

### Practical notes
- `wavelength` = period (px); `t` is the keyframed clock (0 → 2 over frames 1–100; edit keys
  for speed/length — see `wave_sine`).
- Two colours `aR/aG/aB`→`bR/bG/bB`; raw pattern on OutMatte.
""",
    "pulse_rings": """
## Notes

Concentric rings **expanding from Centre over time** — a sonar / shockwave / ripple. The
animated cousin of `rings`.

### Practical notes
- Centred on the node's **Centre** control; `wavelength` = ring spacing (px). Motion comes
  from the keyframed `t` (0 → 2 over frames 1–100), which advances the phase so rings march
  outward — edit the keys for speed/length (see `wave_sine`).
- Two colours `aR/aG/aB`→`bR/bG/bB`; raw pattern on OutMatte.
""",
    "spin_rays": """
## Notes

A **rotating sunburst** — `rays` spokes turning around the node's **Centre**. The animated
cousin of `rays`.

### One turn by default
Its `t` uses the **one-cycle** keyframe (0 → 1 over frames 1–100), and `t` 0→1 maps to exactly
**one full 360° rotation** — so the default spins once across the range. Move the end key past
1 for more turns (or below for a partial sweep); reverse the keys to spin the other way.

### Practical notes
- `rays` = spoke count; Centre positions the hub.
- Two colours `aR/aG/aB`→`bR/bG/bB`; raw pattern on OutMatte. Uses: radial wipes, hypnotic /
  loading spinners, light-ray sweeps.
""",
    "alpha_crunch": """
## Notes

A **hard floor on the matte**: any alpha below `thresh` drops to 0; the rest keeps its value.
RGB passes through untouched (it only rewrites alpha).

### The default keeps only solids
With `thresh` 1.0, *everything below fully-opaque* goes to 0 — so only pixels that were
exactly 1.0 survive. That's a "core / solids only" crunch: it strips semi-transparent edges,
spill, and soft fringe. **Lower `thresh`** to keep more of the partial alpha.

### Practical notes
- Matte on **Matte 1**. Use before a hard composite to kill a noisy/feathered edge, or to
  pull a clean core out of a soft matte. Pair with `fill_alpha` (its rough inverse) and
  `matte_grade` to reshape density.
""",
    "fill_alpha": """
## Notes

**Solidifies the matte** — any alpha above 0 becomes fully opaque (1.0). RGB passes through.
The rough inverse of `alpha_crunch`: where crunch removes partial alpha, fill promotes it.

### Practical notes
- Matte on **Matte 1**. Fills interior holes and semi-transparency to a solid holdout —
  handy before an erode/blur, or to turn a soft/dotty matte into a watertight one.
- It's binary (`>0 → 1`), so it won't clean stray single-pixel speckle — crunch first (or
  grade the matte) if noise is getting promoted.
""",
    "alpha_fringe": """
## Notes

**Isolates the matte's soft edge.** The expression `4 * (1 - m1) * m1` is a parabola that is
0 where alpha is 0 or 1 and peaks at **1.0 when alpha = 0.5** — so it lights up exactly the
semi-transparent transition band and ignores the solid interior and the clear exterior. RGB
passes through; the edge band is written to the matte.

### Practical notes
- Matte on **Matte 1**. Use it as a mask to confine work to the edge: light-wrap / edge
  blend, despill or de-contaminate only the fringe, or grade just the transition.
- Wider, softer mattes give a wider fringe; tighten the source matte first if the band is too
  broad.
""",
    "luma_key": """
## Notes

A **soft luminance key**: `smoothstep(lo, hi, luma)` on Rec.709 luma, written to **RGB and
the Matte** (so you see the key on Result and get OutMatte at once).

### Controls
- `lo` = the luma where the key starts (black point), `hi` = where it reaches full (white
  point). The gap between them is the softness — widen for a gentle ramp, narrow for a hard
  key. Invert by swapping `lo` and `hi`.

### Practical notes
- **Luma weights are Rec.709** — exact in scene-linear; in a display/log space it's an
  approximation (still useful, just not photometric).
- Quick pulls: skies/highlights (high `lo`/`hi`), shadows (low, inverted), a self-matte for a
  glow or a brightness-driven grade.
""",
    "difference_matte": """
## Notes

A **difference key against a clean plate**: the RGB distance between Front 1 and Front 2,
scaled by `gain` and clamped — white where the two images differ, black where they match.
Written to RGB and the Matte.

### Setup
- **Front 1 = the shot, Front 2 = a locked-off clean plate** of the same scene without the
  element. They must be **registered** (same camera, alignment) — it compares pixel-for-pixel.
- `gain` boosts sensitivity (default 5.0); raise it to catch subtle differences, lower it to
  reject noise.

### Practical notes
- **Most even in scene-linear.** It's sensitive to grain, exposure flicker and lighting
  change between shot and plate — **denoise / match levels first**, then soften the result
  with `matte_grade`.
- Great as a *starting* garbage matte to combine with a real key, rarely a final key alone.
""",
    "stmap": """
## Notes

The **identity ST map** — `red = x/width`, `green = y/height` — i.e. each pixel's own
normalised coordinate. The baseline UV map you feed an **STMap node**.

### Why a no-op map is useful
On its own, STMapping a source through this reproduces the source unchanged (every pixel
samples itself). Its value is as a **starting point**: add offsets/expressions to red/green to
build a custom warp, or use it as a reference to sanity-check an STMap setup. The whole
`uv_distortion/` folder is specialised versions of this (lens, anamorphic, zoom/pan).

### Practical notes
- `blue` = 0, alpha = 1. **Tag the output Raw/Data** — it's coordinates, not colour, so
  colour management would corrupt the warp.
""",
    "nan_cleanup": """
## Notes

A **NaN / Inf scrubber** — replaces any pixel that is `isnan` or `isinf` with 0, per channel.
Renderers (and some filters) emit these, and they **poison everything downstream**: a single
NaN spreads through blurs, merges, and medians. Drop this in early as a safety net.

### The Front-2 patch variant
Instead of zeroing a bad pixel, you can **patch it from a second input**: swap the `0.0` in
each channel for `r2`/`g2`/`b2` so a NaN samples Front 2 (a clean frame, a filtered version)
at that pixel. Because the setup files are generated, make that change in `generate_setups.py`
and regenerate — don't hand-edit the `.pixel_expression_node`.

### Practical notes
- Per-channel and independent; keeps alpha (`matte = m1`). No controls in the default
  (zero-replace) form.
""",
    "premult": """
## Notes

Multiplies RGB by the matte (`r1 * m1`). Run **before** ops that expect premultiplied
footage. Inverse of `unpremult`.
""",
    "unpremult": """
## Notes

Divides RGB by the matte, guarding 0 (where `m1 = 0`, RGB passes through). Run **before**
colour-correcting an edge so the soft alpha doesn't darken it; re-`premult` after. Inverse of
`premult`.
""",
    "matte_and": """
## Notes

Intersection of two mattes (`m1 * m2`) — white only where **both** are white. Inputs on
Matte 1 and Matte 2.
""",
    "matte_or": """
## Notes

Union of two mattes (`max(m1, m2)`) — white where **either** is white. Inputs on Matte 1 and
Matte 2.
""",
    "matte_subtract": """
## Notes

Matte 1 minus Matte 2, clamped to 0..1 — cuts Matte 2 out of Matte 1 (holdouts). Inputs on
Matte 1 and Matte 2.
""",
    "matte_xor": """
## Notes

Exclusive-or of two mattes — white only where **exactly one** is white (the overlap cancels).
Inputs on Matte 1 and Matte 2.
""",
    "matte_invert": """
## Notes

Inverts the matte (`1 - m1`) — flips inside and outside.
""",
    "matte_grade": """
## Notes

Gamma + gain on the matte, clamped. `gamma` shifts the midpoint (choke vs spread the edge),
`gain` scales density. Tightens or opens a matte's edge.
""",
    "despill_green": """
## Notes

**Green-screen despill** — clamps the green channel to no more than the average of red and
blue (`min(g, (r+b)/2)`), the standard suppression. `spill` blends from 0 (off) to 1 (full).

### Practical notes
- Removes green contamination on edges and transmissive areas before/after keying; red and
  blue pass through untouched.
- For a **blue** screen you'd suppress blue instead — that's a separate generated variant
  (edit `generate_setups.py`, don't hand-edit the file).
""",
    "saturation": """
## Notes

**Saturation grade** — `mix(luma, colour, sat)` per channel using Rec.709 luma. `sat` 0 =
greyscale, 1 = unchanged, > 1 = boosted (can clip), < 1 desaturates toward grey.

### Practical notes
- **Luma weights are Rec.709** — correct in scene-linear, approximate elsewhere.
- This is a flat, global push. For saturation that **protects already-vivid colours and
  skin**, use `vibrance`; for a single hue, `hsl_targeted`.
""",
    "voxelize": """
## Notes

**Posterize / colour quantize** — `floor(c * scale) / scale` per channel snaps each channel to
`scale` discrete levels. (Despite the name, it's a 2D colour quantize, not a 3D voxel op.)

### Practical notes
- Lower `scale` = fewer, chunkier bands; higher = subtler. Turns smooth gradients into flats.
- Uses: cel / graphic-poster looks, banding tests, reducing an image to a few tones.
""",
    "rgb_to_hsv": """
## Notes

Converts RGB → **HSV**, packing **H on red, S on green, V on blue** (branchless Hocevar
conversion). The foundation of the `hsv_color/` folder.

### How to use it
Decode here, manipulate the H/S/V channels with any value op, then `hsv_to_rgb` to reconstruct
— the round-trip that makes hue/sat/value individually addressable. H is 0..1 and **wraps**
(0 and 1 are the same red).

### Practical notes
- The node does **no colour management** — it operates on the values as given; results depend
  on the space your pixels are in.
- Most tools here (`chroma_key`, `vibrance`, `sat_matte`…) reuse this same decode internally,
  so you rarely need it explicitly unless you want to view or hand-edit the channels.
""",
    "hsv_to_rgb": """
## Notes

Converts **HSV → RGB** — the inverse of `rgb_to_hsv`. Expects Front 1 to hold **H on red, S on
green, V on blue**.

### Practical notes
- The back half of the decode → modify → encode round-trip. Hue wraps (`fract`), so values
  outside 0..1 are fine.
- Feed it the output of `rgb_to_hsv` after you've graded the H/S/V channels.
""",
    "hue_rotate": """
## Notes

**Global hue rotation** — spins every colour around the wheel by a fixed amount; `hue` 0..1 =
one full turn. Uses a luma-preserving rotation matrix (no HSV decode), so **brightness is
unchanged**.

### Practical notes
- Affects the **whole image** equally. To rotate only one colour band, use `color_replace`
  (hue→hue) or `hsl_targeted` (band + sat/value).
- Keyframe `hue` for a cycling-colour effect.
""",
    "chroma_key": """
## Notes

The **hue qualifier**: a matte that's white where a pixel's hue is near `keyHue` and its
saturation clears `satMin`, black elsewhere. Written to RGB **and** the Matte.

### Controls
- `keyHue` = target hue (0..1: red 0.0, green 0.33, blue 0.66…); `tol` = band half-width;
  `soft` = edge feather; `satMin` = saturation floor that **rejects greys** (whose hue is
  meaningless/unstable).

### Practical notes
- Quick key by colour (greens, skies, skin). Its saturation-axis sibling is `sat_matte`;
  `matte_and` the two for a tighter "this hue *and* this vividness" selection.
""",
    "color_replace": """
## Notes

**Recolour one hue, protect the rest.** It rotates only the hue band near `srcHue` toward
`dstHue` (luma-preserving), passing everything outside the band through untouched.

### Controls
- `srcHue` = the colour to change, `dstHue` = what to change it to; `tol` = band half-width,
  `soft` = edge feather.

### Practical notes
- This is the **`dHue`-only special case** of `hsl_targeted` (which also gives saturation and
  value). Reach for it when you just need a clean hue swap on one object.
""",
    # --- fractals ---
    "mandelbrot": """
## Notes

A real **escape-time Mandelbrot** computed per pixel — but a deliberately **shallow,
experimental** one, not a deep-zoom renderer. Read the architecture note below before you
judge the image.

### Why it's shallow (the architecture limit)
The node has **no reassignable state** — you can't write a loop that updates `z`. The only
way to iterate is the **4-formula chain**: `z0` does a couple of inlined steps from the
seed, `z1` references `z0` by name and does a couple more, … through `z3`. A complex square
references `z` several times, so each inlined step **expands the expression text by ~8x**.
That caps us at **2 iterations per formula = 8 total** before the string blows past the
node's practical size limit (K=3 would be ~33 KB per formula). So:
- **Interiors read solid** (they never escape in 8 iterations).
- **Edges band** in a few discrete rings rather than the infinitely fine filigree you'd get
  from hundreds of iterations.
- This is a **texture/abstract-pattern** tool, not a fractal explorer.

### How it works
Each pixel maps to the complex plane relative to the node **Centre**, scaled by `zoom`
(bigger `zoom` = closer). `c` = that coordinate, `z` starts at `(cRe, cIm)`. Every iteration
squares `z` and adds `c`, and accumulates `step(|z|^2, 4.0)` — 1 while still inside the
bailout radius, 0 once it escapes. Summing across all 8 iterations gives a 0..1 **smooth
escape value** (`z3.z / 8.0`, normalised to the *maximum possible* count so the tonal range
stays stable even though only 8 steps run).

### The seed (keyframe `cRe`/`cIm`)
`cRe`/`cIm` set the **starting value of `z`** (default `0,0` = the classic Mandelbrot). They
are the structural mirror of Julia's constant: where `julia` keyframes the added constant
`c`, here you keyframe the seed `z0`. Nudging them off zero distorts and morphs the whole
set — **keyframe them** for an animated, breathing fractal. Default `(0,0)` leaves the
familiar Mandelbrot look unchanged.

### Pan / zoom
- **Pan:** move the node **Centre** to the region you want centred.
- **Zoom:** raise `zoom` (default 400). Because iteration depth is fixed at 8, zooming in
  past a point just shows bigger, smoother bands — there's no new detail to reveal.

### Output (`gain` / `gamma`)
**Grayscale** — the escape value written to RGB **and** Matte (via `_solid`). Two shaping
controls ride on it, both default `1.0` (so the default look is the raw value):
- **`gamma`** curves the bands — `>1` darkens the mids and pushes more area to black
  (crisper edges), `<1` lifts them (more glow).
- **`gain`** scales overall brightness after the curve (the result is re-clamped to 0..1).

Order is `clamp(pow(escape, gamma) * gain, 0, 1)`. Tint downstream, or drive a mask off the Matte.

### Downstream
Pure generator (no inputs). Feed the Matte into a comp as a procedural mask, or the RGB as a
background / displacement source. Pair with a **Blur** if the discrete bands read too hard.
""",
    "julia": """
## Notes

The **Julia** companion to `mandelbrot`: same 8-iteration escape-time engine, but `z`
**starts at the pixel** and `c` is a **constant** you control with `cRe`/`cIm`. Sweeping
that constant morphs the whole shape — which is the fun part.

### The morph (keyframe `cRe`/`cIm`)
`cRe`/`cIm` is a point in the complex plane; each value gives a different Julia set.
**Keyframe them** to animate a continuously-morphing fractal. Good values to try:
| `cRe` | `cIm` | Look |
|-------|-------|------|
| -0.8 | 0.156 | default — connected, dragon-ish |
| -0.4 | 0.6 | spiral arms |
| 0.285 | 0.01 | dense, near-circular |
| -0.70176 | -0.3842 | classic "rabbit" |
| -0.835 | -0.2321 | lightning / dendrite |

Animate a small loop (e.g. `cRe` -0.8→-0.7→-0.8 over 100 frames) for a breathing morph.

### Same shallow caveat
Like `mandelbrot`, this is **8 total iterations** (the 4-formula chain expands ~8x per
inlined step, so deeper is impractical). Interiors read solid; edges band. It's a
texture/animation tool, not a deep renderer.

### Output (`gain` / `gamma`)
**Grayscale** — the escape value written to RGB **and** Matte (via `_solid`). As in
`mandelbrot`, `gamma` curves the bands (`>1` darkens mids / crisper, `<1` lifts / more glow)
and `gain` scales brightness after; both default `1.0`, order `clamp(pow(escape, gamma) *
gain, 0, 1)`. Tint downstream or mask off the Matte. Pan/zoom via node **Centre** + `zoom`.
""",
    "burning_ship": """
## Notes

The **Burning Ship** fractal — `mandelbrot` with one change: **fold `z` to its absolute
value on each axis before squaring** (`z = vec2(abs(z.x), abs(z.y))`, then square, `+ c`).
That broken symmetry gives the sharp, hull-and-mast "ship" silhouette the name comes from.

### Same engine, same caveats
8-iteration escape-time over the 4-formula chain (each inlined step expands ~8x, so 2 per
formula is the ceiling). **Shallow and experimental** — interiors solid, edges band; a
texture tool, not a deep-zoom explorer. Pan/zoom via node **Centre** + `zoom`.

### Where the ship is
The famous structure sits down in the **negative-imaginary** region. To frame it, move the
node **Centre** below/left of the origin and raise `zoom`. Because depth is fixed at 8, the
fine antenna detail of real Burning Ship renders won't appear — you get the bold outline.

### The seed (keyframe `cRe`/`cIm`)
As in `mandelbrot`, `cRe`/`cIm` set the **starting value of `z`** (default `0,0` = the
classic Burning Ship) — the structural mirror of Julia's constant. **Keyframe them** to
distort and morph the silhouette; leave them at `(0,0)` for the familiar look.

### Output / downstream (`gain` / `gamma`)
**Grayscale** via `_solid` — escape value to RGB **and** Matte (the Matte masks). As in
`mandelbrot`, `gamma` curves the bands and `gain` scales brightness after, both default `1.0`
(`clamp(pow(escape, gamma) * gain, 0, 1)`). Identical workflow to `mandelbrot`. Blur
downstream if the bands read too hard.
""",
    # --- stmap ---
    "polar_to_cartesian": """
## Notes

A **polar-coordinate ST map**. It does **not** warp the image itself — `red = U, green = V`,
and you feed the result into a downstream **STMap node** (or an **Action ST-map / GMIC ST**)
whose source is the plate you want remapped. Output is tagged **Raw/Data**.

### Required downstream wiring
1. This node → **STMap node**, plugged into the STMap's **map / UV input**.
2. The plate to remap → the STMap's **front / source input**.
3. The STMap resamples the source at each pixel's `(U,V)` = `(red, green)` here.

### What it does
For every output pixel it computes a **source UV from (angle, radius)** measured around the
node **Centre** (drag Centre to set the pole). `red` carries the normalised angle (0..1 around
the circle), `green` the normalised radius. The result is the classic **tiny-planet /
mirror-ball / 360-reframe** unwrap-rewrap.

### Controls
- **`twist`** rotates the angular axis (radians) — spins the planet.
- **`zoom`** scales the radius — `>1` pulls the horizon in, `<1` pushes it out.
- Aspect-corrected (Y normalised by height/width) so the circle stays round at any res.
""",
    "kaleidoscope_map": """
## Notes

A **kaleidoscope ST map** — `red = U, green = V` feeding a downstream **STMap node** (this node
into the STMap's **map/UV input**, the plate into its **source input**). Output tagged
**Raw/Data**.

### What it does
Mirror-folds angular space into **`segments`** wedges around the node **Centre**, then
reconstructs a source UV from the folded angle + original radius. The STMap then samples your
plate through that folded coordinate field, giving the mirror-symmetry kaleidoscope look.

### Controls
- **`segments`** = number of mirrored wedges (6 default).
- **`rot`** = rotation of the fold (radians) — spin it for an animated kaleidoscope.
- Drag **Centre** to move the pivot. Keyframe `rot` for motion.
""",
    "lens_distort_map": """
## Notes

A **radial lens-distortion ST map** with anamorphic squeeze. `red = U, green = V`; feed it to a
downstream **STMap node** (this node → STMap **map/UV input**, plate → STMap **source input**).
Output tagged **Raw/Data** — colour-managing a coordinate map corrupts it.

### Distort vs undistort (same node)
- **`k1` is the main term:** `k1 > 0` = pincushion, `k1 < 0` = barrel. `k2` is the higher-order
  corner term.
- **To UNDISTORT, negate `k1` and `k2`** (use the opposite sign of the values you'd use to add
  the distortion). It's an approximation, so a distort→undistort round-trip won't be
  pixel-exact — match coefficients carefully and check on a grid.

### Controls
- **`squeeze`** = anamorphic X scale (2.0 = a 2x squeeze). Use Centre to set the optical centre.
- Aspect-corrected so distortion stays isotropic at any resolution.

### Typical job
Add a plate's measured distortion onto a clean CG render so it matches, or flatten a plate
(undistort), track/paint/comp, then re-distort with the same node negated.
""",
    "glitch_block_map": """
## Notes

A **block-shuffle / datamosh ST map** — `red = U, green = V` feeding a downstream **STMap node**
(this node → STMap **map/UV input**, plate → STMap **source input**). Output tagged **Raw/Data**.

### What it does
Quantises the frame into **`blockSize`-pixel blocks**, hashes each block's index to a random
2D offset (via the shared `_hash2` helper), and shifts that whole block's source UV by the hash
scaled by **`corruption`**. Each block jumps as a unit, so the STMap tears the plate into
displaced rectangles — a corrupted-codec / datamosh look.

### Controls
- **`corruption`** 0..1 — the trigger. **Keyframe it** (e.g. 0 → 0.8 → 0 over a few frames) so
  the glitch pops in and out; at 0 the map is identity (no displacement).
- **`blockSize`** = block size in pixels (smaller = finer shredding).
- **`seed`** reshuffles which way each block jumps — keyframe it to re-randomise per frame.
""",
    "heat_haze_map": """
## Notes

A **heat-haze / refraction ST map** — `red = U, green = V` feeding a downstream **STMap node**
(this node → STMap **map/UV input**, plate → STMap **source input**). Output tagged **Raw/Data**.

### What it does
Offsets each pixel's source UV by an **animated 3-octave fbm** field (the shared `_FBM_NOISE`
builder) times **`amp`**. X and Y use the same noise field sampled at different offsets, so they
wobble independently — the organic shimmer of hot air or water refraction.

### Controls
- **`seed`** — **keyframe this to animate the shimmer** (the node has no time variable; the seed
  offset into the noise field is how you get motion).
- **`amp`** = displacement strength (UV units; 0.03 default ≈ a few percent of the frame).
- **`scale`** = feature size, **`lacunarity`**/**`persistence`** shape the fbm octaves.
""",
    "coc_from_depth": """
## Notes

**NOT a UV map** — this outputs a **per-pixel circle-of-confusion (blur-amount) map**, written
to RGB **and** the Matte. Depth arrives on **Matte 1 (`m1`)** per the library convention.

### Required downstream wiring
Feed this into a **variable-blur / Defocus / depth-of-field node** as its **blur-amount input**
(the map that says how much to blur each pixel). The blur node does the gathering — this node
only computes the amount (no neighbour sampling is possible here).

### What it does
`coc = clamp(abs(m1 - focusDepth) / focusRange, 0, 1) * maxBlur`. Pixels at `focusDepth` get 0
(sharp); blur ramps up with distance from the focus plane, reaching `maxBlur` at the edge of
`focusRange`.

### Controls
- **`focusDepth`** = the depth value held in focus (match your depth pass's units/scale).
- **`focusRange`** = how far from focus before reaching max blur.
- **`maxBlur`** = output scale (0..1) — set so it matches your blur node's expected amount range.
- Tag the output **Raw/Data** (it's a control map, not an image).
""",
    "chromatic_aberration_map": """
## Notes

A **chromatic-aberration ST map** — `red = U, green = V` for a downstream **STMap node**. Output
tagged **Raw/Data**.

### The one-map limitation (read this)
A single ST map can only carry **one** source UV, but chromatic aberration needs the R/G/B
channels sampled at **different** radii. Two clean ways to wire it:

1. **Per-channel (most accurate):** this map carries the **red channel's** distorted UV (scaled
   by `1 + amount`). Build **green** with `amount = 0` (identity) and **blue** with `-amount`,
   STMap each colour channel of the plate separately, then recombine — R sampled wide, B sampled
   tight. Three instances of this node, one STMap per channel, one Channel-recombine.
2. **Magnitude-driven defringe (simplest):** ignore the per-channel UVs and use the **blue
   channel** here, which carries the **radial offset magnitude** (`length(n) * amount`). Feed
   that as the strength/mask input of a downstream **defringe / lateral-CA** node so it fringes
   strongest at the edges and zero at the optical centre.

### Controls
- **`amount`** = radial divergence (0.02 default). Use **Centre** as the optical centre.
""",
    # --- control ---
    "painted_grade": """
## Notes

A grade whose **parameters are painted, not global**. The usual grade node has one exposure,
one hue, one saturation for the whole frame; here those three knobs live in **Front 2** and
can differ at every pixel. It's a hand-authored control surface — a *spatially-varying* grade
from a single node, with no tracked mattes or stacked secondaries.

### Paint the control map
Build Front 2 in Paint, roto, a ramp, or another Pixel Expression. Each channel is a
**0..1 control, 0.5 = neutral**:
- **red (r2)** → local **exposure**: 0.5 = no change, >0.5 brightens, <0.5 darkens (`exp2`,
  so it's symmetric in stops). `expRange` sets the stops at the 0/1 extremes.
- **green (g2)** → local **hue shift**: 0.5 = no rotation; the rotation is luma-preserving
  (same matrix as `hue_rotate`), so it won't change brightness. `hueRange` = full turns at the
  extremes.
- **blue (b2)** → local **saturation**: 0.5 = no change, 1.0 = more vivid, 0.0 = toward grey
  (mix around Rec.709 luma). `satRange` scales the push.

A **flat 0.5 grey** Front 2 (or no paint) leaves the image untouched — defaults are neutral.

### Order of operations
Exposure first (linear multiply), then saturation, then the hue rotation on the result
(formula `pr`). Work in **scene-linear** so the exposure stops are photometric.

### Recipes
- **Localised relight:** paint a soft white blob on r2 over a face to lift just that area.
- **Selective desaturation:** paint b2 dark over a distracting background to grey it down while
  the hero stays saturated.
- **Animated reveal:** keyframe / animate the painted map upstream to sweep a grade across the
  frame.
""",
    "channel_pack": """
## Notes

A **3-into-1 muxer**: stuff three unrelated single-channel signals into one RGB so they ride a
single connection through a comp, then split them back out with `channel_unpack` at the far
end. Saves wiring and keeps related masks travelling together.

### The packing
- **red** = Matte 1, **green** = Matte 2, **blue** = Front 1 **luma** (Rec.709). Matte = 1.
- Blue is luma rather than a raw channel so the third slot can carry a brightness/key signal;
  swap it for `b1` in `generate_setups.py` if you'd rather ferry a literal blue channel.

### Practical notes
- The packed channels are **data, not colour** — tag the output **Raw/Data** so colour
  management doesn't bend the values before you unpack them.
- Unpack partner: **`channel_unpack`** (route any packed channel to a Matte). Keep both ends in
  the same space/data tag.
""",
    "channel_unpack": """
## Notes

The **demuxer** for `channel_pack` (or any packed RGB). It passes the full RGB through
untouched and additionally **routes one chosen channel to the OutMatte**, so you can recover a
ferried mask and feed it straight to a downstream matte input.

### Picking the channel
`pick` selects which channel goes to the Matte: **0 = red, 1 = green, 2 = blue**. It's a
branchless `step`/`mix` select (no arrays in GLSL): `step(0.5, pick)` switches r→g, then
`step(1.5, pick)` switches that→b.

### Practical notes
- RGB out = RGB in, so this is non-destructive on the image; it only *derives* the Matte.
- **OutMatte only renders when Matte 1 is connected** — the Matte expression here reads Front 1,
  but Flame still requires Matte 1 wired for the OutMatte to appear. Connect anything (even the
  packed clip) to Matte 1.
- Pairs with **`channel_pack`**; keep the Raw/Data tag consistent across the pair.
""",
    "dual_output_depth": """
## Notes

A demonstration that the node makes **two products at once**: the RGB expression and the Matte
expression are independent. Here RGB carries a **depth-tinted beauty look** while the Matte
**keys a depth slab** from the same depth pass — one node, a graded image *and* a holdout
matte.

### The two outputs
- **RGB:** the beauty (Front 1) blended toward a tint (`tintR/G/B`) by depth, strength
  `strength`. Default `strength = 0.0` leaves the beauty untouched, so the look is opt-in.
- **Matte:** `smoothstep(near, far, m1)` — a soft 0..1 isolation of the depth range between
  `near` and `far`. This is computed **independently** of the RGB grade.

### Practical notes
- **Front 1 = beauty, Matte 1 = depth.** `near`/`far` are in the depth pass's own units (raw),
  so read them off your depth values; the tint is in your beauty's space.
- **OutMatte only renders when Matte 1 is connected** — which it must be here anyway, since the
  key reads `m1`.
- Swap `near`/`far` (or feed `1 - smoothstep`) to isolate *outside* the slab instead.
""",
    # --- styliz ---
    "halftone": """
## Notes

The classic **newspaper / comic dot-screen**. The frame is tiled into a regular grid of
`cell`-pixel squares; in each cell a single dot is drawn whose radius grows with that
region's brightness — bright areas pack big overlapping dots (reads as light), dark areas
shrink to tiny dots (reads as dark). Output is two-colour, defaulting to black ink on white
paper.

### How it works
1. Pixel coordinates are rotated by `angle` (radians) so the dot grid can sit at the
   traditional ~15-45 degree screen angle instead of square-on.
2. `mod(coords, cell)` folds everything into one cell; the dot is the SDF of a circle whose
   radius is `0.5 * cell * sqrt(luma)` (the `sqrt` makes dot *area* roughly linear in luma,
   which is what print actually does).
3. A soft threshold of that SDF gives the inked pixel, then `_two_color` maps it from paper
   (`aR/aG/aB`, default black... wait — see below) to ink.

### Controls
- `cell` — dot pitch in pixels. Smaller = finer screen.
- `angle` — screen rotation in radians (~0.4 ≈ 23 deg is a good print angle).
- `aR/aG/aB` (ink) and `bR/bG/bB` (paper) — the two tones. Default is ink black / paper
  white; swap them or set a colour for duotone (e.g. ink = deep blue on cream paper).

### Recipes
- **Comic halftone:** `cell` 6-10, `angle` 0.4, leave colours black/white.
- **Pop-art duotone:** set ink to a saturated magenta and paper to pale yellow.
- **Animated reveal:** keyframe `cell` from large to 1 to dissolve the dot-screen into the
  full image.

### Notes
- Expects a **display-referred / working image** — it shades by Rec.709 luma, so feed it the
  graded look, not scene-linear, or the dots will skew toward the highlights.
""",
    "bayer_dither": """
## Notes

**Ordered (Bayer) dithering** — the retro 1-bit / limited-palette look where smooth
gradients are rendered as a fixed cross-hatch of dots instead of solid tones. Unlike random
dithering it uses a deterministic 4x4 threshold matrix, so it's stable frame-to-frame (no
crawling grain) and gives that unmistakable EGA / Game-Boy / e-ink texture.

### How it works
The 4x4 Bayer matrix is built by **index math, not a lookup table or loop**: the threshold
for a pixel is the bit-interleave of the low two bits of its x and y coordinates, scaled to
0..1 (`bv`). The pixel's luma is then quantized to `levels` steps *with that threshold added
in* before flooring — so neighbouring pixels tip over the step boundary at staggered
brightnesses, and the eye blends them into intermediate tones.

### Controls
- `levels` — number of output tones. `2.0` = pure 1-bit black/white (the iconic look);
  `3.0`-`4.0` gives a few grey steps with the dither filling the gaps.
- `aR..bB` — the two palette anchors the quantized value is mixed between (default
  black->white). Set them for a tinted duotone.

### Notes
- Expects a **display-referred / working image** (luma-driven). Set your contrast/exposure
  *before* this node — dithering is a final stylise, applied to the look you want crunched.
- For a chunkier dither, scale the image down, apply this, then scale back up (the node has
  no neighbour access, so it always dithers at native pixel pitch).
""",
    "crosshatch": """
## Notes

**Pen-and-ink crosshatch shading.** As a region darkens it accumulates more sets of
parallel lines — first one direction, then a second crossing it, then a third and fourth —
exactly how an illustrator builds up tone with a pen. The result is ink-on-paper line art
driven entirely by the image's luminance.

### How it works
Four line fields at **0, 45, 90 and 135 degrees** are generated with `sin` of the
(rotated) coordinates. Each field is gated by a luma threshold: lines at 0 deg appear once
luma drops below 0.8, the 45-deg set joins below 0.6, 90 deg below 0.4, 135 deg below 0.2.
The lit fields are multiplied together (a line in *any* active direction = ink), so darker
pixels are crossed by progressively more hatching.

### Controls
- `spacing` — pixels between hatch lines. Smaller = finer, denser pen.
- `lineW` — 0..1 line weight / softness (how fat each stroke is relative to the gap).
- `aR..bB` — ink and paper colours (default black ink on white paper).

### Notes
- Expects a **display-referred / working image** — the four thresholds (0.8/0.6/0.4/0.2)
  assume a roughly 0..1 display range. If your image is linear or log, run an exposure /
  view transform first so the tones land where the thresholds expect them.
- Great over a high-contrast, slightly blurred version of the plate — fine detail otherwise
  fights the hatch lines.
""",
    "crt": """
## Notes

A stacked **CRT / VHS** stylisation applied multiplicatively over Front 1: horizontal
scanlines, an RGB **phosphor-triad** mask, a corner **vignette**, and a slow **rolling
bright bar** like a mis-synced analogue signal. Every piece is dialable so you can go from a
subtle "this is on a monitor" cue to full retro grunge.

### How it works
- **Scanlines** — `tone` darkens every other line via `sin(y * scanFreq)`, depth set by
  `scanDepth`.
- **Phosphor mask** — `x mod 3` selects which of R/G/B stays bright in each column; the
  other two are knocked back by `maskDepth`, giving the characteristic colour-fringed
  vertical stripes.
- **Vignette** — radial darkening from frame centre, strength `vignette`.
- **Rolling bar** — a soft bright band whose vertical position is the **keyframed** `roll`
  variable (0..1 = one full pass up the frame). Animate it for the drifting-hold-bar look.

### Controls
- `scanDepth` / `maskDepth` / `vignette` — 0..1 strength of each effect (set any to 0 to
  disable it).
- `scanFreq` — scanline pitch (higher = finer lines).
- `roll` — **keyframe this** 0->1 over your shot to make the bright bar crawl. Default is
  one pass over frames 1-100; rescale to taste.

### Notes
- Expects a **display-referred / working image** — the effect multiplies the existing pixel
  values, so it reads correctly on a graded/display look.
- Connect **Matte 1** if you want the alpha passed through (the RGB look ignores it).
- For maximum authenticity, follow with a slight horizontal blur + chromatic-aberration
  offset in a separate node (this node can't sample neighbours).
""",
    "truchet": """
## Notes

**Truchet tiling** — a venerable generative-art trick. Each square cell contains one of two
quarter-circle arc pairs, chosen at random; because the arcs always meet the cell edges at
the same points, adjacent tiles connect into one continuous, endless maze of curves. From a
two-state-per-cell hash you get organic-looking circuit / pipe / labyrinth patterns.

### How it works
The frame is divided into `tile`-pixel cells. Each cell is **hashed** (`_hash2` on the cell
index) to a 0/1 `flip` that mirrors the local coordinates, swapping the arc orientation. Two
quarter-circles (radius = half a cell, centred on opposite corners) are drawn as the
distance band `arc`; a soft threshold of width `lineW` inks them.

### Controls
- `tile` — cell size in pixels (the scale of the weave).
- `lineW` — arc stroke width in pixels.
- `aR..bB` — line and background colours (default white lines on black).

### Notes
- This is a **pure generator** — it ignores any Front input and produces the same pattern
  regardless of what's connected; expects nothing.
- Keyframe the **Centre** to scroll the weave, or `tile` to zoom it.
- Feed the matte into a displacement / edge node for a circuit-board or stained-glass look.
""",
    "palette_quantize": """
## Notes

**Limited-palette posterise.** Front 1 is reduced to `levels` discrete tonal steps and the
result is re-coloured between two palette anchors — the budget-friendly route to a
pixel-art / retro-console look without needing a full per-colour palette match (which would
blow the 8-variable cap three times over).

### How it works
The Rec.709 luma is quantized: `floor(luma * levels) / (levels - 1)` snaps it to `levels`
evenly-spaced values. That stepped value `q` then drives `_two_color`, so each tone lands
on a `mix` between colour A (darkest) and colour B (lightest). Pick the two endpoints and
the intermediate steps fall on the ramp between them.

### Controls
- `levels` — number of tones (4 = the classic 4-shade console look; 2 = hard duotone).
- `aR/aG/aB` (dark) and `bR/bG/bB` (light) — the palette endpoints.

### Recipes
- **Game-Boy green:** `levels` 4, A = dark green (≈0.06, 0.22, 0.06), B = pale green
  (≈0.61, 0.74, 0.06).
- **Sepia duotone:** `levels` 2-3, A = deep brown, B = cream.

### Notes
- Expects a **display-referred / working image** — it snaps by display luma, so grade
  first, quantize last.
- This is the tonal-ramp approach; for a *hue*-based limited palette, qualify with
  `chroma_key` / `hsl_targeted` upstream and quantize the regions separately.
""",
    "seven_segment": """
## Notes

A **single 7-segment digit** rasterised straight into the frame from a number — no Text
node, no font, no external matte. The seven bars are signed-distance boxes laid out in the
classic calculator/LED arrangement, and which ones light is decided by an **arithmetic
truth table** on the `digit` variable (0..9). Keyframe `digit` and you have a **frame
counter / timer** baked into the comp.

### How it works
Local coordinates are taken relative to **Centre** and normalised by `digScale`. For each of
the seven segments (a=top ... g=middle) a per-digit selector — built from `step()` equality
tests against `floor(digit + 0.5)` — multiplies that bar's box fill, and the seven results
are `max`-combined into the lit shape `seg`. No loop, no array: the truth table is unrolled
into the expression.

### Controls
- `digit` — 0..9. **Keyframe it** (e.g. 0->9 over 10 frames, repeating) to count. Values are
  rounded, so a linear keyframe steps cleanly through the digits.
- `digScale` — pixel half-height of the digit.
- `thick` — stroke half-width (segment fatness) in local units.
- `hw` / `hh` — half-length of the horizontal / vertical bars (tune the proportions).
- `lit` — brightness of the lit segments (the unlit/background tone is near-black with a
  faint green tint for an LED feel).

### Recipes
- **Frame counter:** keyframe `digit` 0->9 linearly across 10 frames, set the channel to
  cycle/repeat. Place several copies at different Centres for multi-digit readouts.
- **Countdown leader:** keyframe `digit` 9->0 over your countdown and composite over the
  plate.

### Notes
- A **generator** — composite the result over your plate (the matte gives you the digit
  shape for the merge).
- It's **one digit by design**; for a multi-digit display, duplicate the node and offset
  each Centre, driving each `digit` from the appropriate place value.
""",
    # --- optics ---
    "thin_film": """
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
""",
    "wave_interference": """
## Notes

A **ripple tank**: two circular point sources dropped into still water, their wavefronts
crossing to make the classic interference lattice (bright where crests meet, dark where a crest
meets a trough).

### How it works
- Source **A** sits at the node **Centre**; source **B** is offset by `srcX` pixels on X. Each
  contributes `cos(k·distance − phase)` where `k = 2π/wavelength` (wavelength baked to 80 px in
  formula `k`), and the two are summed and remapped to 0..1.
- Only **two** sources — the node has no loops, so each source is written out by hand. With the
  two-colour vars eating 6 of 8 slots, only **two** own vars are exposed (`srcX` + `phase`);
  edit the `k` formula to change the ripple wavelength.

### Practical notes
- `srcX` = horizontal separation of the second source (set to 0 to collapse onto a single source
  = plain concentric rings; widen for a finer interference lattice).
- **`phase` is the keyframed clock** (0 → 4π over frames 1–100 = two full ripple cycles) — scrub
  to make the wavefronts travel outward.
- Two colours `aR/aG/aB`→`bR/bG/bB` (default black→white); raw field on OutMatte. Uses: caustic
  refs, energy fields, sonar interference.
""",
    "moire": """
## Notes

An **intentional moiré**: lay two near-identical line gratings over each other and the tiny
frequency/angle mismatch beats into a slow, large-scale pattern — the same artefact you get
photographing a CRT or a striped shirt, here made on purpose.

### How it works
- `sin(x·freqA)` is grating A (vertical lines); `sin((x·0.9992 + y·0.04)·freqB)` is grating B
  rotated by a fixed small angle. **Multiplying** them produces the beat (their sum/difference
  frequencies); the product is remapped to 0..1.
- The two-colour vars eat 6 of 8 slots, so the two **frequencies** are the exposed knobs (the
  rotation is baked); the frequency mismatch is what drives the moiré anyway.

### Practical notes
- Keep `freqA` and `freqB` **close** (e.g. 0.08 vs 0.085) — the closer they are, the wider and
  slower the moiré bands.
- Nudge `freqA`/`freqB` by hundredths to "tune" the pattern; keyframe one for a living,
  breathing moiré.
- Two colours `aR/aG/aB`→`bR/bG/bB`; raw pattern on OutMatte. Uses: op-art, interference/aliasing
  FX, screen-artefact looks.
""",
    "starfield": """
## Notes

A **procedural starfield** — no plotting, no loop. Space is tiled into `cellSize` cells; each
cell is hashed once (`_hash2`) and may hold a single star. Because the hash is deterministic per
cell, the field is stable when you scrub (only the twinkle moves).

### How it works
- `h = _hash2(floor(pixel / cellSize))` — a per-cell random vec2. `h.y` gates whether the cell
  has a star (`smoothstep(threshold, 1.0, h.y)` — raise `threshold` for fewer, brighter stars);
  `h.x` seeds its twinkle phase and a faint warm/cool tint.
- `d` is the distance from the pixel to the star's sub-cell position; a `smoothstep` makes a
  small round dot.

### Practical notes
- `cellSize` = average star spacing (px); `threshold` (0..1) = density (higher = sparser);
  `brightness` scales them all.
- **`twinkle` is the keyframed clock** (0 → 1 over frames 1–100 = one twinkle cycle); each star
  pulses on its own `h.x` phase so they don't blink in unison.
- One star per cell by construction — drop `cellSize` for a denser sky. RGB carries a subtle
  hash tint; OutMatte is the clean star mask (good for glow/comp).
""",
    "radar_sweep": """
## Notes

A **radar / oscilloscope sweep**: a bright line rotates around the **Centre**, trailing a
phosphor afterglow that fades the further behind the line you are, over faint range rings.

### How it works
- `gap = mod(sweep − pixelAngle, 2π)` is the **angular distance behind** the sweep line (0 at the
  line, growing all the way round). `exp(−gap·decay)` is the afterglow — bright at the line,
  decaying smoothly behind it.
- `rings` adds faint concentric range rings from radius (`length` to Centre) at `ringFreq`.
- The trail and rings are tinted by `glowR/glowG/glowB` (default phosphor green); OutMatte is the
  combined brightness.

### Practical notes
- **`sweep` is the keyframed clock** (0 → 2π over frames 1–100 = one full revolution) — scrub to
  spin it. Reverse the keys to sweep the other way; extend past 2π for multiple turns.
- `decay` sets afterglow length (higher = shorter, tighter trail); `ringFreq` sets range-ring
  spacing. Recolour via `glowR/glowG/glowB`.
- Generated look (tag Raw/Data). Screen it over a HUD/background; OutMatte drives glow or comps
  the sweep on its own.
""",
    # --- diag ---
    "color_blindness": """
## Notes

A **colour-blindness simulator** for accessibility QC: it shows roughly how Front 1 looks to a
viewer with one of the three dichromacies, so you can confirm graphics, mattes overlays, and
status colours still read for everyone.

### Matrices
Uses the **Machado, Oliveira & Fernandes (2009)** severity-1.0 LMS-deficiency matrices —
the same set Chrome DevTools and many accessibility tools ship — applied as a single 3×3 per
type (the LMS round-trip is pre-baked into the matrix). One matrix each for:
- `type` **0 = protanopia** (no L / red cones)
- `type` **1 = deuteranopia** (no M / green cones)
- `type` **2 = tritanopia** (no S / blue cones)

The three simulated colours are computed in parallel (formulas `simP`/`simD`/`simT`, three dot
products each), then **selected with `step()` weights** `w = (wProtan, wDeutan, wTritan)` — no
arrays or branches — and each output channel is a single `dot()` against `w`.

### Controls
- `type` picks the deficiency (round to 0/1/2; the step thresholds are at 0.5 and 1.5).
- `amount` 0..1 blends original→full simulation (handy for an A/B nudge).

### Practical notes
- **Feed display-referred, sRGB-ish values.** The matrices are fit in sRGB display space; on
  scene-linear footage add a view transform / `linear_to_srgb` before this node.
- Matte just passes **Matte 1** through; connect it if you need the alpha preserved.
""",
    "exposure_zebra": """
## Notes

A **camera-style zebra** overlay: animated diagonal hatching marks where Front 1 is clipping,
without changing the underlying pixels you grade against.

### How it works
- Clipping is detected on the **per-channel max**, `chmax = max(r,g,b)`: at or above `hi`
  (default 1.0) the pixel is "over" → **red** stripes; at or below `lo` (default 0.0) it is
  "under" → **blue** stripes; everything between passes through untouched.
- The stripe pattern is `step(0.0, sin((x + y) * freq + phase))` — a hard diagonal hatch.
  `freq` sets the stripe pitch; **`phase` is keyframable**, so animate it to make the stripes
  crawl (a moving hatch is easier to spot than a static one).

### Controls
- `hi` / `lo` — clip thresholds (raise `hi` to flag only true whites, etc.).
- `freq` — stripe spacing; `phase` — keyframe to crawl.

### Practical notes
- Detection is on the channel max, so a single blown channel still flags (matches how a real
  zebra warns on the brightest component).
- **OutMatte** carries the clipped mask (`max(over, under)`) — connect **Matte 1** to render
  it; use it to drive a fix downstream or just to count clipped pixels.
""",
    "gamut_clip": """
## Notes

Flags **illegal / out-of-gamut pixels** so negative light and over-range values don't sneak
through a comp.

### How it works
- **Negative** (`min(r,g,b) < 0`) → tinted **magenta** (1,0,1).
- **Over-ceiling** (`max(r,g,b) > ceiling`, default 1.0) → tinted **yellow** (1,1,0).
- In-range pixels pass through. Negative wins where a pixel is both.
- `tint` 0..1 sets how strongly the warning colour replaces the pixel (1.0 = solid flag,
  lower = a translucent wash so you can still see the image under it).

### Controls
- `ceiling` — the upper legal bound (set to your delivery white, e.g. 1.0 for 0–1 deliverables).
- `tint` — warning opacity.

### Practical notes
- **Negative light** is the common culprit after a saturated grade, a colour-space matrix, or
  a sharpen — this makes it visible instead of silently clamped later.
- **OutMatte** is the union mask (`max(neg, over)`) — connect **Matte 1** to render it and feed
  a clamp/repair only where it's needed.
""",
}


# --- Per-setup node-dependency notes (rendered into each .md as "## Node dependencies") ---
# Setups that are one stage of a Batch graph: they need a specific pass wired UPSTREAM and/or
# emit an intermediate a DOWNSTREAM node must consume. Full wiring guide + diagrams:
# documentation/node_dependencies.md (hand-maintained — keep it and these entries in sync).
_DEP_REF = "See `documentation/node_dependencies.md` for the full wiring guide."


def _dep(pipeline, body):
    """One dependency block: a one-line Pipeline arrow + explanation + doc cross-ref."""
    return f"**Pipeline:** {pipeline}\n\n{body}\n\n{_DEP_REF}"


# Shared bodies (reused across a family of setups).
_DEP_STMAP = (
    "Outputs a 0..1 **ST/UV map** (`red`=U, `green`=V) — *coordinates*, not a warped image. On "
    "its own it looks like a red/green gradient and changes nothing. Wire its output into a "
    "downstream **STMap** node's map/UV input, and the plate you want warped into the STMap's "
    "source — the STMap does the re-sample (the pixel gather this node can't do). **Tag the "
    "map Raw/Data**; colour-managing a coordinate map corrupts the warp.")
_DEP_DEPTH = (
    "Reads the **Z/depth pass on Matte 1** (the library convention — `m1`). Raw Z is in scene "
    "units, so set the normalising range to your near/far. No depth on Matte 1 = no useful "
    "result (input wiring is never saved in the setup file — re-wire it in Batch every time).")
_DEP_DEFOCUS = (
    "Emits a per-pixel **blur amount** (0..1), not a blurred image — the node can't gather "
    "neighbours. Feed it into a downstream **variable-blur / Defocus** node as its blur-amount "
    "(matte) input, with the plate on that node's front. Output is data — tag it Raw/Data.")
_DEP_P = (
    "Reads a **world-position (P) pass on Front 1** (RGB encode XYZ). Set the centre/extent "
    "variables to the world point/size you want to isolate; without a P pass it produces "
    "nothing meaningful. Tip: test without a render by feeding the `stmap` node into Front 1.")
_DEP_NORMAL = (
    "Reads a **normal pass on Front 1**, expected in **-1..1**. If yours is 0..1-encoded "
    "(common in EXRs), remap upstream (`*2-1`) or inline `vec3(r1,g1,b1)*2.0-1.0`.")
_DEP_AOV = (
    "Consumes specific **render AOVs/passes** delivered by your renderer or extracted from EXR "
    "layers upstream (a Read/MUX/Channel node). The passes are data/light — keep them in the "
    "right space (linear for light math) and wire each to the input named below.")


DEPENDS = {
    # ---- Downstream STMap: coordinate-map generators ----
    "stmap": _dep("**this node** → **STMap**",
                  _DEP_STMAP + " `stmap` is the *identity* map: warps nothing by itself — it's "
                  "the baseline you offset to build a custom warp, and a handy test source for "
                  "the P-matte setups."),
    "lens_distort": _dep("**this node** → **STMap**",
                         _DEP_STMAP + " Adds radial barrel (`k1<0`) / pincushion (`k1>0`) "
                         "distortion; typical job is baking a plate's measured distortion onto a "
                         "clean CG render."),
    "lens_undistort": _dep("**this node** → **STMap**",
                           _DEP_STMAP + " Approximate *inverse* of `lens_distort`. For a clean "
                           "round-trip, undistort → work → re-apply `lens_distort` with the same "
                           "coefficients rather than trusting a perfect inverse."),
    "anamorphic_unsqueeze": _dep("**this node** → **STMap**",
                                 _DEP_STMAP + " Horizontal unsqueeze (e.g. `squeeze` 2.0 for 2x "
                                 "anamorphic)."),
    "uv_transform": _dep("**this node** → **STMap**",
                         _DEP_STMAP + " Zoom/pan a source through the STMap (`zoom`, `panX`, "
                         "`panY`)."),
    "polar_to_cartesian": _dep("**this node** → **STMap**",
                               _DEP_STMAP + " Polar/rectangular remap — tiny-planet, mirror-ball, "
                               "360 reframe (`twist` rotates, `zoom` scales the radius)."),
    "kaleidoscope_map": _dep("**this node** → **STMap**",
                             _DEP_STMAP + " Mirror-folds angular space into `segments` wedges "
                             "around Centre; `rot` spins it."),
    "lens_distort_map": _dep("**this node** → **STMap**",
                             _DEP_STMAP + " Barrel/pincushion (`k1`,`k2`) plus an anamorphic "
                             "`squeeze`; negate `k1`/`k2` to undistort."),
    "glitch_block_map": _dep("**this node** → **STMap**",
                             _DEP_STMAP + " Block-shuffle / datamosh — **keyframe `corruption`** "
                             "(0→1) to trigger; `seed` reshuffles the blocks."),
    "heat_haze_map": _dep("**this node** → **STMap**",
                          _DEP_STMAP + " fbm-driven shimmer — **keyframe `seed`** to animate the "
                          "wobble; `amp` sets strength."),
    "chromatic_aberration_map": _dep("**this node** → **STMap** (per channel)",
        "Outputs the **red** channel's ST/UV in `red`/`green` and the **radial-offset "
        "magnitude** in `blue` — one ST map can't carry three different per-channel UVs. Two "
        "downstream options: (1) **per-channel STMap** — generate the map three times (red "
        "as-is; a green variant with `amount`=0; a blue variant with `-amount`), STMap each "
        "colour channel of the plate, recombine; or (2) feed `blue` into a **defringe** node as "
        "its strength map (simpler, approximate). Tag Raw/Data."),

    # ---- Downstream variable-blur / Defocus ----
    "coc_from_depth": _dep("depth pass (Matte 1) → **this node** → variable-blur / Defocus",
                           _DEP_DEFOCUS + " It reads the **depth pass on Matte 1** and outputs a "
                           "circle-of-confusion radius from `focusDepth` / `focusRange` / "
                           "`maxBlur` — so it needs depth *in* and a defocus node *out*. Set "
                           "`focusDepth` to your focal plane's depth value."),
    "depth_dof_mask": _dep("depth pass (Matte 1) → **this node** → variable-blur / Defocus",
                           _DEP_DEFOCUS + " A 0..1 in-focus/out-of-focus **mask** from the depth "
                           "pass on Matte 1 — art-directed falloff rather than a physical CoC."),

    # ---- Upstream depth pass (Matte 1) ----
    "depth_normalize": _dep("depth pass (Matte 1) → **this node**", _DEP_DEPTH),
    "depth_matte": _dep("depth pass (Matte 1) → **this node**", _DEP_DEPTH +
                        " Output is a matte (RGB + OutMatte) you carry into a downstream comp."),
    "depth_contours": _dep("depth pass (Matte 1) → **this node**", _DEP_DEPTH),
    "depth_posterize": _dep("depth pass (Matte 1) → **this node**", _DEP_DEPTH),
    "depth_fog": _dep("beauty (Front 1) + depth pass (Matte 1) → **this node**", _DEP_DEPTH +
                      " Also needs the **beauty on Front 1** — it tints by depth."),
    "depth_fade": _dep("beauty (Front 1) + depth pass (Matte 1) → **this node**", _DEP_DEPTH +
                       " Also needs the **beauty on Front 1**."),
    "depth_grade": _dep("beauty (Front 1) + depth pass (Matte 1) → **this node**", _DEP_DEPTH +
                        " Also needs the **beauty on Front 1**."),
    "depth_mix": _dep("near plate (Front 1) + far plate (Front 2) + depth pass (Matte 1) → **this node**",
                      _DEP_DEPTH + " Blends **two plates** (Front 1 near, Front 2 far) at a depth "
                      "threshold."),
    "dual_output_depth": _dep("beauty (Front 1) + depth pass (Matte 1) → **this node** → (matte to comp)",
                              _DEP_DEPTH + " Two products from one node: RGB is a depth-tinted "
                              "grade of the beauty, while OutMatte is an independent depth-slab "
                              "key (needs a clip on Matte 1 for OutMatte to render)."),

    # ---- Upstream world-position (P) pass (Front 1) ----
    "pmatte_sphere": _dep("P-world pass (Front 1) → **this node** → (matte to comp)", _DEP_P),
    "pmatte_rings": _dep("P-world pass (Front 1) → **this node** → (matte to comp)", _DEP_P),
    "pmatte_rays": _dep("P-world pass (Front 1) → **this node** → (matte to comp)", _DEP_P),
    "box_matte": _dep("P-world pass (Front 1) → **this node** → (matte to comp)", _DEP_P),

    # ---- Upstream normal pass (Front 1) ----
    "normal_relight": _dep("normal pass (Front 1) → **this node**", _DEP_NORMAL +
                           " Output is scene-linear light to add/comp downstream."),
    "fresnel_facing": _dep("camera-space normal pass (Front 1) → **this node**", _DEP_NORMAL +
                           " It additionally wants a **camera-space** normal (so `.z` faces the "
                           "lens); world-space normals need a camera transform this node can't do."),

    # ---- Upstream render AOVs ----
    "albedo_divide": _dep("beauty (Front 1) + albedo (Front 2) → **this node**", _DEP_AOV +
                          " De-lights: beauty ÷ albedo → lighting."),
    "albedo_multiply": _dep("albedo (Front 1) + lighting (Front 2) → **this node**", _DEP_AOV +
                            " Re-lights: albedo × lighting → beauty."),
    "ao_multiply": _dep("beauty (Front 1) + AO (Matte 1) → **this node**", _DEP_AOV +
                        " The **AO pass goes on Matte 1** (it's data, not a matte to key)."),
    "aov_add": _dep("pass A (Front 1) + pass B (Front 2) → **this node**", _DEP_AOV +
                    " Recombine light AOVs by addition (work in scene-linear)."),
    "aov_grade_add": _dep("running sum (Front 1) + next pass (Front 2) → **this node**", _DEP_AOV +
                          " Grade one pass and add it back to the sum (scene-linear)."),
    "screen_merge": _dep("pass A (Front 1) + pass B (Front 2) → **this node**", _DEP_AOV +
                         " Screen two passes (e.g. additive glints) in scene-linear."),
    "id_isolate": _dep("beauty (Front 1) + ID mask (Matte 1) → **this node**", _DEP_AOV +
                       " The **ID/matte pass goes on Matte 1** to isolate a region of the beauty."),
    "crypto_pick_2rank": _dep("crypto value (Front 1) + crypto coverage (Matte 1) → **this node**",
                              "Needs **Cryptomatte rank layers** extracted upstream (a Cryptomatte/"
                              "Channel node): the rank's value on Front 1, its coverage on Matte 1. "
                              "It picks the object hash `id` from those ranks — no extracted ranks, "
                              "no matte."),
    "crypto_pick_4rank": _dep("crypto ranks (Front 1 + Matte 1, Front 2 + Matte 2) → **this node**",
                              "Needs **two Cryptomatte rank pairs** extracted upstream — value/"
                              "coverage on Front 1/Matte 1 and Front 2/Matte 2 — for a cleaner edge "
                              "across four ranks."),

    # ---- Upstream clean plate / painted control map ----
    "difference_matte": _dep("shot (Front 1) + aligned clean plate (Front 2) → **this node** → (matte to comp)",
                             "Keys what *changed* between the shot (Front 1) and a **clean plate** "
                             "(Front 2) — so it needs that aligned clean plate wired upstream. "
                             "`gain` scales the difference."),
    "painted_grade": _dep("image (Front 1) + painted control map (Front 2) → **this node**",
                          "The grade is driven by a **painted control map on Front 2**: `r2` = "
                          "local exposure, `g2` = local hue, `b2` = local saturation (flat 0.5 grey "
                          "= neutral). The upstream 'node' is wherever you paint/generate that map "
                          "— Paint, a roto fill, a ramp, or another generator."),

    # ---- Paired Pixel Expression nodes ----
    "channel_pack": _dep("Matte 1 + Matte 2 + Front 1 → **this node** → `channel_unpack`",
                         "Ferries three single-channel signals down **one** RGB connection (red = "
                         "Matte 1, green = Matte 2, blue = Front 1 luma). Useless without its "
                         "partner **`channel_unpack`** at the far end to recover them."),
    "channel_unpack": _dep("`channel_pack` output (Front 1) → **this node**",
                           "The other half of the pair: takes a **packed RGB** (from "
                           "`channel_pack`) on Front 1 and routes one channel to OutMatte (`pick` = "
                           "0/1/2 selects r/g/b)."),
    "rgb_to_hsv": _dep("**this node** → an HSV consumer (e.g. `hsv_to_rgb`)",
                       "Emits an **HSV-encoded** image (H,S,V in R,G,B) — not a display picture. "
                       "Bracket a hand-built HSV operation with `rgb_to_hsv` … `hsv_to_rgb`, or "
                       "feed any node that expects HSV."),
    "hsv_to_rgb": _dep("HSV source (e.g. `rgb_to_hsv`) → **this node**",
                       "Expects an **HSV-encoded** input, which in practice comes from "
                       "`rgb_to_hsv` (or another HSV source) upstream."),
}


def _fmt_vars(variables):
    if not variables:
        return "_No variables._"
    parts = []
    for n, v in variables:
        parts.append(f"`{n}` (animated)" if isinstance(v, (list, tuple)) else f"`{n}` ({v})")
    return "**Variables:** " + ", ".join(parts)


def write_doc(s):
    name = s["name"]
    what, use, inputs = DOCS.get(name, ("", "", "—"))
    md = (
        f"# {name}\n\n"
        f"**What it does:** {what}\n\n"
        f"**Use case:** {use}\n\n"
        f"**Inputs:** {inputs}\n\n"
        f"**Expects:** {EXPECTS.get(name, _ANY)}\n\n"
        f"{_fmt_vars(s.get('variables'))}\n"
    )
    if name in DEPENDS:
        md += "\n## Node dependencies\n" + DEPENDS[name].strip() + "\n"
    if name in NOTES:
        md += "\n" + NOTES[name].strip() + "\n"
    path = os.path.join(OUT_DIR, s["category"], f"{name}.md")
    with open(path, "w") as f:
        f.write(md)


missing_docs = [s["name"] for s in SETUPS if s["name"] not in DOCS]
missing_expects = [s["name"] for s in SETUPS if s["name"] not in EXPECTS]

for s in SETUPS:
    s.setdefault("category", CATEGORY.get(s["name"], "utility"))
    build(**s)
    write_doc(s)

print(f"\nDone — {len(SETUPS)} setups generated (+ per-setup .md docs).")
if missing_docs:
    print("WARNING: missing DOCS entries:", ", ".join(missing_docs))
if missing_expects:
    print("WARNING: missing EXPECTS entries:", ", ".join(missing_expects))
