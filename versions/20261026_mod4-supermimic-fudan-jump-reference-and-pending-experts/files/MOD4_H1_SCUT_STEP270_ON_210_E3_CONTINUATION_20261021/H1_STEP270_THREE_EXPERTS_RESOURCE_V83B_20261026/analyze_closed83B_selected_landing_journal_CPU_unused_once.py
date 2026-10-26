"""Read selected, immutable CPU journal records; never reconstruct platform identities or policy success."""
from pathlib import Path
import ast,hashlib,json,time,traceback
import numpy as np
N=Path(__file__).resolve().parent;R=N/'reports'
def summarize_arrays(z,case,contract):
 controls=z['recorded_control_no'];root=z['root13'];post=controls>=case['landing_control'];count=len(controls)
 assert 0<count<=81 and controls.ndim==1 and np.issubdtype(controls.dtype,np.integer) and np.all(np.diff(controls)==1) and int(controls[-1])==case['last_control'] and post.any()
 assert root.shape==(count,13) and np.isfinite(root).all() and np.all(z['episode']==case['episode'])
 # Use the exact convention already used by the original H1 physical callback,
 # not an assumed convention from a different SDK/backend.
 x,y,zz,w=root[:,3:7].T;roll=np.arctan2(2*(w*x+y*zz),1-2*(x*x+y*y));pitch=np.arcsin(np.clip(2*(w*y-zz*x),-1,1))
 planar=np.linalg.norm(root[:,7:9],axis=-1);vz=np.abs(root[:,9]);tilt=contract['stable_tilt_rad'];speed=contract['stable_speed_m_s'];pose_ok=(np.abs(roll)<tilt)&(np.abs(pitch)<tilt);speed_ok=(planar<=speed)&(vz<=speed)
 history=z['history5ms'];assert history.shape==(count,3,2,3) and np.isfinite(history).all();wheel_N=np.linalg.norm(history[:,0],axis=-1);support=(wheel_N>contract['support_N']).all(-1)
 raw=z['raw_sampled6'];executed=z['executed6'];assert raw.shape==executed.shape==(count,6) and np.isfinite(raw).all() and np.isfinite(executed).all()
 stable=z['step_stable_ticks'];success=z['step_success'];done=z['done'];request=z['public_request'];assert stable.shape==success.shape==done.shape==request.shape==(count,)
 known=speed_ok&pose_ok&support
 timeline=[]
 for i in np.flatnonzero(post)[:8]:timeline.append(dict(control=int(controls[i]),root_planar_speed_m_s=float(planar[i]),root_vz_m_s=float(root[i,9]),roll_rad=float(roll[i]),pitch_rad=float(pitch[i]),wheel_mean_force_norm_N=wheel_N[i].tolist(),original_stable_callback_ticks=int(stable[i]),original_success=bool(success[i]),selected_done=bool(done[i]),public_request=bool(request[i])))
 return dict(case_id=case['case_id'],env_id=case['env_id'],episode=case['episode'],frames=count,post_landing_sampled_controls=int(post.sum()),landing_control=case['landing_control'],end_reason=case['closed_reason'],reset_censored=bool(done.any()) or 'censored' in str(case['closed_reason']),recorded_original_success_any=bool(success.any()),original_stable_callback_ticks_max=int(stable.max()),original_stable_callbacks_required=contract['stable_callbacks'],post_planar_speed_min_m_s=float(planar[post].min()),post_planar_speed_above_original_fraction=float((planar[post]>speed).mean()),post_vertical_speed_above_original_fraction=float((vz[post]>speed).mean()),post_tilt_above_original_fraction=float((~pose_ok[post]).mean()),post_both_wheel_force_above_original_support_threshold_fraction=float(support[post].mean()),post_known_necessary_conditions_all_met_fraction=float(known[post].mean()),post_request_active_fraction=float(request[post].mean()),post_raw_leg_clip_hit_fraction=np.mean(np.abs(raw[post,:4])>=6,axis=0).tolist(),executed6_equals_original_clip6=bool(np.array_equal(executed,np.clip(raw,-6,6))),first_post_landing_samples=timeline,platform_contact_ID_full_footprint_nonwheel_clean_heading_error_and_unsampled_callbacks_unknown=True,no_causal_rootcause_or_frozen_graduation_inferred=True)
def main():
 source=json.loads((R/'CLOSED83B_LANDING_JOURNAL_SMALL_CASES_CPU_RETURNED_ACTUAL.json').read_bytes());assert source['status']=='COMPLETE_EXACT_SMALL_DERIVED_CASES_RETURNED'
 goal=N/'payloads/h1/step270_goal_and_scut_rates_candidate.py';tree=ast.parse(goal.read_bytes());node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Contract');contract={n.target.id:ast.literal_eval(n.value) for n in node.body if isinstance(n,ast.AnnAssign)}
 physical=N/'payloads/h1/job0/runtime/isaac/mod4/h1_takeoff_progress_environment_v2.py';physical_source=physical.read_text('utf8');assert 'x,y,z,w=root[:,3:7].unbind(-1)' in physical_source and 'wheelmean=self._integrated_contact.history[:,0]' in physical_source
 cases=[]
 for a in source['files']:
  with np.load(Path(a['local_path']),allow_pickle=False) as arrays:cases.append(summarize_arrays(arrays,a,contract))
 result=dict(epoch=time.time(),status='DESCRIPTIVE_SELECTED_CENSORED_LANDING_TAILS_ONLY',cases=cases,case_count=len(cases),original_contract=contract,original_goal_source_SHA=hashlib.sha256(goal.read_bytes()).hexdigest(),original_physical_callback_source_SHA=hashlib.sha256(physical.read_bytes()).hexdigest(),quaternion_interpretation='exact original physical callback root[:,3:7] x,y,z,w',source_case_cap=source['original_index']['case_cap'],source_skipped_by_cap=source['original_index']['skipped_by_case_cap'],recorded_original_success_cases=sum(x['recorded_original_success_any'] for x in cases),recorded_reset_censored_cases=sum(x['reset_censored'] for x in cases),all_selected_clip_consistent=all(x['executed6_equals_original_clip6'] for x in cases),not_wholewindow_callback_replay_frozen_policy_graduation_or_causal_reward_comparison=True,no_model_originalraw_policy_GPU_physics_budget_or_remote_action=True,no_new_training_success_or_numerical_gate=True)
 with (R/'CLOSED83B_SELECTED_LANDING_STABILITY_CPU_DESCRIPTIVE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
 print(json.dumps(dict(selected_cases=len(cases),recorded_original_success_cases=result['recorded_original_success_cases'],reset_censored_cases=result['recorded_reset_censored_cases'])))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('CLOSED83B_SELECTED_JOURNAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_replay_or_training_mutation=True),f,indent=2)
  raise
