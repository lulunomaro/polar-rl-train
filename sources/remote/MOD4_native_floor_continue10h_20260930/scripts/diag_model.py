import io, json, os, re
import mujoco
xml = r"D:/claude2/fangzhen/robot/out_cc/rm_vehicle_cc.xml"
t = io.open(xml, encoding="utf-8").read()
print("=== 红色 / 非绿非灰的 geom 或 site（截图里那个红柱子） ===")
for m in re.finditer(r'<(geom|site)[^>]*rgba="([^"]*)"[^>]*>', t):
    rgb = [float(x) for x in m.group(2).split()]
    if rgb[0] > 0.6 and rgb[1] < 0.4 and rgb[2] < 0.4:
        print("   ", m.group(0)[:150])
for m in re.finditer(r'<(geom|site)[^>]*>', t):
    if "rgba" not in m.group(0):
        print("   no-rgba line:", m.group(0)[:120])
print()
m = mujoco.MjModel.from_xml_path(r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml")
print("=== 每个 body 的质量 / 挂了的 mesh ===")
for b in range(m.nbody):
    nm = mujoco.mj_id2name(m, 1, b)
    if nm is None: continue
    print("   %-22s mass=%6.3f kg  geoms=%d" % (nm, float(m.body_mass[b]), int((m.geom_bodyid == b).sum())))
print()
print("=== 从 STEP 里丢掉/未导出的零件统计（link_physics_cc.json） ===")
p = r"D:/claude2/fangzhen/robot/out_cc/link_physics_cc.json"
j = json.load(io.open(p, encoding="utf-8"))
print("   keys:", list(j.keys())[:12])
for k in ("dropped", "skipped", "excluded", "not_exported", "notes"):
    if k in j:
        v = j[k]
        print("   %s: %s" % (k, str(v)[:600]))