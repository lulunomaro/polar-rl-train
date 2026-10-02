"""Build a MuJoCo MJCF robot description from an extracted STEP manifest + a spec.

Fixes over v1
  * manifest OBJ meshes are already baked into the STEP world frame -> only the
    CAD->robot frame matrix is applied (v1 applied the solid transform twice, which
    inflated every bounding box by ~4x).
  * OCCT ``GProp_GProps.MatrixOfInertia`` is already taken about the solid centre of
    mass, so the parallel-axis term must not be subtracted again (v1 did, which
    produced non-physical inertia -> "A + B >= C" failures).
  * every joint sits at the origin of its child body, so ``<joint pos="0 0 0">``.
  * fullinertia is converted kg*mm^2 -> kg*m^2, inertial pos mm -> m.
  * collisions are explicit primitives from the spec (box / capsule / cylinder) and
    self-collision between non-adjacent bodies is suppressed with contype bits.
  * visual meshes are decimated twice (per solid, then per link) and split so that no
    STL exceeds MuJoCo's 200k-triangle STL reader limit.

Usage: python build_robot.py <spec.yaml> <out_dir>
"""
import argparse, collections, json, os, re, time
import numpy as np
import yaml
import trimesh

ap = argparse.ArgumentParser()
ap.add_argument("spec")
ap.add_argument("outdir")
ap.add_argument("--scale", type=float, default=1.0, help="extra visual decimation scale")
ap.add_argument("--no-mesh", action="store_true",
                help="reuse the STLs already in <outdir>/meshes (XML only)")
ap.add_argument("--visual-manifest", default="",
                help="manifest whose (coarse) OBJs are used for the visual meshes")
args = ap.parse_args()

spec = yaml.safe_load(open(args.spec, encoding="utf-8"))
mdir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(args.spec)),
                                     os.path.dirname(spec["manifest"])))
man = json.load(open(os.path.join(mdir, os.path.basename(spec["manifest"])), encoding="utf-8"))
S = man["solids"]
os.makedirs(os.path.join(args.outdir, "meshes"), exist_ok=True)

# ------------------------------------------------------------------ CAD(mm) -> robot(mm)
R = np.array(spec["frame"]["rot"], dtype=float)
assert np.allclose(R @ R.T, np.eye(3)), "frame.rot must be orthonormal"
A = np.eye(4)
A[:3, :3] = R
A[:3, 3] = -R @ np.array(spec["frame"]["origin_cad"], dtype=float)


def rho_of(text):
    for rule in spec["density_rules"]:
        if re.search(rule["match"], text, re.I):
            return float(rule["rho"])
    return float(spec["density_rules"][-1]["rho"])


def link_of(path):
    for lk in spec["links"]:
        if lk.get("all") and not all(re.search(p, path) for p in lk["all"]):
            continue
        if lk.get("any") and not any(re.search(p, path) for p in lk["any"]):
            continue
        if lk.get("not") and any(re.search(p, path) for p in lk["not"]):
            continue
        return lk["name"]
    return None


sel = collections.defaultdict(list)
for s in S:
    sel[link_of(s["path"])].append(s)
print("== link assignment ==")
for lk in spec["links"]:
    print("  %-10s %5d solids  %8.1f cm3" % (lk["name"], len(sel[lk["name"]]),
                                             sum(s["volume_mm3"] for s in sel[lk["name"]]) / 1000))
print("  %-10s %5d" % ("<unmatched>", len(S) - sum(len(v) for v in sel.values())))


# ------------------------------------------------------------------ mass properties
def link_physics(ss, anchor):
    """Exact mass / COM / inertia of a set of solids, about the link COM, robot axes."""
    m_tot, sm, H = 0.0, np.zeros(3), np.zeros((3, 3))
    for s in ss:
        rho = rho_of(s["path"] + "|" + s["product"]) / 1e9      # kg/mm^3
        dm = s["volume_mm3"] * rho
        Mw = A @ np.array(s["M"], dtype=float)
        Rb = Mw[:3, :3]
        c = Rb @ np.array(s["com_local"], dtype=float) + Mw[:3, 3]
        # inertia_local is already about the solid COM, expressed in solid axes
        Iw = Rb @ (np.array(s["inertia_local"], dtype=float) * rho) @ Rb.T
        H += Iw + dm * (c.dot(c) * np.eye(3) - np.outer(c, c))
        m_tot += dm
        sm += dm * c
    com = sm / m_tot
    I = H - m_tot * (com.dot(com) * np.eye(3) - np.outer(com, com))
    return m_tot, com, I


def balance(I):
    """Project a symmetric tensor onto the set of physically valid inertia tensors."""
    w, V = np.linalg.eigh(np.asarray(I, dtype=float))
    w = np.maximum(w, 1e-9)
    for _ in range(4):
        s = np.argsort(w)
        w = w[s]
        if w[2] <= w[0] + w[1]:
            break
        d = w[2] - w[0] - w[1]
        w[0] += d / 2
        w[1] += d / 2
    return V[:, s] @ np.diag(w) @ V[:, s].T, w[s]


# ------------------------------------------------------------------ meshes
STL_CAP = 150000


def decimate_to(mesh, target, passes=6):
    """fast_simplification clamps one pass to ~10x reduction, so iterate."""
    for _ in range(passes):
        if len(mesh.faces) <= target:
            break
        want = max(target, len(mesh.faces) // 6)
        try:
            n = mesh.simplify_quadric_decimation(face_count=want)
        except Exception:
            break
        if len(n.faces) >= len(mesh.faces):
            break
        mesh = n
    return mesh


VSUB = {}
if args.visual_manifest:
    cman = json.load(open(args.visual_manifest, encoding="utf-8"))
    cdir = os.path.dirname(os.path.abspath(args.visual_manifest))
    for s in cman["solids"]:
        VSUB[(s["path"], round(s["volume_mm3"], 1))] = s["obj"]
    print("visual override: %d coarse solids from %s" % (len(VSUB), cdir))


def link_mesh(ss, anchor, target):
    t0 = time.time()
    total = max(1, sum(s["ntris"] for s in ss))
    parts = []
    for s in ss:
        obj = VSUB.get((s["path"], round(s["volume_mm3"], 1)), s["obj"])
        me = trimesh.load(os.path.join(cdir if VSUB else mdir, "meshes", obj), process=False)
        me.apply_transform(A)
        me.apply_translation(-anchor)
        if target:
            budget = max(16, int(len(me.faces) * target / total))
            if len(me.faces) > budget:
                me = decimate_to(me, budget, passes=4)
        parts.append(me)
    mesh = trimesh.util.concatenate(parts)
    if target:
        mesh = decimate_to(mesh, target)
    mesh.merge_vertices()
    mesh.remove_unreferenced_vertices()
    print("    mesh %d -> %d faces (%.1fs)" % (total, len(mesh.faces), time.time() - t0))
    chunks = []
    for cur in range(0, len(mesh.faces), STL_CAP):
        chunks.append(mesh.submesh([np.arange(cur, min(cur + STL_CAP, len(mesh.faces)))],
                                   append=True))
    return chunks


# ------------------------------------------------------------------ per link build
mesh_index, mesh_faces = {}, {}
idx_path = os.path.join(args.outdir, "mesh_index.json")
if os.path.exists(idx_path):
    jj = json.load(open(idx_path, encoding="utf-8"))
    mesh_index = {k: v["files"] for k, v in jj.items()}
    mesh_faces = {k: v["nfaces"] for k, v in jj.items()}

info = collections.OrderedDict()
print("== link physics ==")
for lk in spec["links"]:
    name = lk["name"]
    ss = sel[name]
    if not ss:
        continue
    anchor = np.array(lk["anchor"], dtype=float)
    mass, com, I = link_physics(ss, anchor)
    if lk.get("mass_override"):
        I = I * (float(lk["mass_override"]) / mass)
        mass = float(lk["mass_override"])
    I, w = balance(I)
    nfaces = 0
    if args.no_mesh:
        files = mesh_index.get(name)
        assert files, "no cached mesh for %s (run without --no-mesh first)" % name
        nfaces = int(mesh_faces.get(name, 0))
    else:
        chunks = link_mesh(ss, anchor, int(lk.get("visual_faces", 0) * args.scale))
        files = []
        for i, mm in enumerate(chunks):
            fn = "%s.stl" % name if len(chunks) == 1 else "%s_%02d.stl" % (name, i)
            mm.export(os.path.join(args.outdir, "meshes", fn))
            files.append(fn)
            nfaces += len(mm.faces)
        mesh_index[name] = list(files)
        mesh_faces[name] = nfaces
    geoms = []
    cg = lk.get("collision", [])
    if isinstance(cg, dict):
        cg = [cg]
    for g in cg:
        g = dict(g)
        if g["type"] == "box":
            lo, hi = np.array(g["min"], float), np.array(g["max"], float)
            geoms.append(dict(type="box", size=((hi - lo) / 2000.0).tolist(),
                              pos=((hi + lo) / 2000.0).tolist(), quat=[1, 0, 0, 0]))
        elif g["type"] == "capsule":
            p0, p1 = np.array(g["from"], float), np.array(g["to"], float)
            geoms.append(dict(type="capsule", radius=float(g["radius"]),
                              p0=p0.tolist(), p1=p1.tolist()))
        elif g["type"] == "cylinder":
            ax = np.array(g.get("axis", [0, 1, 0]), float)
            ax = ax / np.linalg.norm(ax)
            q = trimesh.transformations.quaternion_from_matrix(
                trimesh.geometry.align_vectors([0, 0, 1], ax))
            geoms.append(dict(type="cylinder", size=[g["radius"] / 1000.0, g["halflen"] / 1000.0],
                              pos=(np.array(g["center"], float) / 1000.0).tolist(),
                              quat=[float(x) for x in q]))
    info[name] = dict(n=len(ss), mass=mass, com=com, inertia=I, eig=w, geoms=geoms,
                      mesh=files, nfaces=nfaces, spec=lk)
    print("  %-10s n=%-4d m=%7.3f kg  com=%s  I=%s faces=%d" %
          (name, len(ss), mass, np.round(com / 1000.0, 4), np.round(w / 1e6, 5), nfaces))

if not args.no_mesh:
    json.dump(mesh_index and {k: dict(files=v, nfaces=mesh_faces[k])
                              for k, v in mesh_index.items()},
              open(idx_path, "w"), indent=1)
    print("wrote", idx_path)

raw_total = sum(v["mass"] for v in info.values())
target_total = spec.get("mass_target_total")
if target_total:
    fixed = sum(float(l["mass_override"]) for l in spec["links"] if l.get("mass_override"))
    free_names = [n for n, v in info.items() if not v["spec"].get("mass_override")]
    free_now = sum(info[n]["mass"] for n in free_names)
    need = float(target_total) - fixed
    k = need / free_now
    print("mass calibration: fixed %.2f kg, free %.2f kg -> %.2f kg (x%.3f)"
          % (fixed, free_now, need, k))
    for n in free_names:
        info[n]["mass"] *= k
        info[n]["inertia"] *= k

if not args.no_mesh:
    json.dump({k: dict(files=v, nfaces=mesh_faces[k]) for k, v in mesh_index.items()},
              open(idx_path, "w"), indent=1)
    print("wrote", idx_path)

raw_total = sum(v["mass"] for v in info.values())
print("TOTAL MASS %.3f kg" % raw_total)

json.dump({k: dict(mass=round(v["mass"], 4), com_mm=[round(x, 2) for x in v["com"]],
                   inertia_kg_m2=[[round(x, 6) for x in r] for r in v["inertia"] / 1e6],
                   eig=[round(x, 6) for x in v["eig"] / 1e6], n=v["n"],
                   mesh=v["mesh"], nfaces=v["nfaces"])
           for k, v in info.items()},
          open(os.path.join(args.outdir, "link_physics.json"), "w"), indent=1)


def f3(v):
    return " ".join("%.6g" % x for x in np.atleast_1d(v))


# ------------------------------------------------------------------ kinematic tree
children = collections.defaultdict(list)
jinfo = {}
for j in spec["joints"]:
    children[j["parent"]].append(j["child"])
    jinfo[j["child"]] = j

order = [lk["name"] for lk in spec["links"] if lk["name"] in info]
roots = [n for n in order if n not in jinfo]
assert len(roots) == 1, roots
root = roots[0]
CT = {"base": 16, "thigh": 32, "shank": 64, "wheel": 128}


def emit_body(name, depth):
    v = info[name]
    lk = v["spec"]
    j = jinfo.get(name)
    pad = "  " * depth
    anchor = np.array(lk["anchor"], float) / 1000.0
    if j is None:
        out.append('%s<body name="%s" pos="%s">' % (pad, name, f3(anchor)))
        out.append('%s  <freejoint name="root"/>' % pad)
        out.append('%s  <site name="imu" size="0.01" group="5"/>' % pad)
    else:
        pa = np.array(info[j["parent"]]["spec"]["anchor"], float) / 1000.0
        out.append('%s<body name="%s" pos="%s">' % (pad, name, f3(anchor - pa)))
        rng = j.get("range")
        extra = ' range="%s"' % f3(rng) if rng else ""
        out.append('%s  <joint name="%s" type="%s" pos="0 0 0" axis="%s"%s '
                   'damping="%g" armature="%g" frictionloss="%g" actuatorfrcrange="%g %g"/>'
                   % (pad, j["name"], j.get("type", "hinge"), f3(j["axis"]), extra,
                      j.get("damping", 0.0), j.get("armature", 0.0),
                      j.get("frictionloss", 0.0), -j["effort"], j["effort"]))
    com = v["com"] / 1000.0 - anchor
    I = v["inertia"] / 1e6
    out.append('%s  <inertial pos="%s" mass="%.4f" fullinertia="%s"/>'
               % (pad, f3(com), v["mass"],
                  f3([I[0, 0], I[1, 1], I[2, 2], I[0, 1], I[0, 2], I[1, 2]])))
    rgba = " ".join("%.3f" % x for x in lk.get("rgba", [.7, .7, .75, 1]))
    for fn in v["mesh"]:
        out.append('%s  <geom type="mesh" contype="0" conaffinity="0" group="3" density="0" '
                   'rgba="%s" mesh="%s"/>' % (pad, rgba, fn[:-4]))
    bit = CT[name.split("_")[0]]
    common = 'group="4" contype="%d" conaffinity="0" density="0" rgba="0 0.55 0.15 0.15"' % bit
    for gi, g in enumerate(v["geoms"]):
        if g["type"] == "box":
            out.append('%s  <geom name="%s_col%d" type="box" size="%s" pos="%s" quat="%s" %s/>'
                       % (pad, name, gi, f3(g["size"]), f3(g["pos"]), f3(g["quat"]), common))
        elif g["type"] == "capsule":
            a, b = np.array(g["p0"], float) / 1000.0, np.array(g["p1"], float) / 1000.0
            out.append('%s  <geom name="%s_col%d" type="capsule" size="%g" fromto="%s %s" %s/>'
                       % (pad, name, gi, g["radius"] / 1000.0, f3(a), f3(b), common))
        else:
            out.append('%s  <geom name="%s_col%d" type="cylinder" size="%s" pos="%s" quat="%s" %s/>'
                       % (pad, name, gi, f3(g["size"]), f3(g["pos"]), f3(g["quat"]), common))
    for c in children.get(name, []):
        emit_body(c, depth + 1)
    out.append(pad + "</body>")


out = []
out.append('<mujoco model="%s">' % spec["name"])
out.append('  <compiler angle="radian" meshdir="meshes/" autolimits="true" '
           'balanceinertia="true" inertiafromgeom="false"/>')
out.append('  <option timestep="0.002" iterations="50" ls_iterations="20" '
           'integrator="implicitfast"/>')
out.append('  <default>')
out.append('    <geom condim="3" friction="1.2 0.01 0.001" solref="0.01 1" '
           'solimp="0.9 0.95 0.001"/>')
out.append('    <default class="leg"><joint damping="0.05" armature="0.0036" '
           'frictionloss="0.05"/></default>')
out.append('    <default class="wheel"><joint damping="0.0" armature="0.0021" '
           'frictionloss="0.02"/></default>')
out.append('  </default>')
out.append('  <asset>')
for name, v in info.items():
    for fn in v["mesh"]:
        out.append('    <mesh name="%s" file="%s" scale="0.001 0.001 0.001"/>'
                   % (fn[:-4], fn))
out.append('  </asset>')
out.append('  <worldbody>')
emit_body(root, 2)
out.append('  </worldbody>')
out.append('  <actuator>')
for j in spec["joints"]:
    e = j["effort"]
    out.append('    <motor name="%s" joint="%s" gear="1" forcerange="-%g %g" '
               'ctrlrange="-%g %g"/>' % (j["name"], j["name"], e, e, e, e))
out.append('  </actuator>')
out.append('  <sensor>')
out.append('    <framequat name="proj_grav" objtype="site" objname="imu"/>')
out.append('    <gyro name="gyro" site="imu"/>')
out.append('    <accelerometer name="acc" site="imu"/>')
for j in spec["joints"]:
    out.append('    <jointpos name="q_%s" joint="%s"/>' % (j["name"], j["name"]))
    out.append('    <jointvel name="dq_%s" joint="%s"/>' % (j["name"], j["name"]))
out.append('  </sensor>')
out.append('</mujoco>')

mjcf = os.path.join(args.outdir, spec["name"] + ".xml")
open(mjcf, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("wrote", mjcf, len(out), "lines")

# ------------------------------------------------------------------ scene.xml
jnames = [j["name"] for j in spec["joints"]]
wheel_r = min(g["size"][0] for n, v in info.items() if n.startswith("wheel")
              for g in v["geoms"] if g["type"] == "cylinder")
key_qpos = [0.0, 0.0, wheel_r + 0.002, 1.0, 0.0, 0.0, 0.0] + [0.0] * len(jnames)
sc = []
sc.append('<mujoco model="%s_scene">' % spec["name"])
sc.append('  <include file="%s.xml"/>' % spec["name"])
sc.append('  <asset>')
sc.append('    <texture type="skybox" builtin="gradient" rgb1="0.55 0.6 0.68" '
           'rgb2="0.25 0.28 0.33" width="256" height="256"/>')
sc.append('    <texture type="2d" name="grid" builtin="checker" rgb1="0.42 0.45 0.50" '
           'rgb2="0.62 0.65 0.70" width="200" height="200"/>')
sc.append('    <material name="floor" texture="grid" texrepeat="8 8" reflectance="0.0"/>')
sc.append('  </asset>')
sc.append('  <visual>')
sc.append('    <global offwidth="1280" offheight="720"/>')
sc.append('    <map znear="0.02"/>')
sc.append('  </visual>')
sc.append('  <worldbody>')
sc.append('    <light name="t" pos="0.6 0.4 2.2" dir="0 0 -1" diffuse="1.0 1.0 1.0" '
           'specular="0.2 0.2 0.2" castshadow="true"/>')
sc.append('    <light name="s" pos="-0.8 0.6 1.6" dir="0.4 -0.3 -1" diffuse="0.4 0.4 0.4"/>')
sc.append('    <geom name="floor" type="plane" size="0 0 0.05" material="floor" '
           'contype="1" conaffinity="255" friction="1.6 0.01 0.001"/>')
sc.append('    <camera name="front" pos="2.0 -1.1 0.55" xyaxes="0.5 0.87 0 -0.35 0.2 0.91"/>')
sc.append('    <camera name="side" pos="0.0 -2.2 0.45" xyaxes="1 0 0 0 -0.2 0.98"/>')
sc.append('    <camera name="top" pos="0 0 2.4" xyaxes="1 0 0 0 -1 0"/>')
sc.append('    <body name="target" pos="0 0 0.15" mocap="true">')
sc.append('      <geom type="box" size="0.02 0.02 0.02" contype="0" conaffinity="0" '
           'rgba="1 0.2 0.2 0.6" group="5"/>')
sc.append('    </body>')
sc.append('  </worldbody>')
sc.append('  <keyframe>')
sc.append('    <key name="stand" qpos="%s"/>' % f3(key_qpos))
sc.append('  </keyframe>')
sc.append('</mujoco>')
scene = os.path.join(args.outdir, "scene.xml")
open(scene, "w", encoding="utf-8").write("\n".join(sc) + "\n")
print("wrote", scene, "wheel_r=%.4f" % wheel_r)
