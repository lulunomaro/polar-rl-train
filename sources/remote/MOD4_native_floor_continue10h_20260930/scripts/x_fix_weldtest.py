import io
F=r"D:\claude2\fangzhen\scripts\joint_limit_physics_test.py"
lines=io.open(F,encoding="utf-8").read().split("\n")
for i,l in enumerate(lines):
    print(i+1, repr(l[:90])) if ("txt" in l or "from_xml_string" in l or "freejoint" in l or "re.sub" in l) else None