from pathlib import Path
import json,time,hashlib,torch,numpy as np,psutil,msvcrt
D=Path(__file__).resolve().parent;A=D.parent/'MOD4_LOCAL_WAVE50_CONTINUE_20261013/attempts/same128_continue_second7200_v1';O=A/'output';R=D/'reports'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 f=json.loads((O/'LOCAL_PPO_FORMAL_FINAL_ACTUAL.json').read_bytes());e=json.loads((A/'EXIT_RECEIPT.json').read_bytes());s=json.loads((A/'DISPATCH_RECEIPT.json').read_bytes());g=json.loads((A/'GUARDIAN_CURRENT.json').read_bytes())
 assert f['passed'] and e['exit_code']==0 and f['pid']==e['child_pid']==s['child_pid']
 for pid in (s['child_pid'],g['parent_pid']):
  if psutil.pid_exists(pid):assert psutil.Process(pid).create_time()>e['epoch'],'original owned process still active'
 assert (A.parent.parent/'STOP_AFTER_SAVE').exists() and not (O/'ORIGINAL_ERROR.json').exists()
 cp=Path(f['latest']['path']);assert H(cp)==f['latest']['sha256']=='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4'
 ck=torch.load(cp,map_location='cpu',weights_only=False);source=torch.load(O/'LOCAL_PROJECTED_FULLSTATE_SOURCE.pt',map_location='cpu',weights_only=False);floats=[]
 def walk(v):
  if isinstance(v,torch.Tensor) and v.is_floating_point():assert torch.isfinite(v).all();floats.append(v)
  elif isinstance(v,dict):
   for x in v.values():walk(x)
  elif isinstance(v,(tuple,list)):
   for x in v:walk(x)
 walk(ck);assert len(floats)==107 and ck['LOCAL_TEMPORARY_BRANCH']['own_actual_PPO_updates']==f['actual_updates']==92
 assert sum(not torch.equal(v,source['actor_state_dict'][k]) for k,v in ck['actor_state_dict'].items())==9
 delta=min(float(v['step'])-float(source['optimizer_state_dict']['state'][k]['step']) for k,v in ck['optimizer_state_dict']['state'].items());assert delta==1840
 trace=[];indices=[];end=0
 for p in sorted(O.glob('retention_prefix_*.npz'),key=lambda p:int(p.stem.split('_')[-2])):
  lo,hi=map(int,p.stem.split('_')[-2:]);assert lo==end
  with np.load(p,allow_pickle=False) as z:
   x=z['rows'];assert x.shape==(hi-lo,128,16) and np.isfinite(x).all();trace.append(x.copy())
  indices.append(dict(path=str(p),bytes=p.stat().st_size,sha256=H(p),start=lo,end=hi));end=hi
 raw=np.concatenate(trace);assert end==f['actual_controls']==2208 and len(indices)==46
 resets=raw[:,:,14].astype(bool)|raw[:,:,15].astype(bool);h=f['health']
 assert raw[:,:,14].sum()==h['ordinary_episode_reset_events']==0 and raw[:,:,15].sum()==h['actual_truncation_reset_events']==194
 assert np.array_equal(raw[1:,:,:3][~resets[:-1]],raw[:-1,:,3:6][~resets[:-1]])
 assert torch.equal(ck['E1_terrain_state']['episode'],source['E1_terrain_state']['episode']+1+torch.from_numpy(resets.sum(0)))
 assert h['actual_physics_callbacks']==h['expected_physics_callbacks']==8832 and h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact'] and not h['nonfinite_observed'] and h['stop_reason'] is None
 assert h['integrity_task_reset_events']==h['unknown_task_reset_events']==0
 lock=D.parent/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/LOCAL_GPU_EXCLUSIVE.lock'
 with lock.open('r+b') as stream:
  stream.seek(0);msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1);stream.seek(0);msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)
 p=R/'TRAINING_HANDOFF_FULLSAVE_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),passed=True,checkpoint=f['latest'],startup_receipts=12,actual_updates=92,controls=2208,environment_steps=2208*128,callbacks=8832,actor_changed=9,optimizer_delta=1840,finite107=True,health=h,complete_training_trace_indices=indices,no_reset_teleport_progress=True,actual_episode_delta_raw_exact=True,first_local1800_plus_this_partial_second_block=True,stop_requested_for_human_factor_diagnosis_not_failure=True,original_worker_stop_reason=f['stop_reason'],parent_full_loadlearnsaveexit_seconds=e['wall_seconds'],worker_pre_teardown_seconds=f['cost_seconds'],not_added_together=True,canonical_reconciliation_pending=True,parent_and_child_actual_exit=True,shared_native_GPU_lock_free=True,source_original_preserved=True,no_PPO_GPU_remote_or_budgetwrite_by_reader=True),indent=2),encoding='utf8')
 print(json.dumps(dict(passed=True,report=str(p),checkpoint_SHA=f['latest']['sha256'],controls=2208,parent_seconds=e['wall_seconds'],lock_free=True)))
if __name__=='__main__':main()
