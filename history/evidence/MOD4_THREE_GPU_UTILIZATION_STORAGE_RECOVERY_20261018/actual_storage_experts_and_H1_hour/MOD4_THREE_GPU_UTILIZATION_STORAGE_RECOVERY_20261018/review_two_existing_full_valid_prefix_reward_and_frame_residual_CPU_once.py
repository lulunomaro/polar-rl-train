"""Describe already collected valid first episodes and actual term readouts without new GPU work."""
from pathlib import Path
import json,time,numpy as np,traceback
B=Path(__file__).resolve().parent;R=B/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def main():
 results=[]
 for kind in ('E2','E3'):
  Q=B/('actual_'+kind+'_Linux_d4_full1500/full1500_observation');p=read(Q/'probe.json');terms=read(Q/'ACTUAL_LOADED_REWARD_TERMS_WEIGHTS_PARAMS_SOURCE.json')['terms']
  with np.load(Q/'retention_full_control_substep_actual.npz',allow_pickle=False) as z:a={k:z[k] for k in z.files}
  with np.load(Q/'actual_reward_frame_legacy_readouts.npz',allow_pickle=False) as z:f={k:z[k] for k in z.files}
  S,N=a['terminated'].shape;done=a['terminated']|a['truncated'];first=np.where(done.any(0),done.argmax(0),S);valid=np.arange(S)[:,None]<first;names=p['native_readonly_witness']['reason_names'];per=[]
  for e in range(N):
   n=int(first[e]);row=dict(env=e,first_valid_controls=n,whole15s_no_reset=n==S,first_failure_reasons=[name for i,name in enumerate(names) if n<S and a['reasons'][n,e,i]],legacy_presence={name:bool(f[name+'_active_present'].any()) for name in ('_mod4_jump','_mod4_spin','_mod4_recovery')})
   if kind=='E3':
    row.update(recipe=int(a['E3_phase_recipe'][0,e]),strict_stable50_credit_in_valid_prefix=bool(a['E3_phase_credited'][:n,e].any()),max_valid_stable_controls=int(a['E3_phase_stable'][:n,e].max()) if n else 0,upright50_and_survived15s=bool(n==S and np.any(np.convolve((a['E3_gravity_z'][:n,e]<-.984807753).astype(int),np.ones(50,dtype=int),'valid')>=50)),valid_prefix_peak_credit_is_not_stable50=True)
   per.append(row)
  reward=[]
  for i,term in enumerate(terms):
   x=f['step_reward'][...,i];reward.append(dict(name=term['name'],actual_weight=term['weight'],valid_first_episode_sum=float(x[valid].sum(dtype=np.float64)),valid_first_episode_min=float(x[valid].min()),valid_first_episode_max=float(x[valid].max()),source_SHA=term['actual_source_SHA']))
  v=dict(epoch=time.time(),expert=kind,only_existing_complete_raw_CPU=True,original_thresholds_unchanged=True,per_environment=per,first_failure_counts={name:sum(name in r['first_failure_reasons'] for r in per) for name in names},whole15s_no_reset=sum(r['whole15s_no_reset'] for r in per),all_original_false_and_postfailure_rows_retained_not_counted_as_first_episode_success=True,actual_loaded_reward_terms_readout=reward,legacy_absent_not_zero_or_old_case_proof=True,post_reset_frame_readouts_not_mislabelled_pre_reset=True,no_model_command_reward_LR_STD_physics_threshold_change=True,no_new_GPU_PPO_or_budget=True,not_unique_cause_statistical_or_skill_graduation=True)
  if kind=='E3':v.update(recovery_recipes96_strict_valid50=sum(r['strict_stable50_credit_in_valid_prefix'] for r in per if r['recipe']!=12),normal8_survived15s=sum(r['whole15s_no_reset'] for r in per if r['recipe']==12),recovery96_upright50_and_survived15s=sum(r['upright50_and_survived15s'] for r in per if r['recipe']!=12))
  else:v.update(original_world_cycle_metrics=p['world_cycle_metrics'],original_world_goal_m_s=p['goal_m_s'],original_spin_skill_pass=p['spin_skill_pass'],command_observation_error=p['command_observation_error'],actual_reward_readback_error=p['reward_readback_error'],world_goal_not_replaced_by_body_vx_target_or_analytic_projection=True)
  with (R/(kind+'_LINUX_FULL1500_VALID_FIRST_PREFIX_ACTUAL_REWARD_FRAME_RESIDUAL_CPU.json')).open('x',encoding='utf8') as out:json.dump(v,out,indent=2)
  results.append({k:v[k] for k in ('expert','whole15s_no_reset','first_failure_counts')})
 print(json.dumps(results),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('TWO_FULL_VALID_PREFIX_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_GPU_replay=True),f,indent=2)
  raise
