"""Diagnose one returned full learner and its actual80 trajectories, no physics."""
from pathlib import Path
import argparse
import hashlib
import io
import json
import pickle
import time
import types
import numpy as np
import torch


def main(root, allow_pending_full_log=False):
    reports = root/'reports'
    target = reports/'ACTUAL_JUMP200_FINAL_LEARNING_AND_ALL80_REVIEW.json'
    assert not target.exists()
    returned = json.loads((reports/'POSTROUND_FULL_RETURNED.json').read_bytes())
    f = returned['files'];result = f['evaluation/RESULT.json']
    rows = f['evaluation/ALL80.json']['first_episodes']
    curves = f['evaluation/CONTROL_CURVES.json']['curves']
    final = f['production/FINAL.json'];expected = final['checkpoint']
    release = f['OWNER_EXIT.json']; log_path=reports/'FINAL_COMPLETE_LOG_ACTUAL.json'
    logs=json.loads(log_path.read_bytes())if log_path.exists()else None
    assert logs is not None or allow_pending_full_log, 'Complete native log still pending'
    source_iteration=f['production/FULL_STATE_RESTORE.json']['source_iteration']
    source_Adam=int(f['production/FULL_STATE_RESTORE.json']['optimizer_step_min'])
    updates=final['PPO_updates']; iteration=expected['iteration']; Adam=source_Adam+updates*20
    assert final['passed_execution'] and f['TRAIN_CLOSED.json']['passed_execution']
    assert all(release[k]for k in('all_own_waited','original_cost_settled','original_leases_released'))
    assert release['error'] is None
    if logs is not None:
        assert not logs['exact_owner_alive'] and not any(logs['actual_error_lines'].values())
    assert not any(k.endswith('ERROR.json')for k in f)
    assert all(x is None for x in returned['exact_original_identities'].values())
    assert result['passed_execution'] and len(rows)==80
    assert updates>0 and iteration==source_iteration+updates
    assert expected['physics_ticks']==updates*24*8
    go=f['GO_PRODUCTION.json']
    assert go==json.loads((reports/'FIRST_ACTUAL_RETURNED.json').read_bytes())['files']['GO_PRODUCTION.json']
    assert final['epoch']<go['save_deadline'] and release['epoch']<go['nominal_end_epoch']
    # This is the one necessary full learner diagnosis, not an archival decode.
    class CompatUnpickler(pickle.Unpickler):
        def find_class(self,module,name):
            if module.startswith('numpy._core'):module=module.replace('numpy._core','numpy.core',1)
            return super().find_class(module,name)
    compat=types.ModuleType('numpy_rng_compat_pickle')
    compat.Unpickler,compat.load=CompatUnpickler,pickle.load
    model=root/'models/model_final.pt';raw=model.read_bytes()
    assert len(raw)==expected['bytes'] and hashlib.sha256(raw).hexdigest()==expected['SHA']
    saved=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False,pickle_module=compat)
    del raw
    required=('actor_state_dict','critic_state_dict','optimizer_state_dict','learning_rate',
        'components','command_rng','command_fields','physical_rng','physical_episode',
        'motor_episode_gain','cpu_rng','cuda_rng','python_rng','numpy_rng',
        'source_reward_state','source_reward_dicts','source_global_counters','target_interface')
    assert all(k in saved for k in required)
    assert saved['format']=='MOD4V1_SCUT_FULL_V4' and saved['profile']=='jump200'
    assert saved['iter']==iteration and saved['num_envs']==20000 and saved['actor_dim']==35 and saved['critic_dim']==78
    optimizer=saved['optimizer_state_dict']['state'];steps=[int(v['step'])for v in optimizer.values()]
    assert len(optimizer)==17 and min(steps)==max(steps)==Adam
    nonfinite=[]
    def finite_tensors(value,path=''):
        if torch.is_tensor(value):
            mask=~torch.isfinite(value)
            if bool(mask.any()):
                nonfinite.append(dict(path=path,shape=list(value.shape),count=int(mask.sum()),
                    nan=int(torch.isnan(value).sum()),positive_infinity=int(torch.isposinf(value).sum()),
                    negative_infinity=int(torch.isneginf(value).sum())))
            return 1
        if isinstance(value,dict):return sum(finite_tensors(v,path+'/'+str(k))for k,v in value.items())
        if isinstance(value,(list,tuple)):return sum(finite_tensors(v,path+'/'+str(k))for k,v in enumerate(value))
        return 0
    finite_count=finite_tensors(saved)
    assert not any(row['path'].split('/')[1] in ('actor_state_dict','critic_state_dict','optimizer_state_dict')for row in nonfinite)
    arr=lambda key:np.asarray([x[key]for x in curves])
    active=arr('active');phase=arr('jump_takeoff_phase');trigger=arr('jump_takeoff_trigger_event')
    action,applied,targets=(arr(k)for k in('action','applied_action','joint_target'))
    motor,velocity,torque=(arr(k)for k in('actual_motor_position','actual_motor_velocity','actual_motor_torque'))
    low=np.asarray([-1.2,-.5,-1.2,-.5]);high=np.asarray([.9,.5,.9,.5])
    assert np.isfinite(targets[active]).all() and abs(applied[active]).max()<=6
    assert (targets[active]>=low-1.e-6).all()and(targets[active]<=high+1.e-6).all()
    difference=targets[...,[0,2]]-targets[...,[1,3]]
    assert (difference[active]>=-1.0843-1.e-6).all()and(difference[active]<=.85+1.e-6).all()
    counts={k:sum(bool(r[k])for r in rows)for k in('terminated','time_out','closure_reset','mimic_reset','numerical_reset','observation_outlier')}
    controls=np.asarray([r['controls']for r in rows])
    assert all(r['physics_ticks']==r['controls']*8 for r in rows)
    origins=np.asarray(result['environment_origins'])
    with np.load(root/'evaluation/actual400hz.npz')as tick:
        mask=tick['active'];local=tick['root_pos']-origins[None]
        assert mask.shape==(len(curves)*8,80)
        rootvel=tick['root_velocity'][7::8];stationary=np.linalg.norm(rootvel[...,:2],axis=-1)<.03
        reward=arr('reward');idle=active&(phase==0)&stationary
        callbacks=dict(actual_callbacks=len(mask),first_episode_samples=int(mask.sum()),
            flight_envs=int(((tick['flight_id']>0)&mask).any(0).sum()),
            upward_flight_envs=int((tick['upward_flight']&mask).any(0).sum()),
            wholeclear_envs=int((tick['wholeclear']&mask).any(0).sum()),
            landed_top_envs=int((tick['landed_top']&mask).any(0).sum()),success_envs=int((tick['strict']&mask).any(0).sum()),
            max_actual_top_force=float(tick['top_force'][mask].max()),
            root_x_range=[float(local[...,0][mask].min()),float(local[...,0][mask].max())],
            root_height_range=[float(local[...,2][mask].min()),float(local[...,2][mask].max())],
            forward_velocity_mean=float(rootvel[...,0][active].mean()),
            stationary_fraction=float(stationary[active].mean()),
            actual_mean_reward=float(reward[active].mean()),idle_stationary_mean_reward=float(reward[idle].mean()),
            phase_fraction={str(i):float((phase[active]==i).mean())for i in np.unique(phase)},
            push_world_vz_mean=float(rootvel[...,2][active&(phase==1)].mean()),
            push_world_vz_max=float(rootvel[...,2][active&(phase==1)].max()),
            selected={str(i):dict(final_root_x=float(local[-1,i,0]),max_root_x=float(local[:,i,0].max()),
                first_takeoff_request_seconds=float((np.flatnonzero(trigger[:,i])[0]+1)*.02)if trigger[:,i].any()else None)
                for i in(0,1,40,41)})
    renders=[];images=[]
    for subdir in('recorded_native','recorded_native_late'):
        p=root/'evaluation'/subdir/'RENDER_REPORT.json';r=json.loads(p.read_bytes())
        assert r['model_SHA']==expected['SHA'] and r['NN']==r['physics_steps']==0
        renders.append(str(p));images.extend(r['media'])
    report=dict(epoch=time.time(),kind='ACTUAL_JUMP200_FINAL'+str(iteration)+'_FULL_LEARNER_AND80_REVIEW',
        final=final,train_closed=f['TRAIN_CLOSED.json'],owner_exit=release,GO=go,
        full_save_diagnosis=dict(path=str(model),bytes=expected['bytes'],SHA=expected['SHA'],
            production_model_decodes=1,prior_reader_failed_after_decode=False,
            purpose='One necessary learned STD, full Adam, RNG and queue diagnosis; no new model or physics',
            required_keys=list(required),tensor_fields_scanned=finite_count,nonfinite_state_fields=nonfinite,
            actor_critic_Adam_finite=True,Adam_entries=len(optimizer),Adam_min=min(steps),Adam_max=max(steps),
            STD=saved['actor_state_dict']['distribution.std_param'].tolist(),learning_rate=saved['learning_rate'],
            components=list(saved['components']),global_counters=saved['source_global_counters'],
            new_constructor_nominal_preserved=f['production/STARTUP.json']['D0_D7']['new_constructor_nominal_caches_preserved']),
        new_PPO_updates=updates,new_samples=updates*480000,new_Adam_steps=updates*20,result=result,
        all80=dict(counts=counts,mean_seconds=float(controls.mean()*.02),controls_min=int(controls.min()),controls_max=int(controls.max()),
            takeoff_request_envs=int(trigger.any(0).sum()), takeoff_requests_per_env=trigger.sum(0).tolist(),
            takeoff_requests_total=int(trigger.sum()),
            raw_action_mean=action[active].mean(0).tolist(),
            all_targets_and_CAD_compliant=True,raw_action_min=action[active].min(0).tolist(),raw_action_max=action[active].max(0).tolist(),
            clip_fraction=(abs(action[active])>6).mean(0).tolist(),target_min=targets[active].min(0).tolist(),target_max=targets[active].max(0).tolist(),
            target_upper_hit_fraction=np.isclose(targets[active],high,atol=1.e-6).mean(0).tolist(),
            motor_target_tracking_MAE=abs(motor[...,:4][active]-targets[active]).mean(0).tolist(),
            motor_velocity_abs_mean=abs(velocity[active]).mean(0).tolist(),motor_torque_abs_mean=abs(torque[active]).mean(0).tolist(),
            command_min=arr('command')[active].min(0).tolist(),command_max=arr('command')[active].max(0).tolist(),
            observed_height_range=[float(arr('observed_height')[active].min()),float(arr('observed_height')[active].max())],
            weighted_reward_active_curve_means={k:float(np.mean([c['weighted_reward_active_mean'][k]for c in curves]))
                for k in curves[0]['weighted_reward_active_mean']},**callbacks),
        complete_logs={key:{k:row[k]for k in('path','bytes','SHA')}for key,row in logs['logs'].items()}if logs else None,
        complete_log_review_pending=logs is None, actual_error_lines=logs['actual_error_lines']if logs else None,all4_actual_images_reviewed=True,current_model_view_image=True,
        render_reports=renders,images=images,saved_pose_quaternion_order='wxyz',
        visual_findings=['Current model native early and late side/top saved-pose frames all reviewed with native vision.',
            'All selected env0/1/40/41 approach rootx .50-.534m before edge .8m, then repeatedly pump while wheel-supported. Early spawn drops are not takeoff. Late side/top frames show no selected airborne clearance or tabletop landing.'],
        diagnosis='Final488 reaches79/80 requesting episodes and362requests, but no actual flight. Projection penalty reduced raw left-crank mean from-2.584 to-.058 and both hip request means, yet hip targets still hit the upper bound99.9937%/99.5551%. Measured mean projection cost-.00834/control is outweighed during positive-reward push pumping; present weight-2 has not removed that plateau.',
        decision='Increase only the existing projection cost weight from-2 to-10 using measured feasibility residuals and actual saved-trajectory reward counterfactuals. Preserve action mapping, motor/CAD limits, D4, physics and full learner. Continue from fullfinal488 under existing100h authorization/originalbudget after complete native log validation.',
        baseline=dict(request_envs=80,upward_flight=0,wholeclear=0,success=0,contact_terminated=78,mean_seconds=2.65875),
        optimizer_operations=0,new_physics=0,production_model_decode_for_archive=False)
    with target.open('x',encoding='utf8',newline='\n')as stream:json.dump(report,stream,ensure_ascii=False,indent=2)
    print(json.dumps(dict(report=str(target),final_iteration=saved['iter'],Adam_steps=steps[0],STD=report['full_save_diagnosis']['STD'],
        counts=counts,requests=report['all80']['takeoff_request_envs'],upwardflight=callbacks['upward_flight_envs'],
        idle_reward=callbacks['idle_stationary_mean_reward'],new_samples=report['new_samples'],images=4)))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--allow-pending-full-log',action='store_true')
    args=parser.parse_args();main(args.root.resolve(),args.allow_pending_full_log)
