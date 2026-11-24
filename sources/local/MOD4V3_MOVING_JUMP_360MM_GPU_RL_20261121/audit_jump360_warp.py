"""Compare native MuJoCo and gathered Warp contact forces at the 360 mm top."""
from argparse import ArgumentParser
from pathlib import Path

import mujoco_warp as mjw
import numpy as np
import warp as wp

from jump360_gpu import gather_contacts
from jump360_scene import HERE, WALL_HEIGHT, JumpPlant, json_save, mujoco
from train_jump360_gpu import binding


def compare(plant, surface):
    plant.setup(.28)
    plant.wall("platform", .5)
    plant.d.qpos[0] = 1.25 if surface == "platform" else -1.25
    height = WALL_HEIGHT if surface == "platform" else 0.
    plant.d.qpos[2] += height-plant.frame().tire_low-.0015
    mujoco.mj_forward(plant.m, plant.d)
    cpu = plant.frame()
    geom = plant.hurdle_gids[0] if surface == "platform" else plant.ground_gid
    reference = {}
    for i in range(plant.d.ncon):
        c = plant.d.contact[i]
        if geom not in c.geom or c.efc_address < 0:
            continue
        robot = int(c.geom[0] if c.geom[1] == geom else c.geom[1])
        if robot in plant.tire_map:
            mujoco.mj_contactForce(plant.m, plant.d, i, plant._local_force)
            reference.setdefault(robot, []).append(float(plant._local_force[0]))

    gpu_model = mjw.put_model(plant.m)
    gpu_model.opt.graph_conditional = False
    data = mjw.put_data(plant.m, plant.d, nworld=1, nconmax=48, njmax=192)
    mjw.forward(gpu_model, data)
    lookup = np.zeros(plant.m.ngeom, dtype=np.int32)
    lookup[plant.ground_gid] = -1
    lookup[plant.hurdle_gids] = [-2, -3, -4]
    lookup[plant.groups[0]] = [1, 2]
    lookup[plant.groups[1]+plant.groups[2]] = 3
    out = wp.zeros((1, 9), dtype=float)
    c = data.contact
    wp.launch(gather_contacts, data.naconmax,
              [data.nacon, c.geom, c.worldid, c.frame, c.pos, c.dim, c.efc_address,
               data.nefc, data.efc.force, wp.array(lookup, dtype=wp.int32), out])
    sums = out.numpy()[0]
    n = int(data.nacon.numpy()[0])
    ids = wp.array(np.arange(n, dtype=np.int32), dtype=wp.int32)
    forces = wp.zeros(n, dtype=wp.spatial_vector)
    mjw.contact_force(gpu_model, data, ids, False, forces)
    rows = []
    g, w, addr, native, force = (c.geom.numpy(), c.worldid.numpy(), c.efc_address.numpy(),
                                 forces.numpy(), data.efc.force.numpy())
    for i in range(n):
        if geom not in g[i] or addr[i, 0] < 0:
            continue
        robot = int(g[i, 0] if g[i, 1] == geom else g[i, 1])
        if robot in plant.tire_map:
            rows.append(dict(tire=plant.m.geom(robot).name, world=int(w[i]), row=int(addr[i, 0]),
                             raw_normal_n=float(force[w[i], addr[i, 0]]), warp_native_n=float(native[i, 0])))
    cpu_support = cpu.wheel_top_force if surface == "platform" else cpu.wheel_up_force
    gpu_support = sums[6:8] if surface == "platform" else sums[1:3]
    native_agrees = all(np.isclose(row["raw_normal_n"], row["warp_native_n"], atol=1e-6) for row in rows)
    passed = (len(reference) == len({row["tire"] for row in rows}) == 2
              and min(cpu_support) > 1. and min(gpu_support) > 1.
              and native_agrees and np.allclose(cpu_support, gpu_support, rtol=.02, atol=2.)
              and (surface != "floor" or not sums[6:8].any()))
    return dict(surface=surface, passed=bool(passed), cpu_support_n=cpu_support, warp_support_n=gpu_support.tolist(),
                cpu_contact_normal_n={plant.m.geom(k).name:v for k,v in reference.items()},
                max_abs_support_error_n=float(np.max(np.abs(np.array(cpu_support)-gpu_support))),
                warp_platform_force_n=sums[6:8].tolist(), warp_contacts=rows)


def main():
    parser = ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    gpu = binding()
    wp.set_device("cuda:0")
    wp.config.kernel_cache_dir = str(HERE/"cache/warp")
    plant = JumpPlant()
    cases = [compare(plant, surface) for surface in ("floor", "platform")]
    passed = all(case["passed"] for case in cases)
    json_save(args.out/"CONTACT_AUDIT.json", dict(gpu=gpu, passed=passed, nworld=1, cases=cases))
    print(cases, flush=True)
    if not passed:
        raise RuntimeError("CPU/Warp contact comparison failed")


if __name__ == "__main__":
    main()
