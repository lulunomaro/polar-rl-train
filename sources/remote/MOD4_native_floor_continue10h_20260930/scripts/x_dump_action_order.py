"""Compare the TRAINING-side action / observation joint order with the deployed xacro's
commandable-joint order.  Config-only: no sim, no GPU (v12 is still training)."""
import os, re, sys
sys.path.insert(0, r"D:/claude2/fangzhen/train/rmvehicle/src")
import rmvehicle  # noqa
from mjlab.tasks.registry import load_env_cfg
cfg = load_env_cfg("RMVehicle-CC-Skills-v0", play=True)

print("=== MJCF <actuator> block order (what an ideal_pd term indexes if it follows nu) ===")
xml = open(r"D:/claude2/fangzhen/robot/out_cc/rm_vehicle_cc.xml", encoding="utf-8").read()
blk = re.search(r"<actuator>(.*?)</actuator>", xml, re.S).group(1)
for i, m in enumerate(re.finditer(r'name="([^"]+)"\s+joint="([^"]+)"', blk)):
    print("  nu[%d]  %-22s -> %s" % (i, m.group(1), m.group(2)))

print("\n=== action terms in the training cfg (index order = action vector order) ===")
for i, (nm, t) in enumerate(cfg.actions.items()):
    ac = getattr(t, "asset_cfg", None) or (getattr(t, "params", {}) or {}).get("asset_cfg")
    jn = getattr(ac, "joint_names", None) if ac is not None else None
    print("  action[%d] term=%-16s joint_names=%s" % (i, nm, jn))

print("\n=== observation terms that carry joint blocks ===")
for gname in cfg.observations:
    for tname, t in cfg.observations[gname].terms.items():
        p = dict(t.params or {})
        ac = p.get("asset_cfg")
        if ac is not None and getattr(ac, "joint_names", None):
            print("  obs[%s] %-18s joint_names=%s" % (gname, tname, ac.joint_names))

print("\n=== deployed xacro commandable order (from robot_sim.xacro) ===")
x = open(r"D:/claude2/fangzhen/sim2sim_cc/rm_vehicle/xacro/robot_sim.xacro",
         encoding="utf-8").read()
order = []
for m in re.finditer(r'<joint name="([^"]+)">(.*?)</joint>', x, re.S):
    if "command_interface" in m.group(2):
        order.append(m.group(1))
for i, jn in enumerate(order):
    print("  joints[%d] = %s" % (i, jn))