"""Build the unchanged259 frame ONLY from predicted224 state and known commands.

The original Fudan contact API consumes WORLD forces, so the learned BODY suffix
is rotated back by predicted R. No future/live PhysX measurement is queried.
"""
import torch
from measured_state224_v268 import FORCE_SCALE_N, require, tensor_field


def predicted_literal_frame(previous_state, state, commands, *, environment_origins, layout, binding,
                            synthetic_CPU_test=False):
    binding.validate(synthetic_CPU_test=synthetic_CPU_test)
    layout.validate(previous_state)
    layout.validate(state)
    p, R, v, w, q, dq, aux = state
    require(p.ndim == 2, 'One current imagined step [N,...] required')
    n = p.shape[0]
    tensor_field(commands, (n, 4), name='known original Fudan command4', reference=p)
    tensor_field(environment_origins, (n, 3), name='known actual environment origins', reference=p)
    require(previous_state[0].shape == p.shape and
            previous_state[0].device == p.device, 'Previous physical state batch/device differs')
    # Native WM uses wxyz; the original actual SDK frame is xyzw.
    wxyz = layout.geometry.mat_to_quat(R)
    xyzw = wxyz[:, [1, 2, 3, 0]]
    root = torch.cat((p + environment_origins, xyzw, v, w), -1)
    RT = R.transpose(-1, -2)
    body_difference_velocity = (RT @ ((p - previous_state[0]) / .02).unsqueeze(-1)).squeeze(-1)
    body_angular_velocity = (RT @ w.unsqueeze(-1)).squeeze(-1)
    gravity_world = p.new_tensor([0., 0., -1.]).expand_as(p)
    gravity_body = (RT @ gravity_world.unsqueeze(-1)).squeeze(-1)
    body_forces = aux[:, 58:151].reshape(n, 31, 3) * FORCE_SCALE_N
    world_forces = torch.einsum('nij,nkj->nki', R, body_forces)
    # Original aux54[18:48] already holds all30 applied efforts.
    torques = aux[:, 18:48][:, list(binding.motor_ids_reward_order)]
    return dict(commands=commands, root_states=root,
        base_lin_vel=body_difference_velocity, base_ang_vel=body_angular_velocity,
        projected_gravity=gravity_body, L0=aux[:, 54:56], theta0=aux[:, 56:58],
        torques=torques, contact_forces=world_forces)
