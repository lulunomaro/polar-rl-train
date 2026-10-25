"""One bounded pure-spin rolling/support cost; no sensor or dynamics writes.

The point is the input wheel's midplane-circle bottom, not a PhysX manifold.
Load weighting uses the existing physical impulse accumulated over10ms. This
control snapshot is not the substep contact diagnosis and does not replace it.
"""
import torch

PROFILE = "loaded_rolling_v1"


def consistency_cost(point_velocity, axle_world, normal_force_mean, command,
                     speed_scale=.15, yaw_min=3.5, support_weight=.25):
    up = torch.zeros_like(axle_world)
    up[..., 2] = 1.
    rolling = torch.cross(axle_world, up, dim=-1)
    rolling = rolling / rolling.norm(dim=-1, keepdim=True).clamp_min(1e-8)
    signed = (point_velocity * rolling).sum(-1)
    load = (normal_force_mean.clamp_min(0.) / 10.).clamp(0., 1.)
    squared = (signed / speed_scale).square().clamp_max(4.)
    rolling_cost = (squared * load).sum(-1) / load.sum(-1).clamp_min(1.)
    support_deficit = (1. - load).mean(-1)
    pure = (command[:, :2].abs().max(-1).values <= 1e-6) & (command[:, 2].abs() >= yaw_min)
    cost = torch.where(pure, rolling_cost + support_weight * support_deficit, 0.)
    return cost, signed, load, pure


class RollingConsistency:
    def __init__(self, env):
        import numpy as np
        import mod4_task as task
        from contact_geometry import ControlGeometry
        self.env = env
        self.robot = env.scene["robot"]
        assert task.TERRAIN == "flat"
        from physics_clock import validate_clock
        validate_clock(float(env.physics_dt), float(env.step_dt))
        geometry = ControlGeometry(env, task.USD_PATH)
        self.ids = geometry.ids
        centers, axes, radii, meta = [], [], [], []
        for points in geometry.vertices[0]:
            p = points.cpu().numpy().astype("float64")
            center = p.mean(0)
            eigenvalues, basis = np.linalg.eigh(np.cov((p - center).T))
            axis = basis[:, 0]
            axial = (p - center) @ axis
            radial = p - center - axial[:, None] * axis
            radius = float(np.linalg.norm(radial, axis=1).max())
            half_width = float((axial.max() - axial.min()) / 2)
            assert .06 < radius < .067 and .005 < half_width < .015
            centers.append(center)
            axes.append(axis)
            radii.append(radius)
            meta.append(dict(center_link_m=center.tolist(), axle_link=axis.tolist(),
                             input_mesh_radius_m=radius, half_width_m=half_width))
        kw = dict(device=env.device, dtype=torch.float32)
        self.center = torch.tensor(np.array(centers), **kw)[None]
        self.axle = torch.tensor(np.array(axes), **kw)[None]
        self.radius = torch.tensor(radii, **kw)[None, :, None]
        self.metadata = dict(version=PROFILE, geometry=meta, load_source="actual %.9gs impulse /10ms" % env.physics_dt,
                             point_source="input-mesh midplane circle bottom; not manifold",
                             evaluation_gate_changed=False, dynamics_changed=(env.physics_dt != float(task.CONTRACT["physics_dt_s"])))
        import json
        print("ROLLING_CONSISTENCY_CONFIG " + json.dumps(self.metadata), flush=True)

    def values(self, speed_scale=.15, yaw_min=3.5, support_weight=.25):
        from isaaclab.utils.math import quat_apply
        env, robot = self.env, self.robot
        n = env.num_envs
        q = robot.data.body_quat_w[:, self.ids]
        apply = lambda v: quat_apply(q.reshape(-1, 4), v.expand(n, -1, -1).reshape(-1, 3)).reshape(n, 2, 3)
        axis = apply(self.axle)
        center_arm = apply(self.center)
        up = torch.zeros_like(axis)
        up[..., 2] = 1.
        radial_down = -(up - (up * axis).sum(-1, keepdim=True) * axis)
        radial_down = radial_down / radial_down.norm(dim=-1, keepdim=True).clamp_min(1e-8)
        support_arm = center_arm + self.radius * radial_down
        # body_link_lin_vel_w is the velocity at the SAME link reference as support_arm.
        velocity = robot.data.body_link_lin_vel_w[:, self.ids] + torch.cross(
            robot.data.body_ang_vel_w[:, self.ids], support_arm, dim=-1)
        capture = getattr(env, "_integrated_contact", None)
        if capture is None:
            raise RuntimeError("Rolling adaptation requires validated integrated wheel impulse")
        load = capture.impulse / env.step_dt
        command = env.command_manager.get_command("twist")
        cost, signed, weights, enabled = consistency_cost(
            velocity, axis, load, command, speed_scale, yaw_min, support_weight)
        self.last = dict(cost=cost.detach(), rolling_signed=signed.detach(),
                         mean_force=load.detach().clone(), load_weight=weights.detach(),
                         enabled=enabled.detach(), point_velocity=velocity.detach(),
                         support_arm=support_arm.detach(), axle_world=axis.detach())
        return cost


def spin_contact_consistency(env, speed_scale=.15, yaw_min=3.5, support_weight=.25):
    if not hasattr(env, "_spin_rolling_consistency"):
        env._spin_rolling_consistency = RollingConsistency(env)
    return env._spin_rolling_consistency.values(speed_scale, yaw_min, support_weight)
