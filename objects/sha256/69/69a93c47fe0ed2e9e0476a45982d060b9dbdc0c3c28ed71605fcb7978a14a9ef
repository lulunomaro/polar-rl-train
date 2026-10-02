import io,ast,os,shutil
p=r"D:/claude2/fangzhen/scripts/export_sim2sim.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace("""for f in sorted(os.listdir(args.mesh_src)):
    if f.endswith(".stl"):""","""for f in os.listdir(me):
    os.remove(os.path.join(me, f))
USED = [m for v in phys.values() for m in v["mesh"]]
for f in sorted(os.listdir(args.mesh_src)):
    if f.endswith(".stl") and f in USED:""")
t=t.replace("""        out.append('    <mesh name="%s" file="%s" scale="0.001 0.001 0.001"/>'
                   % (m[:-4] + ".STL", m[:-4] + ".STL"))""",
"""        out.append('    <mesh name="%s" file="../meshes/%s" scale="0.001 0.001 0.001"/>'
                   % (m[:-4] + ".STL", m[:-4] + ".STL"))""")
t=t.replace("""'  <compiler angle="radian" meshdir="meshes/" autolimits="true" '""",
            """'  <compiler angle="radian" autolimits="true" '""")
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t); print("ok")
