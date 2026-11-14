"""Reject historical failures and non-jumping shortcuts before native admission."""
import ast
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import torch
from autonomous_stair.objective import Outcome, scan_target, task_slots, SCHEMA

T = Path(__file__).resolve().parent
R = T.parents[2]


def frame(state, x, z, *, air, both=True, vz=0., requested=True, failure=False):
    wheel = torch.tensor([[[x, .15, z + .0625], [x, -.15, z + .0625]]])
    force = torch.zeros(1, 2, 3)
    if not air:
        force[0, 0, 2] = 8.
        if both:
            force[0, 1, 2] = 8.
    return state.update(requested=torch.tensor([requested]), wheel=wheel, forces=force,
        all_force=force, edge=torch.tensor([0.]), next_edge=torch.tensor([1.5]),
        ground=torch.zeros(1), height=torch.tensor([.165]), vz=torch.tensor([vz]),
        vx=torch.tensor([.6]), command_vx=torch.tensor([.6]), roll=torch.zeros(1),
        pitch=torch.zeros(1), angular=torch.zeros(1, 3), terminated=torch.tensor([failure]))


def airborne_start(state):
    for _ in range(5):
        frame(state, -.2, .2, air=True, vz=1.)
    frame(state, .2, .2, air=True, vz=-.1)


def main():
    checks = {}
    state = Outcome(1, 'cpu')
    for _ in range(35):
        frame(state, .3, .165, air=False)
    checks['rolling_cannot_pass'] = not bool(state.success[0])
    state = Outcome(1, 'cpu')
    airborne_start(state)
    for _ in range(35):
        frame(state, .3, .165, air=False, both=False)
    checks['one_wheel_cannot_pass'] = not bool(state.success[0])
    state = Outcome(1, 'cpu')
    airborne_start(state)
    for _ in range(24):
        frame(state, .3, .165, air=False)
    checks['less_than_half_second_cannot_pass'] = not bool(state.success[0])
    frame(state, .3, .165, air=False)
    checks['valid_synthetic_sequence_passes'] = bool(state.success[0])
    state = Outcome(1, 'cpu')
    airborne_start(state)
    for _ in range(35):
        frame(state, .3, .165, air=False, failure=True)
    checks['terminated_landing_cannot_pass'] = not bool(state.success[0])
    state = Outcome(1, 'cpu')
    for _ in range(5):
        frame(state, -.5, .2, air=True, vz=1.)
    frame(state, -.3, 0., air=False)
    for _ in range(35):
        frame(state, .3, .165, air=False)
    checks['early_jump_then_roll_cannot_pass'] = not bool(state.success[0])
    x = torch.arange(0., 2.401, .05)
    z = torch.where(x >= .6, .165, 0.) + torch.where(x >= 2.1, .165, 0.)
    hits = torch.stack((x, torch.zeros_like(x), z), -1)[None]
    distance, height, tread = scan_target(hits, torch.zeros(1, 3), torch.zeros(1))
    checks['scan_edge_height_and_depth'] = abs(float(distance) - .6) < .03 and abs(float(height) - .165) < 1e-6 and abs(float(tread) - 1.5) < .03
    distance, height, tread = scan_target(torch.full_like(hits, float('nan')), torch.zeros(1, 3), torch.zeros(1))
    checks['missing_scan_finite'] = bool(torch.isfinite(task_slots(torch.ones(1), torch.zeros(1), distance, height, tread, torch.zeros(1))).all())
    prior = R / 'sources/local/MOD4V3_MUJOCO_JUMP_STEP_20261114/evidence'
    historical = []
    for path in sorted(prior.glob('*/*/trajectory.npz')):
        result_path = path.with_name('RESULT.json')
        if not result_path.exists():
            continue
        result = json.loads(result_path.read_bytes())
        if result.get('flat') or result.get('no_jump'):
            continue
        state = Outcome(1, 'cpu')
        with np.load(path) as data:
            for i in range(len(data['t'])):
                def one(value, dtype=torch.float32):
                    return torch.as_tensor(np.array(value), dtype=dtype).unsqueeze(0)
                force = torch.zeros(1, 2, 3)
                force[0, :, 2] = torch.as_tensor(data['support'][i].astype(float)) * 8.
                contact = force.clone()
                if not bool(data['no_support'][i]):
                    contact[0, 0, 2] = max(float(contact[0, 0, 2]), 2.)
                state.update(requested=one(data['requested'][i], torch.bool), wheel=one(data['wheels'][i]),
                    forces=force, all_force=contact, edge=one(result['step_edge_x_m']),
                    next_edge=one(-1.4000000953674316), ground=torch.zeros(1), height=one(result['step_height_m']),
                    vz=one(data['qvel'][i, 2]), vx=one(data['vx'][i]), command_vx=one(data['command_vx'][i]),
                    roll=one(data['roll'][i]), pitch=one(data['pitch'][i]), angular=one(data['qvel'][i, 3:6]),
                    terminated=torch.zeros(1, dtype=torch.bool))
        historical.append(dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                               original_accepted=result['accepted'], new_accepted=bool(state.success[0])))
    checks['all_31_original_failures_remain_failures'] = len(historical) == 31 and not any(row['new_accepted'] for row in historical)
    for path in T.rglob('*.py'):
        ast.parse(path.read_text(encoding='utf-8-sig'))
    receipt = dict(epoch=time.time(), observation_schema=SCHEMA, checks=checks,
                   passed=all(checks.values()), historical=historical,
                   synthetic_checks_are_not_physical_successes=True, optimizer_updates=0)
    (T / 'evidence').mkdir(exist_ok=True)
    (T / 'evidence/OBJECTIVE_CHECK.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
    print(json.dumps(dict(passed=receipt['passed'], checks=checks, historical_cases=len(historical)), indent=2))
    assert receipt['passed']


if __name__ == '__main__':
    main()
