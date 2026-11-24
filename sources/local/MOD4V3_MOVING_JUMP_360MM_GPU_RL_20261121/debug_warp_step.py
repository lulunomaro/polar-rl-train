from argparse import ArgumentParser
import json
from pathlib import Path

import warp as wp
import mujoco_warp as mw

from jump360_scene import HERE
from jump360_gpu import JumpGpu
from train_jump360_gpu import DEFAULT_TIMING, binding

p = ArgumentParser()
p.add_argument("--out", type=Path)
p.add_argument("--timing", type=Path, default=DEFAULT_TIMING)
a = p.parse_args()
binding()
wp.config.kernel_cache_dir = str(HERE/"cache/warp")
timing = json.loads((HERE/a.timing).read_text(encoding="utf-8"))
env = JumpGpu(4, 31, timing)
def report(label):
    wp.synchronize()
    for name,tensor in [("qpos",env.p),("qvel",env.v),("qacc",wp.to_torch(env.d.qacc)),
                        ("ctrl",wp.to_torch(env.d.ctrl)),("time",wp.to_torch(env.d.time)),
                        ("mass",env.mass),("nefc",wp.to_torch(env.d.nefc)),
                        ("solve_iter",wp.to_torch(env.d.solver_niter)),("stats",env.stats)]:
        print(label, name, tensor[0,:10].tolist() if tensor.ndim==2 else float(tensor[0]))
report("initial")
env.action[:, 4:]=3
for _ in range(8):
    env.step(env.action)
report("graph")
for _ in range(8):
    with wp.ScopedStream(env.warp_stream):
        env.substeps()
report("direct")
m,d=env.m,env.d
for i in range(8):
    mw.step(m,d)
report("direct-no-controller")

cpu = env.cpu
for name, expanded, do_reset, conditional in (("native",False,False,False),
    ("native_reset",False,True,False),("expanded",True,False,False),("cond_true",False,False,True)):
    probe_model = mw.put_model(cpu.m)
    probe_model.opt.graph_conditional = conditional
    probe_data = mw.put_data(cpu.m,cpu.d,nworld=4,nconmax=48,njmax=192)
    if expanded:
        probe_model.body_mass = env.m.body_mass
        probe_model.body_ipos = env.m.body_ipos
        probe_model.geom_friction = env.m.geom_friction
    if do_reset:
        mw.reset_data(probe_model,probe_data,wp.ones(4,dtype=wp.bool))
        wp.to_torch(probe_data.qpos)[:] = env.reset_q
        wp.to_torch(probe_data.mocap_pos)[:] = env.mocap
    wp.to_torch(probe_data.ctrl)[:,4:] = 3.
    for _ in range(3):
        mw.step(probe_model,probe_data)
    wp.synchronize()
    for label in ("qvel","qacc","qacc_smooth","qfrc_smooth","qfrc_actuator","qfrc_bias","solver_niter","nefc","actuator_force"):
        print(name, label, getattr(probe_data,label).numpy()[0])
    print(name, "mocaps", probe_data.mocap_pos.numpy()[0], "gravity",probe_model.opt.gravity.numpy())
