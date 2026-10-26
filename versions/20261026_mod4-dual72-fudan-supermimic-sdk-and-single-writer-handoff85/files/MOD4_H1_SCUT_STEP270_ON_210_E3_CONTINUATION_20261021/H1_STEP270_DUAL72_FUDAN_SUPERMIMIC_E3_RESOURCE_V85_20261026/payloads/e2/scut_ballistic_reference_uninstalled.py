# Copyright (c) 2026 SCUTRobotLab, SPDX-License-Identifier: MIT.
# Original ballistic reference body copied without AST changes from fixed commit
# b8ff79f3df855faf9dc92f4a282bd80c42649466. MOD4 wrapper and target mapping
# are separate below. CPU candidate only; no force/torque assistance or air reset.
import torch
from types import SimpleNamespace
def _get_ballistic_reference(self, env, cfg: dict) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    traj_cfg = cfg.get('trajectory', {})
    gravity = max(float(traj_cfg.get('gravity', 9.81)), 1e-06)
    push_start_height = float(traj_cfg.get('push_start_height', 0.2))
    release_height = float(traj_cfg.get('release_height', 0.38))
    peak_height = env.jump_takeoff_ref_target_height
    timing_mode = traj_cfg.get('tuck_timing_mode', 'dynamic_push_time')
    if timing_mode == 'fixed_tuck_time':
        push_time = torch.full_like(peak_height, max(float(traj_cfg.get('fixed_tuck_time_s', 0.14)), env.step_dt))
        discriminant = torch.square(gravity * push_time) + 8.0 * gravity * torch.clamp(peak_height - push_start_height, min=0.0)
        release_vel_z = 0.5 * (-gravity * push_time + torch.sqrt(discriminant))
        raw_release_height = push_start_height + 0.5 * release_vel_z * push_time
        max_release_height = float(traj_cfg.get('max_release_height', release_height))
        release_height_for_flight = torch.clamp(raw_release_height, max=max_release_height)
        release_vel_z = torch.sqrt(torch.clamp(2.0 * gravity * (peak_height - release_height_for_flight), min=0.0))
    else:
        flight_peak_time = torch.sqrt(torch.clamp(2.0 * (peak_height - release_height) / gravity, min=0.0))
        release_vel_z = gravity * flight_peak_time
        push_distance = max(release_height - push_start_height, 0.0)
        push_time = torch.where(release_vel_z > 1e-06, 2.0 * push_distance / release_vel_z, torch.zeros_like(release_vel_z))
        release_height_for_flight = torch.full_like(peak_height, release_height)
    push_accel = torch.where(push_time > 1e-06, release_vel_z / push_time, torch.zeros_like(release_vel_z))
    elapsed = torch.clamp(env.jump_takeoff_phase_time, min=0.0)
    push_elapsed = torch.minimum(elapsed, torch.clamp(push_time, min=0.0))
    push_height = push_start_height + 0.5 * push_accel * torch.square(push_elapsed)
    push_vel_z = push_accel * push_elapsed
    flight_elapsed = torch.clamp(elapsed - push_time, min=0.0)
    flight_height = release_height_for_flight + release_vel_z * flight_elapsed - 0.5 * gravity * torch.square(flight_elapsed)
    flight_vel_z = release_vel_z - gravity * flight_elapsed
    ref_height = torch.where(elapsed <= push_time, push_height, flight_height)
    ref_vel_z = torch.where(elapsed <= push_time, push_vel_z, flight_vel_z)
    return (ref_height, ref_vel_z, push_time)

def reference(*,elapsed,peak_height,push_start_height,release_height,control_dt=.01,
              timing_mode='dynamic_push_time',fixed_tuck_time_s=.14):
    if not all(torch.isfinite(v).all() for v in (elapsed,peak_height)):
        raise ValueError('nonfinite trajectory input')
    if not (peak_height>release_height).all() or not release_height>push_start_height:
        raise ValueError('Require peak>actual release>actual push-start height')
    if timing_mode not in ('dynamic_push_time','fixed_tuck_time') or control_dt!=.01:
        raise ValueError('Unqualified H1 timing mode or 100Hz control clock')
    env=SimpleNamespace(jump_takeoff_ref_target_height=peak_height,
                        jump_takeoff_phase_time=elapsed,step_dt=control_dt)
    cfg={'trajectory':dict(gravity=9.81,push_start_height=push_start_height,
         release_height=release_height,tuck_timing_mode=timing_mode,
         fixed_tuck_time_s=fixed_tuck_time_s,max_release_height=release_height)}
    return _get_ballistic_reference(None,env,cfg)

def peak_body_height_from_actual_wheel_geometry(*,body_world_z,wheel_bottom_world_z,
                                               reference_ground_world_z,
                                               platform_top_world_z,margin_m):
    if not all(torch.isfinite(v).all() for v in (body_world_z,wheel_bottom_world_z,
             reference_ground_world_z,platform_top_world_z)):
        raise ValueError('nonfinite actual geometry')
    if margin_m<0 or not ((platform_top_world_z-reference_ground_world_z)>=.270).all():
        raise ValueError('Platform below the human 270mm minimum')
    offset=(body_world_z-wheel_bottom_world_z.amin(-1)).clamp_min(0)
    return platform_top_world_z-reference_ground_world_z+offset+margin_m
