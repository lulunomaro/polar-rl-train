from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
import deploy_two50_reconciled_original_writer_once as d
read=lambda p:json.loads(Path(p).read_bytes())
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
import hashlib,json,math,os,psutil,time
import numpy as np
assert psutil.virtual_memory().available>8*1024**3
out=Path(v['out']);assert not out.exists();out.mkdir()
arrays={};sources=[]
keys=('root13','q30','policy35','raw_sampled6','executed6','joint_velocity','applied_torque','public_request','progress_peak','progress_paid','step_wheel_crossed','takeoff_count','landing_count','recovery_count','episode','done','history5ms','impulse','reward_term_contribution','event_expected','total_reward','progress_expected','closure','mimic','step_stable_ticks','step_success')
for row in v['files']:
 p=Path(row['target_path']);s=p.stat();assert p.is_file() and not p.is_symlink() and s.st_size==row['bytes']
 with np.load(p,allow_pickle=False) as z:
  for key in keys:arrays.setdefault(key,[]).append(z[key])
 after=p.stat();assert (s.st_size,s.st_mtime_ns,s.st_ino)==(after.st_size,after.st_mtime_ns,after.st_ino)
 sources.append(dict(path=str(p),bytes=s.st_size,producer_SHA=row['SHA'],mtime_ns=s.st_mtime_ns,inode=s.st_ino,no_rehash_for_Git=True))
arrays={k:np.concatenate(x,axis=0) for k,x in arrays.items()};root=arrays['root13'];n=root.shape[1];assert n==20000 and root.shape[0]==48
nr=int(math.ceil(n/math.sqrt(n)));nc=int(math.ceil(n/nr));ids=np.arange(n);origins=np.stack((-(ids//nc-(nr-1)/2)*2.5,(ids%nc-(nc-1)/2)*2.5,np.zeros(n)),-1).astype(np.float32)
local=root[...,:3]-origins[None,:,:];req=arrays['public_request'].astype(bool);valid=~arrays['done'].any(0);same=(arrays['episode']==arrays['episode'][0]).all(0)
pool=np.where(valid&same&req.any(0))[0];assert len(pool)>64
selected=[]
for score in (local[:,:,2].max(0),local[:,:,0].max(0),root[:,:,7].max(0),-root[:,:,7].min(0),local[-1,:,0]-local[0,:,0]):
 for i in pool[np.argsort(score[pool])[-12:][::-1]]:
  if int(i) not in selected:selected.append(int(i))
selected=np.array(selected,dtype=np.int64)
save={k:x[:,selected] for k,x in arrays.items()};save.update(env_ids=selected,env_origins=origins[selected],control_rows=np.arange(117*24+1,119*24+1),root_local=local[:,selected]);p=out/'SELECTED_RECORDED_MOTION.npz';np.savez_compressed(p,**save)
quat=root[:,:,3:7];x,y,z,w=np.moveaxis(quat,-1,0);yaw=np.arctan2(2*(w*z+x*y),1-2*(y*y+z*z))
def quant(a):return {str(q):float(np.quantile(a,q)) for q in (0,.1,.5,.9,1)}
same_transition=(arrays['episode'][1:]==arrays['episode'][:-1])&~arrays['done'][:-1].astype(bool)
terms=v['reward_terms'];contrib=arrays['reward_term_contribution'];assert np.allclose(arrays['policy35'][:,:,0],req*.8,rtol=0,atol=1e-6)
events={k:int(np.maximum(arrays[k][1:]-arrays[k][:-1],0)[same_transition].sum(dtype=np.int64)) for k in ('takeoff_count','landing_count','recovery_count')}
reward_diagnostics={term:dict(request_mean=float(contrib[:,:,j][req].mean(dtype=np.float64)),not_request_mean=float(contrib[:,:,j][~req].mean(dtype=np.float64)),all_envframe_sum=float(contrib[:,:,j].sum(dtype=np.float64))) for j,term in enumerate(terms)}
summary=dict(epoch=time.time(),recorded_event_counter_positive_increments=events,actual_weighted_reward_contributions=reward_diagnostics,reward_terms=terms,policy_command_matches_original_public_request=True,scope='Actual saved stochastic-PPO pre-selected-reset control records, last two adjacent retained prefixes; not new frozen FINAL evaluation or full physical-callback replay',frames=48,dt=.01,seconds=.48,full_environment_count=n,selected_ids=selected.tolist(),sources=sources,selected_shapes={k:list(x.shape) for k,x in save.items()},continuous_controls=[117*24+1,119*24],same_episode_request_pool=len(pool),requested_rows=int(req.sum()),requested_root_local_x_m_quantiles=quant(local[:,:,0][req]),requested_root_local_y_m_quantiles=quant(local[:,:,1][req]),requested_world_vx_m_s_quantiles=quant(root[:,:,7][req]),requested_world_vy_m_s_quantiles=quant(root[:,:,8][req]),requested_yaw_rad_quantiles=quant(yaw[req]),requested_root_z_m_quantiles=quant(root[:,:,2][req]),requested_root_vx_positive_fraction=float((root[:,:,7][req]>0).mean()),artifact=dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()),no_GPU_optimizer_scene_change_or_account_write=True,original_raw_not_modified=True)
print(json.dumps(summary))
'''
def main():
 P=T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V31_20261023';proof=read(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');assert proof['passed'] and proof['all_owner_nodes_children_actual_out']
 files=read(P/'reports/PEER_FORENSICS_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json')['files'];files=sorted([x for x in files if x['name'] in ('control_prefix_117.npz','control_prefix_118.npz')],key=lambda x:x['name']);assert len(files)==2
 put('EXTRACTION_STARTED_ACTUAL.json',dict(epoch=time.time(),user_requested_actual_jump_step_replay=True,source_closed_FINAL=proof['models']['h1']['final'],raw_are_recorded_before_LAST_optimizer_updates_not_FINAL_policy_rerun=True,files=files,no_training_hotpatch=True))
 spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);secret=m.recover();c=None
 try:
  c=d.connect72(secret);secret=None;result=d.code(c,d.PY72,CODE,dict(reward_terms=read(P/'current_pair_closed_text/h1/job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json')['reward_terms'],files=files,out='/home/lc01/Zonglin Li/zonglin2/forensic_originals/H1_STEP270_REPLAY_REPAIR_V2_20261023'),timeout=180)
  put('EXTRACTION_SOURCE_CPU_ACTUAL.json',result);target=D/'SELECTED_RECORDED_MOTION.npz';assert not target.exists();sf=c.open_sftp()
  try:sf.get(result['artifact']['path'],str(target))
  finally:sf.close()
  assert target.stat().st_size==result['artifact']['bytes'] and hashlib.sha256(target.read_bytes()).hexdigest()==result['artifact']['SHA']
  put('EXTRACTION_LOCAL_COMPLETE_SHA_ACTUAL.json',dict(epoch=time.time(),path=str(target),bytes=target.stat().st_size,SHA=result['artifact']['SHA'],twohost_complete_SHA=True,no_original_raw_download_or_model_load=True))
  print(json.dumps({k:result[k] for k in ('frames','seconds','same_episode_request_pool','requested_world_vx_m_s_quantiles','requested_root_local_x_m_quantiles','artifact')}))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('EXTRACTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_rerun_same_once=True));raise
