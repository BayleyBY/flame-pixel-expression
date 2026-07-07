#!/usr/bin/env python3
"""Offline GLSL compile-check for every generated setup — an optional pre-Flame gate.

`validate_setups.py` is a static text check (slot counts, reserved names, undefined idents).
This goes further: it reconstructs each setup's GLSL as a real fragment shader and compiles it
with `glslangValidator`, catching genuine compile errors (type mismatches, bad swizzles, wrong
function signatures) that the text checker can't see.

It is a *proxy*, not a guarantee. The harness is calibrated against the setups already verified
loading in Flame — they all compile here, so a clean run is strong evidence a new setup will
compile in Flame too. It does NOT prove Flame's exact dialect/expression-length limits accept
it, nor that the image is visually correct: a real in-Flame load is still the final word.

Requires `glslangValidator` (not a Python dep):  brew install glslang

Usage:
    python3 tools/glsl_compile_check.py            # check all; exit 1 if any fail
    python3 tools/glsl_compile_check.py -v         # also print the shader for each failure
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "setups")
FTYPE = {"0": "float", "1": "vec2", "2": "vec3", "3": "vec4"}

# Injected by the node, declared here so the expressions type-check exactly as written.
# uv/x/y/width/height/centre + the Front/Matte inputs; E/PI as constants.
HEADER = """#version 410 core
uniform float x, y, width, height;
uniform vec2 centre;
uniform vec2 center;
uniform vec2 uv;
uniform float r1, g1, b1, r2, g2, b2, m1, m2;
const float E = 2.718281828459045;
const float PI = 3.141592653589793;
out vec4 _frag;
"""


def _parse(path):
    root = ET.parse(path).getroot()

    def txt(tag):
        e = root.find(f".//{tag}")
        return (e.text or "") if e is not None else ""

    channels = [txt(f"{c}Expression") for c in ("Red", "Green", "Blue", "Matte")]
    # New format (PR245+): variables are a <Variables> list of <Variable name="..">.
    vars_el = root.find(".//Variables")
    variables = []
    if vars_el is not None:
        variables = [nm for nm in ((v.get("name") or "").strip()
                                   for v in vars_el.findall("Variable")) if nm]
    formulas = []
    for i in range(4):
        nm, ex = txt(f"FormulaName{i}").strip(), txt(f"FormulaExpression{i}").strip()
        ty = txt(f"FormulaType{i}").strip() or "0"
        if nm and ex:
            formulas.append((nm, ex, FTYPE.get(ty, "float")))
    return channels, variables, formulas


def _shader(channels, variables, formulas):
    red, green, blue, matte = channels
    lines = [HEADER]
    lines += [f"uniform float {v};" for v in variables]
    lines.append("void main() {")
    lines += [f"    {ty} {nm} = {ex};" for nm, ex, ty in formulas]
    lines.append(f"    float _r = {red or '0.0'};")
    lines.append(f"    float _g = {green or '0.0'};")
    lines.append(f"    float _b = {blue or '0.0'};")
    lines.append(f"    float _a = {matte or '0.0'};")
    lines.append("    _frag = vec4(_r, _g, _b, _a);")
    lines.append("}")
    return "\n".join(lines)


def _check(path, frag_path):
    src = _shader(*_parse(path))
    with open(frag_path, "w") as f:
        f.write(src)
    r = subprocess.run(["glslangValidator", "-S", "frag", frag_path],
                       capture_output=True, text=True)
    errs = [l.strip() for l in (r.stdout + r.stderr).splitlines()
            if "ERROR" in l and "compilation errors" not in l and "Linking" not in l]
    return r.returncode == 0, errs, src


def main():
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    if not shutil.which("glslangValidator"):
        print("glslangValidator not found. Install it:  brew install glslang", file=sys.stderr)
        return 2

    paths = sorted(glob.glob(os.path.join(ROOT, "*", "*.pixel_expression_node")))
    failures = []
    with tempfile.TemporaryDirectory() as td:
        frag = os.path.join(td, "setup.frag")
        for path in paths:
            name = os.path.relpath(path, ROOT)[:-len(".pixel_expression_node")]
            ok, errs, src = _check(path, frag)
            if not ok:
                failures.append((name, errs, src))

    n = len(paths)
    if not failures:
        print(f"{n} setups compiled — 0 GLSL errors (glslangValidator).")
        return 0

    print(f"{n - len(failures)}/{n} compiled; {len(failures)} FAILED:\n")
    for name, errs, src in failures:
        print(f"--- {name} ---")
        for e in errs[:6]:
            print("   ", e)
        if verbose:
            print("    shader:\n" + "\n".join(f"      {l}" for l in src.splitlines()))
        print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
