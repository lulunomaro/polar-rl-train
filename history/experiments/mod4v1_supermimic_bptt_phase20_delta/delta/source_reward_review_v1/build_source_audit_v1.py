"""Bounded read-only source join and scalar evidence writer; stdlib/CPU only.
No import/exec of audited task, SDK, torch, model, raw, JSONL or training code.
Writes only this newly-created review directory. Run with Python -S -B.
"""
from __future__ import annotations
import ast
import hashlib
import json
import math
from pathlib import Path
from reward_command_candidates_v1 import (
    exp_denominator, exp_error_slope, scut_linear_rate, scut_yaw_rate,
    scut_height_rate, scut_orientation_cost, original_nonholonomic_body_vx,
    rolling_scalar_cost,
)

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
SOURCE = ROOT / 'discovery' / 'reward_command_audit_v1'
ROLES = ('E0', 'E2', 'E3', 'W35', 'CURB_PROTECTED878',
         'CURB_INDEPENDENT113', 'SLOPE135', 'SLOPE_INDEPENDENT50')
ENTRIES = {
    'E0': 'train_mod4v1_e0.py', 'E2': 'train_mod4v1_e2.py',
    'E3': 'train_mod4v1_e3.py', 'W35': 'train_mod4v1_w35.py',
    'CURB_PROTECTED878': 'train_host72_backend_admission_v1.py',
    'CURB_INDEPENDENT113': 'train_independent_owned_axis_v1.py',
    'SLOPE135': 'train_slope5_snapshot_reviewed_resume_ppo.py',
    'SLOPE_INDEPENDENT50': 'train_independent_owned_axis_v1.py',
}
ROLE_FILES = {
    'E0': ['directional_spin_runtime.py', 'spin_commands.py', 'spin_translation_math.py',
           'world_drift_reward.py', 'world_drift_isaac.py', 'rolling_consistency.py',
           'mod4v1_fresh_dr_guard.py', 'mod4_env.py'],
    'E2': ['e2_directional_spin_runtime_v1.py', 'e2_h1_flat_environment_v1.py',
           'spin_translation_math.py', 'world_drift_reward.py', 'world_drift_isaac.py'],
    'E3': ['e3_recovery_runtime_v1.py', 'e3_public_recovery_phase_v1.py'],
    'W35': ['config_mod4v1_w35.py', 'command208_v3.py', 'terrain208_v3.py',
            'learning208_v3.py', 'evidence208_v3.py', 'course_math208.py',
            'e1_scene_query_resource.py', 'e1_terrain_runtime.py'],
    'CURB_PROTECTED878': ['curb20_entry_v3_runtime.py', 'curb20_retention_runtime.py',
                         'curb20_geometry.py'],
    'CURB_INDEPENDENT113': ['curb20_entry_v3_runtime.py', 'curb20_retention_runtime.py',
                           'retention_learning_env.py', 'independent_expert_axis_v1.py',
                           'e1_variant_fullstate_checkpoint.py'],
    'SLOPE135': ['slope5_retention_runtime.py', 'slope5_geometry.py',
                 'retention_flat_runtime_named_owned.py', 'retention_flat_runtime_sdk_reviewed.py',
                 'retention_flat_runtime.py', 'e1_terrain_runtime.py'],
    'SLOPE_INDEPENDENT50': ['independent_expert_axis_v1.py', 'slope5_retention_runtime.py'],
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(name: str, data: object) -> None:
    target = OUT / name
    assert target.parent == OUT and target.suffix == '.json'
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n',
                      encoding='utf-8')


def f_constants(path: Path, env: dict) -> dict:
    """AST data only: _f('ENV', numeric_literal) joined with this role's metadata."""
    tree = ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
    result = {}
    for statement in tree.body:
        if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
            continue
        name = statement.targets[0]
        call = statement.value
        if not isinstance(name, ast.Name) or not isinstance(call, ast.Call):
            continue
        if not isinstance(call.func, ast.Name) or call.func.id != '_f' or len(call.args) != 2:
            continue
        key = ast.literal_eval(call.args[0])
        try:
            default = ast.literal_eval(call.args[1])
        except (ValueError, TypeError):
            continue
        if not isinstance(default, (int, float)):
            continue
        if name.id.startswith(('SCUT_', 'W_HEIGHT_', 'W_RUN_', 'VEL_HEIGHT_')):
            result[name.id] = dict(env_key=key, default=default,
                                   metadata_value=env.get(key),
                                   value=float(env.get(key, default)),
                                   source=str(path), line=statement.lineno,
                                   provenance='metadata_env' if key in env else 'entry_import_default')
    return result


def scut_function_ast(path: Path) -> dict:
    wanted = {'exponential', 'forward_error', 'linear_exp', 'linear_square', 'linear_gap',
              'yaw_exp', 'orientation', 'wheel_positions_body', 'no_fork',
              'leg_gravity_alignment', 'wheel_power'}
    tree = ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
    return {n.name: dict(line=n.lineno,
                        AST_SHA256=hashlib.sha256(ast.dump(n, include_attributes=False).encode()).hexdigest())
            for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in wanted}


def main() -> None:
    roles, inputs = {}, set()
    for role in ROLES:
        base = SOURCE / role
        meta = base / ('E1_CANONICAL_SOURCE_METADATA.json' if role.startswith(('CURB_', 'SLOPE'))
                       else 'original_run_manifest.json')
        data = json.loads(meta.read_text(encoding='utf-8-sig'))
        env = data['original_env'] if 'original_env' in data else data['env']
        task = base / 'runtime' / 'isaac' / 'mod4' / 'mod4_task.py'
        constants = f_constants(task, env)
        entry = base / 'runtime' / 'isaac' / 'mod4' / ENTRIES[role]
        inputs.update((meta, task, entry))
        for filename in ['scut_flat_rescue.py', 'skills_isaac.py'] + ROLE_FILES[role]:
            inputs.add(base / 'runtime' / 'isaac' / 'mod4' / filename)
        roles[role] = dict(
            metadata=str(meta), metadata_SHA256=digest(meta), entry=str(entry),
            metadata_line_for_env=(15 if role == 'SLOPE135' else 10)
                if role.startswith(('CURB_', 'SLOPE')) else 6,
            constants=constants,
            velocity_height_gate=dict(mode=env.get('RM_VEL_HEIGHT_GATE', 'off'),
                                      full=float(env.get('RM_VEL_HEIGHT_GATE_FULL', 0.05)),
                                      zero=float(env.get('RM_VEL_HEIGHT_GATE_ZERO', 0.10)),
                                      real_runtime_verified=False),
            registered_gyro_curriculum=env.get('RM_GYRO_CURRICULUM', '1') != '0',
            imported_task_episode_limit_seconds=float(env.get('RM_EPISODE_S', 20.0)),
            original_height_command_range=[float(env['RM_HEIGHT_MIN']), float(env['RM_HEIGHT_MAX'])],
            spin_world_progress_speed=float(env.get('RM_SPIN_WORLD_PROGRESS_M_S', 0.15)),
            runtime_reward_or_pass_measurement=False,
            scut_reward_function_AST=scut_function_ast(task.parent / 'scut_flat_rescue.py'),
            source_hashes={filename: digest(base / 'runtime' / 'isaac' / 'mod4' / filename)
                           for filename in ['mod4_task.py', 'scut_flat_rescue.py', 'skills_isaac.py']},
        )
    for rel in [
        'CURRENT_PROGRESS_v5_PHASE19_REMOTE_VERIFIED_MEASUREMENT_SEAL_PENDING_APPEND.md',
        'source_acceptance_review/EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.json',
        'source_runtime/worker_supermimic_bptt.py', 'source_runtime/native_supermimic_bridge.py',
        'source_core_review/ctx_reward_learner.py', 'source_core_review/evidence/learner.py',
        'discovery/sdk_reward_command_call_order_v1/envs/manager_based_rl_env.py',
        'discovery/sdk_reward_command_call_order_v1/managers/command_manager.py',
    ]:
        inputs.add(ROOT / rel)
    optional_reward_manager = ROOT / 'discovery/sdk_reward_scale_v1/managers/reward_manager.py'
    assert optional_reward_manager.is_file()
    inputs.add(optional_reward_manager)
    inputs.add(ROOT / 'discovery/sdk_reward_scale_v1/envs/mdp/rewards.py')
    input_rows = [dict(path=str(p), bytes=p.stat().st_size, SHA256=digest(p))
                  for p in sorted(inputs, key=str)]
    dump('ROLE_EFFECTIVE_REWARD_PARAMS_SOURCE_V1.json', dict(
        kind='METADATA_PLUS_ENTRY_IMPORT_SOURCE_JOIN_NOT_LIVE_CFG', roles=roles,
        all_eight_task_hashes_equal=len({v['source_hashes']['mod4_task.py'] for v in roles.values()}) == 1,
        all_eight_scut_hashes_equal=len({v['source_hashes']['scut_flat_rescue.py'] for v in roles.values()}) == 1,
        all_eight_scut_reward_functions_AST_equal=len({json.dumps(v['scut_reward_function_AST'], sort_keys=True)
                                                      for v in roles.values()}) == 1,
        all_eight_skills_hashes_equal=len({v['source_hashes']['skills_isaac.py'] for v in roles.values()}) == 1,
        wrapper_effects='See report: E3 masks + event; terrain rolling disabled; CURB113 bind unknown.',
        actual_live_cfg=False))
    dump('AUDIT_INPUTS_SHA256_V1.json', dict(
        kind='EXPLICIT_BOUNDED_SOURCE_INPUTS_NO_WORKSPACE_WALK', files=input_rows,
        file_count=len(input_rows), SDK_imports=0, model_reads=0, raw_reads=0,
        JSONL_reads=0, GPU_operations=0, source_edits=0, git_operations=0))
    errors = [0.0, 0.05, 0.1, 0.3, 0.5, math.sqrt(0.5), 1.0, 1.5, 4.0, 4 * math.pi]
    table = [dict(error=e, broad=exp_denominator(e, 0.25),
                  broad_slope=exp_error_slope(e, 0.25), tight=exp_denominator(e, 0.01),
                  tight_slope=exp_error_slope(e, 0.01), linear_rate=scut_linear_rate(e),
                  yaw_rate=scut_yaw_rate(e), quadratic_slope=-0.125 * e)
             for e in errors]
    stand_rate = scut_linear_rate(0.3) + scut_yaw_rate(0) + scut_height_rate(0) + 0.2
    moving_rate = scut_linear_rate(0) + scut_yaw_rate(0) + scut_height_rate(0) + 0.2
    moving_deflected_rate = scut_linear_rate(0) + scut_yaw_rate(0) + scut_height_rate(0.1) + 0.2
    h, yaw, dt = 16, 4.0, 0.02
    span = h * dt * yaw
    dump('FORMULA_COUNTEREXAMPLES_CPU_V1.json', dict(
        kind='PURE_SCALAR_SOURCE_COUNTEREXAMPLES_NOT_PHYSICAL_TRAJECTORIES', table=table,
        exp_e_minus_one_errors={str(d): math.sqrt(d) for d in [0.25, 0.01, 0.001, 0.1]},
        exp_gaussian_standard_deviation_if_exp_half={str(d): math.sqrt(d / 2)
                                                   for d in [0.25, 0.01, 0.001, 0.1]},
        stationary_moving=dict(command_vx=0.3, other_terms_idealized=True,
            stationary_rate=stand_rate, ideal_tracking_rate=moving_rate,
            moving_height_error_0p1_rate=moving_deflected_rate,
            tracking_advantage_rate=moving_rate-stand_rate,
            height_loss_0p1_rate=scut_height_rate(0)-scut_height_rate(0.1),
            reward_manager_multiply_dt_pending_source=False if optional_reward_manager.is_file() else True,
            step_dt=dt, stationary_reward_if_manager_dt=stand_rate*dt),
        recovery=dict(idealized_upside_down_gx_gy_zero_orientation_cost=scut_orientation_cost(0, 0, 0),
            idealized_pitch_90deg_orientation_cost=scut_orientation_cost(1, 0, 0),
            zero_twist_tracking_rate=scut_linear_rate(0)+scut_yaw_rate(0),
            pitch_90deg_orientation_per_step_if_dt=-dt*scut_orientation_cost(1, 0, 0),
            event_transition_reward_if_dt=1.0, physical_reachability_proven=False),
        held_command=dict(horizon=h, dt=dt, yaw_rate=yaw, angular_span_rad=span,
            angular_span_degrees=math.degrees(span),
            initial_heading_zero_vx_difference=1.0-math.cos(span),
            max_phase_vx_difference_for_unclipped_V_0p5=2*math.sin(span/2)),
        rolling=dict(speed_saturation_m_s=0.30,
            loaded_high_slip_cost=rolling_scalar_cost(1, 10),
            unloaded_high_slip_cost=rolling_scalar_cost(1, 0),
            acceptance_replaced=False),
        unknown_binary_predicates=dict(E0=None, SLOPE_INDEPENDENT50=None),
        measured_pass_rates={role: None for role in ROLES},
        training_or_simulator_executed=False))
    print(json.dumps(dict(roles=len(roles), input_files=len(input_rows),
                          source_only=True, outputs=3), ensure_ascii=False))


if __name__ == '__main__':
    main()
