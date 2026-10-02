import io
F=r"D:\claude2\fangzhen\scripts\joint_limit_physics_test.py"
lines=io.open(F,encoding="utf-8").read().split("\n")
i=[n for n,l in enumerate(lines) if l.strip()=="m = mujoco.MjModel.from_xml_string(txt)"]
assert len(i)==1, i
i=i[0]
lines[i:i+1] = [
 "# write next to the meshes so meshdir=\"meshes/\" still resolves",
 "# (from_xml_string has no base directory)",
 'WELD = os.path.join(ROOT, "robot/out_cc/_welded_leg_test.xml")',
 'open(WELD, "w", encoding="utf-8").write(txt)',
 "m = mujoco.MjModel.from_xml_path(WELD)",
 "for _g in range(m.ngeom):          # this test needs no visuals at all",
 "    if m.geom_group[_g] == 2:",
 "        m.geom_group[_g] = 5",
]
io.open(F,"w",encoding="utf-8").write("\n".join(lines))
print("patched to load from a sibling file")