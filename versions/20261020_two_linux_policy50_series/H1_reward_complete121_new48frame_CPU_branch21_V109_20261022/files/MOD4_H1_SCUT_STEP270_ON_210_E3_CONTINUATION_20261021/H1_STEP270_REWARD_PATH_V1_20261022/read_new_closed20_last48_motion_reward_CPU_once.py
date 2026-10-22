"""New diagnostic on previously unread closed20 records; never a simulation replay."""
from pathlib import Path
import json,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent.parent;R=B/'reports';P=B.parent/'H1_STEP270_REWARD_H1_ONLY_V20_20261022'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
import json,os,psutil,time,numpy as np
q=v['q'];root=Path(q['roots']['h1']);owner=Path(q['owner_root']);base=root/'job0/production/control_prefix_raw'
assert json.loads((root/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited'] and json.loads((owner/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled']
assert not any(p.pid!=os.getpid() and any(a.startswith((str(root)+'/',str(owner)+'/')) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
index=json.loads((base/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').read_bytes());chosen=[x for x in index['retention_status'] if x['raw_retained']][-2:];assert [x['index'] for x in chosen]==[119,120]
keys=['root13','policy35','public_request','reward_term_contribution','done','episode','progress_peak','step_wheel_crossed','step_stable_ticks','step_success','takeoff_count','landing_count','recovery_count']
blocks={k:[] for k in keys};sources=[]
for pick in chosen:
 row=index['index'][pick['index']];p=Path(row['path']);assert p.resolve().is_relative_to(base.resolve()) and p.is_file() and not p.is_symlink();st=p.stat();assert st.st_size==row['bytes'] and st.st_nlink==1
 with np.load(p,allow_pickle=False) as z:
  for k in keys:blocks[k].append(z[k])
 sources.append(dict(row,actual_inode=st.st_ino,actual_mtime_ns=st.st_mtime_ns,identity_SHA_scope='Original producer SHA, no new whole-file raw hash. Selected NPZ arrays read with ZIP integrity; unused arrays not re-read.'))
a={k:np.concatenate(x,axis=0) for k,x in blocks.items()};root13=a['root13'];req=a['public_request'].astype(bool);same=(a['episode'][1:]==a['episode'][:-1])&~a['done'][:-1].astype(bool)
assert root13.shape==(48,20000,13) and req.shape==(48,20000) and np.isfinite(root13).all() and np.isfinite(a['reward_term_contribution']).all()
command=a['policy35'][:,:,:3];assert np.allclose(command[:,:,0],req*.8,rtol=0,atol=1e-6) and np.count_nonzero(command[:,:,1:])==0
dx=root13[1:,:,0]-root13[:-1,:,0];dx=np.where(same,dx,0);net=dx.sum(0);vx=root13[:,:,7];mask=req
quant=lambda x:{str(q):float(np.quantile(x,q)) for q in (0,.1,.5,.9,.99,1)}
terms=index['reward_terms'];weights=a['reward_term_contribution'];chosen_terms=['track_lin_vel','h1_scut_fudan_air_wheel_zero_torque','h1_step270_path_progress','h1_step270_requested_forward','h1_step270_release_shortfall','h1_scut_fudan_orientation']
contributions={k:dict(all_recorded_env_frames_sum=float(weights[:,:,terms.index(k)].sum(dtype=np.float64)),request_env_frames_mean=float(weights[:,:,terms.index(k)][mask].mean(dtype=np.float64))) for k in chosen_terms}
cross=a['step_wheel_crossed'].all(-1);cross_new=cross[1:]&~cross[:-1]&same
events={k:int(np.maximum(a[k][1:]-a[k][:-1],0)[same].sum(dtype=np.int64)) for k in ('takeoff_count','landing_count','recovery_count')}
result=dict(epoch=time.time(),passed_recorded_data_CPU=True,scope='Closed20 stochastic PPO prefixes119/120: 48 measured control frames / 0.48s, not FINAL rerun, whole-window totals, unbiased evaluation or graduation. Position differences cover47 transitions; reset boundaries excluded.',source_run=q['run_id'],closed_H1_final=v['final'],prefix_sources=sources,request_env_frames=int(req.sum()),total_env_frames=int(req.size),actual_request_vx_world_m_s_quantiles=quant(vx[mask]),request_forward_vx_above_half_command_fraction=float((vx[mask]>.4).mean()),net_root_world_x_47_same_episode_transitions_m_quantiles=quant(net),max_forward_environment=int(net.argmax()),max_forward_environment_net_dx_m=float(net.max()),positive_forward_net_envs=int((net>0).sum()),recorded_event_counter_positive_increments_47_transitions=events,new_both_wheel_cross_transitions=int(cross_new.sum()),success_seen_in_saved_frames=int(a['step_success'].any(0).sum()),max_retained_episode_peak_seen_m=float(a['progress_peak'].max()),peak_scope='Retained episode peak state, may precede these48frames; no instantaneous wheel height or edge-gap inference.',actual_weighted_reward_contributions=contributions,no_new_whole_raw_hash_download_PT_load_actor_optimizer_RNG_GPU_query_or_simulation=True,current_active_owner_and_budget_untouched=True)
print(json.dumps(result))
'''
try:
 proof=json.loads((P/'reports/H1_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert proof['passed']
 q=json.loads((P/'reports/H1_ONLY_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());c=d.t.connect()
 try:out=d.code(c,d.t.PY,CODE,dict(q=q,final=proof['models']['h1']['final']),timeout=150)
 finally:c.close()
 put('V109_NEW_CLOSED20_LAST48_ACTUAL_ROOT_MOTION_AND_REWARD_CPU_ACTUAL.json',out)
 print(json.dumps({k:out[k] for k in ('passed_recorded_data_CPU','actual_request_vx_world_m_s_quantiles','max_forward_environment_net_dx_m','recorded_event_counter_positive_increments_47_transitions','new_both_wheel_cross_transitions','success_seen_in_saved_frames')}))
except BaseException:
 put('CLOSED20_NEW_RECORDED_MOTION_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_rerun_or_training_change=True));raise
