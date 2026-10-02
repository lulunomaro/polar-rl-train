"""Closed-chain (相似连杆 / kite four-bar) rebuild of the STEP wheel-leg robot.

Structure per leg, taken from the SJTU reference model and confirmed against our own
B-rep joint axes:

    base
     ├─ rear1  THIGH   hinge @ hip   (ACTUATED - hip motor, chain to 一级腿链轮铝件)
     │    └─ rear2  SHANK  hinge @ knee          (passive)
     │         └─ wheel   hinge @ axle           (ACTUATED)
     │              ├─ link4  hinge @ P3         (二级腿连杆, passive)
     │              └─ spring1 hinge @ S1 -> spring2 slide
     └─ front1 CRANK   hinge @ hip   (ACTUATED - knee motor, chain to 二级腿链轮铝件)
          └─ link2 hinge @ P2 (等效前二级腿)
               └─ link3 hinge @ A  (等效后二级腿)

    connect(link3, thigh,  P1)   -> closes the deltoid four-bar  (hip-P2-A-P1)
    connect(link4, shank,  Q)    -> drives the knee from the crank
    connect(spring2, shank, S2)  -> the nitrogen gas spring

All pivot coordinates below are measured from the STEP B-rep (see scripts/leg_graph.py);
the four-bar closes exactly at the zero pose:
    |hip->P2| = |hip->P1| = 115.1 mm,  |P2->A| = |P1->A| = 137.0 mm
which is the doc's 0.1134 / 0.133 with similarity ratio 115.1/210.0 = 0.548.
"""
import collections, json, math, os, re, shutil
import numpy as np
import trimesh
import yaml

ROOT = r"D:/claude2/fangzhen"
FINE = os.path.join(ROOT, "cad/out/vehicle")
COARSE = os.path.join(ROOT, "cad/out/vehicle_coarse")
OUT = os.path.join(ROOT, "robot/out_cc")
OUT = os.environ.get("CC_OUT", OUT)   # build a variant without touching the working plant

# visual fidelity of the chassis mesh: FINE CAD facets, decimated once.
BASE_FROM_FINE = os.environ.get("CC_BASE_FINE", "1") == "1"
BASE_FACE_BUDGET = int(os.environ.get("CC_BASE_FACES", "10000000"))
# legs keep their coarse LOD untouched: quadric decimation shreds thin wall
# features and made the linkage look like scattered debris.
LEG_FROM_FINE = os.environ.get("CC_LEG_FINE", "0") == "1"

# --- motor profile -------------------------------------------------------------
# The plant v3..v10 were trained on copied the *reference* MJCF numbers (armature
# 0.035, forcerange +-54/+-5).  The datasheet-faithful profile instead uses the real
# motors that are in the CAD - see docs/MOTOR_PARAMS.md:
#   DM-J8009-2EC, 9:1  peak 40 N*m / rated 20 N*m, rotor inertia 1.95e-4 kg*m^2
#                      -> armature   = 1.95e-4*9^2   = 0.0158 kg*m^2
#                      -> no-load    335 rpm @48 V => 167 rpm @24 V = 17.5 rad/s
#   DM3519 + 15.8:1    current plateau 6.4188 N*m, no-load 55.3557 rad/s
#                      (user-confirmed hardware; derived from the DM datasheet)
# Friction follows the reference file: 1.5 N*m Coulomb on the crank, 0 on the thigh.
MOTOR_PROFILE = os.environ.get("CC_MOTOR", "dm8009").lower()
if MOTOR_PROFILE == "legacy54":
  LEG_ARMATURE, CRANK_FRICTION, THIGH_FRICTION = 0.035, 1.5, 1.5
  LEG_TORQUE, WHEEL_TORQUE = 54.0, 5.0
elif MOTOR_PROFILE == "dm8009":
  LEG_ARMATURE, CRANK_FRICTION, THIGH_FRICTION = 0.0158, 1.5, 0.0
  LEG_TORQUE, WHEEL_TORQUE = 40.0, 6.4188
else:
  raise SystemExit("unknown CC_MOTOR profile: " + MOTOR_PROFILE)
print("motor profile:", MOTOR_PROFILE, "armature", LEG_ARMATURE,
      "leg torque", LEG_TORQUE, "wheel torque", WHEEL_TORQUE)

# ------------------------------------------------------------------ appearance
# The STEP carries no colours, so every part used to be drawn in one flat grey:
# 2.6 M triangles of 2-3 mm sheet all the same tone reads as "debris" even when the
# model is complete.  Each functional group now gets its own material.
MATERIALS = {
    "m_frame":  "0.42 0.44 0.48 1",   # machined alu / carbon structure
    "m_armor":  "0.17 0.18 0.20 1",   # anodised armour plates
    "m_motor":  "0.09 0.09 0.11 1",   # DM-J8009 / DM3519 housings, slip rings
    "m_gimbal": "0.63 0.65 0.69 1",   # gimbal + launcher
    "m_elec":   "0.11 0.34 0.17 1",   # batteries, PCBs
    "m_leg":    "0.24 0.25 0.29 1",   # leg links, cranks, sprockets
    "m_spring": "0.72 0.13 0.10 1",   # nitrogen gas spring
    "m_rubber": "0.06 0.06 0.07 1",   # tyre
}
BASE_BUCKETS = [
    ("motor",  r"DM_8116|DM80|电机铝件|电机涨块|电机座|滑环|中心轴|拨盘电机|步进|舵机|卡簧"),
    ("armor",  r"装甲|防弹板|挡板|链轮保护"),
    ("gimbal", r"^0120|云台|[Pp]itch|[Yy][Aa][Ww]|弹仓|鹅颈|大测速|斜板|复活赛|枪管|雷达"),
    ("elec",   r"电池|超电|继电器|电管|电容|TOF|UWB|开发板|电脑|PCB|线束|30A|蚊香|转接|开关|模块"),
]
BASE_BUCKET_ORDER = ["frame", "armor", "motor", "gimbal", "elec"]
BASE_MAT = {b: "m_" + b for b in BASE_BUCKET_ORDER}
COL = lambda key: MATERIALS[key]
LEG_MAT = {"thigh": "m_leg", "shank": "m_leg", "crank": "m_leg", "link2": "m_leg",
           "link3": "m_leg", "link4": "m_leg", "spring1": "m_spring",
           "spring2": "m_spring", "wheel": "m_rubber"}

def bucket_of(s):
    txt = s["product"].strip() + "|" + s["path"]
    for name, pat in BASE_BUCKETS:
        if re.search(pat, txt):
            return name
    return "frame"

# ------------------------------------------------------------------ frame
spec = yaml.safe_load(open(os.path.join(ROOT, "robot/vehicle.spec.yaml"), encoding="utf-8"))
R = np.array(spec["frame"]["rot"]); A4 = np.eye(4)
A4[:3, :3] = R; A4[:3, 3] = -R @ np.array(spec["frame"]["origin_cad"], float)
man = json.load(open(os.path.join(FINE, "manifest.json"), encoding="utf-8"))
cman = json.load(open(os.path.join(COARSE, "manifest.json"), encoding="utf-8"))
CSUB = {(s["path"], round(s["volume_mm3"], 1)): s["obj"] for s in cman["solids"]}

# ------------------------------------------------------------------ measured pivots (mm, robot frame, LEFT leg)
HIP = np.array([0.0, 212.1]); KNEE = np.array([-200.7, 150.3]); AXLE = np.array([-0.8, 0.1])
P2 = np.array([109.7, 177.3])      # crank pin (on 二级腿曲柄)
P1 = np.array([-110.0, 178.2])     # thigh pin (on 一级腿 / 等效后二级腿)
APEX = np.array([-0.5, 95.9])      # 等效前 <-> 等效后
P3 = np.array([-151.3, 230.9])     # 等效后 third hole -> 二级腿连杆
Q = np.array([-242.0, 203.0])      # 二级腿连杆 <-> 二级腿 (shank)
S1 = np.array([0.6, 161.1])        # 弹簧推杆端铝件 on the thigh
S2 = np.array([-165.5, 115.5])     # 弹簧外壳端铝件 on the shank
Y_THIGH, Y_SHANK, Y_WHEEL = -223.85, -223.85, -270.25
for nm, p in (("hip->P2", P2 - HIP), ("hip->P1", P1 - HIP)):
    pass
print("four-bar closure check: |hip-P2|=%.1f |hip-P1|=%.1f |P2-apex|=%.1f |P1-apex|=%.1f"
      % (np.linalg.norm(P2 - HIP), np.linalg.norm(P1 - HIP),
         np.linalg.norm(P2 - APEX), np.linalg.norm(P1 - APEX)))
print("knee lever: |knee-Q|=%.1f  |P3-Q|=%.1f  spring length=%.1f"
      % (np.linalg.norm(KNEE - Q), np.linalg.norm(P3 - Q), np.linalg.norm(S1 - S2)))

# ------------------------------------------------------------------ part -> body
# (motors, slip ring, central shaft and the whole armour set are chassis-side: they are
#  bolted to the 髋腿加工件 on the robot side of the hip bearing, exactly as in the
#  SJTU reference where the thigh mass is only 0.383 kg)
BODY_RULES = [
    ("wheel",   [r"24\s+轮毂", r"包胶_2", r"24\s+1_1$", r"外圈铝件", r"行星架端盖",
                 r"双联行星齿", r"太阳齿加固", r"输入齿轮装配", r"id2", r"后轴承座"]),
    ("shank",   [r"24\s+二级腿$", r"二级腿锁盖", r"膝关节", r"连杆轴承座", r"30\.2-39",
                 r"8\s*16\s*4深沟球", r"弹簧外壳端铝件", r"电机座\(镜像\)", r"内8外16法兰"]),
    ("crank",   [r"二级腿曲柄", r"二级腿链轮"]),
    ("link2",   [r"等效前二级腿"]),
    ("link3",   [r"等效后二级腿"]),
    ("link4",   [r"二级腿连杆"]),
    ("spring1", [r"氮气弹簧推杆"]),
    ("spring2", [r"氮气弹簧外壳"]),
    ("thigh",   [r"24\s+一级腿", r"一级腿链轮", r"锥形轴", r"机械限位", r"限位安装销",
                 r"弹簧推杆端铝件", r"锁紧块", r"锥面螺母", r"47\.8"]),
]
BASE_SIDE = [r"DM_8116", r"DM80-V3", r"电机铝件", r"电机涨块", r"滑环", r"中心轴",
             r"装甲", r"防弹板", r"链轮保护"]

def body_of(path, product):
    p = product.strip()
    if not (path.startswith("整车总装/24    髋腿")
            or path.startswith("整车总装/Mirror24    髋腿")):
        return "base"
    for pat in BASE_SIDE:
        if re.search(pat, p):
            return "base"
    for body, pats in BODY_RULES:
        for pat in pats:
            if re.search(pat, p):
                return body
    return "base"

man_left = [s for s in man["solids"] if s["path"].startswith("整车总装/24    髋腿")]
man_right = [s for s in man["solids"] if s["path"].startswith("整车总装/Mirror24    髋腿")]
other = [s for s in man["solids"] if s not in man_left and s not in man_right]
groups = collections.defaultdict(list)
for s in other:
    groups["base"].append(s)
for side, lst in (("L", man_left), ("R", man_right)):
    for s in lst:
        b = body_of(s["path"], s["product"])
        groups[b if b != "base" else "base"].append((side, s))
print("\n== part -> body ==")
def vol_of(item):
    return item["volume_mm3"] if isinstance(item, dict) else item[1]["volume_mm3"]
def path_of(item):
    return item["path"] if isinstance(item, dict) else item[1]["path"]
for k, v in groups.items():
    print("  %-8s %4d solids  %8.1f cm3" % (k, len(v), sum(vol_of(s) for s in v) / 1000))
un = sorted({s[1]["product"].strip() for s in groups.get("base", [])
             if isinstance(s, tuple)})
print("  (leg parts kept chassis-side: %d distinct)" % len([u for u in un if u]))

# ---- audit: what actually landed on the MOVING leg bodies? ----
MOTOR_WORDS = ("电机", "DM_8116", "DM80", "链轮", "链条", "齿轮", "起步齿轮", "轴承",
               "滑环", "中心轴", "涨块", "轴系", "卡簧", "键")
print("\n== leg-body audit (motor / sprocket / chain / bearing parts on moving bodies) ==")
for body in [b for b in groups if b != "base"]:
    items = [i for i in groups.get(body, []) if isinstance(i, tuple)]
    if not items:
        continue
    names = sorted({i[1]["product"].strip() for i in items})
    bad = [n for n in names if any(w in n for w in MOTOR_WORDS)]
    print("  %-8s %3d solids, %3d distinct names, SUSPECT=%d" % (body, len(items), len(names), len(bad)))
    for n in bad[:14]:
        print("       ! ", n[:70])
    if not bad:
        for n in names[:6]:
            print("       . ", n[:70])


# ------------------------------------------------------------------ mass properties
def rho_of(text):
    for rule in spec["density_rules"]:
        if re.search(rule["match"], text, re.I):
            return float(rule["rho"])
    return float(spec["density_rules"][-1]["rho"])

def solids_of(body, side=None):
    out = []
    for item in groups.get(body, []):
        if isinstance(item, dict):
            if side is None:
                out.append(item)
        else:
            s_side, s = item
            if side is None or s_side == side:
                out.append(s)
    return out

def props(ss, anchor_fn):
    m_tot, sm, H = 0.0, np.zeros(3), np.zeros((3, 3))
    for s in ss:
        rho = rho_of(s["path"] + "|" + s["product"]) / 1e9
        dm = s["volume_mm3"] * rho
        Mw = A4 @ np.array(s["M"], float)
        Rb = Mw[:3, :3]
        c = Rb @ np.array(s["com_local"], float) + Mw[:3, 3]
        c = c - anchor_fn(c)
        Iw = Rb @ (np.array(s["inertia_local"], float) * rho) @ Rb.T
        H += Iw + dm * (c.dot(c) * np.eye(3) - np.outer(c, c))
        m_tot += dm; sm += dm * c
    com = sm / m_tot
    I = H - m_tot * (com.dot(com) * np.eye(3) - np.outer(com, com))
    w, V = np.linalg.eigh(I)
    return m_tot, com, V @ np.diag(w) @ V.T

def balance(I):
    w, V = np.linalg.eigh(np.asarray(I, float)); w = np.maximum(w, 1e-9)
    for _ in range(6):
        o = np.argsort(w); w = w[o]
        if w[2] <= w[0] + w[1]:
            break
        d = w[2] - w[0] - w[1]; w[0] += d / 2; w[1] += d / 1
    return V[:, o] @ np.diag(w) @ V[:, o].T

# body -> (hinge point in the PARENT frame, parent, axis)
TOPO = {
    "thigh":   dict(parent="base",  pin=HIP,   y=Y_THIGH, act="rear1"),
    "shank":   dict(parent="thigh", pin=KNEE,  y=Y_SHANK, act=None),
    "wheel":   dict(parent="shank", pin=AXLE,  y=Y_WHEEL, act="wheel"),
    "crank":   dict(parent="base",  pin=HIP,   y=Y_THIGH, act="front1"),
    "link2":   dict(parent="crank", pin=P2,    y=Y_THIGH, act=None),
    "link3":   dict(parent="link2", pin=APEX,  y=Y_THIGH, act=None),
    "link4":   dict(parent="link3", pin=P3,    y=Y_THIGH, act=None),
    "spring1": dict(parent="thigh", pin=S1,    y=Y_THIGH, act=None),
    "spring2": dict(parent="spring1", pin=S2,  y=Y_THIGH, act=None),
}
os.makedirs(os.path.join(OUT, "meshes"), exist_ok=True)
BODIES = {}
print("\n== body properties (CAD-derived, left leg) ==")
for body, cfg in TOPO.items():
    ss = solids_of(body, "L")
    if not ss:
        print("  %-8s EMPTY" % body); continue
    pin = cfg["pin"]; y = cfg["y"]
    anc = lambda c, pin=pin, y=y: np.array([pin[0], y, pin[1]])
    m, com, I = props(ss, anc)
    I = balance(I)
    BODIES[body] = dict(mass=m, com=com, inertia=I, n=len(ss))
    print("  %-8s m=%6.3f kg com(rel)=%s I=%s" % (body, m, np.round(com, 1),
                                             np.round(np.sort(np.linalg.eigvalsh(I)), 1)))
ss = solids_of("base")
# ---- FIX (2026-09-05): anchor_fn is "the point that becomes the new origin", so
# `lambda c: c` made every part's lever arm c - c = 0.  That (a) forced the chassis COM to
# exactly (0, 0, 0), which is the WHEEL-AXLE body origin, and (b) deleted the whole
# parallel-axis term of 593 parts, so the base inertia tensor only contained each part's
# own inertia about itself.  Consequences, all measured:
#   Izz 0.0435 kg*m^2 instead of ~0.9  -> a 20 kg / 0.71 m machine spins up ~20x too
#                                         easily, which is exactly the 小陀螺 skill;
#   Ixx 0.0323 instead of ~0.3         -> pitch/roll respond ~10x too fast after a jump;
#   COM at axle height                 -> no gravity pendulum about the axle at all, i.e.
#                                         the two-wheel balance the policy must learn was
#                                         free in simulation and is not free on hardware.
# The correct anchor is the body-frame origin, i.e. subtract zeros.
m, com, I = props(ss, lambda c: np.zeros(3))
BODIES["base"] = dict(mass=m, com=com, inertia=balance(I), n=len(ss))
print("  %-8s m=%6.3f kg com=%s" % ("base", m, np.round(com, 1)))
# --- guard: a chassis that fills a 0.714 x 0.392 x 0.229 m envelope cannot have a
# point-mass inertia.  Compare against the uniform box of the base_col collision box.
# props() works in mm / kg*mm^2 (that is what the STEP manifest stores); convert once.
_com = np.asarray(com, float)                       # mm, relative to the body origin
_eig = np.sort(np.linalg.eigvalsh(BODIES["base"]["inertia"])) / 1e6   # kg*m^2
# envelope of the chassis parts, straight from the same CAD solids
_ext = np.array([[s["aabb_min"][i], s["aabb_max"][i]] for i in range(3)], dtype=float) \
    if ss and "aabb_min" in ss[0] else None
if _ext is None:
    _ext = np.array([[-357.0, 357.0], [-196.0, 196.0], [54.0, 283.0]])   # base_col box
_d = _ext[:, 1] - _ext[:, 0]
# kg*mm^2 -> kg*m^2 is /1e6; the envelope stays in mm
_boxI = m / 1e6 / 12.0 * np.array([_d[1] ** 2 + _d[2] ** 2,
                                   _d[0] ** 2 + _d[2] ** 2,
                                   _d[0] ** 2 + _d[1] ** 2])
print("  base CAD envelope mm: x[%g,%g] y[%g,%g] z[%g,%g]"
      % (_ext[0, 0], _ext[0, 1], _ext[1, 0], _ext[1, 1], _ext[2, 0], _ext[2, 1]))
print("  base COM (%s) mm   I=%s kg*m^2   I/uniform-box %s"
      % (np.round(_com, 1), np.round(_eig, 4), np.round(_eig / _boxI, 2)))
assert np.linalg.norm(_com) < 600.0, "base COM left the machine: %s mm" % np.round(_com, 1)
assert (_eig > 0.10 * _boxI).all(), (
    "base inertia too small for its own envelope (%s vs box %s): the parallel-axis term "
    "is missing again -- this was the bug that made 小陀螺 20x too easy to spin"
    % (np.round(_eig, 4), np.round(_boxI, 4)))
tot = BODIES["base"]["mass"] + 2 * sum(b["mass"] for k, b in BODIES.items() if k != "base")
print("  raw CAD total = %.2f kg" % tot)
json.dump({k: dict(mass=round(v["mass"], 4), com_mm=np.round(v["com"], 2).tolist(),
                   inertia_kg_mm2=np.round(v["inertia"], 1).tolist(), n=v["n"])
           for k, v in BODIES.items()},
          open(os.path.join(OUT, "link_physics_cc.json"), "w"), indent=1)
print("wrote", os.path.join(OUT, "link_physics_cc.json"))


# ------------------------------------------------------------------ calibration
TARGET_TOTAL = 20.0          # SJTU note 3.5: 全车减重到 20 kg 以下
raw_total = BODIES["base"]["mass"] + 2 * sum(
    b["mass"] for k, b in BODIES.items() if k != "base")
K = TARGET_TOTAL / raw_total
for b in BODIES.values():
    b["mass"] *= K
    b["inertia"] *= K
print("\nmass calibration: raw %.2f kg -> %.2f kg (x%.4f)" % (raw_total, TARGET_TOTAL, K))
for k in ("base", "thigh", "shank", "wheel", "crank"):
    print("   %-7s %6.3f kg" % (k, BODIES[k]["mass"]))
leg_kg = sum(BODIES[k]["mass"] for k in TOPO)
print("   per leg = %.3f kg  (SJTU reference model: 1.57 kg)" % leg_kg)

# ------------------------------------------------------------------ meshes
def export_mesh(body, side, budget):
    ss = [i[1] for i in groups.get(body, []) if isinstance(i, tuple) and i[0] == side]
    parts = []
    tot = sum(s["ntris"] for s in ss) or 1
    for s in ss:
        obj = CSUB.get((s["path"], round(s["volume_mm3"], 1)), s["obj"])
        try:
            m = trimesh.load(os.path.join(COARSE if obj in os.listdir(
                os.path.join(COARSE, "meshes")) else FINE, "meshes", obj), process=False)
        except Exception:
            continue
        m.apply_transform(A4)
        parts.append(m)
    if not parts:
        return None
    mesh = trimesh.util.concatenate(parts)
    pin, y = TOPO[name_of(body)][0] if False else (None, None)
    return mesh

name_of = lambda b: b
ANCHOR = {}
for body, cfg in TOPO.items():
    ANCHOR[body] = np.array([cfg["pin"][0], cfg["y"], cfg["pin"][1]])
ANCHOR["base"] = np.zeros(3)

def write_mesh(body, side, budget=int(os.environ.get("CC_LEG_FACES", "10000000"))):
    ss = [i[1] for i in groups.get(body, []) if isinstance(i, tuple) and i[0] == side]
    parts = []
    for s in ss:
        # NOTE: CSUB maps (path, volume) -> the *coarse* manifest's file name, so it may
        # only ever be used to build a COARSE path.  The FINE mesh of a solid is its own
        # s["obj"]; mixing the two ids rendered ~700 chassis parts as the wrong part.
        obj = CSUB.get((s["path"], round(s["volume_mm3"], 1)), s["obj"])
        cand = [(os.path.join(COARSE, "meshes", obj)), os.path.join(FINE, "meshes", s["obj"])]
        if LEG_FROM_FINE:
            cand = cand[::-1]
        for f in cand:
            if os.path.exists(f):
                break
        try:
            me = trimesh.load(f, process=False)
        except Exception:
            continue
        VISLOG.append(dict(id=s["id"], solid_obj=s["obj"], used=os.path.basename(f),
                           _dir=os.path.basename(os.path.dirname(os.path.dirname(f))),
                           faces=len(me.faces), body=body, side=side))
        me.apply_transform(A4)
        parts.append(me)
    if not parts:
        return None
    mesh = trimesh.util.concatenate(parts)
    try:
        if len(mesh.faces) > max(400, budget):
            mesh = mesh.simplify_quadric_decimation(face_count=budget)
    except Exception:
        pass
    # centre the mesh on its own hinge, using the SIDE-specific lateral offset
    # (ANCHOR holds the left-leg y; the right leg must be mirrored, otherwise the
    # right-hand meshes end up 2*|y| = 448 mm away from their body)
    _pin, _y = TOPO[body]["pin"], TOPO[body]["y"]
    mesh.apply_translation(-np.array([_pin[0], (1.0 if side == "L" else -1.0) * _y, _pin[1]]))
    fn = "%s_%s.stl" % (body, side.lower())
    mesh.export(os.path.join(OUT, "meshes", fn))
    return fn

print("\n== meshes ==")
MESH = {}
VISLOG = []   # one row per CAD solid that reached a mesh file
for body in list(TOPO) + ["base"]:
    for side in ("L", "R"):
        if body == "base":
            continue
        f = write_mesh(body, side)
        if f:
            MESH[(body, side)] = f
    if body == "base":
        # ALL chassis-fixed solids, including the 66 leg-side parts that are bolted to the
        # frame: the 4x DM-J8009 hip motors, DM80-V3, slip rings, central shafts, sprocket
        # guards and the 16 大装甲板 armour plates (2640 cm3 / 461k triangles).  Dropping
        # them is what made the body look gutted and left the rotating leg sprockets as the
        # only motor-like geometry on screen.
        ss = [s if isinstance(s, dict) else s[1] for s in groups["base"]]
        parts = []
        _names = []
        _empty = []
        for s in ss:
            # the coarse LOD drops thin connectors (light bar, ammo-path plates, carbon
            # sheets) to zero facets, which is what made the chassis look "incomplete".
            # The visual mesh now comes from the FINE export, decimated once, gently.
            # CSUB's value is a COARSE file name -> only valid under COARSE/.
            obj = CSUB.get((s["path"], round(s["volume_mm3"], 1)), s["obj"])
            fine_f = os.path.join(FINE, "meshes", s["obj"])
            coarse_f = os.path.join(COARSE, "meshes", obj)
            use = fine_f if (BASE_FROM_FINE and os.path.exists(fine_f)) else (
                coarse_f if os.path.exists(coarse_f) else fine_f)
            try:
                me = trimesh.load(use, process=False)
            except Exception as e:
                print("    MISSING MESH for chassis solid %-40r (%s: %s)"
                      % (s["product"].strip()[:40], type(e).__name__, str(e)[:60]))
                continue
            if len(me.faces) == 0:
                _empty.append(s["product"].strip())
                continue
            VISLOG.append(dict(id=s["id"], solid_obj=s["obj"], used=os.path.basename(use),
                               _dir=os.path.basename(os.path.dirname(os.path.dirname(use))),
                               faces=len(me.faces), body="base", bucket=bucket_of(s)))
            me.apply_transform(A4)
            parts.append(me)
            _names.append((s["product"].strip(), bucket_of(s)))
        mesh = trimesh.util.concatenate(parts)
        # --- integrity report: which chassis-side solids made it into the mesh? ---
        import collections as _c
        _miss = getattr(write_mesh, "_missing", [])
        print("  base solids: %d listed, %d used, %d FAILED to load, %d EMPTY in coarse LOD"
              % (len(ss), len(parts), len(ss) - len(parts) - len(_empty), len(_empty)))
        for e in sorted(set(_empty))[:12]:
            print("     EMPTY:", e[:60])
        _z = sorted(((float(mm.bounds[0][2]), float(mm.bounds[1][2]), nm)
                     for mm, (nm, _) in zip(parts, _names)), key=lambda t: -t[1])
        print("  highest chassis parts (z mm):")
        for z0, z1, nm in _z[:8]:
            print("     z %6.1f .. %6.1f   %s" % (z0, z1, nm[:70]))
        try:
            if len(mesh.faces) > BASE_FACE_BUDGET:
                mesh = mesh.simplify_quadric_decimation(face_count=BASE_FACE_BUDGET)
            print("  base decimated -> %d faces" % len(mesh.faces))
        except Exception as e:
            print("  base decimation skipped:", type(e).__name__, str(e)[:90])
        # one merged + chunked mesh per visual bucket, so materials can differ
        for _stale in os.listdir(os.path.join(OUT, "meshes")):
            if _stale.startswith("base_") and _stale.endswith(".stl"):
                os.remove(os.path.join(OUT, "meshes", _stale))
        byb = collections.defaultdict(list)
        for mm, (nm, bk) in zip(parts, _names):
            byb[bk].append(mm)
        for bk in BASE_BUCKET_ORDER:
            if bk not in byb:
                continue
            bm = (byb[bk][0] if len(byb[bk]) == 1
                  else trimesh.util.concatenate(byb[bk]))
            bb = bm.bounds
            print("    bucket %-7s %3d solids  %8d faces  y[%6.1f %6.1f] z[%6.1f %6.1f]"
                  % (bk, len(byb[bk]), len(bm.faces), bb[0][1], bb[1][1], bb[0][2], bb[1][2]))
            for i in range(0, len(bm.faces), 150000):
                sub = bm.submesh([np.arange(i, min(i + 150000, len(bm.faces)))], append=True)
                fn = "base_%s_%02d.stl" % (bk, i // 150000)
                sub.export(os.path.join(OUT, "meshes", fn))
                MESH.setdefault("base", []).append((fn, bk))
        print("  base -> %s faces" % len(mesh.faces))
print("  leg meshes:", len(MESH) - 1, "files")

# --- visual completeness / identity guard -------------------------------------
# The chassis mesh is built from the FINE export, whose file names are per-solid ids.
# The COARSE export numbers its solids differently, so a COARSE name must never be
# resolved inside the FINE directory: that is how ~700 chassis parts once ended up
# being drawn as some other part (screws in place of armour plates), which is exactly
# the "parts flying around / gutted body" symptom.  Assert it cannot happen again.
_ids = [v["id"] for v in VISLOG]
assert len(_ids) == len(man["solids"]), \
    ("visual mesh has %d solids but the CAD has %d" % (len(_ids), len(man["solids"])))
assert len(set(_ids)) == len(_ids), "a CAD solid was emitted twice"
_fine_dir = os.path.join(FINE, "meshes")
_foreign = [v for v in VISLOG
            if v["_dir"] == "vehicle" and v["used"] != v["solid_obj"]]
assert not _foreign, "a FINE mesh was resolved through a COARSE id: %s" % _foreign[:3]
json.dump(VISLOG, open(os.path.join(OUT, "visual_manifest_cc.json"), "w"), indent=1)
print("  visual guard: %d/%d CAD solids accounted for, 0 foreign-id FINE loads"
      % (len(_ids), len(man["solids"])))


# ------------------------------------------------------------------ emit MJCF
SIDE_Y = {"L": 1.0, "R": -1.0}          # left leg sits at negative robot y in our frame
SIDE = {"L": "left", "R": "right"}
def f3(v):
    return " ".join("%.6g" % x for x in np.atleast_1d(v))

# per-body: parent, hinge (x,z), lateral y (left leg), collision primitive
BODY_DEF = {
    "thigh":   dict(parent="base",    pin=HIP,  y=Y_THIGH, col=("capsule", HIP, KNEE, 45.0)),
    "shank":   dict(parent="thigh",   pin=KNEE, y=Y_SHANK, col=("capsule", KNEE, AXLE, 32.0)),
    "wheel":   dict(parent="shank",   pin=AXLE, y=Y_WHEEL, col=("cylinder", AXLE, 73.0, 13.0)),
    "crank":   dict(parent="base",    pin=HIP,  y=Y_THIGH, col=("capsule", HIP, P2, 28.0)),
    "link2":   dict(parent="crank",   pin=P2,   y=Y_THIGH, col=("capsule", P2, APEX, 18.0)),
    "link3":   dict(parent="link2",   pin=APEX, y=Y_THIGH, col=("capsule", P1, P3, 18.0)),
    "link4":   dict(parent="link3",   pin=P3,   y=Y_THIGH, col=("capsule", P3, Q, 14.0)),
    "spring1": dict(parent="thigh",   pin=S1,   y=Y_THIGH, col=("capsule", S1, ((S1[0]+S2[0])/2, (S1[1]+S2[1])/2), 14.0)),
    "spring2": dict(parent="spring1", pin=S2,   y=Y_THIGH, col=("capsule", ((S1[0]+S2[0])/2, (S1[1]+S2[1])/2), S2, 17.0)),
}
# contract names used by wheelbipe_ros2_sim2sim: the two leg actuators are both
# hip-axis cranks (front1 = knee drive, rear1 = thigh drive)
ACT_OF = {"thigh": "rear1", "crank": "front1", "wheel": "wheel"}
BNAME = {"thigh": "rear1", "shank": "rear2", "wheel": "wheel", "crank": "front1",
         "link2": "front2", "link3": "front3", "link4": "front4",
         "spring1": "spring1", "spring2": "spring2"}
# Hip travel is intentionally UNLIMITED, as in V11 and as in the reference crank.
# hip_workspace.py shows the similar-link four-bar closes for all 130321 (thigh, crank)
# pairs over +-180 deg, so the linkage puts no boundary on the hip drives; a real stop has
# to come from the CAD limiter (机械限位 / 限位安装销) swept volume.
# Imposing the reference plant rear1 range=-3.14..1 was measured to BIND in normal
# operation and cost the policy 13% of both top speed (2.89 -> 2.50 m/s) and gyro rate
# (5.75 -> 5.01 rad/s), so it is reverted.  See docs/HOWTO.md section 18.
JOINT_PAR = {
    "rear1":  dict(rng=None, armature=LEG_ARMATURE, damping=0.0, frictionloss=THIGH_FRICTION),
    "front1": dict(rng=None, armature=LEG_ARMATURE, damping=0.0, frictionloss=CRANK_FRICTION),
    "wheel":  dict(rng=None, armature=0.001, damping=0.0, frictionloss=0.023),
}
# NOTE: the reference MJCF ranges are tied to *its* assembly pose (its qpos0 puts the
# thigh along -x and the crank almost straight back).  Our qpos0 is the CAD pose, which
# sits ~30..80 deg away in crank angle, so reusing those ranges jams front2 at its stop
# and freezes the whole leg.  The values below come from scripts/cc_workspace.py, which
# sweeps the closed chain with the analytic solver (scripts/leg2d.py).
# Solver-measured joint ranges (scripts/passive_range_solver.py): the base is welded,
# gravity off, the two hip-axis drives are held at the training PD gains and swept across
# the whole envelope the policy can command (thigh/crank +-0.80 rad, 441 poses, worst
# equality gap 0.027 mm) with the stops opened.  The previous numbers were taken in the
# ANALYTIC sign while an MJCF hinge stores the NEGATED value, so four of the five stops sat
# on the wrong side of the workspace and the closed chain jammed against its own limiter -
# front3 reached +1.072 rad against a +0.400 stop (38 deg of hard clamp).
# Each entry below brackets the measured motion with 0.15 rad of margin.
# ---- passive-joint ranges and the linkage end stop (2026-09-06, docs/HOWTO.md sec.38)
# The closed chain is a KITE (loop 1: hip-P2-APEX-P1) plus an exact PARALLELOGRAM (loop 2:
# P1-knee-Q-P3, |P1-knee|=|Q-P3|=94.89 mm and |knee-Q|=|P1-P3|=66.96 mm).  Because
# |hip->P1| = |hip->P2| = 115.1 mm, the whole internal configuration - and therefore every
# passive angle - depends ONLY on the relative hip angle delta = thigh - crank.  The knee is
# a monotone function of delta and delta has two singular ends:
#   delta_analytic -> +2.26 rad : loop-2 diagonal -> 161.8 mm  (parallelogram goes FLAT)
#   delta_analytic -> +2.54 rad : loop-1 diagonal -> 0 mm      (the kite FOLDS)
# Past either end the chain cannot close at all, so stops placed beyond them let the two hip
# motors drive the mechanism into an unsolvable equality constraint: the solver thrashes and
# the leg jumps to the mirror assembly branch.  Measured in the native-MuJoCo harness at
# t=0.20 s: rear1=+1.387, front1=-1.310 -> delta=-2.70, knee pinned on its -0.84 stop,
# equality gap 0.03 -> 0.17 mm, then the whole leg oscillated and the robot fell over.
# scripts/derive_passive_ranges2.py sweeps all 130321 (thigh, crank) poses on a 1 deg grid and
# keeps the singularity-safe set (loop-2 diagonal in [40,155] mm, loop-1 diagonal >= 30 mm):
#   rear2 [-0.843,+1.331]  front2 [-1.331,+0.843]  front3 [-0.134,+1.074]
#   front4 [-1.331,+0.843]  spring1 [-0.034,+0.217]  spring2 [-0.0202,+0.0607] m
#   delta_analytic [-2.601,+1.588]   (leg extension 46..418 mm, i.e. the whole 0.16-0.34 m
#   commanded height band stays inside)
# Every passive range below brackets that attainable set with 0.02 rad of margin, so a passive
# joint can never fight the equality constraint.  KITE_DELTA is the stop that actually bounds
# the mechanism and it is applied to the ACTUATED coordinates (q_rear1 - q_front1), where the
# solver can honour it directly instead of resolving it through the closed loop.
KITE_DELTA = (-1.588, 2.601)      # MJCF q_rear1 - q_front1, rad  ( = -delta_analytic )
# The margin has to clear mjlab soft_joint_pos_limit_factor = 0.95 (entity.py:706), which
# shrinks every range by 5% for the dof_pos_limits reward.  With a 0.02 rad bracket the
# reward fired on LEGAL poses (rear2 attainable +1.331 vs soft limit 1.296), i.e. the policy
# was penalised for using its own workspace.  0.08 rad keeps the soft band outside.
PASSIVE_RNG = {"shank":   (-0.923, 1.411),   # rear2  knee
               "link2":   (-1.411, 0.923),   # front2 coupler
               "link3":   (-0.214, 1.154),   # front3 deltoid plate
               "link4":   (-1.411, 0.923),   # front4 knee-drive link
               "spring1": (-0.114, 0.297)}   # gas-spring pivot
SPRING_SLIDE = (-0.030, 0.085)      # m of stroke about the CAD installed length
                                    # (analytic full-workspace stroke -0.020..+0.076 m)
SPRING_K, SPRING_C, SPRING_FRIC = 6000.0, 150.0, 15.0
SPRING_PRELOAD = 350.0            # N of thrust at the CAD installed length

def anchor(body, side):
    d = BODY_DEF[body]
    return np.array([d["pin"][0], SIDE_Y[side] * d["y"], d["pin"][1]])
def anchor_parent(body, side):
    par = BODY_DEF[body]["parent"]
    return np.zeros(3) if par == "base" else anchor(par, side)
def to3(pt, y):
    return np.array([pt[0], y, pt[1]])

out = ['<mujoco model="rm_vehicle_cc">',
       '  <compiler angle="radian" meshdir="meshes/" autolimits="true" balanceinertia="true" '
       'inertiafromgeom="false"/>',
       '  <option timestep="0.001" iterations="100" ls_iterations="50" integrator="Euler" '
       'solver="Newton" tolerance="1e-8"/>',
       '  <default><geom condim="3" friction="1.2 0.01 0.001" margin="0"/>',
       '    <default class="motor"><joint damping="0.0" frictionloss="%g" '
       'armature="%g"/></default></default>' % (CRANK_FRICTION, LEG_ARMATURE),
       '  <asset>']
for f, _bk in MESH.get("base", []):
    out.append('    <mesh name="%s" file="%s" scale="0.001 0.001 0.001"/>' % (f[:-4], f))
for key, fn in sorted(((k, v) for k, v in MESH.items() if k != "base"), key=lambda kv: str(kv[0])):
    body, side = key
    out.append('    <mesh name="%s_%s" file="%s" scale="0.001 0.001 0.001"/>'
               % (BNAME[body], side.lower(), fn))
out.append('  </asset>')
out.append('  <worldbody>')
out.append('    <body name="base_link" pos="0 0 0">')
out.append('      <freejoint name="floating_base"/>')
out.append('      <site name="imu" pos="0 0 0.3" size="0.01"/>')
b = BODIES["base"]; Ib = b["inertia"] / 1e6
out.append('      <inertial pos="%s" mass="%.4f" fullinertia="%s"/>'
           % (f3(b["com"] / 1000.0), b["mass"],
              f3([Ib[0, 0], Ib[1, 1], Ib[2, 2], Ib[0, 1], Ib[0, 2], Ib[1, 2]])))
for f, _bk in MESH.get("base", []):
    out.append('      <geom type="mesh" contype="0" conaffinity="0" group="2" density="0" '
               'mesh="%s" rgba="%s"/>' % (f[:-4], MATERIALS[BASE_MAT[_bk]]))
out.append('      <geom name="base_col" type="box" size="0.357 0.196 0.1145" '
           'pos="0 0 0.1685" contype="0" conaffinity="1" group="3" density="0" '
           'rgba="0 0.5 0.1 0.12"/>')

def emit(body, side, depth):
    d = BODY_DEF[body]; bb = BODIES[body]
    pad = "  " * depth
    nm = "%s_%s" % (SIDE[side], BNAME[body])
    rel = (anchor(body, side) - anchor_parent(body, side)) / 1000.0
    out.append('%s<body name="%s" pos="%s">' % (pad, nm, f3(rel)))
    jn = ACT_OF.get(body)
    if jn:
        jp = JOINT_PAR[jn]
        rng = ' range="%s"' % f3(jp["rng"]) if jp["rng"] else ""
        out.append('%s  <joint name="%s_joint" type="hinge" pos="0 0 0" axis="0 1 0"%s '
                   'class="motor" armature="%g" damping="%g" frictionloss="%g"/>'
                   % (pad, nm, rng, jp["armature"], jp["damping"], jp["frictionloss"]))
    elif body == "spring2":
        ax = np.array([S2[0] - S1[0], 0.0, S2[1] - S1[1]])
        ax = ax / np.linalg.norm(ax)
        out.append('%s  <joint name="%s_joint" type="slide" pos="0 0 0" axis="%s" '
                   'range="%s" stiffness="%g" springref="%g" damping="%g" '
                   'frictionloss="%g" armature="0.01"/>'
                   % (pad, nm, f3(ax), f3(SPRING_SLIDE), SPRING_K, SPRING_PRELOAD / SPRING_K,
                      SPRING_C, SPRING_FRIC))
    else:
        rng = PASSIVE_RNG.get(body)
        lim = (' range="%s"' % f3(rng)) if rng else ""
        out.append('%s  <joint name="%s_joint" type="hinge" pos="0 0 0" axis="0 1 0" '
                   '%s damping="0.05" armature="0.01" frictionloss="0.2"/>'
                   % (pad, nm, lim))
    I = bb["inertia"] / 1e6
    out.append('%s  <inertial pos="%s" mass="%.4f" fullinertia="%s"/>'
               % (pad, f3(bb["com"] / 1000.0), bb["mass"],
                  f3([I[0, 0], I[1, 1], I[2, 2], I[0, 1], I[0, 2], I[1, 2]])))
    if (body, side) in MESH:
        out.append('%s  <geom type="mesh" contype="0" conaffinity="0" group="2" density="0" '
                   'mesh="%s_%s" rgba="%s"/>'
                   % (pad, BNAME[body], side.lower(), MATERIALS[LEG_MAT[body]]))
    y = anchor(body, side)[1]
    c = d["col"]
    if c[0] == "capsule":
        a0 = (to3(c[1], y) - anchor(body, side)) / 1000.0
        a1 = (to3(c[2], y) - anchor(body, side)) / 1000.0
        out.append('%s  <geom name="%s_col" type="capsule" size="%g" fromto="%s %s" '
                   'contype="0" conaffinity="1" group="3" density="0" '
                   'rgba="0 0.5 0.1 0.12"/>' % (pad, nm, c[3] / 1000.0, f3(a0), f3(a1)))
    else:
        a0 = (to3(c[1], y) - anchor(body, side)) / 1000.0
        out.append('%s  <geom name="%s_col" type="cylinder" size="%g %g" pos="%s" '
                   'quat="0.5 -0.5 0.5 0.5" condim="6" priority="1" contype="0" '
                   'conaffinity="1" group="3" density="0" rgba="0 0.5 0.1 0.12"/>'
                   % (pad, nm, c[2] / 1000.0, c[3] / 1000.0, f3(a0)))
    for child, cd in BODY_DEF.items():
        if cd["parent"] == body:
            emit(child, side, depth + 1)
    out.append(pad + "</body>")

for side in ("L", "R"):
    for top in ("thigh", "crank"):
        emit(top, side, 3)
out.append('    </body>')
out.append('  </worldbody>')

out.append('  <equality>')
for side in ("L", "R"):
    s = SIDE[side]
    def rel_pt(body, pt):
        y = anchor(body, side)[1]
        return (to3(pt, y) - anchor(body, side)) / 1000.0
    for b1, b2, pt, who in ((s + "_front3", s + "_rear1", P1, "link3"),
                            (s + "_front4", s + "_rear2", Q, "link4"),
                            (s + "_spring2", s + "_rear2", S2, "spring2")):
        out.append('    <connect body1="%s" body2="%s" anchor="%s" solref="0.002 1" '
                   'solimp="0.99 0.999 1e-05 0.5 2"/>' % (b1, b2, f3(rel_pt(who, pt))))
out.append('  </equality>')

# ---- linkage end stop ---------------------------------------------------------
# A fixed tendon on (q_rear1 - q_front1) bounds the relative hip angle, which is the ONE
# coordinate that decides whether the closed chain can be assembled at all (see PASSIVE_RNG
# above).  Applied to the actuated pair, so the solver stops the drives instead of trying to
# resolve an impossible equality constraint through the loop.  MuJoCo-warp implements tendon
# limits too (_src/constraint.py: _limit_tendon), so training and deployment agree.
out.append('  <tendon>')
for side in ('left', 'right'):
    out.append('    <fixed name="%s_kite_delta" range="%s"'
               ' solreflimit="0.002 1">'
               % (side, f3(KITE_DELTA)))
    out.append('      <joint joint="%s_rear1_joint" coef="1"/>' % side)
    out.append('      <joint joint="%s_front1_joint" coef="-1"/>' % side)
    out.append('    </fixed>')
out.append('  </tendon>')
out.append('  <actuator>')
for side in ("left", "right"):
    for jn in ("front1", "rear1"):
        out.append('    <motor name="%s_%s_ctrl" joint="%s_%s_joint" gear="1" '
                   'forcerange="-%g %g" ctrlrange="-%g %g"/>'
                   % (side, jn, side, jn, LEG_TORQUE, LEG_TORQUE, LEG_TORQUE, LEG_TORQUE))
    out.append('    <motor name="%s_wheel_ctrl" joint="%s_wheel_joint" gear="1" '
               'forcerange="-%g %g" ctrlrange="-%g %g"/>'
               % (side, side, WHEEL_TORQUE, WHEEL_TORQUE, WHEEL_TORQUE, WHEEL_TORQUE))
out.append('  </actuator>')
out.append('  <sensor>')
out.append('    <framequat name="imu" objtype="site" objname="imu"/>')
out.append('    <gyro name="gyro" site="imu"/>')
out.append('    <accelerometer name="accelerometer" site="imu"/>')
out.append('  </sensor>')
out.append('</mujoco>')
open(os.path.join(OUT, "rm_vehicle_cc.xml"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\nwrote rm_vehicle_cc.xml (%d lines)" % len(out))
sc = ['<?xml version="1.0"?>', '<mujoco model="rm_vehicle_cc scene">',
      '  <include file="rm_vehicle_cc.xml"/>',
      # MuJoCo fog defaults to start=0.7 m / end=7 m, which veils a 1.5 m product shot
      # in flat grey and makes a solid machine look translucent.  Push it far out.
      '  <visual><global offwidth="1600" offheight="900"/>',
      '    <map znear="0.02" fogstart="25" fogend="80"/>',
      '    <headlight ambient="0.38 0.38 0.40" diffuse="0.45 0.45 0.45" specular="0.2 0.2 0.2"/></visual>',
      '  <asset><texture type="skybox" builtin="gradient" rgb1="0.55 0.6 0.68" '
      'rgb2="0.25 0.28 0.33" width="256" height="256"/>',
      '    <texture type="2d" name="grid" builtin="checker" rgb1="0.42 0.45 0.5" '
      'rgb2="0.62 0.65 0.7" width="512" height="512"/>',
      '    <material name="floor" texture="grid" texrepeat="8 8" reflectance="0.0"/></asset>',
      # three-point rig: without it 2.6 M triangles of same-tone sheet metal reads as noise
      '  <worldbody><light name="key" pos="1.8 -2.0 2.6" dir="-0.45 0.5 -0.8" '
      'diffuse="1 0.98 0.95" specular="0.4 0.4 0.4" cutoff="55" exponent="15"/>',
      '    <light name="fill" pos="-2.2 1.6 1.4" dir="0.6 -0.45 -0.4" '
      'diffuse="0.42 0.47 0.56" specular="0.08 0.08 0.08" cutoff="70" exponent="20"/>',
      '    <light name="rim" pos="-0.5 -2.6 1.0" dir="0.12 0.62 -0.3" '
      'diffuse="0.5 0.55 0.66" cutoff="60" exponent="20"/>',
      '    <geom name="floor" type="plane" size="8 8 0.05" material="floor" contype="1" '
      'conaffinity="255" friction="1.6 0.01 0.001" rgba="0.55 0.55 0.58 1"/>',
       '    <camera name="side" pos="0 -1.15 0.10" xyaxes="1 0 0 0 0 1"/>',
       '    <camera name="front" pos="1.9 -1.3 0.5" xyaxes="0.6 0.8 0 -0.3 0.25 0.95"/>',
      '  </worldbody>',
      '  <keyframe><key name="stand" qpos="0 0 0.075 1 0 0 0 ' +
      " ".join(["0"] * 18) + '"/></keyframe>', '</mujoco>']
open(os.path.join(OUT, "scene_cc.xml"), "w", encoding="utf-8").write("\n".join(sc) + "\n")
print("wrote scene_cc.xml")
