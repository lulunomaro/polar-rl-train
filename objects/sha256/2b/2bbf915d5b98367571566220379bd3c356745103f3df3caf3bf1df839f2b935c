"""Would a software hip limit stop the catastrophic branch wind-up seen in native MuJoCo?

The harness (native MuJoCo, mjlab's collision model) diverges the moment the four-bar crosses its
branch singularity: 0.9 s into a spin command the hips are at 4.2/2.9/3.6/2.8 rad while training
holds them at 0.22/0.10.  Nothing in the plant prevents that - the hip joints are declared with NO
range at all (docs/audit/joint_workspace.json: rear1/front1 limited=false), because the closed
chain itself never bounds them (130321/130321 poses close).  Real DM drives DO have a software
angle limit, so adding one is both a fidelity fix and a safety net.

This builds a COPY of the plant with hip ranges, so the live plant that v15 is training on is
untouched, and reports whether the wind-up disappears.
"""
import os, re, subprocess
ROOT = r"D:/claude2/fangzhen"
SRC = os.path.join(ROOT, "robot/out_cc")
DST = os.path.join(ROOT, "robot/out_cc_hiplim")
os.makedirs(DST, exist_ok=True)
xml = open(os.path.join(SRC, "rm_vehicle_cc.xml"), encoding="utf-8").read()
LIM = os.environ.get("RM_HIP_LIMIT", "1.6")
n = 0
def add_range(mo):
    global n
    n += 1
    tag = mo.group(0)
    close = "/>" if tag.endswith("/>") else ">"
    return tag[:-len(close)] + ' range="-%s %s"%s' % (LIM, LIM, close)
xml2 = re.sub(r'<joint name="(?:left|right)_(?:front1|rear1)_joint"[^>]*>', add_range, xml)
assert n == 4, n
xml2 = xml2.replace('meshdir="meshes/"', 'meshdir="%s"' % os.path.join(SRC, "meshes").replace("\\", "/"))
open(os.path.join(DST, "rm_vehicle_cc.xml"), "w", encoding="utf-8", newline="\n").write(xml2)
scene = open(os.path.join(SRC, "scene_cc.xml"), encoding="utf-8").read()
open(os.path.join(DST, "scene_cc.xml"), "w", encoding="utf-8", newline="\n").write(scene)
print("built %s with hip range +-%s rad on %d hip joints" % (DST, LIM, n))
