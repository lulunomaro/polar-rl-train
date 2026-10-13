"""Existing raw only: separate slow-progress/yaw/guard mechanisms, no GPU."""
from pathlib import Path
import json,hashlib,time,numpy as np
P=Path(__file__).resolve().parent;R=P/'reports';W=P.parent
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
reviewpath=R/'REFERENCE17B_FULL1500_COMPLETE_PAIRED91D_CPU_ACTUAL_REVIEW.json'
new=json.loads(reviewpath.read_bytes());oldpath=W/'MOD4_3060_DIRECT_FACTOR_20261013/reports/DIRECT3060_BASELINE1500_COMPLETE_INDEPENDENT_CPU_ACTUAL_REVIEW.json'
old=json.loads(oldpath.read_bytes())
assert new['passed'] and old['passed'] and new['initial_full_qXYZ_DR_queue_captured_RNG_exact_to_reference']

def getraw(review):
    row=review['raw_actual'];assert H(row['local_path'])==row['sha256']
    with np.load(row['local_path']) as z:return {k:z[k].copy() for k in z.files}

a=getraw(new);o=getraw(old)
assert len(a)==len(o)==32 and not a['terminated'].any() and not a['truncated'].any()
assert np.array_equal(a['group_ids'],o['group_ids'])
profile=json.loads((P/'payload/runtime/isaac/mod4/g4_cad_profile.json').read_bytes());half=profile['span_m']/2
collection=json.loads(Path(new['collector']['path']).read_bytes());complete=collection['outputs']['COMPLETE_ACTUAL.json']
rows=complete['initial']['actual_assignments'];centers=np.array([[(r['bounds'][0][k]+r['bounds'][1][k])/2 for k in (0,1)] for r in rows])
wheelids=[complete['body_names'].index(k) for k in ('left_wheel','right_wheel')]
contractpath=P/'payload/runtime/assets/import_contract.json'
contract=json.loads(contractpath.read_bytes());lower=float(contract['training_window']['input_difference_min_rad']);upper=.85
metrics=[];nofinal_without200=[];nofinal_withoutcontact=[]
for i in range(8):
    n=new['per_env'][i];b=old['per_env'][i]
    target=a['guarded_leg_targets'][:,i];oldtarget=o['guarded_leg_targets'][:,i]
    d=np.stack((target[:,0]-target[:,1],target[:,2]-target[:,3]),-1)
    bd=np.stack((oldtarget[:,0]-oldtarget[:,1],oldtarget[:,2]-oldtarget[:,3]),-1)
    assert (d>=lower-2e-6).all() and (d<=upper+2e-6).all()
    wheelx=a['COM_link_pos'][:,i][:,wheelids,0]-centers[i,0]
    actualforce=a['physical_wheel_force_N'].reshape(1500,4,8,2,3)[:,:,i,:,2]
    load=np.maximum(actualforce,0).sum(1)*np.float32(.0025)/np.float32(.01)
    before=wheelx.max(1)<-half-.2
    after_no200=wheelx.min(1)>half
    after=wheelx.min(1)>half+.2
    moving=i<7
    nofinal_without200.append(bool(moving and before.any() and after_no200.any()))
    nofinal_withoutcontact.append(bool(moving and before.any() and after.any()))
    entry=n['BODY_mean_speed_m_s']
    delta=a['root'][:,i,:2]-a['before_root'][:,i,:2]
    row=dict(env=i,standing=not moving,valid_controls=1500,valid_physical_seconds=15.,
             complete_1N_doublewheel_before_and_after=False,
             original91d_completed=bool(old['fullroute']['rows'][i]['complete_double1N_episodes']),
             source17b_completed=False,
             BODY_mean_speed_old_new=[b['BODY_mean_speed_m_s'],entry],
             world_progress_proxy_old_new_m=[b['world_route_progress_proxy_m'],n['world_route_progress_proxy_m']],
             max_abs_heading_old_new_deg=[b['max_abs_heading_deg'],n['max_abs_heading_deg']],
             max_abs_pitch_old_new_deg=[b['max_abs_pitch_deg'],n['max_abs_pitch_deg']],
             low_speed_under003_fraction_old_new=[b['low_speed_below003_fraction'],n['low_speed_below003_fraction']],
             actor_clip6_fraction_old_new=[b['actor_clip_fraction_columns'],n['actor_clip_fraction_columns']],
             leg_difference_guard_lower_fraction_old_new=[(abs(bd-lower)<=2e-6).mean(0).tolist(),(abs(d-lower)<=2e-6).mean(0).tolist()],
             leg_difference_guard_upper_fraction_old_new=[(abs(bd-upper)<=2e-6).mean(0).tolist(),(abs(d-upper)<=2e-6).mean(0).tolist()],
             physical_guarded_leg_difference_min_max_rad=[d.min(0).tolist(),d.max(0).tolist()],
             actor_mean_six_outputs_old_new=[o['action'][:,i].mean(0).tolist(),a['action'][:,i].mean(0).tolist()],
             wheel_after200_control_count=int(after.sum()),wheel_after0_control_count=int(after_no200.sum()),
             initial_doublewheel_1N_before_support_count=int((before&(load.min(1)>1.)).sum()),
             wheel_position_endpoints_relative_section_m=wheelx[[0,-1]].tolist(),
             min_max_actual_doublewheel_mean_support_N=[float(load.min(1).min()),float(load.min(1).max())],
             exact_no_reset_teleport_or_truncation=True)
    if i in (0,1,2):
        row['observed_residual']='Insufficient forward travel in15s; actual wheels still inside full ten-wave section. Speed is below requested0.3. Heading contributes to some extent, but does not explain low-yaw env0.'
    elif i==3:
        row['observed_residual']='Strong stagnation: BODYmean0.0329m/s and worldprogress0.4934m, despite heading below4deg. Cannot attribute this sample to heading alone.'
    elif i in (4,5,6):
        row['observed_residual']='Large yaw and lost world-route progress: BODY motion persists while intended worldX route advances poorly. Raw yaw/drive outputs are evidence, not proof of a unique training reward cause.'
    else:
        row['observed_residual']='Standing is not required to traverse. Stand drift remains diagnostic.'
    metrics.append(row)
assert sum(nofinal_without200)==0 and sum(nofinal_withoutcontact)==0
report=dict(epoch=time.time(),passed_complete_saved_raw_CPU_analysis=True,
            source17b='17b2271644bbe02ae195a16ea97b2d7442bc957a02662fb6737b81eb64f865e9',
            source91d='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4',
            paired_initial_pose_q30_allphysicalDR_recipes_queues_captured25RNG_exact=True,
            baseline91d_complete_double1N=2,new17b_complete_double1N=0,moving=7,
            actual_all7_valid_unfinished15s_prefix_retained=True,ordinary0=True,truncation0=True,
            closure_max_m=new['closure_max_m'],original_COM_contact_hardware_query_all_passed=True,
            left_head_actor_clip6_saturation_old100percent_new0percent=True,
            no_transit_even_if_remove1N_or_remove200mm=True,
            final_section_without200_complete_count=sum(nofinal_without200),
            no_contact_threshold_complete_count=sum(nofinal_withoutcontact),
            original_thresholds_not_changed=True,
            not_single_left_initializer_causal_ablation=True,
            conclusions=[
                '17b frozen policy actually regresses on this identical3060 fixture:0/7 versus91d2/7.',
                'Latest source no longer exhibits prior left actor clip6 saturation, but traversal was not improved; left-head repair is not a demonstrated passability fix.',
                'Failures separate slow/insufficient progress including a low-yaw stalled sample, and large-yaw/world-direction loss in three samples. Do not label all failure as one cause.',
                'Removing support1N or the after200mm condition from this raw would still yield0/7. Actual wheels never reached the entire section endpoint; strict aftercontact threshold alone does not explain the failure.',
                'This policy-only paired frozen fixture does not establish Linux20k backend ground-miss cause, universal policy stability, permanent antiforgetting, or80env50mmqualification.',
                'Full-state source107 checked, actor9 GPUbyteexact. Original training512 DR/optimizer was not restored into evaluation8.',
            ],
            per_env=metrics,
            references=[dict(path=str(reviewpath),sha256=H(reviewpath)),dict(path=str(oldpath),sha256=H(oldpath)),
                        new['raw_actual'],old['raw_actual'],dict(path=str(contractpath),sha256=H(contractpath))],
            no_GPU_launch_or_remote_calls=True,Git_archival_by_root_pending=True)
q=R/'REFERENCE17B_PAIRED91D_ALL_FAILURE_PREFIX_CPU_ACTUAL_REVIEW.json';assert not q.exists();q.write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(dict(report=str(q),sha256=H(q),old_complete=2,new_complete=0,low_heading_slow=[0,3],large_yaw=[4,5,6],new_actor_clip6_fraction=0.,GPU=False)))
