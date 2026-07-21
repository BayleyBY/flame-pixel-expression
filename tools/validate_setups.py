#!/usr/bin/env python3
"""Sanity-check every generated .pixel_expression_node setup.

Checks (ERRORS): well-formed XML; mandatory slots present (4 expressions, 4 declaration
blocks, 4 formula slots, Centre X/Y); no empty channel expressions; at most 8 variables;
no duplicate variable/formula names (or a variable and formula sharing one name); no
reserved-name collisions (a declared name shadowing a node built-in/input, or a GLSL
keyword); valid FormulaType (0-3); balanced AND properly nested parens; formulas only
referencing EARLIER formula slots; and — the useful one — every identifier used in an
expression resolves to a GLSL builtin, a node input/built-in variable, or a declared
variable/formula. That catches typos like a variable declared `radius` but referenced as
`raduis`. Swizzles only count after a '.', and numeric literals (incl. scientific
notation) are tokenized atomically so `1.0e-3` can't shed a fake `e3` identifier.

Warnings: declared-but-unused variables/formulas; a formula name with an empty
expression (or vice versa); a declared name shadowing a GLSL *function* name.

Exits 1 if any ERROR was found (so `validate && next-step` actually gates).
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

# This script lives in tools/; setups live in <repo>/setups/.
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "setups")

GLSL = {
    "sin", "cos", "tan", "asin", "acos", "atan", "radians", "degrees",
    "sinh", "cosh", "tanh", "asinh", "acosh", "atanh",
    "pow", "exp", "log", "exp2", "log2", "sqrt", "inversesqrt",
    "abs", "sign", "floor", "ceil", "fract", "trunc", "round", "roundEven",
    "mod", "min", "max", "fma",
    "clamp", "mix", "step", "smoothstep", "length", "distance", "dot", "cross",
    "normalize", "reflect", "refract", "isnan", "isinf", "matrixCompMult",
    "vec2", "vec3", "vec4", "ivec2", "ivec3", "ivec4", "bvec2", "bvec3", "bvec4",
    "mat2", "mat3", "mat4", "float", "int", "bool", "true", "false",
}
# GLSL keywords that can never be a user identifier — a variable/formula with one of
# these names cannot compile, whatever Flame's dialect.
GLSL_KEYWORDS = {
    "const", "uniform", "in", "out", "inout", "attribute", "varying", "void", "main",
    "if", "else", "for", "while", "do", "return", "break", "continue", "discard",
    "switch", "case", "default", "struct", "layout", "precision",
    "highp", "mediump", "lowp", "sampler2D",
}
# The node-update recognises both spellings of the centre built-in.
BUILTINS = {"E", "PI", "x", "y", "width", "height", "centre", "center", "uv"}
INPUTS = {"r1", "g1", "b1", "r2", "g2", "b2", "m1", "m2",
          "front1", "front2", "matte1", "matte2"}
MAX_VARS = 8   # UI cap — the <Variables> list format would happily hold more

# Swizzles are only swizzles AFTER a dot; strip them before tokenizing so a bare `br`
# typo is NOT silently accepted as swizzle-shaped.
SWIZZLE = re.compile(r"\.\s*[xyzwrgba]{1,4}\b")
# One pass over the text: numeric literals (incl. exponent) are consumed atomically so
# they can never shed identifier-looking fragments; alpha-leading matches are identifiers.
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?")

EXPR_TAGS = ["RedExpression", "GreenExpression", "BlueExpression", "MatteExpression"]
# New format (PR245+): four mandatory per-channel local-declaration blocks.
DECL_TAGS = ["RedDeclarations", "GreenDeclarations", "BlueDeclarations", "MatteDeclarations"]


def idents(expr):
    stripped = SWIZZLE.sub(" ", expr)
    return [t for t in TOKEN.findall(stripped) if t[0].isalpha() or t[0] == "_"]


def paren_problem(expr):
    """Return a message for unbalanced OR mis-nested parens (')r1(' style), else None."""
    depth = 0
    for ch in expr:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return "mis-nested parens (')' before its '(')"
    return "unbalanced parens" if depth != 0 else None


def check(path):
    errs, warns = [], []
    try:
        root = ET.parse(path).getroot()
    except Exception as e:
        return [f"XML parse failed: {e}"], []
    state = root.find("State")
    if state is None:
        return ["no <State>"], []

    # Slot presence. Formulas are still 4 fixed slots; expressions/declarations/centre
    # are mandatory. Variables are a <Variables> list (0..MAX_VARS entries).
    for i in range(4):
        for part in ("FormulaName", "FormulaExpression", "FormulaType"):
            if state.find(f"{part}{i}") is None:
                errs.append(f"missing {part}{i}")
    for t in EXPR_TAGS + DECL_TAGS + ["CentreX", "CentreY"]:
        if state.find(t) is None:
            errs.append(f"missing {t}")

    # Declared variable names — a <Variables> list of <Variable name="..">, absent
    # entirely when a setup has no variables.
    var_names = []
    vars_el = state.find("Variables")
    if vars_el is not None:
        for v in vars_el.findall("Variable"):
            nm = (v.get("name") or "").strip()
            if nm:
                var_names.append(nm)
    if len(var_names) > MAX_VARS:
        errs.append(f"{len(var_names)} variables declared (UI cap is {MAX_VARS})")
    decl_vars = set(var_names)
    for nm in sorted({n for n in var_names if var_names.count(n) > 1}):
        errs.append(f"duplicate variable name '{nm}'")

    # Formula slots, in order (a formula may only reference EARLIER slots).
    form_slots = []
    for i in range(4):
        nm = state.findtext(f"FormulaName{i}", "").strip()
        ex = state.findtext(f"FormulaExpression{i}", "").strip()
        ty = state.findtext(f"FormulaType{i}", "").strip()
        if ty and ty not in {"0", "1", "2", "3"}:
            errs.append(f"FormulaType{i} is '{ty}' (must be 0-3)")
        if nm and not ex:
            warns.append(f"formula '{nm}' (slot {i}) has an empty expression")
        if ex and not nm:
            warns.append(f"FormulaExpression{i} set but FormulaName{i} is empty")
        if nm:
            form_slots.append((i, nm, ex))
    decl_forms = {nm for _, nm, _ in form_slots}

    # Name-collision classes. A declared name that shadows a built-in (uv, x, y, width,
    # height, centre, E, PI) or an input (r1…) collides with the injected identifier —
    # in Flame this silently fails to load (it's how `width` broke hsl_targeted).
    for bad in sorted((decl_vars | decl_forms) & (BUILTINS | INPUTS)):
        errs.append(f"reserved name '{bad}' used as a variable/formula (shadows a built-in/input)")
    for bad in sorted((decl_vars | decl_forms) & GLSL_KEYWORDS):
        errs.append(f"GLSL keyword '{bad}' used as a variable/formula name")
    for bad in sorted(decl_vars & decl_forms):
        errs.append(f"'{bad}' is both a variable and a formula name")
    for shadow in sorted((decl_vars | decl_forms) & GLSL):
        warns.append(f"'{shadow}' shadows a GLSL builtin function/type name")

    base_allowed = GLSL | BUILTINS | INPUTS | decl_vars

    # Channel expressions may use everything; formula bodies only earlier formulas.
    used = set()

    def scan(tag, expr, allowed):
        prob = paren_problem(expr)
        if prob:
            errs.append(f"{tag}: {prob}")
        for tok in idents(expr):
            used.add(tok)
            if tok not in allowed:
                errs.append(f"{tag}: undefined identifier '{tok}'")

    for slot, nm, ex in form_slots:
        earlier = {n for s, n, _ in form_slots if s < slot}
        if ex:
            scan(f"FormulaExpression{slot} ('{nm}')", ex, base_allowed | earlier)

    for t in EXPR_TAGS:
        e = state.findtext(t, "")
        if not e.strip():
            errs.append(f"{t} is empty")
            continue
        scan(t, e, base_allowed | decl_forms)

    # Declared but unused (typo / leftover) — warning only.
    for v in sorted(decl_vars - used):
        warns.append(f"variable '{v}' declared but never used")
    for f in sorted(decl_forms - used):
        warns.append(f"formula '{f}' declared but never used")
    return errs, warns


files = sorted(glob.glob(os.path.join(ROOT, "**", "*.pixel_expression_node"), recursive=True))

total_err = total_warn = 0
for f in files:
    errs, warns = check(f)
    rel = os.path.relpath(f, ROOT)
    if errs or warns:
        print(rel)
        for e in errs:
            print(f"   ERROR: {e}")
            total_err += 1
        for w in warns:
            print(f"   warn:  {w}")
            total_warn += 1

print(f"\n{len(files)} setups checked — {total_err} errors, {total_warn} warnings.")
sys.exit(1 if total_err else 0)
