import io
p = r"D:/claude2/fangzhen/scripts/build_cc.py"
s = io.open(p, encoding="utf-8").read()

old = """            d = COARSE if os.path.exists(os.path.join(COARSE, "meshes", obj)) else FINE
            try:
                me = trimesh.load(os.path.join(d, "meshes", obj), process=False)"""
new = """            # the coarse LOD drops thin connectors (light bar, ammo-path plates, carbon
            # sheets) to zero facets, which is what made the chassis look "incomplete".
            # The visual mesh now comes from the FINE export, decimated once, gently.
            fine_f = os.path.join(FINE, "meshes", obj)
            coarse_f = os.path.join(COARSE, "meshes", obj)
            use = fine_f if (BASE_FROM_FINE and os.path.exists(fine_f)) else (
                coarse_f if os.path.exists(coarse_f) else fine_f)
            try:
                me = trimesh.load(use, process=False)"""
assert old in s, "anchor load"
s = s.replace(old, new, 1)

old2 = """            except Exception as e:
                print("    MISSING MESH for chassis solid %-40r (%s: %s)"
                      % (s["product"].strip()[:40], type(e).__name__, str(e)[:60]))
                continue"""
new2 = """            except Exception as e:
                print("    MISSING MESH for chassis solid %-40r (%s: %s)"
                      % (s["product"].strip()[:40], type(e).__name__, str(e)[:60]))
                continue
            if len(me.faces) == 0:
                _empty.append(s["product"].strip())
                continue"""
assert old2 in s, "anchor empty"
s = s.replace(old2, new2, 1)

old3 = """        parts = []
        _names = []"""
new3 = """        parts = []
        _names = []
        _empty = []"""
assert old3 in s, "anchor parts"
s = s.replace(old3, new3, 1)

old4 = """        print("  base solids: %d listed, %d loaded, %d FAILED to load"
              % (len(ss), len(parts), len(ss) - len(parts)))"""
new4 = """        print("  base solids: %d listed, %d used, %d FAILED to load, %d EMPTY in coarse LOD"
              % (len(ss), len(parts), len(ss) - len(parts) - len(_empty), len(_empty)))
        for e in sorted(set(_empty))[:12]:
            print("     EMPTY:", e[:60])"""
assert old4 in s, "anchor report"
s = s.replace(old4, new4, 1)

old5 = """            mesh = mesh.simplify_quadric_decimation(face_count=60000)"""
new5 = """            if len(mesh.faces) > BASE_FACE_BUDGET:
                mesh = mesh.simplify_quadric_decimation(face_count=BASE_FACE_BUDGET)"""
assert old5 in s, "anchor decim"
s = s.replace(old5, new5, 1)

# knobs
anchor = 'OUT = os.path.join(ROOT, "robot/out_cc")'
s = s.replace(anchor, anchor + """

# visual fidelity of the chassis mesh: FINE CAD facets, decimated once.
BASE_FROM_FINE = os.environ.get("CC_BASE_FINE", "1") == "1"
BASE_FACE_BUDGET = int(os.environ.get("CC_BASE_FACES", "400000"))""", 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched: chassis mesh now uses FINE LOD, budget 400k, empty-part report")