import sys
sys.path.insert(0, r"train/rmvehicle/src")
from rmvehicle import field_cfg as F
g = F.rmuc2026_terrain()
tot = 0.0
for name, sub in g.sub_terrains.items():
    tot += sub.proportion
    print("  %-12s %.4f" % (name, sub.proportion))
print("  SUM = %.4f" % tot)