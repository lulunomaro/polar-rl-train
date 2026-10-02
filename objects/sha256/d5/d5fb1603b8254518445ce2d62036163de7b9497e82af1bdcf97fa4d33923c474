"""Reproduce control/reward contradictions from current source without launching Isaac."""
import ast
import functools
import json
from pathlib import Path
import sys
import torch

code = Path(sys.argv[1])
scope = {'torch': torch, 'functools': functools}
for filename, name in [('route_isaac.py', '_run_brake_scale'),
                       ('mod4_task.py', '_clip_reward_term')]:
    tree = ast.parse((code / filename).read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(code / filename), 'exec'), scope)

errors = torch.tensor([0.5, 1., 1.2, 1.5, 2., 3.])
weighted = scope['_clip_reward_term'](lambda env: errors.square(), -2., 2.5)(None) * -2.
braking = []
for speed in [.3, .6, 1.2]:
    d = torch.tensor([3.5], dtype=torch.float64)
    crossed = False
    for _ in range(1500):
        d -= speed * scope['_run_brake_scale'](d, .35, 1.2) * .01
        crossed |= bool((d < .35).any())
    braking.append({'speed_m_s': speed, 'distance_after_15s_m': float(d),
                    'entered_goal_region_with_perfect_velocity_tracking': crossed})
print(json.dumps({
    'l2_errors_m_s': errors.tolist(), 'weighted_l2_before_dt': weighted.tolist(),
    'clip_saturation_error_m_s': (2.5/2.)**.5,
    'height_kernel_at_measured_mean': {
        'kp2500': float(torch.exp(torch.tensor(-((.194918-.34)/.06)**2))),
        'kp60': float(torch.exp(torch.tensor(-((.234409-.34)/.06)**2)))},
    'braking': braking,
    'six_action_vector_rms_to_scalar_factor': 6**.5,
}, indent=2))
