#!/usr/bin/env python3
"""Sanity-check every generated .pixel_expression_node setup.

Checks: well-formed XML; correct slot counts (4 expressions, 8 var names, 8 var
channels, 4 formulas, Centre X/Y); balanced parens per expression; no reserved-name
collisions; and — the useful one — every identifier used in an expression resolves to a
GLSL builtin, a node input/built-in variable, a swizzle, or a declared variable/formula.
That catches typos like a variable declared `radius` but referenced as `raduis`.
"""
import glob
import os
import re
import xml.etree.ElementTree as ET

# This script lives in tools/; setups live in <repo>/setups/.
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "setups")

GLSL = {
    "sin", "cos", "tan", "asin", "acos", "atan", "radians", "degrees",
    "pow", "exp", "log", "exp2", "log2", "sqrt", "inversesqrt",
    "abs", "sign", "floor", "ceil", "fract", "trunc", "round", "mod", "min", "max",
    "clamp", "mix", "step", "smoothstep", "length", "distance", "dot", "cross",
    "normalize", "reflect", "refract", "isnan", "isinf",
    "vec2", "vec3", "vec4", "float", "int", "bool",
}
BUILTINS = {"E", "PI", "x", "y", "width", "height", "centre", "uv"}
INPUTS = {"r1", "g1", "b1", "r2", "g2", "b2", "m1", "m2",
          "front1", "front2", "matte1", "matte2"}
SWIZZLE = re.compile(r"^[xyzwrgba]{1,4}$")
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
NUMBER_SUFFIX = re.compile(r"^[0-9]")

EXPR_TAGS = ["RedExpression", "GreenExpression", "BlueExpression", "MatteExpression"]


def idents(expr):
    return [t for t in IDENT.findall(expr) if not NUMBER_SUFFIX.match(t)]


def check(path):
    errs, warns = [], []
    name = os.path.splitext(os.path.basename(path))[0]
    try:
        root = ET.parse(path).getroot()
    except Exception as e:
        return [f"XML parse failed: {e}"], []
    state = root.find("State")
    if state is None:
        return ["no <State>"], []

    # Slot counts
    for i in range(8):
        if state.find(f"VariableName{i}") is None:
            errs.append(f"missing VariableName{i}")
        if state.find(f"Variable{i}") is None:
            errs.append(f"missing Variable{i} channel")
    for i in range(4):
        if state.find(f"FormulaName{i}") is None:
            errs.append(f"missing FormulaName{i}")
    for t in EXPR_TAGS + ["CentreX", "CentreY"]:
        if state.find(t) is None:
            errs.append(f"missing {t}")

    # Declared names
    decl_vars = {state.findtext(f"VariableName{i}", "").strip() for i in range(8)}
    decl_vars.discard("")
    decl_forms = {state.findtext(f"FormulaName{i}", "").strip() for i in range(4)}
    decl_forms.discard("")
    # A declared name that shadows a built-in (uv, x, y, width, height, centre, E, PI) or
    # an input (r1…) collides with the injected identifier — in Flame this silently fails
    # to load (it's how `width` as a variable broke hsl_targeted).
    for bad in sorted((decl_vars | decl_forms) & (BUILTINS | INPUTS)):
        errs.append(f"reserved name '{bad}' used as a variable/formula (shadows a built-in/input)")

    allowed = GLSL | BUILTINS | INPUTS | decl_vars | decl_forms

    # Gather all expressions (channels + formula bodies)
    exprs = {t: state.findtext(t, "") for t in EXPR_TAGS}
    for i in range(4):
        fe = state.findtext(f"FormulaExpression{i}", "")
        if fe.strip():
            exprs[f"FormulaExpression{i}"] = fe

    used = set()
    for tag, e in exprs.items():
        if e.count("(") != e.count(")"):
            errs.append(f"{tag}: unbalanced parens")
        for tok in idents(e):
            used.add(tok)
            if tok in allowed or SWIZZLE.match(tok):
                continue
            errs.append(f"{tag}: undefined identifier '{tok}'")

    # Declared but unused (typo / leftover) — warning only.
    for v in decl_vars:
        if v not in used:
            warns.append(f"variable '{v}' declared but never used")
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
