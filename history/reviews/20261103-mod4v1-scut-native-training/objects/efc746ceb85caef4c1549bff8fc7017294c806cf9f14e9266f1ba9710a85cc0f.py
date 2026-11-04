"""Summarize the actual saved stair episodes, without loading policy weights."""
from pathlib import Path
import argparse
import json
import time
import numpy as np


def summarize(returned, directory):
    facts=json.loads(returned.read_bytes())['files']
    result=facts['evaluation/RESULT.json']
    rows=facts['evaluation/ALL80.json']['first_episodes']
    curves=facts['evaluation/CONTROL_CURVES.json']['curves']
    release=facts.get('RELEASE.json') or facts['OWNER_EXIT.json']
    assert result['passed_execution'] and len(rows)==80
    assert release['all_own_waited'] and release.get('locks_released',release.get('original_leases_released')) and release['error'] is None
    if 'OWNER_EXIT.json' in facts:
        assert release['original_cost_settled']
    assert 'ERROR.json' not in facts and 'evaluation/ERROR.json' not in facts
    assert all(row['controls']*8==row['physics_ticks']for row in rows)
    arr=lambda name:np.asarray([row[name]for row in curves])
    active=arr('active')
    actions,applied,targets=(arr(name)for name in ('action','applied_action','joint_target'))
    position,velocity,torque=(arr(name)for name in
        ('actual_motor_position','actual_motor_velocity','actual_motor_torque'))
    low=np.asarray([-1.2,-.5,-1.2,-.5]);high=np.asarray([.9,.5,.9,.5])
    assert np.isfinite(targets[active]).all() and abs(applied[active]).max()<=6
    assert(targets[active]>=low-1.e-6).all()and(targets[active]<=high+1.e-6).all()
    difference=targets[...,[0,2]]-targets[...,[1,3]]
    assert(difference[active]>=-1.0843-1.e-6).all()and(difference[active]<=.85+1.e-6).all()
    counts={key:sum(bool(row[key])for row in rows)for key in
        ('terminated','time_out','closure_reset','mimic_reset','numerical_reset','observation_outlier')}
    controls=np.asarray([row['controls']for row in rows])
    ground,observed,command=(arr(name)for name in('ground_height','observed_height','effective_height'))
    origins=np.asarray(result['environment_origins'])
    with np.load(directory/'actual400hz.npz')as data:
        mask=data['active']
        assert mask.shape[1]==80 and mask.shape[0]==len(curves)*8
        assert not data['strict'][mask].any()
        relative=data['root_pos']-origins[None]
        displacement=np.linalg.norm(data['root_pos'][...,:2]-data['root_pos'][0,:,:2],axis=-1)
        supported=data['surface_support_force']>1
        support_height=data['surface_support_height']
        valid_support=supported&mask[...,None]
        support_range=[float(support_height[valid_support].min()),float(support_height[valid_support].max())]if valid_support.any()else None
        callback_summary=dict(callbacks=len(mask),first_episode_samples=int(mask.sum()),
            actual_support_height_range=support_range,
            root_height_above_generator_origin_range=[float(relative[...,2][mask].min()),float(relative[...,2][mask].max())],
            max_horizontal_displacement_from_first_callback=float(displacement[mask].max()))
    weighted={key:float(np.mean([row['weighted_reward_active_mean'][key]for row in curves]))
              for key in curves[0]['weighted_reward_active_mean']}
    report=dict(epoch=time.time(),returned=str(returned),native_execution_passed=True,
        source_SHA=result['source_SHA'],optimizer_operations=0,production_model_reads=0,new_physics=0,
        current_model_view_image=False,native_images_review_pending=True,
        old270mm_criterion_required=False,course=result['course'],result=result,
        all80=dict(counts=counts,cap8s_without_task_done=sum(not row['terminated']and not row['time_out']for row in rows),
            controls=dict(min=int(controls.min()),max=int(controls.max()),mean=float(controls.mean()),mean_seconds=float(controls.mean()*.02)),
            targets_compliant=True,CAD_difference_compliant=True,
            raw_action_min=actions[active].min(0).tolist(),raw_action_max=actions[active].max(0).tolist(),
            clip_fraction=(abs(actions[active])>6).mean(0).tolist(),
            target_min=targets[active].min(0).tolist(),target_max=targets[active].max(0).tolist(),
            target_upper_hit_fraction=np.isclose(targets[active],high,atol=1.e-6).mean(0).tolist(),
            motor_position_min=position[active].min(0).tolist(),motor_position_max=position[active].max(0).tolist(),
            motor_velocity_abs_mean=abs(velocity[active]).mean(0).tolist(),motor_torque_abs_mean=abs(torque[active]).mean(0).tolist(),
            motor_target_tracking_MAE=abs(position[...,:4][active]-targets[active]).mean(0).tolist(),
            observed_height_range=[float(observed[active].min()),float(observed[active].max())],
            ground_height_range=[float(ground[active].min()),float(ground[active].max())],
            command_height_range=[float(command[active].min()),float(command[active].max())],
            weighted_reward_active_means=weighted,**callback_summary),release=release,
        next='Inspect all actual saved-pose images, append findings and decide within the current authorization; a completed window does not authorize another training hour')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--returned',type=Path,required=True)
    parser.add_argument('--directory',type=Path,required=True);parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    assert not args.report.exists()
    value=summarize(args.returned,args.directory)
    with args.report.open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2)
    print(json.dumps(dict(report=str(args.report),all80=value['all80'],result=value['result'])))
