"""CPU mathematical verification only. No Isaac, policy, contact or PPO claim."""
import json
import math
from pathlib import Path
import torch
from spin_translation_math import body_command, project_velocity


def main():
    torch.set_num_threads(1)
    dtype = torch.float64
    phase = torch.arange(16384, dtype=dtype) * (2 * math.pi / 16384)
    rows = []
    for target in [.15, .3, .5]:
        for direction in [0., .8, math.pi / 2, -2.2]:
            for sign in [-1., 1.]:
                yaw = sign * phase + .37
                phi = torch.full_like(yaw, direction)
                vx, vy = body_command(target, phi, yaw)
                velocity = torch.stack((vx * yaw.cos(), vx * yaw.sin()), -1)
                along, cross = project_velocity(velocity, phi)
                error = abs(float(along.mean()) - target)
                assert error < 1e-12
                assert abs(float(cross.mean())) < 1e-12
                assert float(vy.abs().max()) == 0
                assert float(vx.abs().max()) <= 2 * target + 1e-12
                rows.append({'goal_m_s': target, 'direction_rad': direction, 'yaw_sign': sign,
                             'ideal_mean_along_m_s': float(along.mean()), 'error_m_s': error,
                             'instantaneous_speed_peak_m_s': float(vx.abs().max())})
    # A body speed cap may prevent the requested net progress: preserve the failure.
    vx, _ = body_command(.5, torch.zeros_like(phase), phase, body_speed_limit=.5)
    clipped_along = float((vx * phase.cos()).mean())
    assert clipped_along < .5
    # Negative control: constant body vx plus yaw travels a circle, net progress zero.
    circular = float((.5 * phase.cos()).mean())
    assert abs(circular) < 1e-12
    out = {'cpu_math_pass': True, 'cases': len(rows), 'rows': rows,
           'capped_body_0p5_ideal_mean_along_m_s': clipped_along,
           'constant_body_vx_spin_net_progress_m_s': circular,
           'final_world_goal_m_s': .5, 'unclipped_final_body_peak_m_s': 1.,
           'isaac_runtime_accepted': False, 'policy_accepted': False, 'ppo_accepted': False,
           'production_deployed': False}
    Path('IDEAL_KINEMATICS_VERIFICATION.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in out.items() if k != 'rows'}))


if __name__ == '__main__':
    main()
