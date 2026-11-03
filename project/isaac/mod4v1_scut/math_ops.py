"""Quaternion boundary: detect the actual SDK order; pinned SCUT used wxyz.

All imported SCUT formulas receive wxyz. Simulator data is converted by RobotView.
These torch operations also allow the exact reward code to run without Isaac.
"""
import torch


def wrap_to_pi(x):
    return (x + torch.pi) % (2 * torch.pi) - torch.pi


def quat_inv(q):
    return torch.cat((q[..., :1], -q[..., 1:]), -1) / q.square().sum(-1, keepdim=True)


def quat_apply(q, v):
    xyz = q[..., 1:]
    t = 2 * torch.cross(xyz, v, dim=-1)
    return v + q[..., :1] * t + torch.cross(xyz, t, dim=-1)


def quat_apply_inverse(q, v):
    return quat_apply(quat_inv(q), v)


def quat_from_euler_xyz(r, p, y):
    cr, cp, cy = (torch.cos(a / 2) for a in (r, p, y))
    sr, sp, sy = (torch.sin(a / 2) for a in (r, p, y))
    return torch.stack((cr*cp*cy+sr*sp*sy, sr*cp*cy-cr*sp*sy,
                        cr*sp*cy+sr*cp*sy, cr*cp*sy-sr*sp*cy), -1)


def euler_xyz_from_quat(q):
    w, x, y, z = q.unbind(-1)
    return (torch.atan2(2*(w*x+y*z), 1-2*(x*x+y*y)),
            torch.asin((2*(w*y-z*x)).clamp(-1, 1)),
            torch.atan2(2*(w*z+x*y), 1-2*(y*y+z*z)))


def detect_sdk_quaternion_order(data, tensor=lambda value: value):
    """Match actual SDK gravity AND heading; never infer order from SDK version."""
    raw = tensor(data.root_quat_w)
    gravity = tensor(data.projected_gravity_b)
    heading = tensor(data.heading_w)
    down = torch.zeros_like(gravity)
    down[:, 2] = -1.
    matches = []
    errors = {}
    for order, q in [('wxyz', raw), ('xyzw', raw[:, [3, 0, 1, 2]])]:
        gravity_error = (quat_apply_inverse(q, down)-gravity).abs().max()
        _, _, yaw = euler_xyz_from_quat(q)
        heading_error = wrap_to_pi(yaw-heading).abs().max()
        errors[order] = dict(gravity=float(gravity_error), heading=float(heading_error))
        if float(gravity_error) < 1.e-4 and float(heading_error) < 1.e-4:
            matches.append(order)
    if len(matches) != 1:
        raise RuntimeError('Actual SDK quaternion convention ambiguous/mismatched: '+str(errors))
    return matches[0], errors
