"""Guard: the 35-D observation, the 6-D action and the deployment joint lists must all use
the wheelbipe contract order.  A previous version of this project trained with mjlab's
default `preserve_order=False`, which resolved the leg patterns into *model* order
([rear1_L, front1_L, ...]) while the action vector and the deployment feed
[front1_L, rear1_L, ...] - the policy and the hardware then disagreed about which joint is
which.  Run this after any change to names.py / env_cfgs.py / the exporters."""
import os, re, sys
sys.path.insert(0, r"D:/claude2/fangzhen/train/rmvehicle/src")

CONTRACT_LEG = ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint"]
CONTRACT_WHL = ["left_wheel_joint", "right_wheel_joint"]
CONTRACT8 = CONTRACT_LEG + CONTRACT_WHL + ["left_spring2_joint", "right_spring2_joint"]
fails = []


def check(label, got, want):
    ok = list(got) == list(want)
    print("  %-46s %s" % (label, "OK" if ok else "MISMATCH"))
    if not ok:
        print("      got :", list(got))
        print("      want:", list(want))
        fails.append(label)


print("1) mjlab env config (RMVehicle-CC-Field-v0 / -Skills-v0)")
import rmvehicle  # noqa: F401  registers the tasks
from mjlab.managers import SceneEntityCfg
from mjlab.tasks.registry import load_env_cfg
from rmvehicle.names import CC
for task in ("RMVehicle-CC-Field-v0", "RMVehicle-CC-Skills-v0"):
    cfg = load_env_cfg(task)
    t = cfg.observations["actor"].terms
    for key, want in (("leg_pos", CONTRACT_LEG), ("leg_vel", CONTRACT_LEG),
                      ("wheel_vel", CONTRACT_WHL)):
        ac = t[key].params["asset_cfg"]
        if not ac.preserve_order:
            fails.append("%s/%s preserve_order" % (task, key))
            print("  %-46s MISMATCH (preserve_order=False)" % (task + "/" + key))
        else:
            print("  %-46s OK (patterns in contract order)" % (task + "/" + key))
        if list(ac.joint_names) != [r"^%s$" % n for n in want]:
            fails.append("%s/%s patterns" % (task, key))
    act = cfg.actions["leg_joint_pos"].actuator_names
    if list(act) != [r"^%s$" % n for n in CONTRACT_LEG]:
        fails.append(task + "/action order")
    print("  %-46s %s" % (task + "/action leg actuators",
                          "OK" if list(act) == [r"^%s$" % n for n in CONTRACT_LEG] else "MISMATCH"))

print("2) resolved joint ids inside a live env (the real proof)")
import torch
from mjlab.envs import ManagerBasedRlEnv
cfg = load_env_cfg("RMVehicle-CC-Field-v0"); cfg.scene.num_envs = 2
env = ManagerBasedRlEnv(cfg=cfg, device="cuda:0")
ent = env.scene["robot"]
names = list(ent.joint_names)
sc = SceneEntityCfg("robot", joint_names=tuple(CC.leg_joints), preserve_order=True)
sc.resolve(env.scene)
check("obs leg block resolves to the contract order",
      [names[i] for i in sc.joint_ids], CONTRACT_LEG)
ac = [a for a in ent.actuator_names]
check("model actuators are in the contract order", ac[:6], CONTRACT_LEG + CONTRACT_WHL)
env.close()

print("3) exported ONNX metadata")
import onnx
for f in (r"D:/claude2/fangzhen/train/deploy/rm_cc_v8_final.onnx",):
    if os.path.exists(f):
        md = {p.key: p.value for p in onnx.load(f).metadata_props}
        order = [x for x in md.get("policy_joint_order", "").split(",") if x]
        check("onnx policy_joint_order starts with the contract legs", order[:4], CONTRACT_LEG)
    else:
        print("  (skip) %s not built yet" % f)

print("4) sim2sim deployment description")
mj = r"D:/claude2/fangzhen/sim2sim_cc/rm_vehicle_cc/mjcf/rm_vehicle.xml"
if os.path.exists(mj):
    txt = open(mj, encoding="utf-8").read()
    joints = re.findall(r'<joint name="([^"]+)"', txt)
    missing = [j for j in CONTRACT8 if j not in joints]
    print("  %-46s %s" % ("8-joint contract present in the deployed MJCF",
                          "OK" if not missing else "MISSING %s" % missing))
    if missing:
        fails.append("contract joints")
    xa = re.findall(r'<connect body1="([^"]+)" body2="([^"]+)"', txt)
    print("  %-46s %d connects" % ("closed-chain equality constraints", len(xa)))
    if len(xa) != 6:
        fails.append("connect count")

print("\nRESULT:", "ALL CONTRACT-ORDER CHECKS PASS" if not fails else "FAILED: %s" % fails)
sys.exit(1 if fails else 0)
