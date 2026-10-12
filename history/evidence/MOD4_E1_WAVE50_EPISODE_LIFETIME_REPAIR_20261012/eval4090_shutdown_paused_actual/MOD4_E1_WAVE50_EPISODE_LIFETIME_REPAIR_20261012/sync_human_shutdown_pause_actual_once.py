from pathlib import Path
import json,os,time,hashlib,tomllib,traceback
import stage_lifetime_target_CPU_once as io
D=Path(__file__).resolve().parent;R=D/'reports'
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'
B='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'
h=lambda b:hashlib.sha256(b).hexdigest()

def main():
 assert not (R/'HUMAN_SHUTDOWN_PAUSE_METADATA_SYNCED.json').exists()
 p=max(R.glob('HUMAN_SHUTDOWN_BACKUP_COMPLETE_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]));back=json.loads(p.read_bytes());assert back['passed']
 S=Path(back['backup_directory']);safe=json.loads((S/'SHUTDOWN_SAFE_REMOTE_ACTUAL.json').read_bytes());manifest=json.loads((S/'BACKUP_COMPLETE_BYTEEXACT.json').read_bytes());assert manifest['passed'] and safe['passed']
 settings=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert settings['status']=='PAUSED'
 previous=D/'MONITOR_PREVIOUS_BEFORE_SHUTDOWN_PAUSE.md';assert not previous.exists();previous.write_text(settings['prompt'],encoding='utf8')
 stamp=str(time.time_ns());refs={};n,w=io.connect_linux_only()
 try:
  files={'HUMAN_SHUTDOWN_SAFE_ACTUAL':S/'SHUTDOWN_SAFE_REMOTE_ACTUAL.json','HUMAN_SHUTDOWN_BACKUP_BYTEEXACT':S/'BACKUP_COMPLETE_BYTEEXACT.json','HUMAN_SHUTDOWN_RESUME_HANDOFF':S/'SHUTDOWN_RESUME_HANDOFF.md','WAVE50_LIFETIME459_OWN_FORMAL_CPU_VERIFIED':max(R.glob('LIFETIME459_OWN_FINAL_CPU_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]))}
  with n.open_sftp() as f:
   for name,q in files.items():
    target=E+'/reports/'+name+'_'+stamp+q.suffix
    with f.open(target,'wx') as out:out.write(q.read_bytes());out.flush()
    refs[name]=dict(path=target,bytes=q.stat().st_size,sha256=h(q.read_bytes()))
   target=E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json'
   with f.open(target,'rb') as src:raw=src.read()
   old=h(raw);v=json.loads(raw);rev=v['terrain_subexpert_revision004']
   scope=rev['wave50_episode_lifetime_repair_scope'];assert scope['source_count']==459
   scope.update(current_stage='formal_complete_human_paused',formal_final_pending=False,own_checkpoint=safe['own_checkpoint'],actual_CPU_floating_count=107,actual_module_snapshots=104,own_CPU_ref=refs['WAVE50_LIFETIME459_OWN_FORMAL_CPU_VERIFIED']['path'],final_actual_ref=refs['HUMAN_SHUTDOWN_SAFE_ACTUAL']['path'],unique_completed_segment=safe['unique_completed_segment'],actual_exit_three_locks_free=True,qualified50=False)
   rev['wave50_lifetime459_eval4090_actual_scope']=dict(root=safe['evaluation_root'],human_requested_backend4090=True,all4_actualcomplete_errorfree=True,results=safe['evaluation_results'],raw_backup_manifest_ref=refs['HUMAN_SHUTDOWN_BACKUP_BYTEEXACT']['path'],independent_complete_behavior_review_pending=True,cross_host_equivalence_confirmed=False,no_global_candidate_number_claimed=True)
   rev['human_pause_for_shutdown_actual_scope']=dict(epoch=time.time(),human_request='现在先暂停一下训练，我要关机重启一下，保存好东西',pause_active=True,automatic_training_and_evaluation_launch_prohibited=True,human_explicit_resume_required=True,monitor_id='mod4-10',monitor_status='PAUSED',actual_saved_exit_locks_budget_ref=refs['HUMAN_SHUTDOWN_SAFE_ACTUAL']['path'],backup_manifest_ref=refs['HUMAN_SHUTDOWN_BACKUP_BYTEEXACT']['path'],handoff_ref=refs['HUMAN_SHUTDOWN_RESUME_HANDOFF']['path'],same_lifetime_parallel_second_only_partial_local_prepared_original_SyntaxError_retained=True,newsecond_target_root_CPU_GPU_dispatch_not_created=True,concurrent_training_and_evaluation_not_demonstrated=True)
   rev['latest_actual_scope']='human_pause_for_shutdown_actual_scope';rev['active_next_phase']='HUMAN_PAUSED_FOR_SHUTDOWN_RESTART';rev['active_next_expert']='E1_WAVE';v['human_training_pause_active']=True
   nextpath=E+'/reports/SHUTDOWN_CURRENT_PREPARED_'+stamp+'.json'
   with f.open(nextpath,'wx') as out:out.write(json.dumps(v,ensure_ascii=False,indent=2).encode());out.flush()
  code=r'''from pathlib import Path
import json,time,os,hashlib
R=Path(E_TOKEN)/'reports';p=R/'MOE_PLAN_EXECUTION_CURRENT.json';B=Path(B_TOKEN);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=B.read_bytes();b=json.loads(before);assert b['active_segment'] is None
names=('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json');protected={k:(R/k).read_bytes() for k in names};assert h(p)==OLD_TOKEN
tmp=p.with_name('SHUTDOWN_PAUSE_'+STAMP_TOKEN+'.tmp')
with tmp.open('xb') as f:f.write(Path(NEXT_TOKEN).read_bytes());f.flush();os.fsync(f.fileno())
assert h(p)==OLD_TOKEN;os.replace(tmp,p)
assert B.read_bytes()==before and all((R/k).read_bytes()==v for k,v in protected.items())
v=dict(epoch=time.time(),passed=True,current_SHA=h(p),human_training_pause_active=True,source459_formal_final_and_eval4090_complete_recorded=True,latest_scope='human_pause_for_shutdown_actual_scope',master_approval_tracks_RM004_exact=True,canonical_bytes_unchanged=True,no_training_GPU_launch_signal_budgetwrite_delete=True)
q=R/('HUMAN_SHUTDOWN_PAUSE_METADATA_SYNCED_'+STAMP_TOKEN+'.json')
with q.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
fd=os.open(str(R),os.O_DIRECTORY);os.fsync(fd);os.close(fd);print(json.dumps(v))
'''
  for token,value in [('E_TOKEN',E),('B_TOKEN',B),('OLD_TOKEN',old),('NEXT_TOKEN',nextpath),('STAMP_TOKEN',stamp)]:code=code.replace(token,repr(value))
  result=io.run(n,code);io.save('HUMAN_SHUTDOWN_PAUSE_METADATA_SYNCED.json',dict(result,refs=refs,local_backup=back['backup_directory']))
 finally:n.close();os.environ.pop('RM_SSH_PASSWORD',None)
 prompt=f'''人类2026-10-12明确暂停训练准备关机重启。mod4-10同一heartbeat保持PAUSED/每1h同target；禁止自动启动训练或评测，禁止自动恢复，等待人类明确“继续/恢复”。本提示不是训练恢复授权。实际暂停交接{refs['HUMAN_SHUTDOWN_RESUME_HANDOFF']['path']} SHA{refs['HUMAN_SHUTDOWN_RESUME_HANDOFF']['sha256']}，本机{back['handoff']}；备份manifest{back['manifest']}。

最新source459已自然完整保存退出：model32264 SHA d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a，floatingCPU107/新增3bool-int字段/104module snapshots+459freeze，11startup严格CPUCUDA/episode+1，6updates144controls，unique335.22595477104187s原parent一次结清，actual父guardian孩子全部退出、两训练锁与evaluation_only第三锁fcntl-free、active-Sactive空/GPUcompute空。最新权重与全部run源码、trace、health/startup和四case4090冻结评测raw共696files/482335583B已本机byteexact/fsync备份，远端原件保持。最新actual及之后fresh/proc优先，旧459native/active与3060评测等待只是历史。

4090新独立冻结4case actualcomplete/errorfree，actual raw已备份但完整独立行为/query/contact/route/retention审查仍pending，不称50mm合格/70mm训练、跨host等价或全MoE毕业。原153完整13/23保持，原失败/false/raw/cost保持。第二same-lifetime并行训练仅本地一个worker prepared，原builder SyntaxError在targetCPU/root/GPU/dispatch前，controller与guard未创建；没有真正并行学习，暂停期间不修复/部署。3060按人类暂不可用，不SSH/ping或重启健康worker；WASD播放器不GUI/reset/stop/restart。

人类明确恢复后，先按上述新交接核fresh /proc/ownfullsave-PASSED-sourcefreeze/11startup/unique账段/实际exit锁与budget，再完成这四case全原协议审查，合理下一有界sameidentity窗口或独立诊断。禁止重放任何oldonce/main/resume/SDK-native/PPOpreflight/fresh/publish/record/sync/预算tail。005唯一1188000s330h/七扩展第七100h早once，不扩展/复制/clearactive/refund/tail/recharge；twofcntl不是文件exists，不删锁/kill/hotpatch/dual20k/其它AI干预。source459只Wave出生time_out20→40s/nonWave20s，geometry-entry-direction-route/DRrewardLRhardwareclock五族原合同，冻结50测试.4approach15s1Nafter200mm/query1e-6/contactCOMhealth原阈值不松，35/CURB20/SLOPE/E0接受范围继续冻结/gate未训/S8另具体批准。旧719清理及精确PID终止授权均消费，不扩展新delete/kill。

所有保存source/error/raw-index/report/关机备份交接/sync/monitor/Gitreceipt继续Git，完整actualremote main/tag/peeled工具为准，后receipt普通supplement，大PTNPZUSDZIP只actualpathsizeSHA原件保留/凭据不输出Git。不要为补档重GPU或预算事务。前完整prompt历史{previous} SHA{h(previous.read_bytes())}；最新actual暂停优先。
'''
 io.save('HUMAN_SHUTDOWN_MONITOR_UPDATE_REQUEST.json',dict(id='mod4-10',mode='update',kind='heartbeat',name=settings['name'],rrule=settings['rrule'],status='PAUSED',targetThreadId=settings['target_thread_id'],prompt=prompt))
 print(json.dumps(dict(passed=True,backup=back['backup_directory'],monitor_request=str(R/'HUMAN_SHUTDOWN_MONITOR_UPDATE_REQUEST.json'),central_handoff=refs['HUMAN_SHUTDOWN_RESUME_HANDOFF'])))

if __name__=='__main__':
 try:main()
 except BaseException:io.save('HUMAN_SHUTDOWN_SYNC_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_training_restore=True));raise
