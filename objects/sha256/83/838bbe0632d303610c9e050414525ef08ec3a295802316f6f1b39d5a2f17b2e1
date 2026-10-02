import io
F=r"D:\claude2\fangzhen\scripts\joint_limit_physics_test.py"
lines=io.open(F,encoding="utf-8").read().split("\n")
# point XML back at the plant and rebuild the welded copy on every run
for n,l in enumerate(lines):
    if l.startswith("XML = "):
        lines[n] = 'XML = os.path.join(ROOT, "robot/out_cc/rm_vehicle_cc.xml")'
        hit=n
    if l.strip()=='m = mujoco.MjModel.from_xml_path(XML)':
        lines[n] = ("WELD = os.path.join(ROOT, \"robot/out_cc/_welded_leg_test.xml\")\n"
                    "_t = open(XML, encoding=\"utf-8\").read()\n"
                    "assert '<freejoint name=\"floating_base\"/>' in _t\n"
                    "open(WELD, \"w\", encoding=\"utf-8\").write("
                    "_t.replace('<freejoint name=\"floating_base\"/>', \"\"))\n"
                    "m = mujoco.MjModel.from_xml_path(WELD)")
io.open(F,"w",encoding="utf-8").write("\n".join(lines))
print("test now rebuilds the welded model from the live plant")