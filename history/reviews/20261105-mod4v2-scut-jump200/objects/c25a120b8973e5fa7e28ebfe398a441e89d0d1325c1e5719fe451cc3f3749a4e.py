"""Review returned v2 final60 motion and timing; no inference, physics or PT reads."""
from pathlib import Path
import argparse, json, time
import numpy as np

N = Path(__file__).resolve().parent
A = N/'takeoff_velocity_final239_1h'

def review(returned_path, directory):
    returned = json.loads(returned_path.read_bytes())
    f = returned['files']; result = f['evaluation/RESULT.json']
    rows = f['evaluation/ALL80.json']['first_episodes']
    curves = f['evaluation/CONTROL_CURVES.json']['curves']
    diagnosis = json.loads((A/'reports/TAKEOFF_CLOSED_LEARNER_DIAGNOSIS.json').read_bytes())
    expected = diagnosis['checkpoint']
    assert result['source_SHA'] == expected['SHA'] and result['passed_execution'] and len(rows) == 80
    assert result['optimizer_operations'] == 0 and result['saved_pose_quaternion_order'] == 'wxyz'
    assert not f['OWNER_EXIT.json']['error'] and f['OWNER_EXIT.json']['all_own_waited']
    arr = lambda key: np.asarray([row[key] for row in curves])
    active = arr('active'); phase = arr('jump_takeoff_phase'); trigger = arr('jump_takeoff_trigger_event')
    action, applied, targets = (arr(k) for k in ('action', 'applied_action', 'joint_target'))
    motors, vel, torque = (arr(k) for k in ('actual_motor_position','actual_motor_velocity','actual_motor_torque'))
    assert np.isfinite(targets[active]).all() and abs(applied[active]).max() <= 6
    delta = targets[..., [0, 2]]-targets[..., [1, 3]]
    assert (delta[active] >= -1.0863195404360622-1e-6).all()
    assert (delta[active] <= .49192233306644084+1e-6).all()
    controls = np.asarray([row['controls'] for row in rows])
    counts = {key: sum(bool(row[key]) for row in rows) for key in (
        'terminated', 'time_out', 'closure_reset', 'mimic_reset', 'numerical_reset', 'observation_outlier')}
    with np.load(directory/'actual400hz.npz') as tick:
        mask = tick['active']; local = tick['root_pos']-np.asarray(result['environment_origins'])[None]
        assert mask.shape == (len(curves)*8,80)
        world_vz = tick['root_velocity'][...,2]
        wheel_force = tick['wheel_contact_force']
        contact_free = (wheel_force <= 1).all(-1) & (tick['nonwheel_contact_force'] <= 1) & mask
        entries = contact_free & ~np.concatenate((np.zeros_like(contact_free[:1]),contact_free[:-1]))
        post_ground = (tick['flight_id'] > 0) & mask
        callbacks = dict(actual_callbacks=len(mask), first_episode_samples=int(mask.sum()),
            flight_envs=int(post_ground.any(0).sum()),
            upward_flight_envs=int((tick['upward_flight'] & mask).any(0).sum()),
            wholeclear_envs=int((tick['wholeclear'] & mask).any(0).sum()),
            landed_top_envs=int((tick['landed_top'] & mask).any(0).sum()),
            success_envs=int((tick['strict'] & mask).any(0).sum()),
            max_actual_top_force=float(tick['top_force'][mask].max()),
            root_x_range=[float(local[...,0][mask].min()), float(local[...,0][mask].max())],
            root_z_range=[float(local[...,2][mask].min()), float(local[...,2][mask].max())],
            contact_free_entry_count=int(entries.sum()),
            upward_contact_free_entries=int((entries & (world_vz > .05)).sum()),
            root_world_vz_range=[float(world_vz[mask].min()), float(world_vz[mask].max())],
            first_episode_controls_min=int(controls.min()), first_episode_controls_max=int(controls.max()),
            mean_seconds=float(controls.mean()*.02))
        rootvel = tick['root_velocity'][7::8]
        by_phase = {}
        reward = arr('reward')
        for value in np.unique(phase):
            selected = active & (phase == value)
            by_phase[str(value)] = dict(endpoints=int(selected.sum()), fraction=float(selected.sum()/active.sum()),
                world_vz_mean=float(rootvel[...,2][selected].mean()),
                world_vz_max=float(rootvel[...,2][selected].max()),reward_mean=float(reward[selected].mean()))
        selected = {}
        for eid in result['recorded_envs']:
            indices = np.flatnonzero(mask[:,eid]); last = indices[-1]
            selected[str(eid)] = dict(max_root_x=float(local[indices,eid,0].max()),
                final_root_x=float(local[last,eid,0]), final_root_z=float(local[last,eid,2]),
                controls=int(controls[eid]), success=bool(rows[eid]['jump200_success']))
    renders = []
    for subdir in ['recorded_native', 'recorded_native_late']:
        path = directory/subdir/'RENDER_REPORT.json'
        if path.exists():
            render = json.loads(path.read_bytes())
            assert render['model_SHA'] == expected['SHA'] and render['NN'] == render['physics_steps'] == 0
            renders.append(dict(path=str(path), media=render['media']))
    logs = {}
    for name in ['WORKER.log','OWNER.log']:
        row = json.loads((A/'reports/TAKEOFF_CLOSED_COMPLETE_LOG_ACTUAL.json').read_bytes())['logs'].get(name)
        if row:
            errors = [line for line in row['text'].splitlines() if any(term in line.lower() for term in
                ['[error]','traceback (most recent call last)','cooking failure','patch buffer overflow','outofmemoryerror'])]
            logs[name] = dict(path=row['path'],bytes=row['bytes'],SHA=row['SHA'],errors=errors)
    report = dict(epoch=time.time(),checkpoint_SHA=expected['SHA'],final_iteration=expected['iteration'],
        full_learner_diagnosis=str(A/'reports/TAKEOFF_CLOSED_LEARNER_DIAGNOSIS.json'),
        complete_all80_review=True,all_actual_images_reviewed=False,
        actual_visual_findings_pending=True,decision='WAIT_NATIVE_IMAGE_REVIEW',
        result=result, counts=counts, callbacks=callbacks, selected=selected, phase=by_phase,
        request_envs=int(trigger.any(0).sum()), request_count=int(trigger.sum()),
        request_count_per_env=trigger.sum(0).tolist(),
        target_delta_bounds=[float(delta[active].min()),float(delta[active].max())],
        target_delta_lower_hit_fraction=float(np.isclose(delta[active],-1.0863195404360622,atol=1e-5).mean()),
        target_delta_upper_hit_fraction=float(np.isclose(delta[active],.49192233306644084,atol=1e-5).mean()),
        raw_action_mean=action[active].mean(0).tolist(),
        raw_action_clip_fraction=(abs(action[active])>6).mean(0).tolist(),
        motor_target_tracking_MAE=abs(motors[...,:4][active]-targets[active]).mean(0).tolist(),
        motor_velocity_abs_mean=abs(vel[active]).mean(0).tolist(), motor_torque_abs_mean=abs(torque[active]).mean(0).tolist(),
        command_min=arr('command')[active].min(0).tolist(), command_max=arr('command')[active].max(0).tolist(),
        command_height_range=[float(arr('command_height')[active].min()),float(arr('command_height')[active].max())],
        effective_height_range=[float(arr('effective_height')[active].min()),float(arr('effective_height')[active].max())],
        weighted_reward_curve_means={key:float(np.mean([row['weighted_reward_active_mean'][key] for row in curves]))
            for key in curves[0]['weighted_reward_active_mean']},
        perbody_peak_reset_contact_force=np.max(arr('reset_body_contact_force')[active],axis=0).tolist(),
        reset_contact_body_names=result['reset_contact_body_names'],complete_eval_logs=logs,
        render_reports=renders, saved_pose_quaternion_order='wxyz', new_model_reads=0,new_physics=0,
        original_failed_evaluation_preserved=True)
    target = A/'reports/TAKEOFF_CLOSED_ALL80_NUMERIC_REVIEW.json'
    with target.open('x',encoding='utf8') as stream: json.dump(report,stream,indent=2)
    print(json.dumps(dict(report=str(target),counts=counts,callbacks=callbacks,
        selected=selected,requests=report['request_count'],target_delta_bounds=report['target_delta_bounds'])))

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--returned',type=Path,required=True)
    parser.add_argument('--directory',type=Path,required=True);args=parser.parse_args()
    review(args.returned,args.directory)
