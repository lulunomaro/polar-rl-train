"""CPU-only diagnostic prefix review, preserves every actual failure prefix."""
from pathlib import Path
import argparse,json,hashlib,time,numpy as np
p=argparse.ArgumentParser();p.add_argument('--attempt',required=True);p.add_argument('--output',required=True);p.add_argument('--paired-attempt');args=p.parse_args()
A=Path(args.attempt);O=A/'output';R=Path(args.output);assert not R.exists()
H=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
j=lambda path:json.loads(Path(path).read_bytes())
c=j(O/'COMPLETE_ACTUAL.json');exit=j(A/'PARENT_EXIT_RECEIPT.json');assert exit['exit_code']==0 and c['no_PPO'] and c['callbacks']==c['steps']*4
assert H(c['raw']['path'])==c['raw']['sha256']
with np.load(c['raw']['path']) as archive:raw={k:archive[k].copy() for k in archive.files}
N=c['num_envs'];T=c['steps'];assert raw['root'].shape==(T,N,13) and raw['q'].shape==(T,N,30) and raw['physical_wheel_force_N'].shape==(T*4,N,2,3)
assert all(np.isfinite(v).all() for v in raw.values());assert np.array_equal(raw['processed_action'],np.clip(raw['factor_action'],-6,6))
q=raw['before_root'][...,3:7];yaw=np.arctan2(2*(q[...,3]*q[...,2]+q[...,0]*q[...,1]),1-2*(q[...,1]**2+q[...,2]**2))
delta=raw['root'][...,:2]-raw['before_root'][...,:2];body=delta[...,0]*np.cos(yaw)+delta[...,1]*np.sin(yaw)
world=c['factor']['world_sign']*delta[...,0];cross=-delta[...,0]*np.sin(yaw)+delta[...,1]*np.cos(yaw)
step=np.arange(T)[:,None];fail=np.where(raw['terminated'],step,T).min(0);valid=(step<fail[None])&(raw['episode']==0)
moving=raw['group_ids']!=2;den=valid.sum(0).clip(1)
pitch=np.arcsin(np.clip(2*(q[...,3]*q[...,1]-q[...,2]*q[...,0]),-1,1));relative=(yaw-c['factor']['yaw_rad']+np.pi)%(2*np.pi)-np.pi
integral=np.maximum(raw['physical_wheel_force_N'].reshape(T,4,N,2,3)[...,2],0).sum(1)*.0025
assert float(np.max(abs(integral-raw['impulse'])))/.01<=.1
meanload=raw['impulse']/.01
names=c['body_names'];wheelids=[]
for accepted in (('left_wheel','left_wheel_link'),('right_wheel','right_wheel_link')):
 ids=[i for i,n in enumerate(names) if n in accepted];assert len(ids)==1;wheelids.append(ids[0])
initial=j(O/'INITIAL_ACTUAL.json');centers=np.asarray([[(x['bounds'][0][k]+x['bounds'][1][k])*.5 for k in (0,1)] for x in initial['actual_assignments']])
profile=json.loads((Path(__file__).resolve().parents[2]/'MOD4_LOCAL_WAVE50_CONTINUE_20261013/runtime/isaac/mod4/g4_cad_profile.json').read_bytes());half=profile['span_m']*.5
assert profile['derived_peak_to_trough_m']==.05
assert raw['COM_link_pos'].shape==(T,N,len(names),3)
assert np.max(abs(np.linalg.norm(raw['normal'],axis=-1)-1))<=.01 and raw['normal'][...,2].min()>.01
support_from_raw=(np.maximum(raw['physical_wheel_force_N'].reshape(T,4,N,2,3)[...,2],0).sum(1)*.0025/.01)>1.
fullroutes=[]
for i in range(N):
 local=raw['COM_link_pos'][:,i,:,:][:,wheelids,0]-centers[i,0];ep_rows=[];completepos=[];completecontact=[]
 for ep in np.unique(raw['episode'][:,i]):
  ids=np.flatnonzero((raw['episode'][:,i]==ep)&(np.arange(T)<fail[i]))
  if not len(ids):continue
  signed=c['factor']['world_sign']*local[ids];before=np.max(signed,axis=1)<-half-.2;after=np.min(signed,axis=1)>half+.2
  bothcontact=support_from_raw[ids,i].all(-1);before1N=before&bothcontact;after1N=after&bothcontact
  pos=bool(moving[i] and before.any() and after.any() and np.flatnonzero(before).min()<np.flatnonzero(after).max())
  con=bool(moving[i] and before1N.any() and after1N.any() and np.flatnonzero(before1N).min()<np.flatnonzero(after1N).max())
  if pos:completepos.append(int(ep))
  if con:completecontact.append(int(ep))
  ep_rows.append(dict(episode=int(ep),first_control=int(ids[0]),last_control=int(ids[-1]),valid_control_count=len(ids),wheel_signed_world_route_x_range_m=[float(signed.min()),float(signed.max())],
   before_position_control=ids[before].tolist(),after_position_control=ids[after].tolist(),before_position_and_double1N_control=ids[before1N].tolist(),after_position_and_double1N_control=ids[after1N].tolist(),
   position_full_tenwave_before_to_after200mm=pos,actual_double1N_before_to_after200mm=con,position_and_contact_agree=pos==con,
   valid_unfinished_physical_prefix=not pos and bool(moving[i])))
 fullroutes.append(dict(env=i,stand=not bool(moving[i]),first_ordinary_failure_control=int(fail[i]),complete_position_episodes=completepos,complete_double1N_episodes=completecontact,all_valid_episode_segments=ep_rows))
guard_diff=np.stack((raw['guarded_leg_targets'][...,0]-raw['guarded_leg_targets'][...,1],raw['guarded_leg_targets'][...,2]-raw['guarded_leg_targets'][...,3]),-1)
per=[]
for i in range(N):
 v=valid[:,i];prefix=int(v.sum());per.append(dict(env=i,stand=not bool(moving[i]),valid_physical_prefix_control=prefix,first_ordinary_failure_control=int(fail[i]),
  world_route_progress_proxy_m=float(world[v,i].sum()),BODY_speed_m_s=float(body[v,i].sum()/max(1,prefix)/.01),
  BODY_abs_speed_tracking_error_m_s=float(np.mean(abs(body[v,i]/.01-raw['targets_m_s'][i]))) if prefix else None,
  abs_lateral_proxy_m=float(abs(cross[v,i]).sum()),max_abs_route_heading_deviation_deg=float(np.max(abs(relative[v,i]))*180/np.pi) if prefix else None,
  max_abs_pitch_deg=float(np.max(abs(pitch[v,i]))*180/np.pi) if prefix else None,
  two_wheel_load_at_least1N_fraction=float((meanload[v,i]>=1).all(-1).mean()) if prefix else None,
  raw_actor_clip_fraction_per_column=(abs(raw['action'][v,i])>=6).mean(0).tolist() if prefix else None,
  guarded_left_right_input_difference_minmax=([guard_diff[v,i].min(0).tolist(),guard_diff[v,i].max(0).tolist()] if prefix else None)))
paired=None
if args.paired_attempt:
 base=j(Path(args.paired_attempt)/'output/COMPLETE_ACTUAL.json')
 exact=base['initial']['parameters']==c['initial']['parameters']
 paired=dict(path=args.paired_attempt,checkpoint_SHA_exact=base['checkpoint_sha256']==c['checkpoint_sha256'],seed_and_envcount_exact=(base['seed'],base['num_envs'])==(c['seed'],c['num_envs']),
  actual_initial_all_DR_parameters_and_private_RNG_exact=exact,initial_q30_exact=base['initial']['q']==c['initial']['q'],geometry_identity_exact=base['initial']['geometry']==c['initial']['geometry'],
  factor_baseline=base['factor'],factor_candidate=c['factor'])
 assert all(paired[k] for k in ('checkpoint_SHA_exact','seed_and_envcount_exact','actual_initial_all_DR_parameters_and_private_RNG_exact','initial_q30_exact','geometry_identity_exact')),'Paired causal comparison rejected; initial identities differ'
result=dict(epoch=time.time(),CPU_review_passed=True,case=c['case_id'],complete_data_contract=c['passed_data_contract'],frozen_only=True,
 requested_controls=T,actual_callbacks=T*4,source_sha256=c['checkpoint_sha256'],raw_sha256=c['raw']['sha256'],unique_actual_parent_cost=exit['unique_actual_parent_load_run_save_exit_seconds'],paired=paired,
 per_environment=per,ordinary_events=int(raw['terminated'].sum()),declared_truncation_events=int(raw['truncated'].sum()),
 fullroute=dict(actual_wheel_indices=wheelids,tenwave_span_m=profile['span_m'],root_approach_m=c['factor']['entry_margin'],both_wheels_before_and_after_margin_m=.2,actual_raw_contact_threshold_N=1.,
  body_group='forward' if c['factor']['body_sign']==1 else 'reverse',world_route_sign=c['factor']['world_sign'],moving_environments=int(moving.sum()),
  completed_position_environments=sum(bool(x['complete_position_episodes']) for x in fullroutes),completed_double1N_environments=sum(bool(x['complete_double1N_episodes']) for x in fullroutes),
  all_valid_failed_prefix_preserved=True,rows=fullroutes,production_80environment_protocol_not_claimed_from_subset=True),
 moving_mean_BODY_speed_m_s=float(np.mean([x['BODY_speed_m_s'] for x in per if not x['stand']])),
 moving_mean_route_progress_proxy_m=float(np.mean([x['world_route_progress_proxy_m'] for x in per if not x['stand']])),
 full_15s_requested=T==1500,diagnostic_subset_not_production_qualification=True,root_progress_proxy_not_two_wheel_fullroute_certificate=True,
 data_contract_success_is_not_50mm_passage_improvement=True)
R.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False))
