from argparse import ArgumentParser
import inspect
import os
from pathlib import Path

import mujoco
import mujoco_warp as mw
import torch
import warp as wp

from jump360_scene import JumpPlant

parser = ArgumentParser()
parser.add_argument("--out", type=Path)
args = parser.parse_args()
print(mujoco.__version__, mw.__version__, wp.__version__, torch.__version__)
print("mask", os.environ["CUDA_VISIBLE_DEVICES"])
print(torch.cuda.device_count(), torch.cuda.get_device_properties(0))
print(inspect.signature(mw.put_model), inspect.signature(mw.put_data), inspect.signature(mw.reset_data))
print(inspect.signature(mw.step), inspect.signature(mw.forward))
print(inspect.getfile(mw.put_model))
plant = JumpPlant()
print("ngeom nq nv nu", plant.m.ngeom, plant.m.nq, plant.m.nv, plant.m.nu)
print("action maps", plant.order, plant.ppo_to_env_np, plant.act_ids, plant.active_qadr, plant.dadr_all[plant.leg_ids])
wp.config.kernel_cache_dir = str(args.out.parent.parent / "cache/warp")
m = mw.put_model(plant.m)
d = mw.put_data(plant.m, plant.d, nworld=2, nconmax=64, njmax=320)
for label, obj in (("model", m), ("data", d), ("contact", d.contact), ("opt", m.opt)):
    print(label, {k: (str(v.dtype), v.shape) for k,v in vars(obj).items() if isinstance(v,wp.array)})
print("contact data", vars(d.contact).keys())
mw.step(m,d)
wp.synchronize()
print("ok", d.qpos.numpy()[:, :7])
