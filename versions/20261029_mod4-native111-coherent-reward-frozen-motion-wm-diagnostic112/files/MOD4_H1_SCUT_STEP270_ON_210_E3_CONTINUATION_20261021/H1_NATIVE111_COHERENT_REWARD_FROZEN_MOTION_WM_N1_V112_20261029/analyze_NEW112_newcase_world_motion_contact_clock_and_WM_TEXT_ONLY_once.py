from pathlib import Path
import json,math,time,statistics
S=Path(__file__).resolve().parent;R=S/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def norm(v):return math.sqrt(sum(x*x for x in v))
def main():
 actual=read(R/'FROZEN112_SINGLE_CASE_AND_WM_DIAGNOSTIC_RETURNED_ACTUAL.json');assert actual['actual_finite_returned'] and actual['actual_waited_exit']==0 and actual['actual_case_returned'] and not actual['errors']
 result=actual['case']['result'];count=result['controls'];assert 0<count<=2000 and result['physics_callbacks']==4*count and result['termination']=='actual_original_done'
 manifest=read(R/'FROZEN112_CASE_FULL_TEXT_AND_NEW_RAW_TRANSFER_ACTUAL.json');files={x['relative']:x for x in manifest['rows']};assert manifest['passed']
 control_row=files['case/episode/ACTUAL_100HZ_CONTROLS.jsonl'];physics_row=files['case/episode/ACTUAL_400HZ_31BODY_FRAMES.jsonl'];arrays=[];clock_errors=[];one_step_error=0.;origin=None
 # One newcase-only decoding purpose. No oldcase/PT/NPZ/SDK/model or remote read.
 with Path(control_row['local_path']).open('r',encoding='utf8') as f:
  for expected,line in enumerate(f,1):
   x=json.loads(line);assert x['control']==expected
   age=x['age_for_action'][0];feature=x['task_relative_features7_for_action'][5];actor=x['actor_obs86_for_action'][-2];request=200<=age<2000
   if age!=expected-1 or feature!=float(request) or actor!=float(request):clock_errors.append(dict(control=expected,age=age,feature=feature,actor_bit=actor))
   if origin is None:origin=x['env_origin3_world']
   last=x['terminal_pre_reset']['state'];diag=x['own_actual_goal_contact_geometry'];wm=x['frozen_WM_one_step'];error=max(abs(a-b) for a,b in zip(wm['predicted_wheel_bottom'],wm['actual_wheel_bottom']));one_step_error=max(one_step_error,error)
   arrays.append(dict(control=expected,time_s=expected*.01,age_for_action=age,request_for_action=request,actor_request_bit=actor,root_x=last['root13_sdk_xyzw'][0]-origin[0],root_z=last['root13_sdk_xyzw'][2]-origin[2],goal_root_x=diag['goal_value73'][0],goal_root_z=diag['goal_value73'][2],wheel_bottom2=x['actual_phase_record']['wheel_bottom2'],virtual_leg_length2=diag['virtual_leg_length2'],raw_command3_after_step=diag['raw_original_command3'],action_ingress6=last['executed6'],mean6=x['mean6'],one_step_wheel_max_error_m=error,actual_done=x['actual_original_done'],actual_phase=x['actual_phase_record']))
   arrays[-1].update(world_velocity3=last['root13_sdk_xyzw'][7:10],actor_worldheading_cue=x['actor_obs86_for_action'][3],actual_task_reward_objective=x['actual_Fudan270_objective'])
 assert len(arrays)==count and not clock_errors and sum(x['actual_done'] for x in arrays)==1 and arrays[-1]['actual_done']
 names=result['body_names'];wheels=[names.index(n) for n in ('left_wheel','right_wheel')];other=[i for i in range(len(names)) if i not in wheels]
 physics_count=0;cache_absent=[];peak=-1.;peak_row=None;first_root=None;last_root=None;segments=[];segment=None;air_by_control={};endpoint_air={};supports={};max_each=[-1.,-1.];bodyz=[];rootx=[]
 with Path(physics_row['local_path']).open('r',encoding='utf8') as f:
  for line in f:
   x=json.loads(line);k=x['physics_callback'];state=x['state'];p=state['root13_sdk_xyzw'];root=[p[i]-origin[i] for i in range(3)]
   if first_root is None:first_root=root
   last_root=root
   if k==0:continue
   physics_count+=1;assert k==physics_count
   metric=state['metrics'];bodyz.append(root[2]);rootx.append(root[0])
   if not metric['wheel_cache_available']:cache_absent.append(k);continue
   bottom=metric['wheel_bottom_above_floor_m'];forces=[norm(a) for a in state['body_contact_force31']];wheel_force=[forces[i] for i in wheels];non=max(forces[i] for i in other);both=min(bottom)
   if both>peak:peak=both;peak_row=dict(callback=k,time_s=k*.0025,bottom2=bottom,wheel_force_norm2=wheel_force,nonwheel_max_force_N=non,root_vz=p[9],root_xyz=root)
   max_each=[max(a,b) for a,b in zip(max_each,bottom)]
   air=both>.005 and max(wheel_force)<=1 and non<=1
   control=(k-1)//4+1;air_by_control[control]=air_by_control.get(control,False) or air
   if k%4==0:endpoint_air[control]=air
   supports[k]=max(wheel_force)>1 and min(wheel_force)>1 and non<=1
   if air:
    if segment is None:segment=dict(first_callback=k,last_callback=k,callbacks=0,peak_both_wheel_bottom_m=-1.,max_wheel_contact_N=0.,max_nonwheel_contact_N=0.,max_root_vz=-1e9,min_root_vz=1e9)
    segment.update(last_callback=k,callbacks=segment['callbacks']+1,peak_both_wheel_bottom_m=max(segment['peak_both_wheel_bottom_m'],both),max_wheel_contact_N=max(segment['max_wheel_contact_N'],max(wheel_force)),max_nonwheel_contact_N=max(segment['max_nonwheel_contact_N'],non),max_root_vz=max(segment['max_root_vz'],p[9]),min_root_vz=min(segment['min_root_vz'],p[9]))
   elif segment is not None:segments.append(segment);segment=None
 if segment is not None:segments.append(segment)
 assert physics_count==4*count and not cache_absent
 for x in segments:x.update(start_time_s=x['first_callback']*.0025,end_time_s=x['last_callback']*.0025,duration_s=x['callbacks']*.0025)
 windows=read(files['case/episode/NEW112_ACTUAL_ACTION_CONTIGUOUS_8_32_WM_WINDOWS_ACTUAL.json']['local_path']);phase=windows['phase_records'];wm_summary={};corrections=[]
 for horizon in (8,32):
  rows=[x for x in windows['rows'] if x['horizon']==horizon];all_errors=[];air_endpoint_errors=[];enter=[];contains=[];land=[]
  for x in rows:
   start=x['start_control'];stop=start+horizon-1;pre=phase[start-2] if start>=2 else None
   # Selected112 source records the actual prior endpoint INPUT label.
   # Independently require clean nonwheel force for this strict supported subset.
   known_supported_start=pre is not None and pre['both_supported'] and pre['nonwheel_max_load_N']<=1
   anyair=any(air_by_control.get(i,False) for i in range(start,stop+1))
   if known_supported_start and anyair:enter.append(start)
   if anyair:contains.append(start)
   if anyair and phase[stop-1]['both_supported']:land.append(start)
   corrections.append(dict(horizon=horizon,start_control=start,selected_source_input_grounded_label=x['starts_grounded_not_air'],actual_input_supported=known_supported_start if pre is not None else None,actual_input_phase_source='previous control terminal before reset; no reset until final',contains_5mm_airborne_physics_callback=anyair))
   for step in x['steps']:
    errors=step['wheel_bottom_abs_error2'];all_errors.extend(errors)
    if phase[start+step['offset']-2]['airborne_both_above5mm_and_unloaded']:air_endpoint_errors.extend(errors)
  wm_summary[str(horizon)]=dict(windows=len(rows),contains_airborne_callbacks=len(contains),supported_input_to_actual_airborne_windows=len(enter),supported_input_start_controls=enter,air_then_supported_endpoint_windows=len(land),max_wheel_abs_error_m=max(all_errors) if all_errors else None,max_error_at_airborne_control_endpoints_m=max(air_endpoint_errors) if air_endpoint_errors else None,airborne_endpoint_error_count=len(air_endpoint_errors),not_population_generalization_or_unseen27cm_accuracy=True)
 sensitivity=read(files['case/episode/FROZEN_FUDAN270_32STEP_FIRST_ACTION_SENSITIVITY_ACTUAL.json']['local_path']);derivatives=[]
 for x in sensitivity['rows']:
  a=norm(x['first_action_reward_gradient6'][0]);b=norm(x['first_action_critic_tail_gradient6'][0]);pred=max(min(y['wheel_bottom2'][0]) for y in x['predicted32'])
  derivatives.append(dict(start_control=x['start_control'],reward_first_action_grad_norm=a,critic_tail_first_action_grad_norm=b,tail_to_reward_grad_norm_ratio=b/a if a else None,predicted32_max_both_wheel_bottom_m=pred,all_gradients_finite=x['all_values_finite']))
 active=[x for x in arrays if x['request_for_action']]
 request_motion=dict(actual_controls=len(active),world_forward_target_m_s=.5,world_vx_mean=statistics.fmean(x['world_velocity3'][0] for x in active) if active else None,world_vx_target_abs_error_mean=statistics.fmean(abs(x['world_velocity3'][0]-.5) for x in active) if active else None,world_vy_abs_mean=statistics.fmean(abs(x['world_velocity3'][1]) for x in active) if active else None,actor_heading_cue_range=[min(x['actor_worldheading_cue'] for x in active),max(x['actor_worldheading_cue'] for x in active)] if active else None,world_vx_negative_controls=sum(x['world_velocity3'][0]<0 for x in active),measured_world_velocity_not_reward_proxy=True)
 outcome=dict(actual_request_motion=request_motion,epoch=time.time(),actual_case_returned=True,source111_formal_SHA=read(S/'EVAL_BINDING.json')['source_model']['SHA'],source_model_loads_this_new_purpose=1,no_old104_105_98_model_or_raw_reads=True,controls=count,physics_callbacks=4*count,physical_seconds=count*.01,original_termination_terms=result['last_termination_terms'],full_requested2000controls=count==2000,original270=result['original270_terminal_physics_events'],frozen_Pi_WM_Critic_norms_unchanged=actual['case']['passed'],clock_ages_all_actual_controls_coherent=True,actual_actor_request_matches_200_2000_all_actual_controls=True,clock_mismatches=clock_errors,root_start_xyz=first_root,root_final_terminal_xyz=last_root,root_net_forward_m=last_root[0]-first_root[0],root_x_range_m=[min(rootx),max(rootx)],body_height_range_m=[min(bodyz),max(bodyz)],both_wheel_simultaneous_peak_m=peak,individual_wheel_peaks_m=max_each,peak_callback=peak_row,above5mm_clean_contact_flight_segments=segments,airborne_both_above5mm_callbacks=sum(x['callbacks'] for x in segments),any20cm_or27cm_height_in_this_one_case=peak>=.2,not_hardware_or_population_success_rate_or_training_memory_replay=True,one_step_teacherforced_max_wheel_error_m=one_step_error,contiguous_actual_action_WM=wm_summary,source_window_phase_label_scope_correction='Selected112 source uses previous actual terminal as input, first unknown. This report additionally requires nonwheel<=1N for clean-supported-input subsets. Original flags remain, no model/physics rerun.',window_label_corrections=corrections,frozen_first_action_sensitivity=derivatives,raw_decode_scope='One NEW112 case motion/contact/clock/WM analysis pass; no old raw/weight/SDK/remote/Git content reads',raw_producer_files=[control_row,physics_row],WM_coverage_still_limited_to_this_one_case=True,qualified111_remains_native_method_not_skill=True,wholecase_actually_finished_before_inference_validation=True,source_shares_20s_clock_and_dynamics_not_causal20s_comparison=True)
 put(R/'NEW112_ACTUAL20S_MOTION_CONTACT_CLOCK_AND_CONTIGUOUS_WM_ANALYSIS_ACTUAL.json',outcome);put(R/'NEW112_DERIVED_CONTROL_CURVES_FOR_PLOT_ONLY.json',dict(rows=arrays,source_control_producer=control_row,raw_not_needed_for_plot_again=True))
 print(json.dumps({k:outcome[k] for k in ['controls','physics_callbacks','root_net_forward_m','root_x_range_m','body_height_range_m','both_wheel_simultaneous_peak_m','above5mm_clean_contact_flight_segments','one_step_teacherforced_max_wheel_error_m','contiguous_actual_action_WM','actual_request_motion']}))
if __name__=='__main__':main()
