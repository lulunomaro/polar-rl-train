"""New actual saved-PPO receipt sync, no trainer or budget mutation."""
from entry_second_io import *
import tomllib
def latest(pattern):return max(R.glob(pattern),key=lambda p:int(p.stem.rsplit('_',1)[1]))
def main():
 assert not (R/'OWN_SAVED_PPO_METADATA_SYNCED.json').exists()
 p=latest('ENTRY_SECOND_OWN_STARTUP_CPU_ACTUAL_[0-9]*.json');proof=json.loads(p.read_bytes());assert proof.get('passed') and proof['actual_saved_PPO_updates_positive'] and proof['actual_source_count']==412 and proof['actual_finite_tensor_count']==102
 sp=latest('ENTRY_SECOND_OWN_STARTUP_CONTRACT_ACTUAL_[0-9]*.json');startup=json.loads(sp.read_bytes());assert startup['passed'] and len(startup['seven_own_startup_receipts'])==8
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   checkpoint_bytes=f.stat(proof['own_checkpoint']['path']).st_size
   io.put(f,io.E+'/reports/E1_WAVE50_ENTRY_SECOND_BOUNDED_OWN_STARTUP_CONTRACT_VERIFIED.json',sp.read_bytes())
   io.put(f,io.E+'/reports/E1_WAVE50_ENTRY_SECOND_BOUNDED_OWN_SAVED_PPO_CPU_VERIFIED.json',p.read_bytes())
   raw=f.open(io.E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json','rb').read();oldsha=H(raw);current=json.loads(raw)
  scope=current['terrain_subexpert_revision004']['wave50_entry_second_bounded_scope'];assert scope['root']==ROOT and scope['source_count']==412
  scope.update(actual_startup_fullsame50entry_CUDA_verified=True,actual_saved_PPO_CPU_verified=True,own_activity_checkpoint=proof['own_checkpoint'],own_activity_checkpoint_bytes=checkpoint_bytes,actual_actor_tensors_changed=proof['actor_tensors_changed'],actual_optimizer_step_delta=proof['optimizer_step_delta_min'],actual_saved_trace_controls=proof['actual_saved_trace_controls'],own_formal_final_pending=True,own_saved_PPO_ref=io.E+'/reports/E1_WAVE50_ENTRY_SECOND_BOUNDED_OWN_SAVED_PPO_CPU_VERIFIED.json',corrected_saved_CPU_reader='verify_entry_second_saved_CPU_call_reviewed_actual.py',corrected_formal_CPU_reader='read_entry_second_own_formal_CPU_call_reviewed_actual.py',direct148_reader='review_entry_second_direct148_prefix_actual.py')
  nxt=ROOT+'/reports/OWN_SAVED_PPO_CAS_NEXT_'+str(time.time_ns())+'.json'
  with n.open_sftp() as f:io.put(f,nxt,json.dumps(current,ensure_ascii=False,indent=2).encode())
  v=run(n,r'''from pathlib import Path
import json,time,hashlib,os
D=Path(ROOT_TOKEN);R=Path(E_TOKEN)/'reports';B=Path(B_TOKEN);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=h(B)
protected={k:(R/k).read_bytes() for k in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';assert h(p)==OLD_TOKEN;raw=Path(NEXT_TOKEN).read_bytes();tmp=p.with_name('CURRENT_entry_second_PPO_'+str(time.time_ns())+'.tmp');tmp.write_bytes(raw);assert h(p)==OLD_TOKEN;os.replace(tmp,p);assert all((R/k).read_bytes()==v for k,v in protected.items())
v=dict(epoch=time.time(),passed=True,own412_actual_saved_PPO_CPU_synced=True,current_SHA=h(p),canonical_SHA_before=before,canonical_SHA_after=h(B),canonical_not_written_by_sync=True,master_approval_tracks_RM004_exact=True,no_GPU_or_oldonce_replay=True)
for q in (D/'reports/OWN_SAVED_PPO_METADATA_SYNCED.json',R/'E1_WAVE50_ENTRY_SECOND_BOUNDED_OWN_SAVED_PPO_METADATA_SYNCED.json'):
 assert not q.exists();q.write_text(json.dumps(v,indent=2))
print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)).replace('E_TOKEN',repr(io.E)).replace('B_TOKEN',repr(io.B)).replace('OLD_TOKEN',repr(oldsha)).replace('NEXT_TOKEN',repr(nxt)))
  save('OWN_SAVED_PPO_METADATA_SYNCED.json',v)
 finally:io.cleanup(n,w)
 setting=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert setting['status']=='ACTIVE' and setting['rrule']=='FREQ=HOURLY;INTERVAL=1'
 oldprompt=D/'MONITOR_PREVIOUS_ENTRY_SECOND_DISPATCH_PROMPT.md';oldprompt.write_text(setting['prompt'],encoding='utf8')
 git=json.loads((R/'ENTRY_SECOND_STAGE_GIT_RECORDED.json').read_bytes());assert git['remote_main_tag_peeled_verified']
 prefix=f'''最新补充actual优先：source412同50mm reset-entry第二1800s窗口已真实PPO更新，不仅启动进程。自己的活动保存model32275 SHA{proof['own_checkpoint']['sha256']}/{checkpoint_bytes}B/actualCPU102/source412，9actor tensors改变/optimizerstepdelta{proof['optimizer_step_delta_min']}/savedtrace{proof['actual_saved_trace_controls']}controls已核；8ownstartup same50+entry CPUCUDA严格恢复/磁盘roundtrip/sourceepisode+1真正PASSED。活动保存不是formal final/毕业，以future ownfullsave/PID/PASSED/unique结清/actualphase/自然退出/候选四case优先。

先读中央E1_WAVE50_ENTRY_SECOND_BOUNDED_OWN_STARTUP_CONTRACT_VERIFIED、OWN_SAVED_PPO_CPU_VERIFIED、OWN_SAVED_PPO_METADATA_SYNCED，本机{p}及最新ENTRY_SECOND_ACTUAL/之后OWN_FORMAL/CANDIDATE/FULLTRACE。原生成PPO读者因替换pattern额外把entryfilename加入单参数j(path)，TypeError在任何写/GPU前拒绝；原source/error保留，独立仅修j调用，实际ownCPU/PPO校验通过，不是训练/物理失败、不重GPU。积极用新verify_entry_second_saved_CPU_call_reviewed_actual.py/未来read_entry_second_own_formal_CPU_call_reviewed_actual.py，不用原错误版本；read_entry_second_actual.py、verify_entry_second_startup_contract_actual.py正常。未来collect_entry_second_candidate_actual.py/review_entry_second_candidate_actual.py/review_entry_second_direct148_prefix_actual.py/review_entry_second_complete_dynamic_family_trace_actual.py按actualstage完整四case/raw/query/直接148及全trace审，prepared不是futurepass。

新真实阶段{git['tag']} commit{git['commit']}/tagobject{git['tagobject']}已actualremote main/tag/peeled核验，{git['saved_sources']}savedsource与全部旧tags保持。之后positiveCPU/读者错误+修复/同步/monitor/新增未来准备/Gitreceipt仍ordinarysupplement，最终actualtracked/remote工具优先不能凭此提示假补齐。005总1188000/七扩展第七100h早once，无新扩展/预算事务，actualactive/accounted尾段优先。所有fixed合同/旧410exit原unique325.21946477890015s/完整148正16倒24未qualified和两entry块最多/不第三盲块不70/其它冻结expert与gate保护/WASD不干预继续下文及工作单。mod4-10同heartbeat ACTIVE每1h同target，healthy pending DONT_NOTIFY静默，只实质修复/重大退化/完成/人类动作NOTIFY，不5minSSH/ping/Rich/其它monitor/自动预算；reviewready不删monitor，仅实际预算结束且allfinal全完成才停止。旧全文{oldprompt} SHA{H(oldprompt.read_bytes())}保留历史。

以下旧快照追溯，以上和之后actual优先：

'''
 save('OWN_SAVED_PPO_HOURLY_MONITOR_UPDATE_REQUEST.json',dict(id='mod4-10',mode='update',kind='heartbeat',name=setting['name'],rrule=setting['rrule'],status='ACTIVE',targetThreadId=setting['target_thread_id'],prompt=prefix+setting['prompt']))
 print(json.dumps(dict(actual_saved_PPO_CPU_synced=True,actor_changed=proof['actor_tensors_changed'],optimizer_delta=proof['optimizer_step_delta_min'],monitor_request=str(R/'OWN_SAVED_PPO_HOURLY_MONITOR_UPDATE_REQUEST.json'))))
if __name__=='__main__':
 try:main()
 except BaseException:save('OWN_SAVED_PPO_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
