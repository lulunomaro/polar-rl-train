import io
p = r"D:/claude2/fangzhen/scripts/build_cc.py"
s = io.open(p, encoding="utf-8").read()
old = """        obj = CSUB.get((s["path"], round(s["volume_mm3"], 1)), s["obj"])
        for d in (COARSE, FINE):
            f = os.path.join(d, "meshes", obj)
            if os.path.exists(f):
                break"""
new = """        obj = CSUB.get((s["path"], round(s["volume_mm3"], 1)), s["obj"])
        # same LOD policy as the chassis: FINE first, so sprockets/bearing seats survive
        for d in ((FINE, COARSE) if BASE_FROM_FINE else (COARSE, FINE)):
            f = os.path.join(d, "meshes", obj)
            if os.path.exists(f):
                break"""
assert old in s, "anchor leg lod"
s = s.replace(old, new, 1)
old2 = """        if len(mesh.faces) > 400:
            mesh = mesh.simplify_quadric_decimation(
                face_count=max(120, min(budget, len(mesh.faces))))"""
new2 = """        if len(mesh.faces) > max(400, budget):
            mesh = mesh.simplify_quadric_decimation(face_count=budget)"""
assert old2 in s, "anchor leg budget"
s = s.replace(old2, new2, 1)
s = s.replace('def write_mesh(body, side, budget=12000):',
              'def write_mesh(body, side, budget=int(os.environ.get("CC_LEG_FACES", "30000"))):', 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("leg meshes now FINE, budget 30k/part")