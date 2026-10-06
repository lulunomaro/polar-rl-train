"""CPU contracts for actual exposure/layout math; no simulated skill claim."""
import ast
import json
from pathlib import Path
import numpy as np
import torch
from types import SimpleNamespace
from retention_mix_math import (
    rough_mask, spawn_xy, route_timeout, flat_surface, assert_surface_separation,
)


def run():
    tests = []
    ids = torch.arange(20000)
    terrain = rough_mask(ids)
    assert terrain.sum() == 5000 and (~terrain).sum() == 15000
    tests.append('fullscale_independent75_25_environment_assignment')
    origins = torch.stack((torch.arange(20000).remainder(142)*2.5-177.5,
                           torch.arange(20000).div(142, rounding_mode='floor')*2.5-176.25,
                           torch.zeros(20000)), -1)
    xy = spawn_xy(origins, ids)
    assert torch.unique(xy, dim=0).shape[0] == 20000
    assert torch.equal(xy[terrain], origins[terrain, :2])
    assert torch.equal(xy[~terrain, 0], origins[~terrain, 0]+768.)
    tests.append('fullscale_unique_disjoint_spawn_positions')
    subset = torch.tensor([19999, 7, 4, 0, 3, 177])
    assert torch.equal(spawn_xy(origins, subset), xy[subset])
    assert torch.equal(spawn_xy(origins, subset), spawn_xy(origins, subset))
    assert torch.equal(origins[:, 2], torch.zeros(20000))
    tests.append('subset_resets_do_not_accumulate_translation_or_mutate_origins')
    vertices, faces = flat_surface()
    normals = np.cross(vertices[faces[:, 1]]-vertices[faces[:, 0]], vertices[faces[:, 2]]-vertices[faces[:, 0]])
    assert (normals[:, 2] > 0).all() and (vertices[:, 2] == 0).all()
    assert_surface_separation(np.array([[-190., -190., -.09], [190., 190., .035]]))
    tests.append('finite_upward_mesh_separated_from_actual_gentle_bounds')
    margin = torch.tensor([48., 48.])
    assert (xy[~terrain]-margin > torch.tensor(vertices.min(0)[:2])).all()
    assert (xy[~terrain]+margin < torch.tensor(vertices.max(0)[:2])).all()
    tests.append('flat_route48m_and_footprint_inside_declared_mesh_fullscale')
    anchor = torch.zeros((4, 2)); points = anchor.clone()
    points[:, 0] = 2.001
    assert torch.equal(route_timeout(points, anchor, torch.arange(4)), torch.tensor([False, False, False, True]))
    points[:, 0] = 48.001
    assert route_timeout(points, anchor, torch.arange(4)).all()
    tests.append('terrain2m_truncation_separate_from_flat48m_retention_routes')
    rejects = []
    for name, bad in [('overlap', np.array([[384., 0., 0.]])),
                      ('nonfinite', np.array([[np.nan, 0., 0.]])),
                      ('wrong_shape', np.zeros((4, 2)))]:
        try:
            assert_surface_separation(bad)
        except ValueError:
            rejects.append(name)
        else:
            raise AssertionError(name)
    tests.append('geometry_overlap_nonfinite_missing_dimension_rejected')
    colocated = Path(__file__).with_name('retention_mix_runtime.py')
    runtime = colocated if colocated.is_file() else Path(__file__).parent/'isaac/mod4/retention_mix_runtime.py'
    source = runtime.read_text(encoding='utf-8')
    tree = ast.parse(source)
    for name in ('RetentionMixCommand', 'RetentionMixEnv', 'RetentionTerrainImporter'):
        assert any(isinstance(n, ast.ClassDef) and n.name == name for n in tree.body)
    assert 'rough_full_reset(env, terrain_ids)' in source
    assert 'task.scut_rescue.consistent_reset(env, flat_ids)' in source
    assert 'spin_contact_consistency(env, speed_scale, yaw_min, support_weight)' in source
    rolling = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'mixed_rolling')
    assert [arg.arg for arg in rolling.args.args] == ['env', 'speed_scale', 'yaw_min', 'support_weight']
    assert rolling.args.kwarg is None and len(rolling.args.defaults) == 3
    tests.append('separate_existing_full30q_reset_and_original_flat_rolling_formula')
    # Exercise the actual command methods against a CPU base-API double. This
    # validates isolation/projection without claiming SDK lifecycle evidence.
    root = Path(__file__).resolve().parents[1] / 'MOD4_ROUGH_INTRO_ADMISSION_REVIEW_20261006/isaac/mod4'
    directional = ast.parse((root/'directional_spin_runtime.py').read_text(encoding='utf-8'))
    nodes = [n for n in directional.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in ('transition_yaw', 'DirectionalSpinCommand')]
    nodes += [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'RetentionMixCommand']
    class BaseCommand:
        def __init__(self, cfg, env):
            self.cfg, self.num_envs, self.device = cfg, env.num_envs, 'cpu'
            self.robot = env.robot
            self.vel_command_b = torch.zeros((env.num_envs, 3))
            self.is_standing_env = torch.zeros(env.num_envs, dtype=torch.bool)
            self.is_heading_env = self.is_standing_env.clone()
        def _resample_command(self, ids):
            self.vel_command_b[ids, 0] = 3*torch.rand(len(ids))-1.5
            self.is_standing_env[ids] = torch.rand(len(ids)) < self.cfg.rel_standing_envs
        def _update_command(self):
            pass
    def projection(goal, direction, heading, limit):
        # Independent expression equivalent to the frozen body projection.
        return (2*goal*torch.cos(heading-direction)).clamp(-limit, limit), torch.zeros_like(heading)
    import math, os
    scope = dict(torch=torch, math=math, os=os, UniformVelocityCommand=BaseCommand,
                 body_command=projection, rough_mask=rough_mask)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(root/'directional_spin_runtime.py'), 'exec'), scope)
    env = SimpleNamespace(num_envs=20000, cfg=SimpleNamespace(seed=20261006), step_dt=.01,
                          robot=SimpleNamespace(data=SimpleNamespace(heading_w=SimpleNamespace(torch=torch.zeros(20000)))))
    cfg = SimpleNamespace(heading_command=False, rel_heading_envs=0., rel_standing_envs=.1, resampling_time_range=(12.,16.))
    command = scope['RetentionMixCommand'](cfg, env)
    command._resample_command(ids)
    for _ in range(6):
        env.robot.data.heading_w.torch += .23
        command._update_command()
        assert not command.is_pure_spin[terrain].any()
        assert not command.is_moving_spin[terrain].any()
        assert not command.is_transition_spin[terrain].any()
        assert (command.vel_command_b[terrain, 1:] == 0.).all()
        assert command.vel_command_b[terrain, 0].abs().max() <= .3
        moving = command.is_moving_spin
        expected = 2*command.progress_goal*torch.cos(env.robot.data.heading_w.torch[moving]-command.world_direction[moving])
        assert torch.equal(command.vel_command_b[moving, 0], expected)
        assert command.vel_command_b[command.is_standing_env].abs().max() == 0.
    tests.append('actual_command_methods_keep_rough_yaw0_and_heading_projection_each_step')
    before = command.vel_command_b.clone()
    command._resample_command(subset)
    unchanged = torch.ones(20000, dtype=torch.bool); unchanged[subset] = False
    assert torch.equal(command.vel_command_b[unchanged], before[unchanged])
    assert command.is_pure_spin[~terrain].any() and command.is_moving_spin[~terrain].any()
    tests.append('subset_resample_preserves_other_commands_and_old_flat_skill_exposure')
    return dict(pass_=True, contracts=tests, invalid_geometry_rejections=rejects,
                physics_SDK_verified=False, PPO_started=False, budget_operations=0,
                exposure_fraction_is_not_graduation_threshold=True)


if __name__ == '__main__':
    result = run()
    target = Path(__file__).with_name('CPU_LAYOUT_CONTRACT.json')
    target.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))
