from route_fixture_io import *
import tomllib

def main():
    assert not (R/'COMPLETE152_SECOND_STORAGE_METADATA_SYNCED.json').exists()
    pick=lambda folder,pat:max(folder.glob(pat),key=lambda p:int(p.stem.rsplit('_',1)[1]))
    second=W/'MOD4_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012';sr=second/'reports'
    decision=json.loads((R/'COMPLETE152_ROUTE_SECOND_SCOPE_DECISION.json').read_bytes())
    component=pick(sr,'ROUTE_SECOND1800_COMPONENT_CPU_ACTUAL_[0-9]*.json');cpu=json.loads(component.read_bytes());storage=json.loads((sr/'SECOND1800_DURABLE_STORAGE_ADMISSION_ACTUAL.json').read_bytes())
    assert decision['all_four_actual_complete_errorfree_fullraw_reviewed'] and cpu['passed'] and not storage['passed']
    stamp=str(time.time_ns());files={
      'E1_WAVE50_ROUTE152_COMPLETE_ACTUAL_COLLECTION_'+stamp+'.json':pick(R,'ROUTE443_CANDIDATE_COLLECTED_[0-9]*.json'),
      'E1_WAVE50_ROUTE152_COMPLETE_ACTUAL_REVIEW_'+stamp+'.json':pick(R,'ROUTE443_CANDIDATE_ACTUAL_REVIEW_[0-9]*.json'),
      'E1_WAVE50_ROUTE152_DIRECT151_PREFIX_ACTUAL_REVIEW_'+stamp+'.json':pick(R,'ROUTE443_DIRECT151_PREFIX_ACTUAL_REVIEW_[0-9]*.json'),
      'E1_WAVE50_ROUTE152_COMPLETE_SCOPE_DECISION_'+stamp+'.json':R/'COMPLETE152_ROUTE_SECOND_SCOPE_DECISION.json',
      'E1_WAVE50_ROUTE_SECOND1800_COMPONENT_CPU_ACTUAL_'+stamp+'.json':component,
      'E1_WAVE50_ROUTE_SECOND1800_DURABLE_STORAGE_REJECTED_'+stamp+'.json':sr/'SECOND1800_DURABLE_STORAGE_ADMISSION_ACTUAL.json',
      'E1_WAVE50_ROUTE_SECOND1800_LOCAL_PAYLOAD_PREPARED_'+stamp+'.json':R/'ROUTE_SECOND1800_LOCAL_PAYLOAD_PREPARED.json',
      'E1_WAVE50_ROUTE_SECOND1800_ORIGINAL_CPU_READER_ERROR_'+stamp+'.json':pick(sr,'ROUTE_SECOND_COMPONENT_READER_ERROR_[0-9]*.json'),
      'NEXT_E1_WAVE50_ROUTE_SECOND1800_STORAGE_TARGET_ADMISSION_WORK_ORDER_'+stamp+'.md':second/'NEXT_ROUTE_SECOND1800_STORAGE_AND_TARGET_ADMISSION_WORK_ORDER.md'}
    n,w=io.connect_both()
    try:
      with n.open_sftp() as f:
        for name,p in files.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
        raw=f.open(io.E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json','rb').read();old=H(raw);current=json.loads(raw)
      ref=lambda s:io.E+'/reports/'+next(k for k in files if s in k);rev=current['terrain_subexpert_revision004'];scope=rev['wave50_route_candidate152_actual_scope']
      assert scope['own_source_count']==443 and scope['own_checkpoint_SHA']==decision['default_same_scope_source_SHA']
      scope.update(actual_collection=ref('COMPLETE_ACTUAL_COLLECTION'),actual_review=ref('COMPLETE_ACTUAL_REVIEW'),direct151_prefix_ref=ref('DIRECT151_PREFIX'),complete_scope_decision=ref('COMPLETE_SCOPE_DECISION'),review_complete=True,pending=[],forward_complete=12,reverse_complete=25,ordinary=0,unique_truncations=4,closure_mm=decision['closure_mm'],not_qualified50=True,all_valid_failed_prefixes_and_original_false_preserved=True,next_work_order=ref('NEXT_E1_WAVE50_ROUTE_SECOND1800'))
      rev['wave50_route_second_bounded_component_CPU_scope']=dict(local_payload_folder=str(second),proposed_target_root='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012',proposed_source_count=446,expected_old443_allbytes_plus3_only=True,selected_same_scope_source_SHA=decision['default_same_scope_source_SHA'],selected_source_finite_tensors=107,original35_b026_129_ancestry_preserved=True,CPU_component_passed=True,component_actual_ref=ref('COMPONENT_CPU_ACTUAL'),new_target_fullstate_CPU_not_admitted=True,new_target_root_not_created=True,new_GPU_PPO_controller_not_deployed=True,first300_plus_new_second1800_max2=True,storage_guard_passed=False,storage_rejection_ref=ref('DURABLE_STORAGE_REJECTED'),actual_durable_free_bytes=storage['resources']['actual_durable_free_bytes'],required_second1800_bytes=storage['resources']['required_second1800_bytes'],shortfall_bytes=storage['resources']['shortfall_bytes'],original_CPU_reader_error_ref=ref('ORIGINAL_CPU_READER_ERROR'),human_action_needed=True,next_work_order=ref('NEXT_E1_WAVE50_ROUTE_SECOND1800'),no_lower_guard_tmpfs_evidence_source_weights_env_cache_delete=True,no_more_PPO_before_actual_capacity_target_CPU_and_unique_dispatch=True)
      rev['active_next_expert']='E1_WAVE';rev['active_next_phase']='WAVE50_second_route1800_CPU_components_ready_durable_storage_rejected_target_pending';rev['latest_actual_scope']='wave50_route_second_bounded_component_CPU_scope'
      nxt=io.E+'/reports/COMPLETE152_SECOND_STORAGE_NEXT_CURRENT_'+stamp+'.json'
      with n.open_sftp() as f:io.put(f,nxt,json.dumps(current,ensure_ascii=False,indent=2).encode())
      synced=run(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(E_TOKEN)/'reports';p=R/'MOE_PLAN_EXECUTION_CURRENT.json';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=Path(B_TOKEN);before=h(B)
protected={k:(R/k).read_bytes() for k in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')};assert h(p)==OLD_TOKEN
temp=p.with_name('COMPLETE152_SECOND_STORAGE_'+str(time.time_ns())+'.tmp');temp.write_bytes(Path(NEXT_TOKEN).read_bytes());assert h(p)==OLD_TOKEN;os.replace(temp,p);assert all((R/k).read_bytes()==a for k,a in protected.items())
v=dict(epoch=time.time(),passed=True,current_SHA=h(p),master_approval_tracks_RM004_bytes_exact=True,canonical_SHA_before=before,canonical_SHA_after=h(B),canonical_not_written=True,complete152_direct151_second_CPU_component_and_storage_rejection_synced=True,no_GPU_oldonce_or_budget_mutation=True)
q=R/('E1_WAVE50_COMPLETE152_SECOND_STORAGE_METADATA_SYNCED_'+STAMP_TOKEN+'.json');assert not q.exists();q.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('E_TOKEN',repr(io.E)).replace('B_TOKEN',repr(io.B)).replace('OLD_TOKEN',repr(old)).replace('NEXT_TOKEN',repr(nxt)).replace('STAMP_TOKEN',repr(stamp)))
      save('COMPLETE152_SECOND_STORAGE_METADATA_SYNCED.json',synced)
    finally:io.cleanup(n,w)
    setting=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
    assert setting['status']=='ACTIVE' and setting['rrule']=='FREQ=HOURLY;INTERVAL=1'
    previous=D/'MONITOR_PREVIOUS_ROUTE443_FINAL_BEFORE152_COMPLETE.md';assert not previous.exists();previous.write_text(setting['prompt'],encoding='utf8')
    prefix=f'''最新actual优先：152四case全部actualcomplete/errorfree/twohost8JSONbyteSHA/fullraw182821946B SHA2452d4c4c36a2cfc0d32aa3f14c17ded7ba2477b3d3ccfd2c9a8fed2e2aaffc7/queryNPZ及独立全raw/direct151已审，不再pending。50mm正向12/27倒25/27，ordinary0/route4/closure1.1957105016335845mm，原1N两轮前后支撑与位置逐episode吻合，全部validfailedprefix/原false/cost保留。direct1519/26：正回退6,30,60,69,75，改善24,33,36,39,45,48,51,57；倒回退4,64，改善19。负4pi0/8正7/8/world63/64/maxcross.051384614、直线±1.5误差.066174537/.045016099诊断原false保持，E0冻结/gate未训；未qualified50/不70或全RM-MoE/永久抗遗忘，不造27/27或90-95-100机械晋级线。

已积极准备同50-entry-direction-route第二1800s窗口3独立组件与CPU组件审查：本机{second}/payload的truthfulsameidentityworker、显式005七扩展/sourceguard、uniquecontroller均compile；actualown44368401c/CPU107全state/私有command磁盘fixture/独立actorcriticoptimizerstorage/严格wrong profile-assignment-map-origin-parentBoundarySHA-episode-spawn-limit-initialsource-expert拒绝/noRNG/noCUDA真正通过。首次CPU读者把command-onlysame用于含tupletensor的完整ck在任何proof/targetroot/GPU前失败原error/source保留；独立完整CPUtree等值支持tensor/numpy/listtuple，生产validator不变。仅componentCPU/本地prepared，不冒真正targetfullstateCPU/source446部署/PPO。预期新root old443allbytes+3=446，尚未创建/准入/dispatch。

真实storage准入拒绝：4090持久ext4仅2801319936B可用，second1800保存guard要求5284658838B、缺2483338902B，RAM59500097536B正常。规则2×实际completed1800whole1515186413B+2GiB+2×source delta601182B+105600000B routefile余量；不降guard/不删rawweights-source-env-cache/不用tmpfs/不改预算，不把磁盘拒绝当物理或PPO失败。已向人类请求至少3GB非训练资料空间或另一可写持久目录；人类答复/actual容量优先，时间流逝不是许可或容量。若未变，无新PPO合法待资源，不无限伪称训练；继续有价值只读/证据补档，不重复通知相同需要。容量实际足够后按新工作单新独立targetROOT/旧443bytesexact+3/newsourcefreeze/targetfullstateCPU107/import-main-Popen-guardian-root+seed20260928/strict source684与35b026-129祖先，再唯一1800s含loadlearnsaveexit/save25/15sguardian/20k24control-update自动同canonical正常扣；原443 SDKnative/smallbig/fresh/clockDRgeometryhardware actualPASSED全部SHA复用，不重预检/GPU/旧once。candidate actualbothhostqueue/results/jobsunused才编号，不盲153claim。

先读中央E1_WAVE50_ROUTE152_COMPLETE_ACTUAL_COLLECTION/COMPLETE_ACTUAL_REVIEW/DIRECT151_PREFIX_ACTUAL_REVIEW/COMPLETE_SCOPE_DECISION、E1_WAVE50_ROUTE_SECOND1800_COMPONENT_CPU_ACTUAL/DURABLE_STORAGE_REJECTED/LOCAL_PAYLOAD_PREPARED/ORIGINAL_CPU_READER_ERROR、COMPLETE152_SECOND_STORAGE_METADATA_SYNCED和NEXT_E1_WAVE50_ROUTE_SECOND1800_STORAGE_TARGET_ADMISSION_WORK_ORDER；current.rev004.wave50_route_second_bounded_component_CPU_scope当前，candidate152已complete/nonqualified。本机{D}/reports最新完整152/direct151/decision与{second}/reports新componentCPU/storage actual优先。不能套旧152pending/443formalactive或本地prepared冒targetCPU/GPU学习。

Own443model32264 SHA68401cae6402c5aa38797dabdbb7043f8036ed6fcbacd9c34fda0bdd95a813c5/18701417B/CPU107/source443/100actualmodule snapshots+443freeze/PID3274916/PASSED/unique330.2157027721405s一次结清/actual父guardian孩子exit-twfcntlFree-activeSactive空已核；6updates144controls2.88Msteps576cb，9actorchanged/optimizerdelta120，ordinary-integrityunknown0/nonfinitefalse/STOPnone，closure.85974508mm/mimic.001691456。timeout1469 route1 unique1470两coverageexact。新route只有Wave出生physicalepisode inward2→4m，outward/lateral/nonWave2m exact，geometry-reset-commandabsRNGstanding-DRrewardLRhardwareclock五族不混改。first300 trace1.44s/env不是完整十波暴露/rootcommandproxy不是contact/因果证书；source684只是同expert续训源非qualified或其他expert默认暖启动。下一same50entrydirectionroute actorcriticstdoptimizer/allD0D7-globalnamed-dictprivateCPUCUDA/terraincommand全部strict exact，新geometry-entry-direction-route flagsfalse/CUDAroundtrip/sourceepisode+1，非PhysXexactresume。已用route scope1块300，合理第二1800后fullaudit、max2/no第三盲块/系统性残差无改善独立诊断；其它旧entry/direction/duration scope失败不抹。

新ownfullsave/PID/PASSED/actualfinite107/sourcefreeze/module snapshots/原parentunique结清/actualexit两fcntlFree-idle后新fourcase全审，原50峰谷十波2.406422727m/.4approach→双轮完整十波200mmafter/80env1500control15s20260928white3/allroot30qparams-staticrecipesassignment/6000cb/worldfloat32 query1e-6/groundcontactintegralCOMhardware/1N与position/全部validprefix/no teleport/stand26无需通行、115129signedcircle沿横dedrift左右4pi直线原false、finalsensor动态bias静态配方分列/.0075bound/actualrawlastreset反馈warmup-readyage exact不松。完整dynamiccurrentrootcellfamily4-vsstaticassignment/beforephysicscommands-vsafterupdatehist分列+直接152全配对决定未来，不缩接近延15s/借评测进程fullsave说合格。

005solecanonical1188000s330h/7extensions第七100h早once，本idle663682.6281144619s快照actualactive/accounted尾段优先，无扩展复制clearactive-tail-recharge/自动加时；CPU-SDKnative-frozen-fresh0PPO不扣，PPOloadlearnsaveexit/failedstartup原parent唯一扣，两fcntl held非exists不删锁/kill/hotpatch/dual20k/其他AI-WASD干预。E0/35b026/CURB20own7b/SLOPEown24b5-8-10 ONLYobserved冻结/gate未训/hardware未标定/S8另批准/93-94paused；固定004005/master812a4b/approvaltracks/RM003002001/2.5msx4-TGS32-4-100Hz-history5msbin3-35actor38critic6action/LR1e-4adaptiveKEEPSTD1-rewardhardware-allD0D7/familiesplane30+20-20-15-15/clearplane条件commands/nonplane±.3yaw0standing.2-command12-16s-episode20s/DRwhite_v3+noise_bias_mild_v1原强度/healthv3closure2mm单envordinaryreset继续PPO,mimic.01nonfiniteunknownmissingcallbackcoverage ownSTOP_AFTER_SAVE/ground1e-6-contact1N-COMhardware-fullsignedcircle原tol/otherexpertgate min(18h,.13B)规划保持，无pureteacherS7S8/70-20-10或SCUT10.25mm作MOD4阈值。

所有complete152/direct151/raw-query索引/新prepared3组件/CPU错误与独立tree修复/实际componentCPU/storage拒绝/人类动作请求/syncmonitor工作单Gitreceipt持续Git；新真实diagnostic/rejection stage唯一record_experiment annotatedtrial actualremote main-tag-peeled/alloldtags工具证明，后receiptordinarysupplement，pushfail只续existingobjects不重record-tag-commit。大PTNPZrawJSONUSDZIP仅真实pathsizeSHA原件保留/credentials不输出Git/Git非训练依赖。所有MOD4/SCUT oldonce/stage/main/resume/SDKnative/PPOfresh/record/sync/budgettail已执行不可重跑，仅读按actualstage复用。same mod4-10heartbeatACTIVE每1h同target/healthyDONT_NOTIFY，实质阶段真实修复重大退化完成人类动作NOTIFY，不5minSSH/ping/Rich/额外驻守/自动预算；reviewready不是allcoursefinished不删，仅actualbudgetend/allfinal完停止。旧完整prompt{previous} SHA{H(previous.read_bytes())}保留，以上和之后actual优先。
'''
    save('COMPLETE152_SECOND_STORAGE_MONITOR_UPDATE_REQUEST.json',dict(id='mod4-10',mode='update',kind='heartbeat',name=setting['name'],rrule=setting['rrule'],status='ACTIVE',targetThreadId=setting['target_thread_id'],prompt=prefix))
    print(json.dumps(dict(passed=True,complete152_and_storage_rejection_synced=True,monitor_request=str(R/'COMPLETE152_SECOND_STORAGE_MONITOR_UPDATE_REQUEST.json'))))

if __name__=='__main__':
    try:main()
    except BaseException:save('COMPLETE152_SECOND_STORAGE_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_oldonce_replay=True));raise
