"""ONE sequential read of this NEW case's control trace only.
No motor/contact payload reread, new integration, controller replay or raw hashing.
"""
from pathlib import Path
import json,math,traceback
D=Path(__file__).resolve().parent;C=D/'runs/v2_t01_reverse_observe_nominal_520130_001';O=D/'REDUCTION001'
O.mkdir(exist_ok=False)
(O/'START.json').write_text(json.dumps(dict(case=C.name,new_control_raw_pass_limit=1,
 motor_contact_raw_reads=0,old_raw_reads=0,physics_steps=0,raw_hash_reads=0)),encoding='utf-8')
try:
 result=json.loads((C/'result.json').read_text(encoding='utf-8'));n=0;aligned=0;unknown=0
 projection=0;projected_bins=[];complete=0;clip=[[0]*6 for _ in range(2)]
 age=[];mean_lag=[];epoch_steps=[];previous=None;max_convex_epoch_residual=0.;bad_weights=0
 known_bounds=0;force_ready=0;alpha_known=0;hardware_sync=0;samples=[];last=None
 with (C/'trace.jsonl').open(encoding='utf-8')as stream:
  for line in stream:
   r=json.loads(line);i=n;n+=1;s=r['motor_window_summary']
   complete+=int(s['complete']and s['actual_observed_substeps']==20 and s['driver_tick_delta']==20)
   count=s['target_rewrite_or_lift_count'];projection+=count
   if count:projected_bins.append(dict(control_index=i,count=count))
   for stage,key in enumerate(('first_dc_changed_ticks6','post_gain_dc_changed_ticks6')):
    for j,v in enumerate(s[key]):clip[stage][j]+=v
   a=r['alignment'];f=None if a is None else a['frame'];sample=dict(control_index=i,status=None if a is None else a['status'])
   if f is None:unknown+=1
   else:
    aligned+=1;t=f['evaluation_epoch_s'];age.append(f['arrival_age_s']);mean_lag.append(r['public_packet']['time_s']-t)
    if previous is not None:epoch_steps.append(t-previous)
    previous=t;known_bounds+=int(f['numeric_bounds_complete']);force_ready+=int(f['force_input_ready'])
    alpha_known+=int(f['alpha_B_rad_s2']is not None);hardware_sync+=int(f['hardware_sync_proven'])
    for ch in f['channels'].values():
     weights=ch['weights'];epochs=ch['source_epochs_s']
     bad_weights+=int(len(weights)!=len(epochs)or any(w < 0.0 or w > 1.0 for w in weights)or abs(sum(weights)-1.)>1e-10)
     max_convex_epoch_residual=max(max_convex_epoch_residual,abs(sum(w*x for w,x in zip(weights,epochs))-t))
    sample.update(evaluation_epoch_s=t,arrival_age_s=f['arrival_age_s'],
     encoder_q4_sources=f['channels']['encoder_q4']['source_epochs_s'],
     encoder_q4_weights=f['channels']['encoder_q4']['weights'],
     gyro_sources=f['channels']['gyro_B']['source_epochs_s'],gyro_windows=f['channels']['gyro_B']['source_windows_s'],
     driver_command_sources=f['channels']['motor_tau6']['source_epochs_s'],numeric_bounds_complete=f['numeric_bounds_complete'],force_input_ready=f['force_input_ready'])
   if i<3:samples.append(sample)
   last=sample
 def span(xs):return dict(min=min(xs),max=max(xs))if xs else None
 motor=result['private_motor_observation'];allc=motor['sections']['all']
 consistency=dict(new_rows_match_result=n==result['controls']==1200,
  complete_twenty_substep_windows=complete==n,
  summed_stage_counts_match_streamed_summary=clip==[allc['first_dc_changed_ticks6'],allc['post_gain_dc_changed_ticks6']],
  actual_motor_rows_match_physics=motor['actual_observed_physics_rows']==20*n==result['physics_steps'],
  aligned_counts_match_result=aligned==result['public_signal_observation']['aligned_frames'],
  no_convex_weight_contract_errors=bad_weights==0,
  unknown_force_input_remained_closed=force_ready==alpha_known==hardware_sync==known_bounds==0)
 output=dict(status='NEW_CASE_SINGLE_CONTROL_TRACE_REDUCTION_COMPLETE',case=C.name,
  control_rows_read=n,old_raw_reads=0,motor_contact_raw_reads=0,new_models=0,physics_steps=0,controller_replays=0,raw_hash_reads=0,
  same_actual_case_consistency=consistency,target_rewrite_or_lift_count=projection,nonzero_rewrite_control_bins=projected_bins,
  per_axis_clip_changed_ticks6=clip,aligned_frames=aligned,startup_unknown_frames=unknown,
  arrival_age_s=span(age),packet_epoch_minus_common_evaluation_s=span(mean_lag),evaluation_epoch_step_s=span(epoch_steps),
  maximum_convex_epoch_float_residual_s=max_convex_epoch_residual,bad_weights=bad_weights,
  numeric_bounds_complete_count=known_bounds,force_input_ready_count=force_ready,alpha_known_count=alpha_known,hardware_sync_proven_count=hardware_sync,
  source_examples=samples+[last],
  claim='Within this NEW full12s simulation only,both original DC stages changed no requested driver value. Do not transfer to old forward/M1 cases or hardware.',
  caveat='No clipping is not a unique cause diagnosis. Rewrites include harmless branch lifts as well as clamps;actual source windows remain nonsimultaneous. No certified error budget/force calibration/alpha,so no controller/proxy/FSM authority.')
 (O/'RESULT.json').write_text(json.dumps(output,indent=2,ensure_ascii=False),encoding='utf-8')
 print(json.dumps(output,indent=2,ensure_ascii=False),flush=True)
 if not all(consistency.values()):raise RuntimeError('New trace/receipt inconsistency retained')
except Exception as e:
 (O/'ERROR.json').write_text(json.dumps(dict(type=type(e).__name__,message=str(e),traceback=traceback.format_exc()),indent=2),encoding='utf-8')
 raise
