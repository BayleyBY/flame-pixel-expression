"""ST-map generator demos for the flame-pixel-expression library.

For each stmap_generators setup: build the UV map with the setup's exact GLSL math
(bottom-up y, centre = image middle, per the node), then apply it the way Flame's
STMap node would (bilinear resample of the source at (U*W, V*H)). CoC tools use the
AOV EXR's real depth pass. Outputs land in demo_images/stmap_demos/.
Note: heat_haze/glitch use an equivalent (not bit-identical) value-noise/hash — the
GLSL hash constants differ, the structure (lattice, octaves, ranges) matches.
"""
import os
import numpy as np
import OpenEXR
from PIL import Image, ImageDraw, ImageFont

SCRATCH = ("/private/tmp/claude-509/-Volumes-Flame-Archive-AI-Projects-claude-projects-"
           "flame-flame-pixel-expression/3cdbe482-5db9-40b4-997e-c0b7e1ab9faa/scratchpad")
OUT = "demo_images/stmap_demos"
os.makedirs(OUT, exist_ok=True)

# ---- source image, bottom-up orientation (y = 0 at the bottom, like the node) ----
photo = np.asarray(Image.open(f"{SCRATCH}/arch_base.png").convert("RGB")).astype(np.float64) / 255.0
photo = photo[::-1]
H, W = photo.shape[:2]
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
CX, CY = W / 2.0, H / 2.0          # centre defaults to the image middle (PR245)

def save(name, img_bu):
    Image.fromarray((np.clip(img_bu[::-1], 0, 1) * 255).astype(np.uint8)).save(f"{OUT}/{name}.png")

def warp(src, U, V):
    """Flame STMap: sample src at (U,V) in 0..1, bilinear, clamped borders."""
    sh, sw = src.shape[:2]
    px = np.clip(U * sw - 0.5, 0, sw - 1.001)
    py = np.clip(V * sh - 0.5, 0, sh - 1.001)
    x0 = np.floor(px).astype(int); y0 = np.floor(py).astype(int)
    fx = (px - x0)[..., None]; fy = (py - y0)[..., None]
    c00 = src[y0, x0]; c10 = src[y0, x0 + 1]; c01 = src[y0 + 1, x0]; c11 = src[y0 + 1, x0 + 1]
    return (c00 * (1 - fx) + c10 * fx) * (1 - fy) + (c01 * (1 - fx) + c11 * fx) * fy

def map_img(U, V, B=None):
    return np.stack([U, V, B if B is not None else np.zeros_like(U)], -1)

results = {}   # name -> (map image, result image)

# ---- uv_test_chart (gridN 10, lineW 0.002) — the library's own test source --------
uvx, uvy = (xs + 0.5) / W, (ys + 0.5) / H
grid = np.clip((np.modf(uvx * 10.0)[0] > 0.97) + (np.modf(uvy * 10.0)[0] > 0.97), 0, 1)
chart = np.stack([uvx, uvy, np.full_like(uvx, 0.5)], -1)
chart = chart * (1 - grid[..., None]) + grid[..., None]
cross = np.clip((np.abs(uvx - 0.5) < 0.002) + (np.abs(uvy - 0.5) < 0.002), 0, 1)
chart = chart * (1 - cross[..., None]) + cross[..., None] * np.array([1.0, 0.2, 0.2])
save("uv_test_chart", chart)

# ---- stmap (identity) -------------------------------------------------------------
U, V = (xs + 0.5) / W, (ys + 0.5) / H
results["stmap (identity)"] = (map_img(U, V), warp(photo, U, V))

# ---- polar_to_cartesian (twist 0, zoom 1) -----------------------------------------
nx = ((xs + 0.5 - CX) / W) * 2.0
ny = ((ys + 0.5 - CY) / H) * 2.0 * (H / W)
U = np.modf((np.arctan2(ny, nx)) / (2 * np.pi) + 1.0)[0]
V = np.clip(np.hypot(nx, ny) / 1.0, 0, 1)
results["polar_to_cartesian"] = (map_img(U, V), warp(photo, U, V))

# ---- kaleidoscope_map (segments 6, rot 0) -----------------------------------------
nx = (xs + 0.5 - CX) / W
ny = ((ys + 0.5 - CY) / H) * (H / W)
rad = np.hypot(nx, ny)
seg = 6.0
fa = np.abs(np.mod(np.arctan2(ny, nx), 2 * np.pi / seg) - np.pi / seg)
U = CX / W + np.cos(fa) * rad
V = CY / H + np.sin(fa) * rad * (W / H)
results["kaleidoscope_map (segments 6)"] = (map_img(U, V), warp(photo, U, V))

# ---- lens_distort_map (k1 0.25) — on the chart: straight lines curve --------------
nx = ((xs + 0.5 - CX) / W) * 2.0
ny = ((ys + 0.5 - CY) / H) * 2.0 * (H / W)
r2 = nx * nx + ny * ny
fD = 1.0 + 0.25 * r2
U = CX / W + nx * fD / 1.0 * 0.5
V = CY / H + ny * fD * 0.5 * (W / H)
results["lens_distort_map (k1 0.25)"] = (map_img(U, V), warp(chart, U, V))

# ---- chromatic_aberration_map (amount 0.03) — documented 3-instance workflow ------
amt = 0.03
ca = np.zeros_like(photo)
for chan, a in ((0, amt), (1, 0.0), (2, -amt)):
    U = CX / W + nx * (1.0 + a) * 0.5
    V = CY / H + ny * (1.0 + a) * 0.5 * (W / H)
    ca[..., chan] = warp(photo[..., chan:chan + 1], U, V)[..., 0]
Ur = CX / W + nx * (1.0 + amt) * 0.5
Vr = CY / H + ny * (1.0 + amt) * 0.5 * (W / H)
results["chromatic_aberration_map (0.03)"] = (map_img(Ur, Vr, np.hypot(nx, ny) * amt), ca)

# ---- heat_haze_map (scale 120, amp 0.02) — equivalent value-noise FBM -------------
def vnoise(px, py, seed=0.0):
    ix, iy = np.floor(px), np.floor(py)
    fx, fy = px - ix, py - iy
    u = fx * fx * (3 - 2 * fx); v = fy * fy * (3 - 2 * fy)
    def h(a, b):
        n = np.sin(a * 127.1 + b * 311.7 + seed * 74.7) * 43758.5453
        return n - np.floor(n)
    return ((h(ix, iy) * (1 - u) + h(ix + 1, iy) * u) * (1 - v)
            + (h(ix, iy + 1) * (1 - u) + h(ix + 1, iy + 1) * u) * v)

scale, amp = 120.0, 0.02
nA = sum(vnoise(xs / scale * 2 ** o, ys / scale * 2 ** o) * 0.5 ** (o + 1) for o in range(3)) / sum(0.5 ** (o + 1) for o in range(3))
nB = vnoise(xs / scale + 5.2, ys / scale + 1.7)
U = (xs + 0.5) / W + (nA - 0.5) * amp
V = (ys + 0.5) / H + (nB - 0.5) * amp
results["heat_haze_map (amp 0.02)"] = (map_img(U, V), warp(photo, U, V))

# ---- glitch_block_map (blockSize 64, corruption 0.6) ------------------------------
bx, by = np.floor(xs / 64.0), np.floor(ys / 64.0)
def h2(a, b, k):
    n = np.sin(a * 12.9898 + b * 78.233 + k) * 43758.5453
    return n - np.floor(n)
corr = 0.6
U = (xs + 0.5) / W + (h2(bx, by, 0.0) - 0.5) * corr * 0.2
V = (ys + 0.5) / H + (h2(bx, by, 7.0) - 0.5) * corr * 0.05
results["glitch_block_map (corruption 0.6)"] = (map_img(U, V), warp(photo, U, V))

# ---- uv_transform (zoom 1.5, panX 0.1) --------------------------------------------
U = 0.5 + ((xs + 0.5) / W - 0.5) / 1.5 - 0.1
V = 0.5 + ((ys + 0.5) / H - 0.5) / 1.5 - 0.0
results["uv_transform (zoom 1.5, panX 0.1)"] = (map_img(U, V), warp(photo, U, V))

# ---- anamorphic_unsqueeze (squeeze 2) — build a squeezed source first -------------
sq = np.full_like(photo, 0.18)
xsq = np.clip(((xs - CX) * 2.0 + CX), 0, W - 1.001)      # squeeze photo 2:1 about centre
x0 = np.floor(xsq).astype(int); fx = (xsq - x0)[..., None]
inside = np.abs(xs - CX) < W / 4.0
sq_s = photo[ys.astype(int), x0] * (1 - fx) + photo[ys.astype(int), np.minimum(x0 + 1, W - 1)] * fx
sq = np.where(inside[..., None], sq_s, sq)
save("anamorphic_squeezed_source", sq)
U = 0.5 + ((xs + 0.5) / W - 0.5) / 2.0
V = (ys + 0.5) / H
results["anamorphic_unsqueeze (squeeze 2)"] = (map_img(U, V), warp(sq, U, V))

# ---- CoC tools: real depth from the AOV EXR ---------------------------------------
exr = OpenEXR.File("demo_images/aov_demo_render.exr")
ech = exr.channels()
depth = np.asarray(ech["depth.Z"].pixels, np.float64)[::-1]          # bottom-up
beauty = np.asarray(ech["RGBA"].pixels, np.float64)[::-1][..., :3]
def tonemap(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)
def variable_blur(img, coc, levels=6, max_r=18):
    stack = [img]
    for i in range(1, levels):
        r = max(1, int(round(max_r * i / (levels - 1))))
        k = 2 * r + 1
        b = stack[0]
        for _ in range(3):
            c = np.cumsum(np.pad(b, ((r + 1, r), (0, 0), (0, 0)), "edge"), axis=0)
            b = (c[k:] - c[:-k]) / k
            c = np.cumsum(np.pad(b, ((0, 0), (r + 1, r), (0, 0)), "edge"), axis=1)
            b = (c[:, k:] - c[:, :-k]) / k
        stack.append(b)
    idx = np.clip(coc, 0, 1) * (levels - 1)
    lo = np.floor(idx).astype(int); f = (idx - lo)[..., None]
    hi = np.minimum(lo + 1, levels - 1)
    st = np.stack(stack)
    ih, iw = img.shape[:2]
    rr = np.arange(ih)[:, None]; cc = np.arange(iw)[None, :]
    return st[lo, rr, cc] * (1 - f) + st[hi, rr, cc] * f

coc1 = np.clip(np.abs(depth - 6.5) / 2.5, 0, 1) * 1.0                # coc_from_depth
results["coc_from_depth (focus 6.5, range 2.5)"] = (
    np.repeat(coc1[..., None], 3, -1), tonemap(variable_blur(beauty, coc1)))
fl, fs, fd, bs = 0.05, 2.8, 6.5, 1000.0                              # thin_lens_coc
coc2 = np.clip(np.abs((fl * fl / fs) * (depth - fd) / (depth * (fd - fl) + 1e-4)) * bs, 0, 1.0)
results["thin_lens_coc (f/2.8 at 6.5)"] = (
    np.repeat(coc2[..., None], 3, -1), tonemap(variable_blur(beauty, coc2)))

# ---- save individual results + contact sheets -------------------------------------
def slug(n): return n.split(" (")[0]
for name, (m, r) in results.items():
    save(f"{slug(name)}_map", m)
    save(f"{slug(name)}_result", r)

def sheet(items, path, tw=480):
    th_map = {}
    tiles = []
    for name, (m, r) in items:
        for sub, img in (("map", m), ("result → STMap" if "coc" not in slug(name) else "result → blur", r)):
            h_, w_ = img.shape[:2]
            th = int(tw * h_ / w_)
            tiles.append((f"{name} — {sub}", Image.fromarray(
                (np.clip(img[::-1], 0, 1) * 255).astype(np.uint8)).resize((tw, th))))
    th = max(t.size[1] for _, t in tiles)
    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * tw, rows * (th + 26)), (10, 10, 10))
    d = ImageDraw.Draw(canvas)
    try: fnt = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
    except OSError: fnt = ImageFont.load_default()
    for i, (label, t) in enumerate(tiles):
        r_, c_ = divmod(i, cols)
        canvas.paste(t, (c_ * tw, r_ * (th + 26) + 26))
        d.text((c_ * tw + 5, r_ * (th + 26) + 5), label, font=fnt, fill=(230, 230, 230))
    canvas.save(path)

names = list(results.items())
sheet(names[:8], f"{OUT}/stmap_contact_sheet_1.png")
sheet(names[8:], f"{OUT}/stmap_contact_sheet_2.png")
print("done:", len(results), "tools demoed;", len(os.listdir(OUT)), "files in", OUT)
