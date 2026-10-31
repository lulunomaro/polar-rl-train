"""Pure Torch named-state/observation mapping. No SDK or pretrained policy.

The foreign reward constants remain in the separately frozen literal harness.
MOD4's virtual leg is measured from its own authored hip anchor to wheel AXIS,
never from a collider/AABB centre or the other robot's serial-link lengths.
"""
import math
import torch

CANONICAL = ("left_crank", "left_hip", "left_wheel_spin",
             "right_crank", "right_hip", "right_wheel_spin")
NATIVE = ("left_crank", "left_hip", "right_crank", "right_hip",
          "left_wheel_spin", "right_wheel_spin")
LEGS = (0, 1, 3, 4)
WHEEL_BODIES = ("left_wheel", "right_wheel")
GEOMETRY_DEFINITION = (
    "own MOD4 authored hip local_pos0 on chassis -> actual main-wheel BODY ORIGIN/axis; "
    "v_b=R_chassis^T*(p_wheel-p_chassis)-hip_anchor_b; "
    "L0=sqrt(v_b.x^2+v_b.z^2) metres; theta0=atan2(-v_b.x,-v_b.z) radians, "
    "zero downward, positive wheel rearward; sagittal projection ignores lateral offset; "
    "equivalent atan2(down,forward)-pi/2 on the normal downward branch; "
    "no Fudan rods, per-leg target retargeting, wheel-surface radius or body-rise substitution"
)


def named_indices(names, wanted):
    if len(set(names)) != len(names) or not set(wanted).issubset(names):
        raise ValueError("actual unique named order lacks required axes/bodies")
    return [names.index(n) for n in wanted]


def canonical_to_native(actions):
    return actions[:, named_indices(list(CANONICAL), NATIVE)]


def sdk_quat_to_xyzw(q, order):
    if order == "xyzw":
        return q
    if order == "wxyz":
        return q[..., (1, 2, 3, 0)]
    raise ValueError("ROOT must bind actual SDK quaternion order; historical labels are insufficient")


def rotation_xyzw(q):
    # Normalize only a read-only geometric copy, never write a physical state.
    if not bool(torch.isfinite(q).all()) or bool((q.norm(dim=-1) < .5).any()):
        raise ValueError("invalid source quaternion")
    q = q / q.norm(dim=-1, keepdim=True)
    x, y, z, w = q.unbind(-1)
    return torch.stack((1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w),
                        2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w),
                        2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)), -1).reshape(*q.shape[:-1], 3, 3)


def world_to_body(R, vector):
    return (R.transpose(-1, -2) @ vector.unsqueeze(-1)).squeeze(-1)


def own_virtual_legs(body_position, chassis_R, body_names, hip_anchors):
    chassis = body_position[:, named_indices(body_names, ("chassis",))[0]]
    wheel = body_position[:, named_indices(body_names, WHEEL_BODIES)]
    delta = torch.einsum("nji,nkj->nki", chassis_R, wheel-chassis[:, None])
    v = delta - hip_anchors.to(delta)[None]
    length = torch.sqrt(v[..., 0].square()+v[..., 2].square())
    theta = torch.atan2(-v[..., 0], -v[..., 2])
    return length, theta


def observation25_and_privileged141(*, base_lin_vel, base_ang_vel, projected_gravity,
                                   commands, q6, dq6, default_q6, raw_default_q6,
                                   actions6, last_actions6x2, last_dq6, torques6,
                                   root_height, base_mass, base_com, friction, restitution):
    """Original slot/scales, declared B direct-SDK dq instead of foreign pos-diff.

    Both fields are a known z=0 plane: all 77 measured terrain heights are zero.
    Privileged is assembled before public noise and public clipping.
    """
    n = q6.shape[0]
    clean = torch.cat((base_ang_vel*.25, projected_gravity,
                       commands[:, :3]*q6.new_tensor([3., .25, 5.]),
                       (q6-default_q6)[:, LEGS], dq6*.05, actions6), -1)
    heights = (root_height[:, None]-.5).clamp(-1., 1.).expand(n, 77)*5.
    priv = torch.cat((base_lin_vel*3., clean, last_actions6x2[..., 0],
                      last_actions6x2[..., 1], (last_dq6-dq6)/.01*.0025,
                      heights, torques6*.05,
                      (base_mass-base_mass.mean()).reshape(n, 1), base_com,
                      default_q6-raw_default_q6, friction.reshape(n, 1),
                      restitution.reshape(n, 1)), -1)
    if clean.shape != (n, 25) or priv.shape != (n, 141):
        raise ValueError("original PPO observation width mismatch")
    if not bool(torch.isfinite(clean).all() and torch.isfinite(priv).all()):
        raise ValueError("nonfinite measured observation")
    return clean, priv


def public_noise(clean, enabled):
    if not enabled:
        return clean.clamp(-100., 100.)
    half = clean.new_tensor([.05]*6+[0.]*3+[.02]*4+[.075]*6+[0.]*6)
    return (clean+(2*torch.rand_like(clean)-1)*half).clamp(-100., 100.)


class FudanCommandClock:
    """Original no-heading command sampling, reset and pre-reward 20s clock.

    The original's ranges start as vx +/-2.1, yaw +/-2, height .12..15.
    Exact upstream selected config has commands.curriculum=False and
    heading_command=False; this is not an added curriculum override.
    """
    def __init__(self, n, device):
        self.commands = torch.zeros(n, 4, device=device)

    def reset(self, ids):
        for column, (lo, hi) in enumerate(((-2.1, 2.1), (-2., 2.), (.12, .15))):
            self.commands[ids, column] = (hi-lo)*torch.rand(len(ids), device=self.commands.device)+lo

    def before_reward(self, episode_lengths):
        self.reset(((episode_lengths % 2000) == 0).nonzero(as_tuple=False).flatten())


class ObservationMemory:
    """External public history and original two-action memory; no plant writes."""
    def __init__(self, n, device):
        self.actions = torch.zeros(n, 6, device=device)
        self.last_actions = torch.zeros(n, 6, 2, device=device)
        self.history = torch.zeros(n, 125, device=device)

    def reset(self, ids):
        # Upstream reset_idx clears LAST actions, not current issued self.actions.
        self.last_actions[ids] = 0

    def append_observation(self, public, reset_ids=(), reset_clean=None):
        if len(reset_ids):
            if reset_clean is None:
                raise ValueError("reset history needs original clean proprioception")
            self.history[reset_ids] = reset_clean[reset_ids].repeat(1, 5)
        self.history = torch.cat((self.history[:, 25:], public), -1)

    def finish_control(self):
        self.last_actions[..., 1] = self.last_actions[..., 0]
        self.last_actions[..., 0] = self.actions
