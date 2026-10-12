from route_second_io import *
import tomllib
C=W/'MOD4_OLD_CHECKPOINT_CLEANUP_20261012'

def main():
    assert not (R/'CLEANUP_FAILED446_RESOURCE449_METADATA_SYNCED.json').exists()
    stamp=str(time.time_ns());cr=C/'reports';files={
        'HUMAN_OLD_CHECKPOINT_CLEANUP_ACTUAL':cr/'HUMAN_AUTHORIZED_OLD_CHECKPOINT_DELETE_ACTUAL.json',
        'HUMAN_OLD_CHECKPOINT_CLEANUP_PLAN_ACTUAL':cr/'OBSOLETE_INCOMING_CHECKPOINT_PLAN_ACTUAL.json',
        'WAVE50_ROUTE446_TARGET_CPU_VERIFIED':R/'ROUTE_SECOND_TARGET_CPU_PASSED.json',
        'WAVE50_ROUTE446_DISPATCH_ACTUAL':R/'SECOND_ROUTE_DISPATCH_ACTUAL_RECEIPT.json',
        'WAVE50_ROUTE446_PRECONTROL_FAILURE_SOURCES':R/'FAILED_SECOND_STARTUP_RESTORE_SOURCE_ACTUAL.json',
        'WAVE50_ROUTE446_HUMAN_END_BYTE_REVIEWED_ACTUAL':R/'FAILED_END_BYTE_REVIEWED_ACTUAL.json',
        'WAVE50_POST_FAILURE_PINNED_ALLOCATION_ACTUAL':R/'POST_FAILURE_PINNED_ALLOCATION_ACTUAL.json',
        'WAVE50_ROUTE449_RESOURCE_ADMISSION_ACTUAL':R/'RESOURCE_DURABLE_RAM_GPU_ADMISSION_ACTUAL.json',
        'WAVE50_ROUTE449_TARGET_CPU_VERIFIED':R/'RESOURCE_TARGET_CPU_PASSED.json',
        'WAVE50_ROUTE449_SOURCE_FREEZE':R/'RESOURCE_SOURCE_FREEZE.json',
        'WAVE50_ROUTE449_DISPATCH_ACTUAL':R/'RESOURCE_DISPATCH_ACTUAL_RECEIPT.json'}
    for p in files.values():assert p.is_file()
    end=json.loads(files['WAVE50_ROUTE446_HUMAN_END_BYTE_REVIEWED_ACTUAL'].read_bytes());dispatch=json.loads(files['WAVE50_ROUTE449_DISPATCH_ACTUAL'].read_bytes());cpu=json.loads(files['WAVE50_ROUTE449_TARGET_CPU_VERIFIED'].read_bytes())
    assert end['failed_child_ended'] and cpu['passed'] and dispatch['source_count']==449
    n,w=io.connect_both()
    try:
        with n.open_sftp() as f:
            refs={}
            for name,p in files.items():path=io.E+'/reports/'+name+'_'+stamp+'.json';io.put(f,path,p.read_bytes());refs[name]=path
            raw=f.open(io.E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json','rb').read();old=H(raw);v=json.loads(raw)
        rev=v['terrain_subexpert_revision004'];prior=rev['wave50_route_second_bounded_component_CPU_scope']
        prior.update(new_target_fullstate_CPU_not_admitted=False,new_target_root_not_created=False,new_GPU_PPO_controller_not_deployed=False,storage_guard_passed=True,human_action_needed=False,original_storage_rejection_retained_as_history=True,actual_deployment_source446_followed_by_failed_precontrol_startup=True,failed_startup_ref=refs['WAVE50_ROUTE446_PRECONTROL_FAILURE_SOURCES'],actual_end_and_unique_original_segment_ref=refs['WAVE50_ROUTE446_HUMAN_END_BYTE_REVIEWED_ACTUAL'],own_formal_PPO_completed=False)
        rev['human_authorized_old_checkpoint_cleanup_actual']=dict(actual_ref=refs['HUMAN_OLD_CHECKPOINT_CLEANUP_ACTUAL'],plan_ref=refs['HUMAN_OLD_CHECKPOINT_CLEANUP_PLAN_ACTUAL'],old_obsolete_intermediate_deleted_count=719,actual_deleted_bytes=3219782461,authorization_scope_only_actual_719_list=True,deleted_binary_originals_no_longer_retained=True,old_SHA_history_unchanged=True,no_further_deletion_permission_inferred=True)
        rev['wave50_route_startup_resource_reviewed_scope']=dict(root=dispatch['root'],source_count=449,selected_source_SHA=INIT_SHA,selected_source_finite_tensors=107,old446_allbytes_exact_plus3=True,target_CPU_passed=True,target_CPU_ref=refs['WAVE50_ROUTE449_TARGET_CPU_VERIFIED'],source_freeze_ref=refs['WAVE50_ROUTE449_SOURCE_FREEZE'],resource_ref=refs['WAVE50_ROUTE449_RESOURCE_ADMISSION_ACTUAL'],dispatch_ref=refs['WAVE50_ROUTE449_DISPATCH_ACTUAL'],actual_dispatch=True,owner=dispatch['owner'],actual_GPU_startup_fullstate_and_PPO_proof_pending=True,own_formal_final_pending=True,pinned_empty_context_ref=refs['WAVE50_POST_FAILURE_PINNED_ALLOCATION_ACTUAL'],empty_context_pass_not_original_scene_failure_cause_proof=True,only_prePPO_failure_nonzero_exit_and_resource_guard_change=True,all_normal_learning_save_DR_rng_physics_restoration_validators_unchanged=True,original_failed446_cost_once_preserved=end['completed_own_segments'],no_SDK_native_preflight_replay=True,no_new_budget_seconds=True,max2_route_learning_blocks=True,next_actual_fourcase_required_before_more_PPO_or70=True)
        rev['active_next_expert']='E1_WAVE';rev['active_next_phase']='WAVE50_route449_resource_reviewed_unique_dispatched_actual_startup_pending';rev['latest_actual_scope']='wave50_route_startup_resource_reviewed_scope'
        nxt=io.E+'/reports/CLEANUP_FAILED446_RESOURCE449_CURRENT_'+stamp+'.json'
        with n.open_sftp() as f:io.put(f,nxt,json.dumps(v,ensure_ascii=False,indent=2).encode())
        synced=run(n,r'''from pathlib import Path
import json,time,os,hashlib
R=Path(E_TOKEN)/'reports';p=R/'MOE_PLAN_EXECUTION_CURRENT.json';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected={k:(R/k).read_bytes() for k in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')};assert h(p)==OLD_TOKEN
tmp=p.with_name('RESOURCE449_'+str(time.time_ns())+'.tmp');tmp.write_bytes(Path(NEXT_TOKEN).read_bytes());assert h(p)==OLD_TOKEN;os.replace(tmp,p)
assert all((R/k).read_bytes()==a for k,a in protected.items())
v=dict(epoch=time.time(),passed=True,current_SHA=h(p),protected_master_approval_tracks_RM004_bytes_exact=True,canonical_not_written=True,human_exact719_cleanup_failed446_end_unique_segment_and_resource449_dispatch_synced=True)
q=R/('CLEANUP_FAILED446_RESOURCE449_METADATA_SYNCED_'+STAMP_TOKEN+'.json');assert not q.exists();q.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('E_TOKEN',repr(io.E)).replace('OLD_TOKEN',repr(old)).replace('NEXT_TOKEN',repr(nxt)).replace('STAMP_TOKEN',repr(stamp)))
        save('CLEANUP_FAILED446_RESOURCE449_METADATA_SYNCED.json',synced)
    finally:io.cleanup(n,w)
    setting=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert setting['status']=='ACTIVE' and setting['rrule']=='FREQ=HOURLY;INTERVAL=1'
    priorprompt=D/'MONITOR_PREVIOUS_STORAGE_BLOCKED_BEFORE_HUMAN_CLEANUP.md';assert not priorprompt.exists();priorprompt.write_text(setting['prompt'],encoding='utf8')
    prefix=f'''最新actual优先：人类“远古一些废旧检查点可以清理”已实际完成唯一719份2026-09-08/09 unused incoming中间检查点清理，保留首/最后3/每1000iter/所有referenced basename、current source684/accepted专家/reports/raw/source/env/cache。实际删除3219782461B/allocated3221499904B，持久free2788442112→6009384960B；逐file真实path-size-SHA-inode/时间/新refs/进程FD确认与fsync intent-complete journal保存。该719原binary已不再保留，旧SHA/false/历史不改；明确只此实际approvedlist，不授权更多删除。原duplicateonly177MB不足、SSH10054未知outcome/独立staged续、NUL SyntaxError predelete与独立byte修复全部保留，绝不重delete/oldonce。旧“未答复/空间blocked/source446未部署”仅历史。

source446曾targetCPU107通过且唯一dispatch，但20k初始化在任何control/PPO前实际PxgPinnedMemoryAllocate658725376B/337280000B Result1失败、PhysX scene corrupted，后mild_DR wheel friction .199999988>原1e-6严格拒绝；没有任何10startup marker/manifest/own checkpoint/PPO。不能将下游审查差唯一归因恢复代码或永久资源不足，不松DR/physics阈值。app.close卡住；人类明确仅授权pid3340979-start94499270先SIGTERM必要SIGKILL结束，已实际两个signal，原父guardianchild全exit/twofcntlFree/active-Sactive空/原父unique3466.325003385544s失败load-exit账段保留，不退款/重结/clearactive。原end reader timeout关键字preSSH TypeError及postsignal bytesJSON partialreceipt错误原source/raw保留，独立byteexact只读补齐不重signal。此授权已用，不扩展未来kill/别AI。

已实际独立新source449/root={dispatch['root']}=446全部bytesexact+3，targetCPU107/source684完整状态/8route strictnegative/privatecommanddisk/import-main-Popen-guardian-root/seed20260928/production恢复func与main除observerflag ASTexact通过；新worker仅prePPO失败先fsync原error并os._exit1，避免Kit failed初始化teardown卡住，正常learn-save-exit原样。独立emptyCUDAcontext两原failedsize同时mapped pinned hostallocation成功并free/contextrelease/noPhysX/noPPO/no预算；这不是原scene根因证明，不调OS/driver/physx/DR。真正durable/RAM/GPU新guard根据实际已完成1800wholeoutput、原childpeak+请求size余量与actualdevicefree通过。old446/443不hotpatch/复活/--resume。

449 uniquecontroller已实际dispatch owner{dispatch['owner']['pid']}-start{dispatch['owner']['start_ticks']}只当时定位；之后actual/proc/ownstartup/fullsave/PID/PASSED/phase优先。首1800s含loadlearnsaveexit/save25/15s guardian/20k24controlupdate，从own44368401cae6402c5aa38797dabdbb7043f8036ed6fcbacd9c34fda0bdd95a813c5/18701417B/CPU107、accepted35b026与1293c97祖先；same50-entry-direction-route全actorcriticstdoptimizer/allD0D7/globalnamed-dictprivateCPUCUDA/geometrycommand全部exact/newflagsfalse/实际CUDA磁盘roundtrip/episode+1，非PhysXexactresume。尚无startup或PPO proof为合法pending，不借CPU/进程假训练更新。原SDK/native/smallbig/fresh/clockDRgeometryhardware PASSED exactSHAreuse，不重复任何旧预检/45minclock。活动save不冒final，owncompleteCPU107/source449/实际snapshot+ownfreeze/PID/PASSED/unique结清/actualexit-twofcntlFree-idle后自动newfourcase。实际bothhostunused153在stage核验只是number准入，未actualpublication不可重发/盲claim。

先读中央CLEANUP_FAILED446_RESOURCE449_METADATA_SYNCED与WAVE50_ROUTE449_TARGET_CPU_VERIFIED/RESOURCE_ADMISSION_ACTUAL/DISPATCH_ACTUAL/SOURCE_FREEZE、WAVE50_ROUTE446_HUMAN_END_BYTE_REVIEWED_ACTUAL/PRECONTROL_FAILURE_SOURCES/HUMAN_OLD_CHECKPOINT_CLEANUP_ACTUAL，current.rev004.wave50_route_startup_resource_reviewed_scope；本机{D}/reports最新RESOURCE_REVIEWED_ACTUAL/未来ownstartup-ownsave-final/candidate优先，read_resource_reviewed_actual.py仅读。source446失败不重main/once，read_route_second_actual.py仅旧446历史；新的missingfuture合法pending。真实失败完整原error/source/raw/cost独立诊断，不能Kill/hotpatch/dual20k/clearactive或只无限hold。

152已全部fullraw/errorfree/query/两host8JSONbyteSHA/完整root30q-params-staticrecipesassignment/6000cb/ground1e-6-contactintegralCOMhardware/1N双轮前后support与position/direct151审：50正12/27倒25/27 ordinary0/route4，全部failedprefix/原false保持。不是qualified50，不70/全WaveRM-MoE/永久抗遗忘，不造27/27或90-95-100机械晋级门槛。route只Wave出生episode toward2→4m、outward/lateral/nonWave2m exact；冻结十波2.406422727m/.4approach/15s/双轮after200mm原1N接触与position分列/stand26无需通行/同episodeprereset-before排除teleport不松；115129signedcircle沿横dedrift两4pi直线原false/finalsensor动态bias静态配方/.0075bound/feedbackactualrawlastreset-readyage原容差保持。own完整fulltrace dynamiccurrentrootcellfamily4 vsstaticassignment/beforephysicscommand vsafterupdatehist分相位，再candidate direct152全部初态参数staticrecipesassignments/逐env改善退化prefix审。rootproxy非contact/fullroute或因果证书。route scope已学first300，449是第二1800；446只有failedstartup0PPO，仍如实扣成本，非完成learning块。第二块完整四case+ownfulltrace再独立决定，max2/≤2h，不盲第三/70；系统性无改善独立轴诊断，不只队列。

005solecanonical1188000s330h/7extensions第七100h早once；新parent按真实loadlearnsaveexit/accounted与未accounted尾段唯一扣，CPU/SDK/native/frozen/fresh0PPO不计，不扩展复制clearactive-tail-recharge/退款。两锁以actualfcntl held/free非exists不删，其他AI/WASD不GUI干预。E0/35b026/CURB20own7b/SLOPEown24b5-8-10 ONLYobserved冻结/gate未训/hardware未标定/S8另批准/93-94paused；fixed004005/master812a4b/approvaltracks/RM003002001/clock2.5msx4-TGS32-4-100Hz-history5msbin3-35actor38critic6action/LR1e-4adaptiveKEEPSTD1-rewardhardware-allD0D7/fivefamilies/clearplane条件commands/nonplane±.3yaw0standing.2-command12–16s-episode20s/DRwhite_v3+noise_bias_mild_v1原强度/healthv3closure2mm ordinaryreset继续PPO,mimic.01nonfiniteunknownmissingcallbackcoverage ownSTOP_AFTER_SAVE/ground1e-6-contact1N-COMhardware-fullsignedcircle原tol/otherexpertgate min(18h,.13B)保护保持，无pureteacherS7S8/70-20-10/SCUT10.25mm阈值。

所有cleanup逐file索引和journal/授权/719删除事实/源码错误/446targetCPUdispatchfailedlogs/host资源/终止授权-signal-原partialreceipt-独立byte修复/449newsourceCPUdispatch/之后startup-PPO-save-final-candidate/monitor-sync-Gitreceipt持续Git。新真实阶段唯一record_experiment annotatedtrial实际remote main-tag-peeled/alloldtags最终工具证明；pushfail续existingobjects不重record-tag-commit，后receipt普通supplement；largePTNPZrawJSONUSDZIP actualpathsizeSHA原件保持，唯一人类authorized719例外明确，不输出credentials，Git非训练依赖。旧完整prompt{priorprompt} SHA{H(priorprompt.read_bytes())}保留追溯。mod4-10同heartbeatACTIVE每1h同target，healthy pendingDONT_NOTIFY静默，仅实质阶段真实修复重大退化完成或人类动作NOTIFY，不5minSSH/ping/Rich/额外monitor/自动预算；reviewready不删，仅actualbudgetend/allfinal完停止。
'''
    save('CLEANUP_RESOURCE449_MONITOR_UPDATE_REQUEST.json',dict(id='mod4-10',mode='update',kind='heartbeat',name=setting['name'],rrule=setting['rrule'],status='ACTIVE',targetThreadId=setting['target_thread_id'],prompt=prefix))
    print(json.dumps(dict(passed=True,synced=True,monitor_request=str(R/'CLEANUP_RESOURCE449_MONITOR_UPDATE_REQUEST.json'))))

if __name__=='__main__':
    try:main()
    except BaseException:save('CLEANUP_RESOURCE_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_sync_or_GPU_replay=True));raise
