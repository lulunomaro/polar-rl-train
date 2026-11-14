"""Freeze this task's code and provision only its new Host72 directory."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shlex
import sys
import tarfile
import time

T = Path(__file__).resolve().parent
R = T.parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--access-dir', required=True)
    parser.add_argument('--revision', type=int, default=1)
    parser.add_argument('--continue-from')
    args = parser.parse_args()
    sys.path.insert(0, args.access_dir)
    from ssh72 import connect, execute
    assert json.loads((T / 'evidence/OBJECTIVE_CHECK.json').read_bytes())['passed']
    task_root = '/home/lc01/Zonglin Li/zonglin2/tasks/' + T.name + '_R1'
    revision = 'revision_r' + str(args.revision)
    root = task_root + '/' + revision
    archive = T / (revision + '.tar.gz')
    assert not archive.exists(), 'A frozen revision is immutable; use another revision number'
    files = sorted((T / 'flat_height').glob('*.py')) + [T / 'supervise.py', T / 'check_task.py']
    manifest = []
    with tarfile.open(archive, 'w:gz') as bundle:
        for path in files:
            ast.parse(path.read_text(encoding='utf-8-sig'))
            relative = path.relative_to(T).as_posix()
            bundle.add(path, arcname=relative, recursive=False)
            manifest.append(dict(path=relative, bytes=path.stat().st_size,
                                 sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    previous = json.loads((R / 'sources/local/MOD4V3_AUTONOMOUS_STAIR_JUMP_2H_20261114/PLAN.json').read_bytes())
    plan = {k: previous[k] for k in ('python', 'runtime', 'shared_package', 'package', 'source_paths',
                                    'reset_bank', 'asset_identity', 'base_support')}
    parent_root = '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_FORWARD_JUMP_HEIGHT_2H_20261114_R1'
    plan.update(schema='MOD4V3_FLAT_ACCEL_HEIGHT_TASK_V1', task_root=task_root, root=root,
        parent=parent_root + '/train7200/model_040m.pt',
        parent_sha256='43fbc78c7647ffe6dc108fd4b60dd1d986c30639ec0c59f5ac2707879621bae8',
        parent_iteration=27382, revision=args.revision, admission_job='admit_r' + str(args.revision),
        baseline_job='baseline_r' + str(args.revision), training_job='train7200',
        seed=66, evaluation_seed=10066, optimizer_owners=1, training_GPU=0, evaluation_GPU=1,
        source_archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
        input_manifest=manifest, terrain_inputs=[],
        training_round=dict(seconds=7200, num_envs=2048, rollout=24, learning_rate=.00003,
            schedule='fixed', clip_param=.1, num_learning_epochs=3, value_loss_coef=1.,
            entropy_coef=0., checkpoint_seconds=300, automatic_extension=False),
        task=dict(goal='accelerate on flat ground, jump high with level chassis, recover while moving',
            priorities=['level chassis and low angular velocity', 'wheel-rim clearance and body rise'],
            policy_interface=[35, 78, 6], observation_schema='MOD4V3_MOVING_JUMP_PHASE_OBS_V1',
            producer='spring_aware_preparation_v1', old_phase_input_roles_retained=True,
            actor_MLP_retained_exactly=True, critic_output_reset=True,
            exploration_STD_initial=[.035,.035,.035,.035,.08,.08],
            exploration_STD_min=[.015,.015,.015,.015,.03,.03],
            exploration_STD_max=[.06,.06,.06,.06,.15,.15],
            entropy_bonus=0., matching_STD_value_head_Adam_reset=True,
            stochastic_admission_nominal_recovery_min=.25, stochastic_admission_fullDR_recovery_min=.01,
            leg_pose_targets=False, teacher_actions=False,
            policy_controls_all_six_motors=True, artificial_jump_force=False,
            command_vx_m_s=[.6, 1.], command_ramp_s=[.8, 1.1], jump_request_age_s=[1.9, 2.5],
            approach_height_commands_m=[.26, .30, .36], approach_height_probabilities=[.2, .2, .6],
            low_chassis_threshold_m=.275, preload_ready_both_springs_m=.030,
            max_preparation_s=.32, already_low_or_preloaded_skips_preparation=True,
            spring_stroke_definition='upper physical travel limit minus slide joint coordinate',
            spring_energy_definition='potential above full extension; maximum net drop during grounded push/first40ms',
            spring_assist_bonus_max=2., spring_assist_paid_once_after_stable_completion=True,
            reward=dict(rim_points_per_m=200., body_rise_points_per_m=80., incremental_fraction=.2,
                settled_fraction=.8, settled_multiplied_by_flight_level_quality=True,
                flight_quality='mean exp[-(pitch/10deg)^2-(roll/5deg)^2-(pitchroll_rate/1.5rad_s)^2]',
                extra_air_angle_and_rate_penalty=True, no_crouch_or_takeoff_event_bonus=True,
                first_flight_only=True, failure=-40.),
            max_flight_pitch_deg=10., max_flight_roll_deg=5., min_air_s=.16,
            stable_recovery_s=.5, support_duty_min=.8, landing_pitch_roll_max_deg=15.,
            high_jump_reporting_rim_m=.35, high_jump_reporting_body_rise_m=.25,
            min_recovered_jump_rim_m=.12, moving_takeoff_vx_min_m_s=.3, moving_takeoff_vx_max_m_s=2.,
            command_speed_error_is_soft_penalty=True,
            task_velocity_limit_m_s=2., episode_seconds=6.,
            physics_dt_s=.0025, policy_hz=50, leg_hz=100, wheel_hz=400,
            closure_reset_m=.01, mimic_reset_rad=.01, original_plant_motors_springs=True,
            full_DR_ranges_unchanged=True, nominal_fraction=.2,
            training_layout=dict(rows=4, columns=16, approach_lanes_per_tile=9, lane_spacing_m=.55),
            manual_player_input_update_required=True, old_manual_player_preserved=True,
            single_space_request_latched=True, manual_viewer_tiles=1),
        parent_selection=dict(fixed_old_profile='H40 nominal51/51 recovered,30.9284cm median rim; fullDR117/205',
            height_parent_preferred=True, robustness_reference='repaired85: fullDR172/205, nominal26.84cm rim',
            new_profile_baseline_required=True, failed_stair_child_reused=False),
        user_authorization='2026-11-15: inspect current results; if poor, repair and start another two hours. Preserve level chassis, height and spring-aware no-redundant-crouch behavior.',
        replaces_failed_task='MOD4V3_FLAT_ACCEL_HEIGHT_2H_20261115_R1',
        failed_previous_final_sha256='3d25b60c9925e4bdf19d4863a6c370eed715d9c224db22074e405d5e4e433204',
        fresh_window=True, prior_consumed_windows_reused=False)
    if args.continue_from:
        old = T / 'evidence/remote' / args.continue_from
        closed = json.loads((old / 'SAFE_CLOSED.json').read_bytes())
        final = json.loads((old / 'FINAL.json').read_bytes())
        assert closed['outcome'] == 'complete' and final['request_stop']
        assert final['original_deadline_epoch'] > time.time()
        plan.update(fresh_window=False, repair_continuation=True, previous_training_job=args.continue_from,
            training_job='train_remaining_r' + str(args.revision),
            budget_start_epoch=final['original_start_epoch'], budget_deadline_epoch=final['original_deadline_epoch'],
            budget_contract='Original absolute7200s window includes first segment, source repair and new admission; no extension',
            repair_reason='Replace command-relative upper speed reward gate by soft overspeed penalty; height/level priorities',
            restart_parent_reason='Strong H40 retained; early too-strict-gate child is archived but not promoted')
        plan['task']['moving_takeoff_vx_max_m_s'] = 2.
        plan['task']['command_speed_error_is_soft_penalty'] = True
    frozen = T / ('PLAN_R' + str(args.revision) + '.json')
    assert not frozen.exists()
    frozen.write_text(json.dumps(plan, indent=2) + '\n', encoding='utf8')
    (T / 'PLAN.json').write_bytes(frozen.read_bytes())
    client = connect()
    try:
        script = '''
import json
from pathlib import Path
p=json.loads(PLAN)
t=Path(p['task_root'])
if p['revision']==1:t.mkdir(parents=True,exist_ok=False)
elif p.get('repair_continuation'):
 assert t.is_dir() and (t/'TRAINING_OWNER.json').exists()
 assert json.loads((t/p['previous_training_job']/'SAFE_CLOSED.json').read_bytes())['outcome']=='complete'
else:assert t.is_dir() and not (t/'TRAINING_OWNER.json').exists()
Path(p['root']).mkdir(exist_ok=False)
'''.replace('PLAN', repr(json.dumps(plan)))
        code, out, err = execute(client, 'python3 -c ' + shlex.quote(script), 20)
        assert code == 0, out + err
        sftp = client.open_sftp()
        sftp.put(str(archive), root + '/source.tar.gz')
        sftp.put(str(frozen), root + '/PLAN.json')
        sftp.close()
        script = '''
import hashlib,json,subprocess
from pathlib import Path
r=Path(ROOT)
p=json.loads((r/'PLAN.json').read_bytes())
assert hashlib.sha256((r/'source.tar.gz').read_bytes()).hexdigest()==p['source_archive_sha256']
subprocess.run(['tar','-xzf',str(r/'source.tar.gz'),'-C',str(r)],check=True)
for row in p['input_manifest']:
 assert hashlib.sha256((r/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
assert hashlib.sha256(Path(p['parent']).read_bytes()).hexdigest()==p['parent_sha256']
print(json.dumps(dict(root=str(r),verified_files=len(p['input_manifest']),parent_sha256=p['parent_sha256'],optimizer_updates=0)))
'''.replace('ROOT', repr(root))
        code, out, err = execute(client, 'python3 -c ' + shlex.quote(script), 30)
        assert code == 0, out + err
        receipt = dict(epoch=time.time(), revision=args.revision, remote=json.loads(out),
                       source_archive_sha256=plan['source_archive_sha256'], manifest=manifest)
        (T / ('evidence/INPUTS_R' + str(args.revision) + '.json')).write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
        print(json.dumps(receipt['remote'], indent=2))
    finally:
        client.close()


if __name__ == '__main__':
    main()
