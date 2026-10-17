"""Owned frozen-evaluation signed4 audit; original cap2 runtime source remains unchanged."""
import torch
from directional_spin_runtime import DirectionalSpinCommand
from spin_translation_math import body_command
def audit(env):
    term = env.command_manager.get_term('twist')
    if not isinstance(term, DirectionalSpinCommand):
        raise RuntimeError('Directional stage must install its actual SDK command class')
    c = term.command
    if term.cfg.heading_command or term.is_heading_env.any() or (not torch.isfinite(c).all()):
        raise RuntimeError('Heading override or nonfinite command')
    pure, moving = (term.is_pure_spin, term.is_moving_spin)
    if (pure & moving).any() or (moving & term.is_standing_env).any():
        raise RuntimeError('Command modes overlap')
    if pure.any() and c[pure, :2].abs().max() > 1e-06:
        raise RuntimeError('Preserved pure spin may not translate')
    if c[:, 1].abs().max() > 1e-06 or c[:, 2].abs().max() > term.pure_max + 1e-05:
        raise RuntimeError('Lateral body motion or yaw beyond admitted cap')
    projection_error = 0.0
    if moving.any() and (not term.manual_evaluation_mode):
        vx, _ = body_command(term.progress_goal, term.world_direction[moving], term.robot.data.heading_w.torch[moving], term.body_limit)
        projection_error = float((vx - c[moving, 0]).abs().max())
        if projection_error > 1e-06 or c[moving, 2].abs().max() > 4.00001:
            raise RuntimeError('World-to-body reference or moving yaw bound mismatch')
    return {'stage': 'directional_spin_v1', 'command_frame': 'body', 'manual_frozen_evaluation': term.manual_evaluation_mode, 'world_progress_goal_m_s': term.progress_goal, 'projection_error_m_s': projection_error, 'pure_fraction_actual': float(pure.float().mean()), 'moving_fraction_actual': float(moving.float().mean()), 'transition_fraction_actual': float(term.is_transition_spin.float().mean()), 'stand_fraction_actual': float(term.is_standing_env.float().mean()), 'pure_max_rad_s': term.pure_max, 'moving_yaw_max_rad_s': 4.0, 'world_progress_achieved': 'unmeasured; actual displacement and complete cycles required'}
