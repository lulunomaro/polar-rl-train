"""Copy the validated closed-chain MJCF + meshes into the mjlab task package."""
import os, shutil, sys
SRC = r"D:/claude2/fangzhen/robot/out_cc"
DST = r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/assets"
os.makedirs(os.path.join(DST, "meshes_cc"), exist_ok=True)
xml = open(os.path.join(SRC, "rm_vehicle_cc.xml"), encoding="utf-8").read()
assert 'meshdir="meshes/"' in xml
xml = xml.replace('meshdir="meshes/"', 'meshdir="meshes_cc/"')
open(os.path.join(DST, "rm_vehicle_cc.xml"), "w", encoding="utf-8", newline="\n").write(xml)
n = 0
for f in sorted(os.listdir(os.path.join(SRC, "meshes"))):
    if f.lower().endswith(".stl"):
        shutil.copy2(os.path.join(SRC, "meshes", f), os.path.join(DST, "meshes_cc", f)); n += 1
print("installed rm_vehicle_cc.xml + %d meshes into %s" % (n, DST))

# --- smoke test the training env -------------------------------------------------
sys.path.insert(0, r"D:/claude2/fangzhen/train/rmvehicle/src")
import numpy as np, torch, mujoco
from rmvehicle.env_cfgs import flat_cc_env_cfg
cfg = flat_cc_env_cfg()
cfg.scene.num_envs = 64
from mjlab.envs import ManagerBasedRlEnv
env = ManagerBasedRlEnv(cfg=cfg, device="cuda:32".split(":")[0])
m = env.sim.mj_model
print("model: nq=%d nv=%d nu=%d neq=%d nbody=%d" % (m.nq, m.nv, m.nu, m.neq, m.nbody))
print("actuators:", [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, i) for i in range(m.nu)])
ent = env.scene["robot"]
import numpy as _np
am = env.action_manager
terms = getattr(am, "_terms", None) or getattr(am, "terms", {})
for name, term in (terms.items() if hasattr(terms, "items") else []):
    ids = _np.array(getattr(term, "_joint_ids", getattr(term, "joint_ids", []))).ravel()
    print("   action %-16s dim=%d joints=%s" % (name, int(getattr(term, "action_dim", -1)),
          [ent.joint_names[i] for i in ids]))
obs, _ = env.reset()
print("obs shape", tuple(obs["actor"].shape), "(contract wants (N,35))")
for _ in range(150):
    env.step(_np.zeros((env.num_envs, 6)).astype("float32") if False else __import__("torch").zeros(env.num_envs, 6, device=env.device))
rd = ent.data
print("after 150 zero-action steps: base z mean %.3f (min %.3f)  |pitch| mean %.2f deg  alive %d/%d"
      % (float(rd.root_link_pos_w[:, 2].mean()), float(rd.root_link_pos_w[:, 2].min()),
         float(_np.abs(_np.degrees(_np.arcsin(_np.clip(rd.projected_gravity_b[:, 0].cpu().numpy(), -1, 1)))).mean()),
         int((~env.termination_manager.terminated).sum()), env.num_envs))
m = env.sim.mj_model
d = mujoco.MjData(m); d.qpos[:] = _np.array(env.sim.data.qpos[0].cpu())
mujoco.mj_forward(m, d)
gaps = []
for e in range(m.neq):
    o1, o2 = int(m.eq_obj1id[e]), int(m.eq_obj2id[e]); ed = m.eq_data[e]
    p1 = d.xpos[o1] + d.xmat[o1].reshape(3, 3) @ ed[0:3]
    p2 = d.xpos[o2] + d.xmat[o2].reshape(3, 3) @ ed[3:6]
    gaps.append(1000 * _np.linalg.norm(p1 - p2))
print("env-internal connect gaps: max %.3f mm  all=%s" % (max(gaps), _np.round(gaps, 3)))
print("hip->axle height: %.3f m (commanded 0.22 default)" % float(_np.array(env.scene["robot"].data.body_link_pos_w[:, [i for i, n in enumerate(ent.body_names) if n in ("left_rear1", "left_wheel")], :][:, :, 2].mean(axis=1).ptp(axis=1)).mean()))
