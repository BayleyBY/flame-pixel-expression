"""Analytic AOV test render for the flame-pixel-expression library.

Ray-traces a small scene in numpy and writes one multi-layer EXR with every pass
the library's data tools consume: beauty RGBA, albedo, diffuse, specular, emission,
AO, world normals (-1..1), world position, depth.Z, 2D screen velocity, and a real
2-rank Cryptomatte (MurmurHash3 ids + subsample coverage + manifest metadata).
Color passes are 4x4 supersampled; data passes are unfiltered center samples.
"""
import json
import struct
import numpy as np
import OpenEXR

OUT_DIR = ("/private/tmp/claude-509/-Volumes-Flame-Archive-AI-Projects-claude-projects-"
           "flame-flame-pixel-expression/3cdbe482-5db9-40b4-997e-c0b7e1ab9faa/scratchpad")
W, H = 1920, 1080
SS = 4  # 4x4 subsamples for color + crypto coverage

# ---------------------------------------------------------------- cryptomatte hash
def murmur3_32(data: bytes, seed: int = 0) -> int:
    c1, c2 = 0xCC9E2D51, 0x1B873593
    h = seed
    n = len(data) // 4 * 4
    for i in range(0, n, 4):
        k = int.from_bytes(data[i:i + 4], "little")
        k = (k * c1) & 0xFFFFFFFF
        k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF
        k = (k * c2) & 0xFFFFFFFF
        h ^= k
        h = ((h << 13) | (h >> 19)) & 0xFFFFFFFF
        h = (h * 5 + 0xE6546B64) & 0xFFFFFFFF
    k = 0
    tail = data[n:]
    for i, b in enumerate(tail):
        k |= b << (8 * i)
    if tail:
        k = (k * c1) & 0xFFFFFFFF
        k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF
        k = (k * c2) & 0xFFFFFFFF
        h ^= k
    h ^= len(data)
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & 0xFFFFFFFF
    h ^= h >> 16
    return h

def hash_to_float32(h: int) -> float:
    # cryptomatte spec: keep the float finite/normal by nudging bad exponents
    exp = (h >> 23) & 0xFF
    if exp in (0, 255):
        h ^= 1 << 23
    return struct.unpack("<f", struct.pack("<I", h))[0]

OBJ_NAMES = {1: "ground", 2: "sphere_red", 3: "sphere_blue", 4: "sphere_glow"}
OBJ_HASH_F = {0: 0.0}
OBJ_HASH_HEX = {}
for oid, name in OBJ_NAMES.items():
    hint = murmur3_32(name.encode())
    OBJ_HASH_F[oid] = hash_to_float32(hint)
    OBJ_HASH_HEX[name] = f"{hint:08x}"

# ---------------------------------------------------------------- scene
CAM = np.array([0.0, 1.6, 6.5])
TARGET = np.array([0.0, 0.9, 0.0])
FWD = (TARGET - CAM) / np.linalg.norm(TARGET - CAM)
RIGHT = np.cross(FWD, [0.0, 1.0, 0.0]); RIGHT /= np.linalg.norm(RIGHT)
UP = np.cross(RIGHT, FWD)
HALF_W = np.tan(np.radians(45.0 / 2.0))
HALF_H = HALF_W * H / W

SPHERES = [  # id, center, radius
    (2, np.array([-1.6, 1.0, 0.0]), 1.0),
    (3, np.array([1.6, 1.0, 0.3]), 1.0),
    (4, np.array([0.0, 0.45, 1.9]), 0.45),
]
RED_VEL = np.array([0.55, 0.0, 0.0])          # world units / frame, sphere_red only
ALBEDO = {2: (0.62, 0.06, 0.05), 3: (0.05, 0.12, 0.55), 4: (0.02, 0.02, 0.02)}
CHECKER = ((0.30, 0.30, 0.30), (0.48, 0.46, 0.42))
EMISSION = {4: (5.6, 2.2, 0.5)}               # deliberately over-range
SUN_DIR = np.array([-0.45, 0.80, 0.35]); SUN_DIR /= np.linalg.norm(SUN_DIR)
SUN_COL = np.array([1.0, 0.96, 0.88]) * 2.4
AMBIENT = np.array([0.35, 0.42, 0.55]) * 0.45
GLOSS = {3: (120.0, 1.5), 1: (40.0, 0.12)}    # blinn exponent, strength

def trace(dirs):
    """dirs: (N,3) normalized. Returns id (N,), t (N,), P, Nrm."""
    n = dirs.shape[0]
    t_best = np.full(n, np.inf)
    oid = np.zeros(n, np.int32)
    # ground plane y=0
    dy = dirs[:, 1]
    tp = np.where(dy < -1e-8, -CAM[1] / dy, np.inf)
    hitp = tp < t_best
    t_best[hitp] = tp[hitp]; oid[hitp] = 1
    for sid, c, r in SPHERES:
        oc = CAM - c
        b = dirs @ oc
        disc = b * b - (oc @ oc - r * r)
        ok = disc > 0
        ts = np.where(ok, -b - np.sqrt(np.maximum(disc, 0.0)), np.inf)
        ts = np.where(ts > 1e-6, ts, np.inf)
        hit = ts < t_best
        t_best[hit] = ts[hit]; oid[hit] = sid
    P = CAM + dirs * t_best[:, None]
    Nrm = np.zeros_like(P)
    Nrm[oid == 1] = [0.0, 1.0, 0.0]
    for sid, c, r in SPHERES:
        m = oid == sid
        Nrm[m] = (P[m] - c) / r
    return oid, t_best, P, Nrm

def shade(oid, P, Nrm):
    """Returns albedo, diffuse, specular, emission, ao — each (N,3)."""
    P = np.where((oid > 0)[:, None], P, CAM[None, :])  # sky rays: keep the math finite
    n = oid.shape[0]
    alb = np.zeros((n, 3)); dif = np.zeros((n, 3))
    spc = np.zeros((n, 3)); emi = np.zeros((n, 3))
    for sid, col in ALBEDO.items():
        alb[oid == sid] = col
    g = oid == 1
    if g.any():
        chk = (np.floor(P[g, 0]) + np.floor(P[g, 2])).astype(np.int64) & 1
        alb[g] = np.where(chk[:, None] == 0, CHECKER[0], CHECKER[1])
    # sun shadow: any sphere between P and the sun
    lit = np.ones(n, bool)
    orig = P + Nrm * 1e-4
    for sid, c, r in SPHERES:
        oc = orig - c
        b = oc @ SUN_DIR
        disc = b * b - (np.einsum("ij,ij->i", oc, oc) - r * r)
        ts = -b - np.sqrt(np.maximum(disc, 0.0))
        lit &= ~((disc > 0) & (ts > 1e-4))
    # analytic-ish sphere AO
    occ = np.zeros(n)
    for sid, c, r in SPHERES:
        d = c - P
        dist2 = np.einsum("ij,ij->i", d, d)
        dist = np.sqrt(dist2)
        cosang = np.clip(np.einsum("ij,ij->i", d, Nrm) / np.maximum(dist, 1e-9), 0.0, 1.0)
        occ += np.where(oid == sid, 0.0, cosang * (r * r / np.maximum(dist2, 1e-9)) * 0.85)
    ao = np.clip(1.0 - occ, 0.0, 1.0)
    ndl = np.clip(Nrm @ SUN_DIR, 0.0, 1.0) * lit
    dif_dir = alb * (ndl[:, None] * SUN_COL)          # shadowed by rays; AO plays no part
    dif_ind = alb * AMBIENT[None, :]                  # UNOCCLUDED ambient — AO applied in comp
    dif = dif_dir + dif_ind * ao[:, None]             # baked variant (kept for compatibility)
    view = CAM - P
    view /= np.maximum(np.linalg.norm(view, axis=1, keepdims=True), 1e-9)
    hvec = view + SUN_DIR
    hvec /= np.maximum(np.linalg.norm(hvec, axis=1, keepdims=True), 1e-9)
    ndh = np.clip(np.einsum("ij,ij->i", Nrm, hvec), 0.0, 1.0)
    for sid, (ex, k) in GLOSS.items():
        m = oid == sid
        spc[m] = (ndh[m] ** ex * k * (ndl[m] > 0))[:, None] * SUN_COL
    for sid, col in EMISSION.items():
        emi[oid == sid] = col
    mask = (oid > 0)[:, None]
    return (alb * mask, dif * mask, dif_dir * mask, dif_ind * mask,
            spc * mask, emi * mask, ao[:, None].repeat(3, 1) * mask)

def sky(dirs):
    tgrad = np.clip(dirs[:, 1] * 2.5 + 0.3, 0.0, 1.0)[:, None]
    return (1 - tgrad) * np.array([0.045, 0.05, 0.06]) + tgrad * np.array([0.10, 0.14, 0.22])

def ray_dirs(xo, yo):
    xs = (np.arange(W) + xo) / W * 2.0 - 1.0
    ys = 1.0 - (np.arange(H) + yo) / H * 2.0
    xg, yg = np.meshgrid(xs, ys)
    d = (FWD[None, None] + xg[..., None] * HALF_W * RIGHT[None, None]
         + yg[..., None] * HALF_H * UP[None, None]).reshape(-1, 3)
    return d / np.linalg.norm(d, axis=1, keepdims=True)

def project_px(Pw):
    rel = Pw - CAM
    zf = rel @ FWD
    xn = (rel @ RIGHT) / (zf * HALF_W)
    yn = (rel @ UP) / (zf * HALF_H)
    return (xn + 1.0) * 0.5 * W, (yn + 1.0) * 0.5 * H   # y up, in pixels

# ---------------------------------------------------------------- color + crypto (16 subsamples)
acc = {k: np.zeros((H * W, 3)) for k in ("beauty", "albedo", "diffuse", "diffuse_direct",
                                          "diffuse_indirect", "specular", "emission", "ao")}
acc_a = np.zeros(H * W)
id_counts = np.zeros((H * W, 5))  # ids 0..4
for a in range(SS):
    for b in range(SS):
        dirs = ray_dirs((a + 0.5) / SS, (b + 0.5) / SS)
        oid, t, P, Nrm = trace(dirs)
        alb, dif, dif_dir, dif_ind, spc, emi, ao = shade(oid, P, Nrm)
        beauty = dif + spc + emi + sky(dirs) * (oid == 0)[:, None]
        acc["beauty"] += beauty; acc["albedo"] += alb; acc["diffuse"] += dif
        acc["diffuse_direct"] += dif_dir; acc["diffuse_indirect"] += dif_ind
        acc["specular"] += spc; acc["emission"] += emi; acc["ao"] += ao
        acc_a += oid > 0
        id_counts[np.arange(H * W), oid] += 1
ns = SS * SS
for k in acc:
    acc[k] /= ns
acc_a /= ns

order = np.argsort(-id_counts, axis=1, kind="stable")
hash_lut = np.array([OBJ_HASH_F[i] for i in range(5)], np.float32)
r0_id, r1_id = order[:, 0], order[:, 1]
r0_cov = id_counts[np.arange(H * W), r0_id] / ns
r1_cov = id_counts[np.arange(H * W), r1_id] / ns
r0_hash = hash_lut[r0_id] * (r0_cov > 0)
r1_hash = hash_lut[r1_id] * (r1_cov > 0)

# ---------------------------------------------------------------- data passes (center, unfiltered)
dirs = ray_dirs(0.5, 0.5)
oid_c, t_c, P_c, N_c = trace(dirs)
hit = oid_c > 0
depth = np.where(hit, (P_c - CAM) @ FWD, 1e6)
Pw = np.where(hit[:, None], P_c, 0.0)
Nw = np.where(hit[:, None], N_c, 0.0)
vel = np.zeros((H * W, 2))
mred = oid_c == 2
if mred.any():
    ux1, uy1 = project_px(P_c[mred])
    ux0, uy0 = project_px(P_c[mred] - RED_VEL)
    vel[mred, 0] = ux1 - ux0
    vel[mred, 1] = uy1 - uy0

# ---------------------------------------------------------------- write EXR
def ch(x):
    return np.ascontiguousarray(x.reshape(H, W).astype(np.float32))

channels = {
    "R": ch(acc["beauty"][:, 0]), "G": ch(acc["beauty"][:, 1]), "B": ch(acc["beauty"][:, 2]),
    "A": ch(acc_a),
}
for lay in ("albedo", "diffuse", "diffuse_direct", "diffuse_indirect", "specular", "emission"):
    for i, c in enumerate("RGB"):
        channels[f"{lay}.{c}"] = ch(acc[lay][:, i])
for i, c in enumerate("RGB"):
    channels[f"AO.{c}"] = ch(acc["ao"][:, i])
for i, c in enumerate("XYZ"):
    channels[f"N.{c}"] = ch(Nw[:, i])
    channels[f"P.{c}"] = ch(Pw[:, i])
channels["depth.Z"] = ch(depth)
channels["velocity.X"] = ch(vel[:, 0])
channels["velocity.Y"] = ch(vel[:, 1])
channels["CryptoObject00.R"] = ch(r0_hash)
channels["CryptoObject00.G"] = ch(r0_cov)
channels["CryptoObject00.B"] = ch(r1_hash)
channels["CryptoObject00.A"] = ch(r1_cov)

type_hash = f"{murmur3_32(b'CryptoObject'):08x}"[:7]
manifest = {name: OBJ_HASH_HEX[name] for name in OBJ_NAMES.values()}
header = {
    "compression": OpenEXR.ZIP_COMPRESSION,
    "type": OpenEXR.scanlineimage,
    f"cryptomatte/{type_hash}/name": "CryptoObject",
    f"cryptomatte/{type_hash}/hash": "MurmurHash3_32",
    f"cryptomatte/{type_hash}/conversion": "uint32_to_float32",
    f"cryptomatte/{type_hash}/manifest": json.dumps(manifest),
}
OpenEXR.File(header, channels).write(f"{OUT_DIR}/aov_demo_render.exr")

with open(f"{OUT_DIR}/aov_demo_manifest.txt", "w") as f:
    f.write("Cryptomatte object ids for aov_demo_render.exr (float32 hash -> `id` variable)\n\n")
    for oid in sorted(OBJ_NAMES):
        f.write(f"  {OBJ_NAMES[oid]:<12} hex {OBJ_HASH_HEX[OBJ_NAMES[oid]]}   "
                f"float32 id = {OBJ_HASH_F[oid]!r}\n")
    f.write("\nScene ground truth:\n")
    f.write("  camera at (0, 1.6, 6.5) looking at (0, 0.9, 0), 45 deg horizontal fov\n")
    f.write("  sphere_red   centre (-1.6, 1.0, 0.0) r 1.0, velocity +0.55 x/frame\n")
    f.write("  sphere_blue  centre (1.6, 1.0, 0.3) r 1.0, glossy\n")
    f.write("  sphere_glow  centre (0.0, 0.45, 1.9) r 0.45, emission (5.6, 2.2, 0.5)\n")
    f.write("  ground plane y=0, 1m checker; sky depth = 1e6\n")
    f.write("\nDiffuse split (AO-in-comp workflow):\n")
    f.write("  diffuse          = direct + indirect x AO baked in (legacy/compat layer)\n")
    f.write("  diffuse_direct   = sun x shadow rays -- AO plays no part\n")
    f.write("  diffuse_indirect = UNOCCLUDED ambient -- multiply by AO in comp\n")
    f.write("  exact beauty = diffuse_direct + diffuse_indirect*AO + specular + emission\n")
print("wrote aov_demo_render.exr +", len(channels), "channels")
print("ids:", {OBJ_NAMES[k]: repr(OBJ_HASH_F[k]) for k in OBJ_NAMES})
assert murmur3_32(b"hello") == 0x248BFA47, "murmur3 self-test failed"
for k in acc:
    assert np.isfinite(acc[k]).all(), f"NaN/inf in {k} pass"
print("murmur3 self-test OK; all color passes finite")
