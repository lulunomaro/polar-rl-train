# Build plant variants with a different WHEEL torque ceiling, to test whether the speed
# envelope is actuator-limited.  Usage: python scripts/mk_wheel_effort_variants.py 10 19
import io, os, sys
ROOT = r"D:/claude2/fangzhen"
DIR = os.path.join(ROOT, "robot/out_cc_linkfix")
base = io.open(os.path.join(DIR, "rm_vehicle_cc.xml"), encoding="utf-8-sig").read()
scene = io.open(os.path.join(DIR, "scene_cc.xml"), encoding="utf-8-sig").read()
for eff in [float(x) for x in (sys.argv[1:] or ["10", "19"])]:
    tag = str(int(eff)) if eff == int(eff) else str(eff)
    pair = "-" + tag + " " + tag
    lines = []
    hits = 0
    for line in base.split(chr(10)):
        if "_wheel_ctrl" in line and "-5.5 5.5" in line:
            line = line.replace("-5.5 5.5", pair)
            hits = hits + 1
        lines.append(line)
    assert hits == 2, hits
    stem = "rm_vehicle_cc_w" + tag + ".xml"
    io.open(os.path.join(DIR, stem), "w").write(chr(10).join(lines))
    sname = "scene_cc_w" + tag + ".xml"
    io.open(os.path.join(DIR, sname), "w").write(
        scene.replace("rm_vehicle_cc.xml", stem))
    print("wrote wheel-effort variant " + tag + " N*m, 2 actuators patched")
