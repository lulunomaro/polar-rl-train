from second50_io import *
import tomllib

def main():
 assert not (R/'OWN_SAVED_PPO_METADATA_SYNCED.json').exists()
 p=max(R.glob('SECOND50_OWN_STARTUP_CPU_ACTUAL_[0-9]*.json'),key=lambda q:int(q.stem.rsplit('_',1)[1]));v=json.loads(p.read_bytes())
 assert v['passed'] and v['actual_saved_PPO_updates_positive'] and v['actual_source_count']==386 and v['actor_tensors_changed']==9
 n,w=io.connect_both()
 try:
  folder=D/('own_startup_actual_'+str(time.time_ns()));folder.mkdir();rows=[]
  with n.open_sftp() as f:
   for name,info in v['startup_markers'].items():
    raw=f.open(info['path'],'rb').read();assert len(raw)==info['bytes'] and H(raw)==info['sha256'];(folder/name).write_bytes(raw);rows.append(dict(info,local_path=str(folder/name)))
   for name in ('run_manifest.json','rolling_source_freeze.json'):
    remote=v['own_run']+'/'+name;raw=f.open(remote,'rb').read();(folder/name).write_bytes(raw);rows.append(dict(path=remote,bytes=len(raw),sha256=H(raw),local_path=str(folder/name)))
   for a in f.listdir_attr(ROOT+'/reports'):
    if not a.filename.endswith('.json'):continue
    remote=ROOT+'/reports/'+a.filename;raw=f.open(remote,'rb').read();target=folder/'root_reports'/a.filename;target.parent.mkdir(exist_ok=True);target.write_bytes(raw);rows.append(dict(path=remote,bytes=len(raw),sha256=H(raw),local_path=str(target),actual_stage_snapshot_not_future_final=True))
   ck=v['own_checkpoint'];size=f.stat(ck['path']).st_size;rows.append(dict(path=ck['path'],bytes=size,sha256=ck['sha256'],large_original_index_only=True,not_formal_final=True))
   io.put(f,io.E+'/reports/E1_WAVE50_SECOND_BOUNDED_OWN_SAVED_PPO_CPU_VERIFIED.json',p.read_bytes())
   raw=f.open(io.E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json','rb').read();sha=H(raw);cur=json.loads(raw)
  save('OWN_STARTUP_ACTUAL_COLLECTION.json',dict(epoch=time.time(),passed=True,indices=rows,all_seven_own_startup_receipt_bytes_SHA_exact=True,large_weights_not_copied=True,no_GPU_or_budget_mutation=True))
  scope=cur['terrain_subexpert_revision004']['wave50_second_bounded_scope'];assert scope['root']==ROOT and scope['source_count']==386
  scope.update(own_saved_PPO_positive_actual=True,own_saved_PPO_CPU_ref=io.E+'/reports/E1_WAVE50_SECOND_BOUNDED_OWN_SAVED_PPO_CPU_VERIFIED.json',actual_actor_tensors_changed=v['actor_tensors_changed'],actual_optimizer_step_delta=v['optimizer_step_delta_min'],actual_saved_trace_controls=v['actual_saved_trace_controls'],own_activity_checkpoint_SHA=ck['sha256'],activity_is_not_formal_final_or_qualified=True)
  with n.open_sftp() as f:io.put(f,ROOT+'/reports/OWN_SAVED_PPO_CAS_NEXT.json',json.dumps(cur,ensure_ascii=False,indent=2).encode())
  out=run(n,r'''from pathlib import Path
import os,json,time,hashlib
D=Path(ROOT_TOKEN);R=Path(E_TOKEN)/'reports';B=Path(B_TOKEN);before=B.read_bytes();protected={x:(R/x).read_bytes() for x in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';h=lambda q:hashlib.sha256(q.read_bytes()).hexdigest();assert h(p)==SHA_TOKEN
raw=(D/'reports/OWN_SAVED_PPO_CAS_NEXT.json').read_bytes();tmp=p.with_name('CURRENT_second50_PPO_'+str(time.time_ns())+'.tmp');tmp.write_bytes(raw);assert h(p)==SHA_TOKEN;os.replace(tmp,p)
assert B.read_bytes()==before and all((R/name).read_bytes()==raw for name,raw in protected.items())
v=dict(epoch=time.time(),passed=True,own_positive_saved_PPO_actual_synced=True,current_SHA=h(p),canonical_SHA=hashlib.sha256(before).hexdigest(),protected_exact=True,no_GPU_PPO_or_budget_write=True)
for q in (D/'reports/OWN_SAVED_PPO_METADATA_SYNCED.json',R/'E1_WAVE50_SECOND_BOUNDED_OWN_SAVED_PPO_METADATA_SYNCED.json'):assert not q.exists();q.write_text(json.dumps(v,indent=2))
print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)).replace('E_TOKEN',repr(io.E)).replace('B_TOKEN',repr(io.B)).replace('SHA_TOKEN',repr(sha)))
  save('OWN_SAVED_PPO_METADATA_SYNCED.json',out)
 finally:io.cleanup(n,w)
 setting=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
 prompt=f'''最新补充实际：source386同50mm第二1800s窗口已真实PPO更新，不仅启动进程。CPU仅读自己的活动保存model32275 SHA{ck['sha256']}/{size}B/CPU102/source386，9actor tensors改变/optimizer stepdelta240/实际savedtrace288control已核，七startup strictsame50 CUDAfullrestore/episode+1通过。活动保存不是formal final/毕业，future ownfinal/退出/唯一结清/候选四case优先。先读中央E1_WAVE50_SECOND_BOUNDED_OWN_SAVED_PPO_CPU_VERIFIED/OWN_SAVED_PPO_METADATA_SYNCED，本机{p}和OWN_STARTUP_ACTUAL_COLLECTION。所有原件与错误保留；以后actualownfullsave/PID/phase优先，不能套本活动保存永久状态。\n\n'''+setting['prompt']
 save('MONITOR_PPO_UPDATE_REQUEST.json',dict(id='mod4-10',mode='update',kind='heartbeat',name=setting['name'],rrule=setting['rrule'],status='ACTIVE',targetThreadId=setting['target_thread_id'],prompt=prompt))
 print(json.dumps(dict(PPO_positive_metadata_synced=True,actual_controls=v['actual_saved_trace_controls'],actor_changed=v['actor_tensors_changed'],optimizer_delta=v['optimizer_step_delta_min'],monitor_request=str(R/'MONITOR_PPO_UPDATE_REQUEST.json'))))
if __name__=='__main__':
 try:main()
 except BaseException:save('POSITIVE_PPO_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_budget_or_old_once_replay=True));raise
