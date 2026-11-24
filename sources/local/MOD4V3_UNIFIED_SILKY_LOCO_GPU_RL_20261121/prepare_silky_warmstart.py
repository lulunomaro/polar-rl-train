"""Assemble warm-start examples from graduated rollouts and separate replay starts."""
from argparse import ArgumentParser
import json
from pathlib import Path

import mujoco as mj
import numpy as np
import torch

from eval_silky_rm27 import HERE, Replay
from train_silky_loco import put, sha256

STAIR = HERE.parent/'MOD4V3_RL_SINGLE200_FULLDR_5OF5_20261118'
GRADUATED = STAIR/'evidence/final_official_eval200'
CURB = HERE/'evidence/r2_curb_teacher'


def policy_inputs(obs, actions):
    if obs.shape != (len(actions), 35) or actions.shape[1] != 6:
        raise ValueError('Warm-start samples use the released 35-observation, 6-action order')
    if not np.array_equal(obs[1:, 22:28], actions[:-1]):
        raise ValueError('Previous-action continuity mismatch')
    frames = obs.copy()
    frames[:, 28:35] = (1, 0, 0, 0, 0, 0, 0)
    ids = np.maximum(0, np.arange(len(obs))[:, None] - np.arange(11, -1, -1))
    return np.concatenate((frames, frames[ids].reshape(-1, 420)), axis=1, dtype=np.float32)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=HERE/'evidence/softmoe_r2_warmstart')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(1)
    teacher = STAIR/'weights/model_rl_stair_best.pt'
    prior = json.loads((GRADUATED/'RESULT.json').read_text())
    if prior['sha256'] != sha256(teacher) or not prior['formal_protocol'] or prior['passed'] != 5:
        raise ValueError('The recorded five-start rollouts must match the graduated checkpoint')
    order = torch.load(teacher, map_location='cpu', weights_only=False)['action_order']
    example = GRADUATED/'start_+000mm'
    model = mj.MjModel.from_xml_path(str(example/'scene.xml'))
    with np.load(example/'rollout.npz') as raw:
        standing = raw['qpos'][0]
    pose = dict(joint_position={model.joint(j).name: float(standing[model.jnt_qposadr[j]])
                               for j in range(model.njnt) if model.jnt_type[j] != mj.mjtJoint.mjJNT_FREE},
                height_m=float(standing[2]), command_height_m=.4091)
    inputs, targets, phases, sources = [], [], [], []

    def add(obs, actions, phase, source):
        inputs.append(policy_inputs(obs, actions))
        targets.append(actions)
        phases.append(phase)
        sources.append(dict(source=source, frames=len(obs), by_expert=np.bincount(phase, minlength=4).tolist()))

    for row in prior['rows']:
        assert row['success'] and row['physical_stable_event']
        path = GRADUATED/f"start_{row['start_offset_mm']:+04d}mm"/'rollout.npz'
        with np.load(path) as raw:
            obs, actions, trace = raw['obs'], raw['actions'], raw['trace']
            assert np.all(obs[:, 29] == 1.)
            phase = np.where(trace[:, 1] >= 1.5, 3, 2)
            add(obs, actions, phase, str(path.relative_to(HERE.parent)))

    # Reuse the same teacher's independent 110 mm physical holds. These
    # samples qualify for imitation via wheel support, not its speed score.
    curb = json.loads((CURB/'RESULT.json').read_text())
    if curb['sha256'] != prior['sha256'] or curb['step_height_m'] != .11:
        raise ValueError('Unexpected 110 mm teacher source')
    for row in curb['rows']:
        if not row['physical_stable_event']:
            continue
        path = CURB/f"start_{row['start_offset_mm']:+04d}mm"/'rollout.npz'
        with np.load(path) as raw:
            obs, actions, trace = raw['obs'], raw['actions'], raw['trace']
            phase = np.where(trace[:, 1] >= 1.5, 3, 1)
            add(obs, actions, phase, str(path.relative_to(HERE.parent)))

    native = STAIR/'bootstrap_replay/elegant_r2_clean'
    for path in sorted(native.glob('*.npz')):
        with np.load(path) as raw:
            match = json.loads(str(raw['metadata_json']))
            frames, phase = raw['frames'], raw['phases']
            obs, actions = frames[:, :35], frames[:, 455:]
            if (not match['formal_evaluation_pass'] or match['physics_dt_s'] != .0025
                    or match['history_H'] != 12 or not np.array_equal(obs[1:, 22:28], actions[:-1])):
                continue
            np.testing.assert_array_equal(obs, frames[:, 420:455])
            add(obs, actions, np.where(phase == 3, 3, 2), str(path.relative_to(HERE.parent)))

    # These training-only starts have disjoint offsets from the published
    # serial-step evaluation and its RMUC approaches.
    cases = [
        ('flat', 0., .4091, 0., (-.62, 0.)),
        ('flat', .58, .4091, 0., (-.62, 0.)),
        ('flat', 1.30, .30, 0., (-.62, 0.)),
        ('flat', -1.20, .31, 0., (-.62, 0.)),
        ('flat', 0., .29, 0., (-.62, 0.)),
        ('rough_L9', -.72, .32, -2., (-.31, -.62)),
        ('rough_L9', .72, .39, 2., (-.31, -.62)),
        ('rough_L9', 1.25, .40, 0., (.31, -.62)),
        ('curb_11', .65, .35, 0., (.33, .04)),
        ('curb_11', .90, .40, 0., (.27, -.08)),
        ('curb_11', 1.25, .31, 2., (.28, .06)),
        ('step_20', .58, .4091, 0., (.36, .06)),
        ('step_20', .60, .4091, 0., (.29, -.12)),
        ('step_20', .72, .39, -4., (.21, .12)),
        ('step_20', .90, .40, 0., (.29, 0.)),
        ('step_20', .90, .4091, 0., (.16, 0.)),
        ('step_20', 1.15, .40, 5., (.27, .07)),
        ('oblique_20', .80, .40, 0., (.27, -.06)),
        ('oblique_20', 1.05, .40, -8., (.28, .04)),
        ('rm27_west', .86, .40, 0., (-.08, 0.)),
        ('rm27_east', .86, .40, 0., (-.08, 0.)),
        ('rm27_west_400', .90, .41, 0., (-.05, 0.)),
        ('rm27_east_400', .90, .41, 0., (-.05, 0.)),
    ]
    trials = []
    for index, (course, speed, height, yaw, offset) in enumerate(cases):
        name = 'SELECTED_E0' if course in ('flat', 'rough_L9') else 'R61'
        replay = Replay(name, course, args.out/'maps')
        wz = 1.1 if index == 4 else 0.
        case = dict(id=f'warm_{index:02d}', course=course, speed=speed, height=height, yaw_deg=yaw,
                    offset=offset, seconds=3.8, settle_s=.65, wz=wz, task=None, edge_sign=1)
        obs, actions, ticks = [], [], []

        def capture(observation, action, judge):
            obs.append(observation.copy())
            actions.append(action.copy())
            ticks.append(judge.tick)

        row, _ = replay.run(case, policy_sample=capture)
        trials.append(dict(id=case['id'], course=course, supported_400hz=row['physical_both_wheels_400hz'],
                           stable_seconds=row['stable_seconds_400hz'], failure=row['failure']))
        print(trials[-1], flush=True)
        if row['failure'] or not any(seconds >= .40 for seconds in row['stable_seconds_400hz']):
            continue
        obs, actions, ticks = np.array(obs), np.array(actions), np.array(ticks)
        phase = np.full(len(obs), 0 if course == 'flat' else 1 if course in ('rough_L9', 'curb_11') else 2)
        if phase[0] == 2:
            first = next((tick for tick in reversed(replay.last_support_tick) if tick is not None), None)
            if first is not None:
                phase[ticks >= first+80] = 3
        add(obs, actions, phase, f'{name}/{case["id"]}')
    np.savez_compressed(args.out/'WARMSTART_DATA.npz', inputs=np.concatenate(inputs),
                       actions=np.concatenate(targets), expert=np.concatenate(phases))
    put(args.out/'WARMSTART_SOURCE.json', dict(action_order=order, teacher_sha256=sha256(teacher),
        clip_action=6., standing_pose=pose, data_sha256=sha256(args.out/'WARMSTART_DATA.npz'),
        sources=sources, trials=trials))


if __name__ == '__main__':
    main()
