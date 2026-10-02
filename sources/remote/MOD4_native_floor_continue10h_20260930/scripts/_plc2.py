import io, ast
p = r"D:/claude2/fangzhen/scripts/build_cc.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace("    anc = lambda c, pin=pin, y=y: np.array([c[0] - pin[0], c[1] - y, c[2] - pin[1]])",
              "    anc = lambda c, pin=pin, y=y: np.array([pin[0], y, pin[1]])")
t = t.replace('    print("  %-8s m=%6.3f kg com=%s I=%s" % (body, m, np.round(com, 1),\n                                             np.round(np.sort(np.linalg.eigvalsh(I)), 1)))',
              '    print("  %-8s m=%6.3f kg com(rel)=%s I=%s" % (body, m, np.round(com, 1),\n                                             np.round(np.sort(np.linalg.eigvalsh(I)), 1)))')
# append calibration + emitter
t += '''

# ------------------------------------------------------------------ calibration
TARGET_TOTAL = 20.0          # SJTU note 3.5: 全车减重到 20 kg 以下
raw_total = BODIES["base"]["mass"] + 2 * sum(
    b["mass"] for k, b in BODIES.items() if k != "base")
K = TARGET_TOTAL / raw_total
for b in BODIES.values():
    b["mass"] *= K
    b["inertia"] *= K
print("\\nmass calibration: raw %.2f kg -> %.2f kg (x%.4f)" % (raw_total, TARGET_TOTAL, K))
for k in ("base", "thigh", "shank", "wheel", "crank"):
    print("   %-7s %6.3f kg" % (k, BODIES[k]["mass"]))
leg_kg = sum(BODIES[k]["mass"] for k in TOPO)
print("   per leg = %.3f kg  (SJTU reference model: 1.57 kg)" % leg_kg)

# ------------------------------------------------------------------ meshes
def export_mesh(body, side, budget):
    ss = [s for (sd, s) in groups.get(body, []) if not isinstance(s, dict) and sd == side]
    if isinstance(groups.get(body, [None])[0], dict):
        return None
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

def write_mesh(body, side, budget=12000):
    ss = [s for (sd, s) in groups.get(body, []) if not isinstance(s, dict) and sd == side]
    parts = []
    for s in ss:
        obj = CSUB.get((s["path"], round(s["volume_mm3"], 1)), s["obj"])
        for d in (COARSE, FINE):
            f = os.path.join(d, "meshes", obj)
            if os.path.exists(f):
                break
        try:
            me = trimesh.load(f, process=False)
        except Exception:
            continue
        me.apply_transform(A4)
        parts.append(me)
    if not parts:
        return None
    mesh = trimesh.util.concatenate(parts)
    try:
        if len(mesh.faces) > 400:
            mesh = mesh.simplify_quadric_decimation(face_count=max(200, min(budget, len(mesh.faces) // 3)))
    except Exception:
        pass
    mesh.apply_translation(-ANCHOR[body] / 1000.0 * 1000.0 / 1000.0)
    mesh.apply_translation(-ANCHOR[body])
    fn = "%s_%s.stl" % (body, side.lower())
    mesh.export(os.path.join(OUT, "meshes", fn))
    return fn

print("\\n== meshes ==")
MESH = {}
for body in list(TOPO) + ["base"]:
    for side in ("L", "R"):
        if body == "base":
            continue
        f = write_mesh(body, side)
        if f:
            MESH[(body, side)] = f
    if body == "base":
        ss = [s for s in groups["base"] if isinstance(s, dict)]
        parts = []
        for s in ss:
            obj = CSUB.get((s["path"], round(s["volume_mm3"], 1)), s["obj"])
            d = COARSE if os.path.exists(os.path.join(COARSE, "meshes", obj)) else FINE
            try:
                me = trimesh.load(os.path.join(d, "meshes", obj), process=False)
            except Exception:
                continue
            me.apply_transform(A4)
            parts.append(me)
        mesh = trimesh.util.concatenate(parts)
        try:
            mesh = mesh.simplify_quadric_decimation(face_count=60000)
        except Exception:
            pass
        for i in range(0, len(mesh.faces), 150000):
            sub = mesh.submesh([np.arange(i, min(i + 150000, len(mesh.faces)))], append=True)
            fn = "base_%02d.stl" % (i // 150000)
            sub.export(os.path.join(OUT, "meshes", fn))
            MESH.setdefault("base", []).append(fn)
        print("  base -> %s faces" % len(mesh.faces))
print("  leg meshes:", len(MESH) - 1, "files")
'''
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
try:
    ast.parse(t); print("appended calibration + mesh export")
except SyntaxError as e:
    print("SYNTAX", e.lineno, e.msg)
