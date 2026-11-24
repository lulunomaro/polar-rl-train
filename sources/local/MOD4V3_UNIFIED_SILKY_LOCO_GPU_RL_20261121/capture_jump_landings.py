"""Record measured two-wheel touchdowns for flat-course locomotion resets."""
from argparse import ArgumentParser
from itertools import product
from pathlib import Path

import mujoco as mj
import numpy as np
import torch

from eval_silky_rm27 import HERE, StrictJudge, put
from play_unified_soft_moe import PlayerPolicy, PlayerSimulation, player_metadata


def wheels_supported(sim, judge):
    supported = set()
    for idx in range(sim.d.ncon):
        contact = sim.d.contact[idx]
        a, b = map(int, contact.geom)
        if a in judge.terrain:
            a, b = b, a
        if a in judge.tires and b in judge.terrain:
            mj.mj_contactForce(sim.m, sim.d, idx, judge.force_buffer)
            if judge.force_buffer[0]*abs(contact.frame[2]) >= 5.:
                supported.add(a)
    return len(supported)


def sample(sim, height, speed, settle):
    sim.reset_at_spawn()
    sim.target_h = height
    sim.max_vx = speed
    keys = {'w'} if speed else set()
    for _ in range(settle):
        sim.step(keys)
    ground = sim.ground_z(*sim.d.qpos[:2])
    judge = StrictJudge(sim, {'course': 'flat'}, 0., 1, ground)
    sim.request_jump()
    air = longest_air = 0
    while sim.jump_rem:
        sim.step(keys)
        supported = wheels_supported(sim, judge)
        clearance = float(sim.d.geom_xpos[sim.tire_gids, 2].min())-.0625-ground
        air = air+1 if not supported and clearance > .02 else 0
        longest_air = max(longest_air, air)
        if (longest_air >= 6 and sim.peak_rim_clearance_cm >= 15.
                and supported == 2 and sim.closure_mm <= 2.):
            return dict(touchdown_s=(sim.unified.jump_frames-sim.jump_rem)*.020,
                        airborne_s=longest_air*.020, clearance_cm=sim.peak_rim_clearance_cm,
                        closure_mm=sim.closure_mm, height_cmd=height, speed_cmd=speed, settle_steps=settle)
    return None


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('checkpoint', type=Path)
    parser.add_argument('--out', type=Path, default=HERE/'JUMP_LANDING_POOL.json')
    args = parser.parse_args()
    torch.set_num_threads(1)
    policy = PlayerPolicy(args.checkpoint)
    sim = PlayerSimulation(policy, policy.loco.sha, show_viewer=False)
    rows = []
    conditions = tuple(product((.26, .28, .30), (0., .55, .90), (70, 83)))
    try:
        sim.load_map(player_metadata('flat'))
        joints = [sim.m.joint(i) for i in range(sim.m.njnt)
                  if sim.m.jnt_type[i] in (mj.mjtJoint.mjJNT_HINGE, mj.mjtJoint.mjJNT_SLIDE)]
        pos = [int(j.qposadr[0]) for j in joints]
        vel = [int(j.dofadr[0]) for j in joints]
        for height, speed, settle in conditions:
            info = sample(sim, height, speed, settle)
            if info is None:
                continue
            d = sim.d
            ground = sim.ground_z(*d.qpos[:2])
            rotation = np.empty(9)
            mj.mju_quat2Mat(rotation, d.qpos[3:7])
            root = [0., 0., float(d.qpos[2])-ground, *d.qpos[3:7], *d.qvel[:3],
                    *(rotation.reshape(3, 3) @ d.qvel[3:6])]
            joint_position = d.qpos[pos].copy()
            wheel = [i for i, joint in enumerate(joints) if joint.name in ('left_wheel_joint', 'right_wheel_joint')]
            joint_position[wheel] = (joint_position[wheel]+np.pi) % (2*np.pi)-np.pi
            rows.append(dict(info, root_state=root, joint_position=joint_position.tolist(),
                             joint_velocity=d.qvel[vel].tolist()))
    finally:
        sim.close()
    if {row['speed_cmd'] == 0. for row in rows} != {False, True}:
        raise RuntimeError('Need measured static and running touchdowns')
    put(args.out, dict(format='mod4v3_jump_landing_v1', physics_hz=400, capture_hz=50,
                      rollout_candidates=len(conditions), checkpoint_sha256=policy.loco.sha,
                      jump_sha256=policy.jump_sha, joint_names=[joint.name for joint in joints], landings=rows))
    print(f'{len(rows)}/{len(conditions)} measured touchdowns', flush=True)


if __name__ == '__main__':
    main()
