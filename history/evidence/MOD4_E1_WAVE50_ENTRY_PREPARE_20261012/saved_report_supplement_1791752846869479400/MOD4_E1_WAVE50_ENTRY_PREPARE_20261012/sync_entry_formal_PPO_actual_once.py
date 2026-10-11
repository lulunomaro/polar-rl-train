"""Append actual completed preflight/formal activity evidence; do not replay initial sync."""
from entry_io import *
import tomllib
NEWROOT = '/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012'

def main():
 assert not (R/'ENTRY_FORMAL_PPO_METADATA_SYNCED.json').exists()
 latest=max(R.glob('INITIALIZATION_REVIEWED_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]))
 v=json.loads(latest.read_bytes());assert v['root']==NEWROOT
 proofs=sorted(R.glob('ENTRY_OWN_SAVED_PPO_CPU_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]))
 child=v['current_state'].get('child') or {}
 suitable=[p for p in proofs if (lambda x:x.get('passed') and not x.get('discarded_preflight',True) and x.get('actual_saved_PID')==child.get('pid'))(json.loads(p.read_bytes()))]
 if not suitable:
  print(json.dumps(dict(pending=True,no_matching_own_formal_positive_PPO_save_yet=True,no_metadata_or_monitor_write=True)));return
 proofpath=suitable[-1];proof=json.loads(proofpath.read_bytes());assert proof['actual_num_envs']==20000 and proof['actual_optimizer_step_delta']>0
 reports=v['reports']
 for name in ('WAVE50_SDK10_PASSED.json','WAVE50_NATIVE20K_PASSED.json','wave50_discard128_PASSED.json','wave50_discard20k_PASSED.json','WAVE50_FRESH_PROCESS_SAME_SCOPE_PASSED.json','E1_COMPLETE_PPO_PREFLIGHT_PASSED.json'):
  assert name in reports,name
 assert reports['WAVE50_FRESH_PROCESS_SAME_SCOPE_PASSED.json']['passed']
 stamp=str(time.time_ns());names={
  'E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_FORMAL_CURRENT_ACTUAL_'+stamp+'.json':latest,
  'E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_OWN_FORMAL_SAVED_PPO_CPU_ACTUAL_'+stamp+'.json':proofpath}
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   for name,p in names.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
   raw=f.open(io.E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json','rb').read();oldsha=H(raw);current=json.loads(raw)
  rev=current['terrain_subexpert_revision004'];scope=rev['wave50_entry_initialization_reviewed_GPU_scope'];assert scope['root']==NEWROOT and scope['source_count']==410
  scope.update(phase=v['current_state']['phase'],actual_scope_at_collection_epoch=v['epoch'],actual_child_at_collection=child,
   new_entry_SDK10_native20k_small128x2_big20kx4_fresh_same_entry_actual_passed=True,
   formal_actual_PPO_save_CPU_verified=True,actual_actor_changed_count=len(proof['actual_actor_tensors_changed']),actual_optimizer_step_delta=proof['actual_optimizer_step_delta'],
   own_formal_saved_checkpoint_at_collection=proof['own_current_checkpoint'],formal_final_not_yet_claimed=True,
   current_actual_ref=io.E+'/reports/'+next(iter(names)),own_saved_PPO_CPU_ref=io.E+'/reports/'+list(names)[1])
  rev['active_next_phase']=scope['phase'];rev['latest_actual_scope']='wave50_entry_initialization_reviewed_GPU_scope'
  path=NEWROOT+'/reports/ENTRY_FORMAL_PPO_CURRENT_CAS_NEXT_'+stamp+'.json'
  with n.open_sftp() as f:io.put(f,path,json.dumps(current,ensure_ascii=False,indent=2).encode())
  result=run(n,r'''from pathlib import Path
import json,time,hashlib,os
D=Path(ROOT_TOKEN);R=Path(E_TOKEN)/'reports';B=Path(B_TOKEN)
protected={name:(R/name).read_bytes() for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';h=lambda q:hashlib.sha256(q.read_bytes()).hexdigest();assert h(p)==OLD_TOKEN
before=h(B);raw=Path(NEXT_TOKEN).read_bytes();tmp=p.with_name('CURRENT_entry_formal_'+str(time.time_ns())+'.tmp');tmp.write_bytes(raw);assert h(p)==OLD_TOKEN;os.replace(tmp,p)
assert all((R/name).read_bytes()==value for name,value in protected.items())
v=dict(epoch=time.time(),passed=True,completed_new_entry_preflight_and_own_formal_PPO_activity_synced=True,current_SHA=h(p),canonical_SHA_before=before,canonical_SHA_after=h(B),canonical_never_written_by_sync=True,master_approval_tracks_RM004_exact=True,no_GPU_launch_or_budget_write=True)
for q in (D/'reports/ENTRY_FORMAL_PPO_METADATA_SYNCED.json',R/'E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_FORMAL_PPO_METADATA_SYNCED.json'):
 assert not q.exists();q.write_text(json.dumps(v,indent=2))
print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(NEWROOT)).replace('E_TOKEN',repr(io.E)).replace('B_TOKEN',repr(io.B)).replace('OLD_TOKEN',repr(oldsha)).replace('NEXT_TOKEN',repr(path)))
  save('ENTRY_FORMAL_PPO_METADATA_SYNCED.json',result)
 finally:io.cleanup(n,w)
 setting=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
 assert setting['status']=='ACTIVE' and setting['rrule']=='FREQ=HOURLY;INTERVAL=1'
 oldprompt=D/('MONITOR_PREVIOUS_ENTRY_PREFLIGHT_PROMPT_'+stamp+'.md');oldprompt.write_text(setting['prompt'],encoding='utf8')
 prefix=f'''最新实际：source410自己的new-entry SDK10、native20k、128x2、20kx4弃权重完整PPO和freshsame50+entry20k零control零PPO全部实际PASSED，旧SDK/native/big/freshpending仅历史。当前正式300s窗口已经实际PPO更新；CPU仅读ownPID{proof['actual_saved_PID']}、actualCPU102、9actor tensors改变、optimizer stepdelta{proof['actual_optimizer_step_delta']}，own活动保存SHA{proof['own_current_checkpoint']['sha256']}只是活动证据，不是formal final或毕业。完整旧35来源b026恢复与显式35→50+entry实际CUDA磁盘roundtrip/sourceepisode+1已经真实核验，freshsameentry严格通过，无validator放松。

先读本机{R}最新数字INITIALIZATION_REVIEWED_ACTUAL/ENTRY_OWN_SAVED_PPO_CPU_ACTUAL与自己的futureownfinal/PID/PASSED/phase；中央{', '.join(names)}与E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_FORMAL_PPO_METADATA_SYNCED。current.rev004.wave50_entry_initialization_reviewed_GPU_scope最新实际优先。formal孩子/父guardian定位以actual/proc argv/cwd/start和ownreceipt为准，不假永久active。新entry实际只改resetXY，不混command/direction/reward/DR轴，原2m trainingroute与全3.006m frozen test的区别保持，不借rootproxy称全十波训练认证。

积极仅读read_entry_own_final_closeout_cpu_actual.py/collect_entry_candidate_actual.py/review_entry_candidate_actual.py/review_entry_direct147_prefix_actual.py/review_entry_complete_dynamic_family_trace_actual.py，按actualstage取ownfullsave/unique结清/actualexit/twofcntl-free/active-Sactive空与新fourcase实际publishnumber。准备读者不冒未来pass，missingfuture合法pending，fullscope决定前不更多PPO/70/qualified50/RM/MoE或永久抗遗忘。所有oldonce不重跑，hourly ACTIVE同target与fixed合同/Git要求继续。

旧全文保留{oldprompt} SHA{H(oldprompt.read_bytes())}；以下是前一阶段历史与固定合同，任何后来ownactual/fullscope决定优先：

'''
 save('ENTRY_FORMAL_PPO_HOURLY_MONITOR_UPDATE_REQUEST.json',dict(id='mod4-10',mode='update',kind='heartbeat',name=setting['name'],rrule=setting['rrule'],status='ACTIVE',targetThreadId=setting['target_thread_id'],prompt=prefix+setting['prompt']))
 print(json.dumps(dict(metadata_synced=True,monitor_request=str(R/'ENTRY_FORMAL_PPO_HOURLY_MONITOR_UPDATE_REQUEST.json'))))

if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY_FORMAL_PPO_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
