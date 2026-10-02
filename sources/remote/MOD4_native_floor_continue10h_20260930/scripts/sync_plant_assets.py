"""Copy the freshly built plant into the training package (meshdir rename).

robot/out_cc/rm_vehicle_cc.xml is authoritative; rmvehicle ships its own copy under
src/rmvehicle/assets with meshdir="meshes_cc/" because the mjlab package keeps the meshes
next to the XML.  Doing this by hand is how the plant and the trained policy drift apart.
"""
import argparse, filecmp, os, shutil, sys

ROOT = r"D:/claude2/fangzhen"
SRC = os.path.join(ROOT, "robot/out_cc/rm_vehicle_cc.xml")
DST_DIR = os.path.join(ROOT, "train/rmvehicle/src/rmvehicle/assets")
DST = os.path.join(DST_DIR, "rm_vehicle_cc.xml")

ap = argparse.ArgumentParser()
ap.add_argument("--check", action="store_true", help="only report drift, write nothing")
ap.add_argument("--src", default=SRC,
                help="which built plant to stage: robot/out_cc (baseline) or a variant such "
                      + "as robot/out_cc_linkfix.  Rebuilding without --src used to silently "
                      + "revert the staged plant to the baseline one.")
a = ap.parse_args()
SRC = a.src

s = open(SRC, encoding="utf-8").read()
DQ = chr(34)                                    # the XML attribute quote, spelled safely
WANT = "meshdir=" + DQ + "meshes_cc/" + DQ
for old_dir in ("meshdir=" + DQ + "meshes/" + DQ,
                "meshdir=" + DQ + "../out_cc/meshes/" + DQ):
    if old_dir in s:
        s = s.replace(old_dir, WANT)
        break
else:
    if WANT not in s:
        raise SystemExit("unexpected compiler line in " + SRC)
out = s
if a.check:
    same = os.path.exists(DST) and open(DST, encoding="utf-8").read() == out
    print("plant XML in sync" if same else
          "STALE: %s differs from %s -- rerun this script" % (DST, SRC))
    sys.exit(0 if same else 1)
os.makedirs(DST_DIR, exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(out)
# meshes: the MJCF resolves them through meshdir="meshes_cc/"
srcm = os.path.join(os.path.dirname(SRC), "meshes")
if not os.path.isdir(srcm):        # variants keep their meshes next to the baseline plant
    srcm = os.path.join(ROOT, "robot/out_cc/meshes")
dstm = os.path.join(DST_DIR, "meshes_cc")
os.makedirs(dstm, exist_ok=True)
n = 0
for f in os.listdir(srcm):
    s1, d1 = os.path.join(srcm, f), os.path.join(dstm, f)
    if not os.path.exists(d1) or not filecmp.cmp(s1, d1, shallow=False):
        shutil.copy2(s1, d1); n += 1
print("synced plant XML; copied %d changed meshes into %s" % (n, dstm))
