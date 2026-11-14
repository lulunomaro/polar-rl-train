"""Freeze a new source revision and verify it on the authorized Host72."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shlex
import shutil
import sys
import tarfile
import time

T = Path(__file__).resolve().parent
R = T.parents[2]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--access-dir', required=True)
    p.add_argument('--revision', type=int, required=True)
    a = p.parse_args()
    sys.path.insert(0, a.access_dir)
    from ssh72 import connect, execute
    assert json.loads((T / 'evidence/OBJECTIVE_CHECK.json').read_bytes())['passed']
    revision = 'revision_r' + str(a.revision)
    task_root = '/home/lc01/Zonglin Li/zonglin2/tasks/' + T.name + '_R1'
    root = task_root + '/' + revision
    terrain = T / 'terrain'
    terrain.mkdir(exist_ok=True)
    for name in ('r00_c00.npz', 'r03_c00.npz'):
        shutil.copy2(R / 'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/viewer/tiles' / name, terrain / name)
    files = sorted((T / 'autonomous_stair').glob('*.py')) + sorted(terrain.glob('*.npz')) + [T / 'supervise.py']
    archive = T / (revision + '.tar.gz')
    assert not archive.exists(), 'Retain original revision; use a new revision number'
    manifest = []
    with tarfile.open(archive, 'w:gz') as bundle:
        for path in files:
            if path.suffix == '.py':
                ast.parse(path.read_text(encoding='utf-8-sig'))
            name = path.relative_to(T).as_posix()
            bundle.add(path, arcname=name, recursive=False)
            manifest.append(dict(path=name, bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    parent = json.loads((R / 'sources/local/MOD4V3_FORWARD_JUMP_HEIGHT_2H_20261114/PLAN.json').read_bytes())
    plan = {key: parent[key] for key in ('python', 'runtime', 'shared_package', 'package', 'source_paths',
                                        'reset_bank', 'parent', 'parent_sha256', 'parent_iteration', 'asset_identity')}
    plan.update(schema='MOD4V3_AUTONOMOUS_STAIR_TASK_V1', task_root=task_root, root=root,
        admission_job='admit_r' + str(a.revision),
        training_job='train7200' if a.revision == 1 else 'train_remaining_r' + str(a.revision),
        base_support=parent['support'], seed=66, evaluation_seed=10066,
        optimizer_owners=1, training_GPU=0, evaluation_GPU=1,
        source_archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
        input_manifest=manifest, terrain_inputs=[row for row in manifest if row['path'].endswith('.npz')],
        training_round=dict(seconds=7200, num_envs=2048, rollout=24, learning_rate=.0001,
            schedule='fixed', clip_param=.2, num_learning_epochs=5, value_loss_coef=1.,
            entropy_coef=.01, checkpoint_seconds=300, automatic_extension=False),
        task=dict(goal='moving jump onto first upper tread, then >=0.5s stable recovery',
            policy_interface=[35, 78, 6], observation_schema='MOD4V3_AUTONOMOUS_STAIR_OBS_V1',
            task_slots=['base_mode', 'jump_request', 'measured_air', 'signed_edge_distance_m',
                        'step_height_m', 'tread_depth_m', 'vertical_velocity_m_s_times_0.25'],
            phase_commands=False, phase_clock_observed=False, leg_pose_targets=False,
            teacher_execution=False, motor_actions='all six learned actions only',
            geometry='saved original Isaac Lab r00_c00 and r03_c00; lower heights are explicit scaled warmup copies',
            heights_m=[0., .04, .08, .12, .165, .22], target_heights_m=[.165, .22],
            curriculum_max_level_at_s={'0': 2, '900': 3, '1800': 4, '3600': 5},
            target_exposure_each_from_start=.1, scan_resolution_m=.05,
            single_space_request_latched=True, required_physical_air_s=.08,
            must_cross_in_qualified_flight=True, both_wheel_top_footprints=True,
            stable_recovery_s=.5, support_duty_min=.8, landing_pitch_roll_max_deg=15.,
            physics_dt_s=.0025, policy_hz=50, leg_hz=100, wheel_hz=400,
            closure_reset_m=.01, mimic_reset_rad=.01, original_plant_and_motors=True,
            full_DR_ranges_unchanged=True, nominal_fraction=.2,
            overspeed_penalty=True, task_velocity_limit_m_s=2.,
            manual_player_input_update_required=True, old_manual_player_preserved=True),
        user_authorization='Set up autonomous stair jumping and start training; continue; retain preceding two-hour duration',
        fresh_window=True, prior_consumed_windows_reused=False)
    if a.revision > 1:
        invalid = json.loads((T / 'evidence/remote/INVALID_PHYSICS_R1.json').read_bytes())
        prior_final = json.loads((T / 'evidence/remote/train7200/FINAL.json').read_bytes())
        assert prior_final['request_stop']
        plan.update(budget_start_epoch=invalid['original_start_epoch'],
            budget_deadline_epoch=invalid['original_deadline_epoch'],
            repair_continuation=True, invalid_segment='train7200',
            invalid_weights_reused=False, fresh_window=False,
            budget_contract='Original absolute7200s window includes failed segment and repair/admission; no extension')
    plan['task']['training_layout'] = dict(columns=8, approach_lanes_per_tile=9,
        lane_spacing_m=.5, manual_viewer_tiles=1)
    frozen = T / ('PLAN_R' + str(a.revision) + '.json')
    frozen.write_text(json.dumps(plan, indent=2) + '\n', encoding='utf8')
    (T / 'PLAN.json').write_bytes(frozen.read_bytes())
    client = connect()
    try:
        script = 'from pathlib import Path; Path(' + repr(root) + ').mkdir(parents=True,exist_ok=False)'
        status, out, err = execute(client, 'python3 -c ' + shlex.quote(script), 20)
        assert status == 0, out + err
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
        status, out, err = execute(client, 'python3 -c ' + shlex.quote(script), 30)
        assert status == 0, out + err
        receipt = dict(epoch=time.time(), revision=a.revision, remote=json.loads(out),
                       source_archive_sha256=plan['source_archive_sha256'], manifest=manifest)
        (T / ('evidence/INPUTS_R' + str(a.revision) + '.json')).write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
        print(json.dumps(receipt['remote'], indent=2))
    finally:
        client.close()


if __name__ == '__main__':
    main()
