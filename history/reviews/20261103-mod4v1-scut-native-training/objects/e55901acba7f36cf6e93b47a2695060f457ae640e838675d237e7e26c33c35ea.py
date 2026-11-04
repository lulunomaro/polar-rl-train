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


def main(root):
    reports = root/'reports'
    target = reports/'ACTUAL_JUMP200_FINAL_LEARNING_AND_ALL80_REVIEW.json'
    assert not target.exists()
    returned = json.loads((reports/'POSTROUND_FULL_RETURNED.json').read_bytes())
    f = returned['files'];result = f['evaluation/RESULT.json']
    rows = f['evaluation/ALL80.json']['first_episodes']
    curves = f['evaluation/CONTROL_CURVES.json']['curves']
    final = f['production/FINAL.json'];expected = final['checkpoint']
    release = f['OWNER_EXIT.json'];logs = json.loads((reports/'FINAL_COMPLETE_LOG_ACTUAL.json').read_bytes())
    assert final['passed_execution'] and f['TRAIN_CLOSED.json']['passed_execution']
    assert all(release[k]for k in('all_own_waited','original_cost_settled','original_leases_released'))
    assert release['error'] is None and not logs['exact_owner_alive']
    assert not any(logs['actual_error_lines'].values())
    assert not any(k.endswith('ERROR.json')for k in f)
    assert all(x is None for x in returned['exact_original_identities'].values())
    assert result['passed_execution'] and len(rows)==80
    assert final['PPO_updates']==70 and expected['iteration']==150
    assert expected['physics_ticks']==70*24*8
    go=f['GO_PRODUCTION.json']
    assert go['save_deadline']==1793805094.5800261 and go['nominal_end_epoch']==1793805394.5800261
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
    assert saved['iter']==150 and saved['num_envs']==20000 and saved['actor_dim']==35 and saved['critic_dim']==78
    optimizer=saved['optimizer_state_dict']['state'];steps=[int(v['step'])for v in optimizer.values()]
    assert len(optimizer)==17 and min(steps)==max(steps)==3000
    def finite_tensors(value):
        if torch.is_tensor(value):
            assert bool(torch.isfinite(value).all())
            return 1
        if isinstance(value,dict):return sum(finite_tensors(v)for v in value.values())
        if isinstance(value,(list,tuple)):return sum(finite_tensors(v)for v in value)
        return 0
    finite_count=finite_tensors(saved)
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
        assert not ((tick['flight_id']>0)&mask).any()
        assert not (tick['wholeclear']&mask).any() and not(tick['strict']&mask).any()
        assert not tick['top_force'][mask].any()
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
            selected={str(i):dict(final_root_x=float(local[-1,i,0]),max_root_x=float(local[:,i,0].max()),
                first_takeoff_request_seconds=float((np.flatnonzero(trigger[:,i])[0]+1)*.02)if trigger[:,i].any()else None)
                for i in(0,1,40,41)})
    renders=[];images=[]
    for subdir in('recorded_native','recorded_native_late'):
        p=root/'evaluation'/subdir/'RENDER_REPORT.json';r=json.loads(p.read_bytes())
        assert r['model_SHA']==expected['SHA'] and r['NN']==r['physics_steps']==0
        renders.append(str(p));images.extend(r['media'])
    report=dict(epoch=time.time(),kind='ACTUAL_JUMP200_FINAL150_FULL_LEARNER_AND80_REVIEW',
        final=final,train_closed=f['TRAIN_CLOSED.json'],owner_exit=release,GO=go,
        full_save_diagnosis=dict(path=str(model),bytes=expected['bytes'],SHA=expected['SHA'],
            production_model_decodes=1,purpose='Diagnose actual learned STD, full Adam, RNG and queues after failed skill outcome',
            required_keys=list(required),finite_tensors=finite_count,Adam_entries=len(optimizer),Adam_min=min(steps),Adam_max=max(steps),
            STD=saved['actor_state_dict']['distribution.std_param'].tolist(),learning_rate=saved['learning_rate'],
            components=list(saved['components']),global_counters=saved['source_global_counters'],
            new_constructor_nominal_preserved=f['production/STARTUP.json']['D0_D7']['new_constructor_nominal_caches_preserved']),
        new_PPO_updates=70,new_samples=70*480000,new_Adam_steps=1400,result=result,
        all80=dict(counts=counts,mean_seconds=float(controls.mean()*.02),controls_min=int(controls.min()),controls_max=int(controls.max()),
            takeoff_request_envs=int(trigger.any(0).sum()),
            all_targets_and_CAD_compliant=True,raw_action_min=action[active].min(0).tolist(),raw_action_max=action[active].max(0).tolist(),
            clip_fraction=(abs(action[active])>6).mean(0).tolist(),target_min=targets[active].min(0).tolist(),target_max=targets[active].max(0).tolist(),
            target_upper_hit_fraction=np.isclose(targets[active],high,atol=1.e-6).mean(0).tolist(),
            motor_target_tracking_MAE=abs(motor[...,:4][active]-targets[active]).mean(0).tolist(),
            motor_velocity_abs_mean=abs(velocity[active]).mean(0).tolist(),motor_torque_abs_mean=abs(torque[active]).mean(0).tolist(),
            command_min=arr('command')[active].min(0).tolist(),command_max=arr('command')[active].max(0).tolist(),
            observed_height_range=[float(arr('observed_height')[active].min()),float(arr('observed_height')[active].max())],
            weighted_reward_active_curve_means={k:float(np.mean([c['weighted_reward_active_mean'][k]for c in curves]))
                for k in curves[0]['weighted_reward_active_mean']},**callbacks),
        complete_logs={key:{k:row[k]for k in('path','bytes','SHA')}for key,row in logs['logs'].items()},
        actual_error_lines=logs['actual_error_lines'],all4_actual_images_reviewed=True,current_model_view_image=True,
        render_reports=renders,images=images,saved_pose_quaternion_order='wxyz',
        visual_findings=['All4 early sequences drop from spawn and remain wheel-supported; no upward takeoff.',
            'Late env0/40/41 remain near birth through7.98s; env1 slowly approaches x~.51 and stops below the .8m edge. No selected robot lands on the tabletop.'],
        diagnosis='The reward admits a stationary approach solution: idle positive reward~.0825/control, only41/80 requests and1.74% phase-active endpoints,0groundedlaunch. This is skill failure despite valid native PPO and healthy numerical execution.',
        decision='Do not repeat this reward unchanged. Prepare progress-gated approach bonuses and a dense source upward-velocity push reward; retain physics/source learning state/actual200mm acceptance. Originalhour fullyclosed; no new3600 granted by this review.',
        baseline=dict(request_envs=80,upward_flight=0,wholeclear=0,success=0,contact_terminated=78,mean_seconds=2.65875),
        optimizer_operations=0,new_physics=0,production_model_decode_for_archive=False)
    with target.open('x',encoding='utf8',newline='\n')as stream:json.dump(report,stream,ensure_ascii=False,indent=2)
    print(json.dumps(dict(report=str(target),final_iteration=saved['iter'],Adam_steps=steps[0],STD=report['full_save_diagnosis']['STD'],
        counts=counts,requests=report['all80']['takeoff_request_envs'],upwardflight=callbacks['upward_flight_envs'],
        idle_reward=callbacks['idle_stationary_mean_reward'],new_samples=report['new_samples'],images=4)))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True)
    main(parser.parse_args().root.resolve())
