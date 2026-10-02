import io
p=r"D:/claude2/fangzhen/scripts/build_robot.py"
t=io.open(p,encoding="utf-8").read()
reps=[
 # 1. remove the invalid <statistic> element
 ("sc.append('  <statistic width=\"1600\" height=\"900\"/>')\n", ""),
 # 2. iterative decimation helper
 ("""STL_CAP = 150000
""",
  """STL_CAP = 150000


def decimate_to(mesh, target, passes=6):
    \"\"\"fast_simplification clamps one pass to ~10x reduction, so iterate.\"\"\"
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
"""),
 # 3. use it for the merged link mesh
 ("""    if target and len(mesh.faces) > target * 2:
        try:
            mesh = mesh.simplify_quadric_decimation(face_count=target)
        except Exception:
            pass
""",
  """    if target:
        mesh = decimate_to(mesh, target)
"""),
]
for a,b in reps:
    if a not in t: print("MISS:", a[:70].replace("\n","\\n")); continue
    t=t.replace(a,b); print("ok")
io.open(p,"w",encoding="utf-8").write(t)
