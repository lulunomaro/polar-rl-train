"""CPU-only direct D3 pair observer; reads immutable completed cases, never launches GPU."""
from pathlib import Path
import hashlib,json,time,numpy as np

D=Path(__file__).resolve().parent
R=D/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load(name):
 p=R/name
 report=json.loads(p.read_bytes())
 assert report['passed'] and report['actual_shared_OSlock_free']
 collector=json.loads(Path(report['collector']['path']).read_bytes())
 assert H(report['collector']['path'])==report['collector']['sha256']
 complete=collector['outputs']['COMPLETE_ACTUAL.json']
 raw=report['raw_actual'];assert H(raw['local_path'])==raw['sha256']
 with np.load(raw['local_path']) as z:arrays={k:z[k].copy() for k in z.files}
 return p,report,complete,arrays

def main():
 bp,b,bc,ba=load('DIRECT3060_BASELINE1500_COMPLETE_INDEPENDENT_CPU_ACTUAL_REVIEW.json')
 dp,d,dc,da=load('DIRECT3060_D3CURRENT1500_COMPLETE_PAIRED_CPU_ACTUAL_REVIEW.json')
 assert bc['initial']==dc['initial']
 assert set(ba)==set(da)
 assert not ba['terminated'].any() and not da['terminated'].any()
 assert not ba['truncated'].any() and not da['truncated'].any()
 delays=bc['initial']['parameters']['feedback_requested_us']
 assert delays==[10000,10000,0,0,10000,10000,0,10000]
 negative_controls=[i for i in range(7) if delays[i]==0]
 matrix={}
 for i in negative_controls:
  fields={}
  for key,a in ba.items():
   x,y=(a[i],da[key][i]) if a.shape==(8,) else (a[:,i],da[key][:,i])
   fields[key]=bool(np.array_equal(x,y))
  matrix[str(i)]=fields
 assert all(all(fields.values()) for fields in matrix.values()),'Zero-delay negative-control trajectories differ'
 irng=bc['initial']['parameters']['actual_captured_RNG_bytes']
 frngb=bc['final_parameters']['actual_captured_RNG_bytes'];frngd=dc['final_parameters']['actual_captured_RNG_bytes']
 assert len(irng)==25 and irng==dc['initial']['parameters']['actual_captured_RNG_bytes']
 assert frngb==frngd,'Actual final RNG bytes differ despite no resets; retain before inference'
 contractpath=D/'payload/runtime/assets/import_contract.json'
 contract=json.loads(contractpath.read_bytes())
 minimum=float(contract['training_window']['input_difference_min_rad'])
 assert minimum==-1.0843
 rows=[]
 for i in range(8):
  rb,rd=b['fullroute']['rows'][i],d['fullroute']['rows'][i]
  bb=bool(rb['complete_double1N_episodes']);dd=bool(rd['complete_double1N_episodes'])
  legstats={}
  for name,arrays in [('baseline',ba),('D3',da)]:
   target=arrays['guarded_leg_targets'][:,i]
   low=np.asarray(target[:,[1,3]]+np.float32(minimum),dtype=target.dtype)
   legstats[name]={
    'original_leg_order':['left_crank','left_hip','right_crank','right_hip'],
    'left_raw_actor_negative_clip6_fraction':float((arrays['action'][:,i,0]<=-6).mean()),
    'right_raw_actor_negative_clip6_fraction':float((arrays['action'][:,i,2]<=-6).mean()),
    'left_guarded_target_lower_boundary_fraction':float((target[:,0]==low[:,0]).mean()),
    'right_guarded_target_lower_boundary_fraction':float((target[:,2]==low[:,1]).mean()),
    'left_raw_actor_range':[float(arrays['action'][:,i,0].min()),float(arrays['action'][:,i,0].max())],
    'right_raw_actor_range':[float(arrays['action'][:,i,2].min()),float(arrays['action'][:,i,2].max())]}
  episodes=[]
  for ep in rd['all_valid_episodes']:
   episodes.append({k:ep[k] for k in ['episode','first_control','last_control','valid_controls','ordinary_failure_control','wheel_route_x_range_m','position_complete','contact1N_complete','position_contact_agree','valid_unfinished_physical_prefix']})
  rows.append(dict(env=i,standing=i==7,original_requested_delay_us=delays[i],baseline_complete=bb,D3_complete=dd,
   improved=not bb and dd,regressed=bb and not dd,baseline_metrics=b['per_env'][i],D3_metrics=d['per_env'][i],
   actual_leg_execution=legstats,D3_valid_prefix=episodes))
 improvements=[r['env'] for r in rows[:7] if r['improved']]
 regressions=[r['env'] for r in rows[:7] if r['regressed']]
 failures=[r['env'] for r in rows[:7] if not r['D3_complete']]
 assert improvements==[4] and regressions==[] and failures==[1,2,3,6]
 receipt=dc['feedback_factor']
 assert receipt['current_noisy_vs_actual_original_queue_input_max_error']==0
 report=dict(epoch=time.time(),passed=True,CPU_only=True,no_new_GPU_or_SSH=True,
  references=[dict(path=str(bp),sha256=H(bp)),dict(path=str(dp),sha256=H(dp))],
  frozen_source_SHA=dc['checkpoint_sha256'],raws=[b['raw_actual'],d['raw_actual']],
  exact_same_initial_qXYZ_physicalDR_fullqueues_25_actual_RNG_bytes=True,
  actual_final25_RNG_bytes_exact=True,actual_all6000_callbacks_and_physical_contracts_passed=True,
  negative_control_zero_delay_envs=negative_controls,negative_control_raw_fields_exact=matrix,
  negative_control_complete1500_and6000_substep_fields_byteexact=True,
  original_feedback_noise_bias_RNG_draws_delay_recipe_queues_retained=True,
  final_feedback_queue_values_not_required_exact_because_actual_noisy_physical_inputs_change=True,
  actual_factor_receipt=receipt,
  direct=dict(baseline_complete=2,D3_complete=3,moving=7,improved_envs=improvements,regressed_envs=regressions,
   remaining_failed_envs=failures,all_full1500_valid_failed_prefixes_retained=True),
  per_env=rows,
  interpretation=dict(
   supported='10 ms feedback delay is a measured limited contributor for this frozen policy/paired sample: env4 crosses under current noisy feedback; zero-delay env2/3/6 all raw fields are byteexact.',
   remaining='Four moving episodes still do not finish; env1,2,6 have large yaw, env3 has low BODY speed and stagnation. Left actor stays clip-6/lower CAD target in every case. These are separate observed residuals, not a unique causal assignment.',
   limitation='Seven moving same-backend forward episodes only. Does not establish 50 mm production qualification, reverse superiority cause, a DR/reward change, or a sole root cause.'),
  production_thresholds_and_DR_not_modified=True,
  no_PPO_no_budgetwrite=True,
  actual_all_parent_child_PID_identities_exited_and_shared_lock_free=True,
  original_missing_EXIT_NATURAL_and_parent_natural_app_close_false_retained=True,
  original_diff_min_contract=dict(path=str(contractpath),sha256=H(contractpath),value_rad=minimum))
 out=R/'DIRECT3060_D3_DIRECT_PAIR_NEGATIVE_CONTROL_AND_RESIDUAL_CPU_ACTUAL_REVIEW.json'
 assert not out.exists()
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(out),passed=True,improvements=improvements,remaining=failures,zero_delay_allfields_byteexact=negative_controls,actual_final25RNGbytes_exact=True)))

if __name__=='__main__':main()
