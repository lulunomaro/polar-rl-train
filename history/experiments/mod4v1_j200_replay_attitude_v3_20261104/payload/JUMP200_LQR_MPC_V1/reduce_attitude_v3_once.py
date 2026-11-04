"""One new-trace reduction, old comparisons from saved reductions ONLY. No physics replay."""
from pathlib import Path
import json,math,sys
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent))
from JUMP200_LQR_MPC_V1.attitude_metrics import reduce_trace
C=D/'runs/j200_attitude_v3_nominal_200003';r=json.loads((C/'result.json').read_bytes())
new=reduce_trace(C/'trace.jsonl',maximum_frames=1000);old=json.loads((D/'ATTITUDE_OLD_TWO_ONCE.json').read_bytes())
impacts={};count=0
with(C/'physics_contact_audit.jsonl').open()as f:
 for line in f:
  z=json.loads(line);count+=1
  for kind,key in(('guide','guide_normal_N'),('hard','hard_other_normal_N'),('main_left','main_normal_N2'),('main_right','main_normal_N2')):
   value=float(z[key][0 if kind=='main_left'else 1])if kind.startswith('main_')else float(z[key])
   if kind not in impacts or value>impacts[kind]['peak_N']:impacts[kind]=dict(peak_N=value,time_PRE_s=z['time_s'],contacts=z['contacts'])
comparison=[]
for o in old:
 groups={}
 for k in('all','jump','approach','push','air','landing'):
  a=o['groups'][k];b=new['groups'][k];s=dict(old_frames=a['frames'],new_frames=b['frames'],old_duration_s=a.get('duration_s'),new_duration_s=b.get('duration_s'))
  for ch in('pitch_rad','roll_rad','body_rollrate','body_pitchrate','pitchrate_rad_s','rollrate_rad_s'):
   if ch not in a or ch not in b or a[ch]is None or b[ch]is None:continue
   s[ch]={}
   for m in('peak_abs','rms'):
    ov=a[ch][m];nv=b[ch][m];s[ch][m]=dict(old=ov,new=nv,reduction_pct=(ov-nv)/ov*100 if ov else None)
  groups[k]=s
 comparison.append(dict(old_case=o['trace'],groups=groups))
push=new['groups']['push']['first_snapshot'];pre=new['groups']['approach']['last_snapshot'];air=new['groups']['air']['first_snapshot'];oldpush=old[1]['groups']['push']['pitch_peak_snapshot']
speed=dict(old_capture_first_push_estimated_vx=oldpush['estimated14'][7],old_first_push_true_vx='NOT_RETAINED_IN_FIRST_ALLOWED_REDUCTION; no extra oldraw read; never substitute estimate',new_pre_push=dict(time_post_s=pre['time_post_s'],true_body_vx_post=pre['body_velocity_post'][0],estimated_vx_at_preceding_command=pre['estimated14'][7],root_world_x_post=pre['root_post_xyz'][0]),new_first_push=dict(command_time=push['command_time_s'],estimate_vx=push['estimated14'][7],matched_truth_at_same_command=push['matched_truth_at_command'],post10ms_true_vx=push['body_velocity_post'][0],post_root_world_x=push['root_post_xyz'][0]),new_first_air_control=dict(command_time=air['command_time_s'],estimate_vx=air['estimated14'][7],matched_truth_at_same_command=air['matched_truth_at_command'],post10ms_true_vx=air['body_velocity_post'][0]),physics_first_air_run_start_PRE_s=r['physics_contact_audit']['first_full_air_s'],true_speed_at_exact2k_liftoff='NOT_LOGGED_fullrootqvel2k; use explicit100Hz bracketing, no interpolation',command_target_unchanged_m_s=1.4)
recovery=[]
for p in(D/'runs/j200_nominal_baseline_200001_attempt002/result.json',D/'runs/j200_capture_v2_nominal_200002/result.json',C/'result.json'):
 x=json.loads(p.read_bytes());land=x['physics_contact_audit']['first_landing']['time_s'];start=x['last']['time']-x['end_stable_s'];qualified=x['end_stable_s']>=2.
 recovery.append(dict(case=str(p),first_landing_PRE_s=land,terminal_stable_run_s=x['end_stable_s'],terminal_stable_run_start_post_s=start,landing_to_terminal_stable_start_s=start-land,continuous2s_qualified=qualified,first_proven2s_time_post_s=start+2 if qualified else None,full_mesh_clear_s=x['first_full_mesh_clearance'],guide_ticks=x['physics_contact_audit']['guide_contact_ticks'],hard_ticks=x['physics_contact_audit']['hard_other_contact_ticks'],MPCapproach=x['approach_ground_MPC'],MPClanding=x['landing_ground_MPC']))
result=dict(status='ONE_ATTITUDE_CANDIDATE_FINISHED_NO_SECOND_CANDIDATE',new=new,comparison=comparison,speeds=speed,recovery=recovery,new_physics_impacts=impacts,new_physics_rows_read=count,old_trace_additional_reads=0,old_reduced_JSON_only=True,wholeRMS_durations_differ_not_same_condition_singlevariable_proof=True,phases='controller-command stages; baseline predictedair includes contacts before its latecapture; not falsely named physical airborne',extra_runup_and10s_are_input_timing_changes=True,physics_changes_or_additional_runs=0,clearance_step_height_unchanged_m=.2)
with(D/'ATTITUDE_V3_COMPARISON.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2,allow_nan=False)
print('NEW_SPEEDS',json.dumps(speed))
for k,z in new['groups'].items():print('NEW_GROUP',k,json.dumps({s:z[s]for s in('frames','duration_s','pitch_rad','roll_rad','body_rollrate','body_pitchrate')}))
print('RECOVERY',json.dumps(recovery));print('IMPACTS',json.dumps(impacts));print('STOP_NO_NEW_RUN')
