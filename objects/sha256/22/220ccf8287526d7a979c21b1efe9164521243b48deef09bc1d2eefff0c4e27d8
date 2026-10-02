import json, io
import numpy as np
man = json.load(io.open(r"D:/claude2/fangzhen/cad/out/vehicle/manifest.json", encoding="utf-8"))
sol = man["solids"]
print("sample solid:", {k: (str(v)[:70]) for k, v in list(sol[0].items())})
def cw(s):
    c = s.get("com_world")
    return np.array(c, float) if c else np.array([np.nan] * 3)
WANT = ("电机座", "一级腿链轮", "二级腿链轮", "碗组轴承", "膝关节轴承座", "连杆轴承座",
        "后轴承座", "DM_8116", "电机涨块", "中心轴", "90定制滑环", "30 60滑环", "氮气弹簧")
print("\n%-26s %-30s %26s %9s" % ("part", "assembly path", "CoM world (x,y,z) mm", "vol cm3"))
seen = set()
for s in sol:
    nm = s["product"].strip().replace("24    ", "").replace("Mirror", "M:")
    if not any(w in nm for w in WANT):
        continue
    c = cw(s)
    key = (nm, tuple(np.round(c, 0)))
    if key in seen:
        continue
    seen.add(key)
    print("%-26s %-30s %26s %9.1f" % (nm[:26], s["path"][:30], np.round(c, 1).tolist(), (s.get("volume_mm3") or 0) / 1000.0))