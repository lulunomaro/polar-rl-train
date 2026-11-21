# -*- coding: utf-8 -*-
"""SCUT (华南虎 WheelBipe V14_2) compatible gimbal control & folding adapter for MOD4v4gemini.

Works with both NumPy (MuJoCo) and PyTorch (Isaac Lab / Newton) without importing simulator globals at module load.
Because MOD4v4gemini aligns gimbal_yaw_joint=0 with chassis +X (and gimbal_yaw_link +X with barrel forward),
SCUT's world-heading lock PD and gimbal-frame spin-translate transforms work with zero angle offset.
"""
from __future__ import annotations
import math

DM4310_SPEC = {
    "model": "DM-J4310-2EC",
    "bus_voltage_v": 24.0,
    "gear_ratio_internal": 10.0,
    "external_ratio": 1.0,                 # Yaw: 51T:51T synchronous belt; Fold & Pitch: direct coaxial
    "continuous_torque_nm": 3.0,
    "peak_torque_nm": 7.0,
    "rated_speed_rad_s": 120.0 * 2.0 * math.pi / 60.0,     # 12.56637 rad/s
    "no_load_speed_rad_s": 200.0 * 2.0 * math.pi / 60.0,   # 20.94395 rad/s
    "rotor_inertia_kg_m2": 1.8e-5,
    "output_armature_kg_m2": 0.0018,
    "envelope_intercept_nm": 7.5,
    "envelope_slope_nm_s_rad": 3.0 / ((200.0 - 120.0) * 2.0 * math.pi / 60.0),
}

# Joint travel & coupled clearance bounds (radians)
FOLD_RANGE_RAD = (-0.558505360638, 0.951204442337)   # [-32.0 deg, +54.5 deg]
PITCH_RANGE_RAD = (-0.942477796077, 0.959931088597)  # [-54.0 deg, +55.0 deg]
COUPLED_TENDONS = (
    # (fold_coef, lower_rad, upper_rad) for fold_coef * q_fold + 1.0 * q_pitch
    (1.27, -0.401425727959, 3.49065850399),   # gimbal_chassis_clearance
    (0.605, -0.363028484415, 3.49065850399),  # gimbal_cover_clearance
    (1.85, -3.14159265359, 0.863937979737),   # gimbal_rear_clearance
)

# Canonical stow pose in MOD4v4gemini's forward-zero frame
STOW_YAW_RAD = -2.612592403477097    # -149.6905 deg from chassis +X (diagonal safe pocket between legs)
STOW_FOLD_RAD = 0.951204442337       # +54.50 deg
STOW_PITCH_RAD = -0.938114472947     # -53.75 deg

GIMBAL_CONTACT_BODIES = (
    "gimbal_yaw_link",
    "gimbal_fold_link",
    "gimbal_pitch_link",
    "gimbal_uwb_tray_link",
    "gimbal_uwb_arm_link",
)


def _is_torch(x) -> bool:
    return type(x).__module__.startswith("torch")


def wrap_to_pi(angle):
    if _is_torch(angle):
        import torch
        return torch.atan2(torch.sin(angle), torch.cos(angle))
    import numpy as np
    return np.arctan2(np.sin(angle), np.cos(angle))


def clip_dm4310_torque_envelope(torque, joint_vel, *, peak_nm: float = 7.0):
    """Clip joint torque against the DM-J4310-2EC (24V) peak limit and linear voltage-speed envelope."""
    intercept = DM4310_SPEC["envelope_intercept_nm"]
    slope = DM4310_SPEC["envelope_slope_nm_s_rad"]
    if _is_torch(torque):
        import torch
        upper = torch.clamp(intercept - slope * torch.clamp(joint_vel, min=0.0), min=0.0, max=peak_nm)
        lower = -torch.clamp(intercept - slope * torch.clamp(-joint_vel, min=0.0), min=0.0, max=peak_nm)
        return torch.clamp(torque, min=lower, max=upper)
    import numpy as np
    upper = np.clip(intercept - slope * np.maximum(joint_vel, 0.0), 0.0, peak_nm)
    lower = -np.clip(intercept - slope * np.maximum(-joint_vel, 0.0), 0.0, peak_nm)
    return np.clip(torque, lower, upper)


def clamp_fold_pitch_clearance(fold_rad, pitch_rad, *, margin_rad: float = 0.01):
    """Clamp (fold, pitch) targets onto the feasible polygon of joint limits + 3 coupled clearance tendons."""
    f_lo, f_hi = FOLD_RANGE_RAD[0] + margin_rad, FOLD_RANGE_RAD[1] - margin_rad
    p_lo0, p_hi0 = PITCH_RANGE_RAD[0] + margin_rad, PITCH_RANGE_RAD[1] - margin_rad
    if _is_torch(fold_rad):
        import torch
        f = torch.clamp(fold_rad, min=f_lo, max=f_hi)
        p_lo = torch.full_like(f, p_lo0)
        p_hi = torch.full_like(f, p_hi0)
        for coef, lo, hi in COUPLED_TENDONS:
            p_lo = torch.maximum(p_lo, (lo + margin_rad) - coef * f)
            p_hi = torch.minimum(p_hi, (hi - margin_rad) - coef * f)
        p = torch.clamp(pitch_rad, min=p_lo, max=p_hi)
        return f, p
    import numpy as np
    f = np.clip(fold_rad, f_lo, f_hi)
    p_lo = np.full_like(np.asarray(f, dtype=float), p_lo0)
    p_hi = np.full_like(np.asarray(f, dtype=float), p_hi0)
    for coef, lo, hi in COUPLED_TENDONS:
        p_lo = np.maximum(p_lo, (lo + margin_rad) - coef * f)
        p_hi = np.minimum(p_hi, (hi - margin_rad) - coef * f)
    p = np.clip(pitch_rad, p_lo, p_hi)
    return (float(f), float(p)) if np.ndim(fold_rad) == 0 else (f, p)


def compute_world_heading_pd_torque(
    target_heading_w,
    current_heading_w,
    world_ang_vel_z,
    *,
    kp: float = 28.0,
    kd: float = 1.4,
    joint_vel=None,
    max_effort: float = 7.0,
):
    """SCUT WheelBipe V14_2 style world-frame heading PD torque for fast chassis spin (小陀螺)."""
    err = wrap_to_pi(target_heading_w - current_heading_w)
    tau = kp * err - kd * world_ang_vel_z
    if joint_vel is not None:
        return clip_dm4310_torque_envelope(tau, joint_vel, peak_nm=max_effort)
    if _is_torch(tau):
        import torch
        return torch.clamp(tau, -max_effort, max_effort)
    import numpy as np
    return np.clip(tau, -max_effort, max_effort)


def project_gimbal_spin_translate_cmd(vel_yaw_xy, yaw_joint_angle):
    """Project desired (vx, vy) in gimbal-yaw frame into chassis body frame (SCUT WheelbipeV14FlatEnvCfg_v2)."""
    q = wrap_to_pi(yaw_joint_angle)
    if _is_torch(vel_yaw_xy):
        import torch
        c, s = torch.cos(q), torch.sin(q)
        return torch.stack([c * vel_yaw_xy[..., 0] - s * vel_yaw_xy[..., 1],
                            s * vel_yaw_xy[..., 0] + c * vel_yaw_xy[..., 1]], dim=-1)
    import numpy as np
    c, s = np.cos(q), np.sin(q)
    return np.stack([c * vel_yaw_xy[..., 0] - s * vel_yaw_xy[..., 1],
                     s * vel_yaw_xy[..., 0] + c * vel_yaw_xy[..., 1]], axis=-1)


def is_stow_yaw_safe(yaw_joint_angle, *, half_window_rad: float = 0.35):
    """True when gimbal_yaw_joint is inside the diagonal safe stow pocket around STOW_YAW_RAD (-149.69 deg)."""
    err = wrap_to_pi(yaw_joint_angle - STOW_YAW_RAD)
    if _is_torch(err):
        return err.abs() <= half_window_rad
    import numpy as np
    return np.abs(err) <= half_window_rad


def plan_stow_targets(q_yaw: float, *, stow: bool) -> tuple[float, float, float]:
    """Safe-yaw-first stow/deploy command law: align yaw to STOW_YAW_RAD before folding past +15 deg."""
    if not stow:
        return 0.0, 0.0, 0.0
    if not is_stow_yaw_safe(q_yaw, half_window_rad=0.25):
        return STOW_YAW_RAD, 0.0, 0.0
    f, p = clamp_fold_pitch_clearance(STOW_FOLD_RAD, STOW_PITCH_RAD, margin_rad=0.0)
    return STOW_YAW_RAD, float(f), float(p)


def make_isaaclab_mod4v4_gimbal_actuators():
    """Return Isaac Lab IdealPDActuatorCfg entries adapted from SCUT wheelbipe_V14_2.py for MOD4v4gemini."""
    from isaaclab.actuators import IdealPDActuatorCfg
    return {
        "gimbal_yaw": IdealPDActuatorCfg(
            joint_names_expr=["gimbal_yaw_joint"],
            stiffness=0.0,       # Velocity disturbance mode (kp=0, kd=0.5) or world-heading torque mode (kp=0, kd=0)
            damping=0.5,
            effort_limit=7.0,
            velocity_limit=20.94395,
            armature=0.0018,
        ),
        "gimbal_fold": IdealPDActuatorCfg(
            joint_names_expr=["gimbal_fold_joint"],
            stiffness=40.0,
            damping=1.2,
            effort_limit=7.0,
            velocity_limit=20.94395,
            armature=0.0018,
        ),
        "gimbal_pitch": IdealPDActuatorCfg(
            joint_names_expr=["gimbal_pitch_joint"],
            stiffness=40.0,
            damping=1.2,
            effort_limit=7.0,
            velocity_limit=20.94395,
            armature=0.0018,
        ),
        "gimbal_uwb_passive": IdealPDActuatorCfg(
            joint_names_expr=["gimbal_uwb_tray_joint", "gimbal_uwb_arm_joint"],
            stiffness=0.0,
            damping=0.005,
            effort_limit=10.0,
            velocity_limit=50.0,
            armature=0.0001,
        ),
    }
