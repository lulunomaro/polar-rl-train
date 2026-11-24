"""Compare native CPU and multi-world Warp loads on both R4 obstacle heights."""
import mujoco_warp as mjw
import numpy as np
import warp as wp

from jump380_r4_gpu import gather_contacts
from jump380_r4_scene import Jump380Plant, mujoco


def fixture(plant, kind, side):
    plant.setup(.28)
    plant.wall(kind, .50)
    if side:
        plant.d.qpos[0] += .50 - plant.frame().max_x + .018
        plant.d.qvel[0] = .55
    else:
        plant.d.qpos[0] = 1.30 if kind != "flat" else -1.25
    surface_height = 0. if side else plant.wall_height
    plant.d.qpos[2] += surface_height - plant.frame().tire_low - .0015
    mujoco.mj_forward(plant.m, plant.d)
    return plant.frame(), plant.d.qpos.copy(), plant.d.qvel.copy(), plant.d.mocap_pos.copy()


def audit_contact():
    wp.set_device("cuda:0")
    plant = Jump380Plant()
    cases = (("platform_380", False), ("flat", False), ("platform_360", False),
             ("platform_380", True), ("platform_360", True))
    fixtures = [fixture(plant, *case) for case in cases]
    gpu_model = mjw.put_model(plant.m)
    gpu_model.opt.graph_conditional = False
    data = mjw.put_data(plant.m, plant.d, nworld=len(cases), nconmax=48, njmax=192)
    for i, dest in enumerate((data.qpos, data.qvel, data.mocap_pos), start=1):
        dtype = wp.vec3 if i == 3 else float
        source = wp.array(np.array([item[i] for item in fixtures]), dtype=dtype)
        wp.copy(dest, source)
    mjw.forward(gpu_model, data)

    lookup = np.zeros(plant.m.ngeom, dtype=np.int32)
    lookup[plant.ground_gid] = -1
    lookup[plant.hurdle_gids] = [-2, -3, -4]
    lookup[plant.groups[0]] = [1, 2]
    lookup[plant.groups[1] + plant.groups[2]] = 3
    heights = wp.array([.380, 0., .360, .380, .360], dtype=float)
    output = wp.zeros((len(cases), 9), dtype=float)
    c = data.contact
    wp.launch(gather_contacts, data.naconmax, [
        data.nacon, c.geom, c.worldid, c.frame, c.pos, c.dim, c.efc_address,
        data.nefc, data.efc.force, wp.array(lookup, dtype=wp.int32), heights, output,
    ])
    n = int(data.nacon.numpy()[0])
    indices = wp.array(np.arange(n, dtype=np.int32), dtype=wp.int32)
    native = wp.zeros(n, dtype=wp.spatial_vector)
    mjw.contact_force(gpu_model, data, indices, False, native)
    native_n, world, address = native.numpy()[:, 0], c.worldid.numpy()[:n], c.efc_address.numpy()[:n, 0]
    usable = address >= 0
    force = data.efc.force.numpy()
    raw = force[world[usable], address[usable]]
    errors = np.abs(raw - native_n[usable])

    rows = []
    for i, ((kind, side), (reference, *_), gpu) in enumerate(zip(cases, fixtures, output.numpy())):
        mask = world[usable] == i
        error = float(errors[mask].max(initial=0.))
        indexed_correctly = bool(mask.any() and error <= 1.e-6)
        cpu_support = reference.wheel_up_force if kind == "flat" else reference.wheel_top_force
        gpu_support = gpu[1:3] if kind == "flat" else gpu[6:8]
        support_error = float(np.max(np.abs(cpu_support - gpu_support)))
        if side:
            agrees = reference.face_force > 1. and gpu[4] > 1. and not np.any(gpu[6:8] > 1.)
        else:
            agrees = (reference.face_force < 1. and gpu[4] < 1. and min(cpu_support) > 1.
                      and min(gpu_support) > 1. and np.allclose(cpu_support, gpu_support, rtol=.02, atol=2.)
                      and (kind != "flat" or not gpu[6:8].any()))
        rows.append(dict(world=i, kind=kind, side_face_fixture=side, passed=bool(indexed_correctly and agrees),
                         cpu_support_n=cpu_support, warp_support_n=gpu_support.tolist(),
                         cpu_face_n=reference.face_force, warp_face_n=float(gpu[4]),
                         support_error_n=support_error, indexed_vs_native_normal_error_n=error))
    return dict(passed=all(row["passed"] for row in rows), cases=rows)
