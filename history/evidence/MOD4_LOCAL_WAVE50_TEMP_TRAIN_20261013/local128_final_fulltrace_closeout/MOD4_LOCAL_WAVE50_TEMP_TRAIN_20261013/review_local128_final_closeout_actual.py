from pathlib import Path
import json,time,hashlib,traceback,torch,numpy as np,psutil,msvcrt
D=Path(__file__).resolve().parent;R=D/'reports';A=D/'attempts/temporary_train128_v10_sameidentity_saved_source';O=A/'output'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def main():
 final=read(O/'LOCAL_PPO_FORMAL_FINAL_ACTUAL.json');end=read(A/'EXIT_RECEIPT.json');dispatch=read(A/'DISPATCH_RECEIPT.json');guardian=read(A/'GUARDIAN_CURRENT.json');startup=read(O/'LOCAL_FULLSTATE_STARTUP_VERIFIED.json')
 assert final['passed'] and end['exit_code']==0 and final['pid']==dispatch['child_pid']==end['child_pid']
 assert not (O/'ORIGINAL_ERROR.json').exists() and not (D/'STOP_AFTER_SAVE').exists()
 owned=[]
 for pid in (dispatch['child_pid'],guardian['parent_pid']):
  if psutil.pid_exists(pid):
   proc=psutil.Process(pid)
   if pid==dispatch['child_pid']:assert abs(proc.create_time()-dispatch['child_create_time'])>.001,'own trainer still active'
   else:assert proc.create_time()>end['epoch'],'own parent still active'
  owned.append(dict(pid=pid,original_owned_process_exited=True))
 with (D/'LOCAL_GPU_EXCLUSIVE.lock').open('r+b') as f:
  f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
 latest=final['latest'];p=Path(latest['path']);assert H(p)==latest['sha256'] and p.stat().st_size==latest['bytes']
 ck=torch.load(p,map_location='cpu',weights_only=False);source=torch.load(O/'LOCAL_PROJECTED_FULLSTATE_SOURCE.pt',map_location='cpu',weights_only=False)
 floats=[]
 def finite(v):
  if isinstance(v,torch.Tensor) and v.is_floating_point():assert torch.isfinite(v).all();floats.append(v)
  elif isinstance(v,dict):
   for z in v.values():finite(z)
  elif isinstance(v,(tuple,list)):
   for z in v:finite(z)
 finite(ck);assert len(floats)==107 and ck['LOCAL_TEMPORARY_BRANCH']['own_actual_PPO_updates']==41
 actor=sum(not torch.equal(v,source['actor_state_dict'][k]) for k,v in ck['actor_state_dict'].items());delta=[float(v['step'])-float(source['optimizer_state_dict']['state'][k]['step']) for k,v in ck['optimizer_state_dict']['state'].items()]
 assert actor==9 and min(delta)==820 and final['actual_updates']==41 and final['actual_controls']==984
 assert startup['passed'] and len(startup['actual_disk_roundtrip_startup_markers'])==12
 for name in startup['actual_disk_roundtrip_startup_markers']:
  receipt=read(O/name);assert receipt['pid']==final['pid']
 original=read(R/'SOURCE_FULL_STATE_CPU_ACTUAL.json');assert H(Path(original['path']))==original['sha256'] and Path(original['path']).stat().st_size==original['bytes']
 columns=['before_x','before_y','before_z','pre_reset_x','pre_reset_y','pre_reset_z','heading_before','BODY_vx','BODY_vy','signed_yaw','family','eligible','linear','moving','terminated','truncated']
 trace_receipt=read(O/'RETENTION_COMMAND_ACTUAL.json');arrays=[];files=[];next_control=0
 paths=sorted(O.glob('retention_prefix_*.npz'),key=lambda p:int(p.stem.split('_')[-2]));assert set(p.name for p in paths)==set(trace_receipt['trace_files'])
 for p in paths:
  lo,hi=map(int,p.stem.split('_')[-2:]);assert lo==next_control and hi>lo
  with np.load(p,allow_pickle=False) as npz:
   assert npz['columns'].tolist()==columns;v=npz['rows'].copy();assert v.shape==(hi-lo,128,16) and np.isfinite(v).all();arrays.append(v)
  files.append(dict(path=str(p),bytes=p.stat().st_size,sha256=H(p),start=lo,end=hi));next_control=hi
 raw=np.concatenate(arrays);assert raw.shape==(984,128,16) and trace_receipt['actual_controls']==984
 for k in (11,12,13,14,15):assert np.isin(raw[:,:,k],[0.,1.]).all()
 family=raw[:,:,10].astype(int);assert np.array_equal(family,raw[:,:,10]) and np.isin(family,[-1,0,1,2,3,4]).all()
 terminated=raw[:,:,14].astype(bool);truncated=raw[:,:,15].astype(bool);reset=terminated|truncated
 h=final['health'];assert h['actual_physics_callbacks']==h['expected_physics_callbacks']==3936 and h['control_steps']==984
 assert int(terminated.sum())==h['ordinary_episode_reset_events']==0 and int(truncated.sum())==h['actual_truncation_reset_events']==90
 assert h['integrity_task_reset_events']==h['unknown_task_reset_events']==0 and not h['nonfinite_observed'] and h['stop_reason'] is None
 assert h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact']
 assert np.array_equal(raw[1:,:,:3][~reset[:-1]],raw[:-1,:,3:6][~reset[:-1]]),'consecutive nonreset roots'
 ep=ck['E1_terrain_state']['episode'];assert torch.equal(ep,source['E1_terrain_state']['episode']+1+torch.from_numpy(reset.sum(0)))
 for name in ('E1_WAVE50_episode_direction_state','E1_WAVE50_route_lifecycle_state','E1_WAVE50_episode_lifetime_state'):assert torch.equal(ck[name]['bound_episode'],ep)
 ds=ck['E1_WAVE50_episode_direction_state'];born=ds['wave_mask'].numpy();sign=ds['entry_sign'].numpy();wave=(family==4)&born[None,:];moving=wave&(raw[:,:,7]!=0)
 assert (raw[:,:,7][moving]*np.broadcast_to(sign,wave.shape)[moving]>=0).all() and (abs(raw[:,:,7][wave])<=.300001).all() and (abs(raw[:,:,8:10][wave])<=1e-6).all()
 counts=dict(negative=int((wave&(raw[:,:,7]<0)).sum()),positive=int((wave&(raw[:,:,7]>0)).sum()),standing=int((wave&(raw[:,:,7]==0)).sum()))
 assert all(counts.values())
 max_prefix=0;prefixes=0;durations=[]
 for env in range(128):
  ends=np.flatnonzero(reset[:,env])+1;starts=np.r_[0,ends];ends=np.r_[ends,984]
  for lo,hi in zip(starts,ends):
   if hi==lo:continue
   duration=(hi-lo)*.01;durations.append(duration);max_prefix=max(max_prefix,duration);prefixes+=1
 started=read(O/'LOCAL_PPO_UNIQUE_COST_STARTED.json');ended=read(O/'LOCAL_PPO_UNIQUE_COST_ENDED.json');assert started['epoch']==dispatch['epoch']==ended['started_epoch']
 assert abs(end['wall_seconds']-(end['epoch']-dispatch['epoch']))<.05 and end['wall_seconds']>1800
 assert abs(ended['actual_seconds']-(ended['epoch']-dispatch['epoch']))<.05 and ended['epoch']<end['epoch']
 total=dict(epoch=time.time(),passed=True,own_checkpoint=latest,actor_changed=actor,optimizer_step_delta_min=min(delta),startup_receipts=12,owned_processes=owned,exclusive_local_OS_lock_free=True,original_source_checkpoint_current_SHA_verified=True,actual_updates=41,controls=984,environment_steps=984*128,physics_callbacks=3936,health=h,trace=dict(passed=True,files=files,complete_controls=984,finite=True,unique_reset_events=int(reset.sum()),actual_episode_increment_matches_raw=True,nonreset_root_continuity_exact=True,commands_before_physics=True,saved_histogram_after_update_not_forced_same_phase=True,dynamic_current_rootcell_family=True,birth_Wave_environment_count=int(born.sum()),Wave_signed_standing_counts=counts,physical_episode_prefixes=prefixes,max_observed_physical_episode_prefix_s=max_prefix,root_command_proxy_not_contact_or_fullroute_certificate=True),cost=dict(parent_full_loadlearnsaveexit_seconds=end['wall_seconds'],worker_pre_teardown_seconds=ended['actual_seconds'],worker_formal_field_seconds=final['cost_seconds'],original_fields_retained=True,parent_exit_authoritative_for_future_unique_reconciliation=True,not_added_together=True,canonical_reconciliation_pending=True,no_budgetwrite_or_recharge=True),completed_local_temporary_window_not_qualified50_or70=True,remote_training_and_evaluation_still_paused=True,no_new_PPO_or_GPU_or_automatic_nextblock=True)
 report=R/'LOCAL128_FINAL_FULLTRACE_CLOSEOUT_ACTUAL_REVIEW.json';assert not report.exists();report.write_text(json.dumps(total,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(dict(passed=True,report=str(report),checkpoint=latest['path'],sha256=latest['sha256'],updates=41,controls=984,parent_seconds=end['wall_seconds'],trace_files=len(files),max_physical_prefix_s=max_prefix,Wave_counts=counts,actual_exited=True,OS_lock_free=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=R/('LOCAL128_FINAL_READER_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(error=traceback.format_exc(),no_GPU_or_physical_tolerance_or_source_mutation=True)),encoding='utf8');raise
