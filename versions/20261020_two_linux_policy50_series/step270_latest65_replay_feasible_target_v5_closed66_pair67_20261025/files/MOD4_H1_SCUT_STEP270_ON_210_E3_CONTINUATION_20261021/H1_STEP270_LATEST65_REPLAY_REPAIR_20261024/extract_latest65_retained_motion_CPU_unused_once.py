from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;R=S/'reports';R.mkdir(exist_ok=True);sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
read=lambda p:json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
import hashlib,json,math,os,psutil,time
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='2'
import numpy as np
assert psutil.virtual_memory().available>8*1024**3
out=Path(v['out']);assert not out.exists();out.mkdir(parents=True)
arrays={};sources=[]
for row in v['files']:
 p=Path(row['target_path']);st=p.stat();assert p.is_file() and not p.is_symlink() and st.st_size==row['bytes']
 with np.load(p,allow_pickle=False) as z:
  for key in z.files:arrays.setdefault(key,[]).append(z[key])
 after=p.stat();assert (st.st_size,st.st_mtime_ns,st.st_ino)==(after.st_size,after.st_mtime_ns,after.st_ino)
 sources.append(dict(path=str(p),bytes=st.st_size,producer_SHA=row['SHA'],mtime_ns=st.st_mtime_ns,inode=st.st_ino,no_original_raw_rehash=True))
a={k:np.concatenate(rows,axis=0) for k,rows in arrays.items()};root=a['root13'];frames,n=root.shape[:2];assert frames==48 and n==20000
nr=int(math.ceil(n/math.sqrt(n)));nc=int(math.ceil(n/nr));ids=np.arange(n);origins=np.stack((-(ids//nc-(nr-1)/2)*2.5,(ids%nc-(nc-1)/2)*2.5,np.zeros(n)),-1).astype(np.float32);local=root[...,:3]-origins[None,:,:]
req=a['public_request'].astype(bool);done=a['done'].astype(bool);same_transition=(a['episode'][1:]==a['episode'][:-1])&~done[:-1];continuous=(a['episode']==a['episode'][0]).all(0)&~done.any(0)
def quant(x):return {str(q):float(np.quantile(x,q)) for q in (0,.1,.5,.9,1)} if x.size else None
terms=v['reward_terms'];con=a['reward_term_contribution'];tuck=con[:,:,terms.index('h1_scut_fudan_leg_tuck')]
pool=np.where(continuous&(req.any(0)|(tuck>0).any(0)|(a['progress_peak']>.27).any(0)))[0];assert len(pool)>64
increments={k:np.maximum(a[k][1:]-a[k][:-1],0)*same_transition for k in ('takeoff_count','landing_count','recovery_count')}
selected=[]
scores=[local[:,:,2].max(0),local[:,:,0].max(0),root[:,:,7].max(0),-root[:,:,7].min(0),local[-1,:,0]-local[0,:,0],tuck.max(0),a['progress_peak'].max(0),increments['takeoff_count'].sum(0)]
for score in scores:
 for e in pool[np.argsort(score[pool])[-12:][::-1]]:
  if int(e) not in selected:selected.append(int(e))
failures=np.where(done.any(0))[0]
for e in failures[np.argsort(local[:,:,2].max(0)[failures])[-12:][::-1]]:
 if int(e) not in selected:selected.append(int(e))
selected=np.asarray(selected,dtype=np.int64);save={k:x[:,selected] for k,x in a.items()};save.update(env_ids=selected,env_origins=origins[selected],root_local=local[:,selected],control_rows=np.arange(v['control_first'],v['control_first']+frames),continuous_no_reset=continuous[selected],same_episode_transition=same_transition[:,selected]);p=out/'SELECTED_RECORDED_MOTION.npz';np.savez_compressed(p,**save)
quat=root[:,:,3:7];x,y,z,w=np.moveaxis(quat,-1,0);roll=np.arctan2(2*(w*x+y*z),1-2*(x*x+y*y));pitch=np.arcsin(np.clip(2*(w*y-z*x),-1,1));yaw=np.arctan2(2*(w*z+x*y),1-2*(y*y+z*z))
reward={term:dict(request_mean=float(con[:,:,i][req].mean(dtype=np.float64)) if req.any() else None,not_request_mean=float(con[:,:,i][~req].mean(dtype=np.float64)) if (~req).any() else None,all_envframe_sum=float(con[:,:,i].sum(dtype=np.float64))) for i,term in enumerate(terms)}
cmd=a['policy35'][:,:,0];mismatch=np.abs(cmd-req*.8)>1e-6
result=dict(epoch=time.time(),scope='Latest closed65 stochastic PPO saved pre-selected-reset control records, adjacent prefixes116/117 only.48 frames/0.48s across20k. Selected motion includes explicit reset masks. Not frozen FINAL policy evaluation, full-window totals, or callback dynamic replay.',sources=sources,frames=frames,dt=.01,seconds=.48,full_environment_count=n,selected_ids=selected.tolist(),selected_count=len(selected),continuous_selected=int(continuous[selected].sum()),selected_shapes={k:list(x.shape) for k,x in save.items()},reward_terms=terms,actual_weighted_reward_contributions=reward,recorded_event_counter_positive_increments={k:int(x.sum(dtype=np.int64)) for k,x in increments.items()},requested_rows=int(req.sum()),public_command_mismatch_rows=int(mismatch.sum()),requested_world_vx_quantiles=quant(root[:,:,7][req]),requested_world_vx_positive_fraction=float((root[:,:,7][req]>0).mean()) if req.any() else None,requested_root_local_x_quantiles=quant(local[:,:,0][req]),requested_root_z_quantiles=quant(root[:,:,2][req]),requested_roll_quantiles=quant(roll[req]),requested_pitch_quantiles=quant(pitch[req]),requested_yaw_quantiles=quant(yaw[req]),recorded_both_wheels_crossed_envframes=int(a['step_wheel_crossed'].all(-1).sum()),recorded_success_envframes=int(a['step_success'].sum()),non_request_tuck_positive_envframes=int(((tuck>0)&~req).sum()),selected_artifact=dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()),no_policy_model_optimizer_RNG_PhysX_GPU_or_budget_write=True,original_raw_unchanged=True)
print(json.dumps(result))
'''
try:
 P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V65_20261024';proof=read(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');assert proof['passed'] and proof['all_owner_nodes_children_actual_out']
 index=read(P/'current_pair_closed_text/h1/job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json');move=read(P/'reports/CLOSED65_CURRENT65_OLD63_26_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json');batch=next(b for b in move['batches'] if b['source_stage']==P.name);files=[r for r in batch['files'] if r['name'] in ('control_prefix_116.npz','control_prefix_117.npz')];files.sort(key=lambda r:r['name']);assert len(files)==2
 rows={Path(r['path']).name:r for r in index['index']}
 for r in files:assert (r['SHA'],r['bytes'])==(rows[r['name']]['SHA'],rows[r['name']]['bytes']) and r['target_full_SHA_verified']
 put('EXTRACTION_STARTED_ACTUAL.json',dict(epoch=time.time(),user_request='继续看回放修复上台阶',latest_qualified_complete_h1=proof['models']['h1']['final'],files=files,raw_preupdate_not_frozen_FINAL_policy=True,source_on72_from_complete_relocation_receipt=True,no_active_training_signal_or_hotpatch=True))
 m=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(m);m.loader.exec_module(memory);secret=memory.recover();c=d.connect72(secret);secret=None
 try:
  result=d.code(c,d.PY72,CODE,dict(files=files,reward_terms=index['reward_terms'],control_first=116*24+1,out='/home/lc01/Zonglin Li/zonglin2/replay_diagnostics/H1_STEP270_LATEST65_REPLAY_REPAIR_20261024'),timeout=240);put('LATEST65_RECORDED_MOTION_SOURCE_CPU_ACTUAL.json',result);p=S/'SELECTED_RECORDED_MOTION.npz';assert not p.exists();sf=c.open_sftp()
  try:sf.get(result['selected_artifact']['path'],str(p))
  finally:sf.close()
  assert p.stat().st_size==result['selected_artifact']['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==result['selected_artifact']['SHA']
  put('LATEST65_SELECTED_MOTION_TWOHOST_SHA_ACTUAL.json',dict(epoch=time.time(),path=str(p),bytes=p.stat().st_size,SHA=result['selected_artifact']['SHA'],twohost_complete_SHA=True,no_original_raw_download=True))
 finally:c.close()
 print(json.dumps({k:result[k] for k in ('frames','selected_count','recorded_event_counter_positive_increments','requested_world_vx_quantiles','requested_root_local_x_quantiles','recorded_both_wheels_crossed_envframes','public_command_mismatch_rows','selected_artifact')}))
except BaseException:
 put('LATEST65_EXTRACTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_same_once=True));raise
