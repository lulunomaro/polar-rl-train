"""Strict CPU full-prefix/route/action-factor pairing, no RNG-byte overclaim."""
from pathlib import Path
import argparse,hashlib,json,time,traceback,psutil,msvcrt
import numpy as np
D=Path(__file__).resolve().parent;W=D.parents[1]
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(name,v):
 p=D/name;assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');return p
def alive(pid,creation):
 try:return abs(psutil.Process(pid).create_time()-creation)<.05
 except psutil.NoSuchProcess:return False
def load(a):
 o=a/'output';c=read(o/'COMPLETE_ACTUAL.json');e=read(a/'PARENT_EXIT_RECEIPT.json');di=read(a/'DISPATCH_RECEIPT.json')
 assert c['passed_data_contract'] and c['no_PPO'] and e['exit_code']==0 and not e['original_error_present']
 assert not alive(di['child_pid'],di['child_creation']) and not alive(di['parent_pid'],di['parent_creation'])
 raw=Path(c['raw']['path']);assert raw.stat().st_size==c['raw']['bytes'] and H(raw)==c['raw']['sha256']
 with np.load(raw,allow_pickle=False) as z:r={k:z[k].copy() for k in z.files}
 return c,e,r
def audit(c,r):
 T,N=c['steps'],c['num_envs'];assert T==1500 and c['callbacks']==6000
 assert r['root'].shape==(T,N,13) and r['q'].shape==(T,N,30)
 assert all(np.isfinite(x).all() for x in r.values())
 assert np.array_equal(r['processed_action'],np.clip(r['factor_action'],-6,6))
 assert np.array_equal(np.clip(r['action'],-6,6)[:,:,1:],r['processed_action'][:,:,1:]),'Other five current requested columns changed'
 integral=np.maximum(r['physical_wheel_force_N'].reshape(T,4,N,2,3)[...,2],0).sum(1)*.0025
 err=float(np.max(abs(integral-r['impulse'])))/.01;assert err<=.1
 support=integral/.01>1.
 wheelids=[c['body_names'].index(x) for x in ('left_wheel','right_wheel')]
 assignments=c['initial']['actual_assignments'];centers=np.array([[(x['bounds'][0][k]+x['bounds'][1][k])*.5 for k in (0,1)] for x in assignments])
 half=2.4064227271861264/2;direction=c['factor']['world_sign'];rows=[]
 for i in range(N):
  fail=int(np.where(r['terminated'][:,i],np.arange(T),T).min());moving=r['group_ids'][i]!=2
  valid=(np.arange(T)<fail)&(r['episode'][:,i]==0)
  local=r['COM_link_pos'][:,i,wheelids,0]-centers[i,0];s=direction*local
  segments=[];completed=[]
  for ep in np.unique(r['episode'][:,i]):
   mask=(r['episode'][:,i]==ep)&(np.arange(T)<fail);ids=np.flatnonzero(mask)
   if not len(ids):continue  # Preserve ordinary failure prefix; do not inspect later reset episode.
   before=ids[(s[mask].max(1)<-half-.2)&support[mask,i].all(1)]
   after=ids[(s[mask].min(1)>half+.2)&support[mask,i].all(1)]
   ok=bool(moving and len(before) and len(after) and before.min()<after.max())
   if ok:completed.append(int(ep))
   segments.append(dict(episode=int(ep),controls=len(ids),first=int(ids[0]),last=int(ids[-1]),before_with_both1N=bool(len(before)),after_with_both1N=bool(len(after)),complete_contact_and_position=ok,wheelX_minmax=[float(local[mask].min()),float(local[mask].max())]))
  qq=r['before_root'][:,i,3:7];yaw=np.arctan2(2*(qq[:,3]*qq[:,2]+qq[:,0]*qq[:,1]),1-2*(qq[:,1]**2+qq[:,2]**2))
  relative=(yaw-c['factor']['yaw_rad']+np.pi)%(2*np.pi)-np.pi
  delta=r['root'][:,i,:2]-r['before_root'][:,i,:2];body=delta[:,0]*np.cos(yaw)+delta[:,1]*np.sin(yaw)
  cross=-delta[:,0]*np.sin(yaw)+delta[:,1]*np.cos(yaw)
  guard=r['guarded_leg_targets'][:,i];gd=np.stack((guard[:,0]-guard[:,1],guard[:,2]-guard[:,3]),-1)
  rows.append(dict(env=i,stand=not moving,complete_episodes=completed,segments=segments,
   valid_first_episode_prefix_controls=int(valid.sum()),first_ordinary_failure_control=fail,
   BODY_speed_m_s=float(body[valid].sum()/max(1,int(valid.sum()))/.01),world_route_progress_proxy_m=float(direction*delta[valid,0].sum()),
   abs_cross_proxy_m=float(abs(cross[valid]).sum()),max_abs_birth_heading_error_deg=float(abs(relative[valid]).max()*180/np.pi) if valid.any() else None,
   actual_left_right_guarded_target_lower_fraction=np.isclose(gd[valid],-1.0843,atol=2e-6,rtol=0).mean(0).tolist(),
   two_wheel_1N_fraction=float(support[valid,i].all(1).mean()),ordinary_events=int(r['terminated'][:,i].sum()),truncations=int(r['truncated'][:,i].sum())))
 return dict(moving_complete=sum(bool(x['complete_episodes']) for x in rows if not x['stand']),moving_envs=sum(not x['stand'] for x in rows),rows=rows,
    raw_contact_integral_mean_error_N=err,ordinary_events=int(r['terminated'].sum()),truncation_events=int(r['truncated'].sum()),
    mean_BODY_speed_m_s=float(np.mean([x['BODY_speed_m_s'] for x in rows if not x['stand']])),not_full80env_protocol_qualification=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--baseline',required=True);p.add_argument('--candidate',required=True);args=p.parse_args();b,be,br=load(Path(args.baseline));c,ce,cr=load(Path(args.candidate))
 assert b['checkpoint_sha256']==c['checkpoint_sha256'] and (b['seed'],b['num_envs'],b['steps'])==(c['seed'],c['num_envs'],c['steps'])
 cf=c['factor'].copy();cf['policy_factor']=False;assert cf==b['factor']
 assert b['initial']==c['initial'],'Full captured initial pose/q30/DR/assignments/geometry must be exact'
 assert np.array_equal(br['policy_obs'][0],cr['policy_obs'][0]) and np.array_equal(br['action'][0],cr['action'][0]),'First actual actor input and raw action must be exact'
 closed_path=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/leases'/('policy_leftrequested_factor_1500_v2_absolute_paths_CLOSED_ACTUAL.json')
 closed=read(closed_path)
 assert closed['native_shared_lock_actual_free'] and closed['original_exit_code']==0
 assert closed['complete']['raw_sha256']==c['raw']['sha256'] and all(x['actual_absent'] for x in closed['actual_process_exit'])
 # A later leased peer GPU may legally hold the shared lock; use this case's actual closed boundary.
 ba=audit(b,br);ca=audit(c,cr)
 result=dict(epoch=time.time(),passed=True,CPU_only=True,baseline_case=b['case_id'],candidate_case=c['case_id'],
   source_sha256=c['checkpoint_sha256'],same_seed_N_steps_and_actual_full_captured_initial_exact=True,
   first_actor_observation_and_mean_exact=True,only_requested_left_crank_column_changed_after_clip6=True,
   initial_DR_parameter_readback_and_assignments_exact=True,private_generator_state_bytes_not_saved_no_new_exact_claim=True,
   baseline_raw=b['raw'],candidate_raw=c['raw'],baseline=ba,candidate=ca,
   actual_parent_cost_seconds=[be['unique_actual_parent_load_run_save_exit_seconds'],ce['unique_actual_parent_load_run_save_exit_seconds']],
   actual_parent_child_exited_and_shared_lock_free_at_case_closed_boundary=True,closed_boundary_receipt=dict(path=str(closed_path),sha256=H(closed_path)),current_peer_GPU_slot_not_interfered_with=True,
   original_EXIT_NATURAL_missing_retained=[be['natural_app_close_present'],ce['natural_app_close_present']],
   classification='full15s matched8env single-policy-request diagnostic; no PPO, not production qualification or complete root-cause isolation',
   intervention_is_not_proposed_production_actor_recenter_initialization=True,
   GPU_case_success_not_automatically_50mm_pass=True)
 out=write('POLICY_LEFTREQUESTED_V2_FULL_PAIR_READER_V4_CPU_ACTUAL_REVIEW.json',result)
 print(json.dumps(dict(report=str(out),baseline=ba['moving_complete'],candidate=ca['moving_complete'],moving=ba['moving_envs'],baseline_speed=ba['mean_BODY_speed_m_s'],candidate_speed=ca['mean_BODY_speed_m_s'],baseline_ordinary=ba['ordinary_events'],candidate_ordinary=ca['ordinary_events'],candidate_raw=c['raw'],cost=ce['unique_actual_parent_load_run_save_exit_seconds'])))
if __name__=='__main__':
 try:main()
 except BaseException:
  write('POLICY_PAIR_V4_ORIGINAL_CPU_READER_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),CPU_only=True));raise
