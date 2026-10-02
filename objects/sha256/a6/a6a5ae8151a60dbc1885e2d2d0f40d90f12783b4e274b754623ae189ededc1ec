import io, re, os, struct
p = r"D:/claude2/fangzhen/sim2sim_cc/rm_vehicle_cc/mjcf/rm_vehicle.xml"
t = io.open(p, encoding="utf-8", errors="replace").read()
print("armature:", sorted(set(re.findall(r"armature=.([0-9.]+).", t))))
print("forcerange:", sorted(set(re.findall(r"forcerange=.([-0-9 ]+).", t))))
print("mesh refs:", len(re.findall(r'mesh="', t)), "| .STL paths:", len(re.findall(r'\.\./meshes/', t)))
f = r"D:/claude2/fangzhen/sim2sim_cc/rm_vehicle_cc/meshes/base_00.STL"
n = os.path.getsize(f)
with open(f, "rb") as fh:
    fh.seek(80); tri = struct.unpack("<I", fh.read(4))[0]
print("base_00.STL: %.1f MB, %d triangles" % (n / 1e6, tri))
hf = r"D:/claude2/fangzhen/sim2sim_cc/rm_vehicle_cc/meshes/field.hf"
print("field.hf:", os.path.getsize(hf) if os.path.exists(hf) else "MISSING")