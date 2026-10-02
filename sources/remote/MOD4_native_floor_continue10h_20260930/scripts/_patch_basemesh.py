import io
p = r"D:/claude2/fangzhen/scripts/build_cc.py"
s = io.open(p, encoding="utf-8").read()
old = """        mesh = trimesh.util.concatenate(parts)
        try:
            mesh = mesh.simplify_quadric_decimation(face_count=60000)
        except Exception:
            pass"""
new = """        mesh = trimesh.util.concatenate(parts)
        # --- integrity report: which chassis-side solids made it into the mesh? ---
        import collections as _c
        _miss = getattr(write_mesh, "_missing", [])
        print("  base solids: %d listed, %d loaded, %d FAILED to load"
              % (len(ss), len(parts), len(ss) - len(parts)))
        _z = sorted(((float(mm.bounds[0][2]), float(mm.bounds[1][2]), nm)
                     for mm, nm in zip(parts, _names)), key=lambda t: -t[1])
        print("  highest chassis parts (z mm):")
        for z0, z1, nm in _z[:8]:
            print("     z %6.1f .. %6.1f   %s" % (z0, z1, nm[:70]))
        try:
            mesh = mesh.simplify_quadric_decimation(face_count=60000)
            print("  base decimated -> %d faces" % len(mesh.faces))
        except Exception as e:
            print("  base decimation skipped:", type(e).__name__, str(e)[:90])"""
assert old in s, "anchor"
s = s.replace(old, new, 1)
# collect the names of the parts we actually loaded, and record load failures loudly
old2 = """            try:
                me = trimesh.load(os.path.join(d, "meshes", obj), process=False)
            except Exception:
                continue
            me.apply_transform(A4)
            parts.append(me)"""
new2 = """            try:
                me = trimesh.load(os.path.join(d, "meshes", obj), process=False)
            except Exception as e:
                print("    MISSING MESH for chassis solid %-40r (%s: %s)"
                      % (s["product"].strip()[:40], type(e).__name__, str(e)[:60]))
                continue
            me.apply_transform(A4)
            parts.append(me)
            _names.append(s["product"].strip())"""
assert old2 in s, "anchor2"
s = s.replace(old2, new2, 1)
s = s.replace("""        ss = [s for s in groups["base"] if isinstance(s, dict)]
        parts = []""",
              """        ss = [s for s in groups["base"] if isinstance(s, dict)]
        parts = []
        _names = []""", 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("instrumented build_cc.py base-mesh assembly")