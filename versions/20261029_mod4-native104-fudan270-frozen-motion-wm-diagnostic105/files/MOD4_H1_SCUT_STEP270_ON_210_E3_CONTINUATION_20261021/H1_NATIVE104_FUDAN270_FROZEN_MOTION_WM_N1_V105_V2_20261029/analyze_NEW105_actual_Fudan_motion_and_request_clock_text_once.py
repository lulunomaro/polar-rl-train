from pathlib import Path
import hashlib,json,math,time,traceback
S=Path(__file__).resolve().parent;R=S/'reports'
def main():
 import numpy as np
 receipt=json.loads((R/'FROZEN105_CASE_FULL_TEXT_AND_NEW_RAW_TRANSFER_ACTUAL.json').read_bytes());rows={x['relative']:x for x in receipt['rows']}
 def read_json(name):return json.loads(Path(rows[name]['local_path']).read_bytes())
 def read_lines(name):
  with Path(rows[name]['local_path']).open(encoding='utf8') as f:return [json.loads(line) for line in f]
 # New105 raw is decoded once for this actual-purpose analysis, never old98 raw.
 controls=read_lines('case/episode/ACTUAL_100HZ_CONTROLS.jsonl');frames=read_lines('case/episode/ACTUAL_400HZ_31BODY_FRAMES.jsonl');status=read_json('case/episode/FROZEN_SINGLE_CASE_STATUS_ACTUAL.json');eight=read_json('case/episode/FROZEN_WM_EIGHT_STEP_PAIRED_ACTUAL.json')['rows'];sens=read_json('case/episode/FROZEN_FUDAN270_32STEP_FIRST_ACTION_SENSITIVITY_ACTUAL.json')['rows']
 assert len(controls)==status['controls']==500 and len(frames)==2001 and status['physics_callbacks']==2000
 physical=[x for x in frames if x['physics_callback']>0];assert all(x['state']['metrics']['wheel_cache_available'] for x in physical)
 low=np.asarray([x['state']['metrics']['wheel_bottom_above_floor_m'] for x in physical]);root=np.asarray([x['state']['root13_sdk_xyzw'] for x in physical]);ages=np.asarray([x['age_for_action'][0] for x in controls]);goal=np.asarray([x['own_actual_goal_contact_geometry']['goal_value73'] for x in controls]);legs=np.asarray([x['own_actual_goal_contact_geometry']['virtual_leg_length2'] for x in controls]);step_time=(np.arange(500)+1)*.01
 observed_feature_request=(ages>=100)&(ages<180);actual_request=(ages>=200)&(ages<500);mismatch=observed_feature_request!=actual_request
 def span(mask):return np.flatnonzero(mask).tolist()
 wheel_max=float(np.min(low,axis=1).max());segments=[];start=None
 for i,yes in enumerate(np.min(low,axis=1)>.005):
  if yes and start is None:start=i
  if start is not None and (not yes or i==len(low)-1):
   end=i+1 if yes else i;segments.append((end-start)*.0025);start=None
 def magnitude(x):return math.sqrt(sum(float(a)**2 for row in x for a in row))
 gradients=[]
 for x in sens:
  a=magnitude(x['first_action_reward_gradient6']);b=magnitude(x['first_action_critic_tail_gradient6']);gradients.append(dict(start_control=x['start_control'],reward_objective=x['reward_objective'],critic_tail=x['critic_tail'],reward_first_action_gradient_norm=a,critic_first_action_gradient_norm=b,tail_to_reward_gradient_norm_ratio=b/a if a>0 else None,all_values_finite=x['all_values_finite']))
 errors1=[abs(x['frozen_WM_one_step']['predicted_wheel_bottom'][i]-x['frozen_WM_one_step']['actual_wheel_bottom'][i]) for x in controls for i in range(2)];errors8=[abs(x['predicted_wheel_bottom'][i]-x['actual_wheel_bottom'][i]) for x in eight for i in range(2)]
 value=dict(epoch=time.time(),new_purpose='NEW105 qualified104 frozen Fudan270 own-plant motion and paired WM diagnosis',source_model_SHA='764129c1b4c9ec4560d83423856e9f4f5867f8f18c841215f43ed5552415b89c',source_raw_receipts=[rows[k] for k in ('case/episode/ACTUAL_100HZ_CONTROLS.jsonl','case/episode/ACTUAL_400HZ_31BODY_FRAMES.jsonl')],controls=500,physics_callbacks=2000,simulated_seconds=5,original_termination=status['last_termination_terms'],original270_events=status['original270_terminal_physics_events'],simultaneous_both_wheel_bottom_peak_m=wheel_max,longest_both_wheel_bottom_over5mm_s=max(segments,default=0.),wheel_bottom_perwheel_max_m=low.max(0).tolist(),root_height_min_max_m=[float(root[:,2].min()),float(root[:,2].max())],root_x_initial_final_m=[float(root[0,0]),float(root[-1,0])],root_world_vz_min_max_m_s=[float(root[:,9].min()),float(root[:,9].max())],actual_hip_wheel_virtual_leg_length_range_m=[float(legs.min()),float(legs.max())],active_goal_root_height_range_m=[float(goal[actual_request,2].min()),float(goal[actual_request,2].max())],frozen_pi_norm_unchanged=status['policy_parameters_and_saved_normalizers_literal_unchanged'],frozen_WM_norm_unchanged=status['WM_parameters_and_saved_normalizers_literal_unchanged'],critic_frozen_literal_check_ran_before_successful_function_return=True,request_feature_clock=dict(scope='Exact source function evaluated on recorded actual action ages; no second actor/model forward',feature_request_true_action_age=[100,180],actual_command_and_goal_request_age=[200,500],disagreeing_controls=int(mismatch.sum()),false_positive_controls=int((observed_feature_request&~actual_request).sum()),false_negative_controls=int((actual_request&~observed_feature_request).sum())),WM_actual_action_one_step_max_wheel_error_m=max(errors1),WM_actual_action_eight_step_max_wheel_error_m=max(errors8),WM_accuracy_scope='Only this single recorded actual trajectory; no unseen airborne/global or counterfactual accuracy proof',frozen_first_action_sensitivities=gradients,not_policy_parameter_gradients=True,not_unique_cause_or_mechanical_feasibility_proof=True,no_reward_or_clock_fix_installed=True,source106_clock_repair_only_candidate=True,no_saved_model_reread_or_physics_rerun=True)
 with (R/'NEW105_ACTUAL_MOTION_REQUEST_CLOCK_AND_WM_TEXT_ANALYSIS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False)
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,ax=plt.subplots(4,1,figsize=(11,10),sharex=True,constrained_layout=True);physical_t=np.arange(1,2001)*.0025
 ax[0].plot(physical_t,root[:,2],label='actual body height');ax[0].plot(step_time,goal[:,2],'--',label='input body-height goal');ax[0].set_ylabel('Height (m)');ax[0].legend()
 ax[1].plot(physical_t,low[:,0]*1000,label='left wheel bottom');ax[1].plot(physical_t,low[:,1]*1000,label='right wheel bottom');ax[1].axhline(5,color='black',linestyle='--',label='5 mm low-clearance check');ax[1].set_ylabel('Clearance (mm)');ax[1].legend()
 ax[2].plot(step_time,legs[:,0],label='actual left hip-wheel length');ax[2].plot(step_time,legs[:,1],label='actual right hip-wheel length');ax[2].axhline(.31,color='black',linestyle='--',label='extension reward proposal');ax[2].axhline(.16,color='grey',linestyle=':',label='tuck reward proposal');ax[2].set_ylabel('Length (m)');ax[2].legend()
 ax[3].step(step_time,actual_request.astype(float),where='post',label='actual command request: 2-5 s');ax[3].step(step_time,observed_feature_request.astype(float),where='post',linestyle='--',label='policy input request feature: 1-1.8 s');ax[3].set_ylabel('Request bit');ax[3].set_xlabel('Physical episode time (s)');ax[3].set_ylim(-.1,1.2);ax[3].legend()
 for a in ax:a.axvspan(2,5,color='gold',alpha=.10);a.grid(alpha=.25)
 fig.suptitle('NEW105 frozen native104: actual 270 mm step case; request feature is misaligned')
 p=S/'NEW105_ACTUAL_MOTION_AND_REQUEST_FEATURE_CLOCK.png';fig.savefig(p,dpi=150);plt.close(fig)
 with (R/'NEW105_DERIVED_FIGURE_PRODUCER_METADATA.json').open('x',encoding='utf8') as f:json.dump(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),producer='this new text-only analysis, not a rerender of old raw',original_new_raw_retained=True),f,indent=2)
 print(json.dumps({k:value[k] for k in ['controls','simultaneous_both_wheel_bottom_peak_m','longest_both_wheel_bottom_over5mm_s','root_height_min_max_m','root_x_initial_final_m','actual_hip_wheel_virtual_leg_length_range_m','request_feature_clock','WM_actual_action_one_step_max_wheel_error_m','WM_actual_action_eight_step_max_wheel_error_m','frozen_first_action_sensitivities']}))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('NEW105_TEXT_ANALYSIS_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_model_or_physics_rerun=True),f,indent=2)
  raise
