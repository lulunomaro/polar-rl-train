from route_fixture_io import *
import tomllib

def latest(pattern):return max(R.glob(pattern),key=lambda p:int(p.stem.rsplit('_',1)[1]))

def main():
    assert not (R/'ROUTE443_FINAL_CLOSEOUT_METADATA_SYNCED.json').exists()
    cp=latest('ROUTE443_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json');own=json.loads(cp.read_bytes())
    ap=latest('ROUTE_FIXTURE_ACTUAL_[0-9]*.json');actual=json.loads(ap.read_bytes())
    tp=latest('ROUTE443_FULL_TRAINING_TRACE_ACTUAL_[0-9]*.json');trace=json.loads(tp.read_bytes())
    collection=latest('ROUTE443_CANDIDATE_COLLECTED_[0-9]*.json');review=latest('ROUTE443_CANDIDATE_ACTUAL_REVIEW_[0-9]*.json')
    c=json.loads(collection.read_bytes());r=json.loads(review.read_bytes())
    assert own['passed'] and own['closeout_ready'] and own['actual_source_count']==443 and own['actual_finite_tensor_count']==107
    assert trace['passed'] and trace['actual_controls']==own['own']['health']['control_steps'] and trace['own_checkpoint_SHA']==own['own_checkpoint']['sha256']
    assert actual['reports']['E1_STATE.json']['phase']=='E1_WAVE50_route_lifecycle_saved_review_ready' and actual['actual_owner'] is None and actual['actual_child'] is None and actual['reports'].get('E1_ATTENTION.json') is None
    assert c['own']['checkpoint']['sha256']==own['own_checkpoint']['sha256'] and c['published']['source']['sha256']==own['own_checkpoint']['sha256']
    h=own['own']['health'];final=dict(epoch=time.time(),passed=True,own_CPU_report=str(cp),own_CPU_report_SHA=H(cp.read_bytes()),checkpoint=own['own_checkpoint'],checkpoint_bytes=own['checkpoint_bytes'],source_count=443,finite_tensors=107,actual_module_snapshot_count=own['actual_snapshot_file_count'],actual_updates=own['own']['actual_updates'],actual_environment_steps=own['own']['actual_environment_steps'],health=h,actor_tensors_changed=own['actor_tensors_changed'],optimizer_step_delta=own['optimizer_step_delta_min'],unique_loadlearnsaveexit_seconds=own['unique_loadlearnsaveexit_seconds'],old_source_b026_unchanged=True,actual_exit_two_fcntl_free_active_Sactive_empty=True,full_training_trace_reviewed=True,candidate_full_review_pending=not r['review_complete'],not_PhysX_exact_resume=True,not_qualified50_from_fullsave_or_short_prefix=True,no_GPU_budget_oldonce_write=True)
    save('ROUTE443_FORMAL_FINAL_ACTUAL_REVIEW.json',final)
    work=D/'NEXT_ROUTE443_CANDIDATE152_FULL_ACTUAL_REVIEW_WORK_ORDER.md';assert not work.exists()
    work.write_text('''# Route443 own final complete; actual candidate152 full review next

Own443 accepted35b026 initial restore → explicit50-entry-direction-route identity completed actual6PPOupdates144controls2.88Menvsteps576callbacks. Actual ownfinite107/source443/fullsrcsnapshot-ownfreeze/PID/positive actoroptimizer/tenstartup CUDA diskroundtrip/sourceepisode+1/PASSED/unique originalparent settlement/actual parentguardianchild exits/twofcntl-free/active-Sactive empty verified. Savedreviewready is a legal single-scope review boundary, not allcoursescomplete or supervisorfault; never revive oldmain/resume/once/budgettail. SDK/native/smallbig/fresh new scope all actualPASSED once, oldgeometryclockDRhardware exactreuse. Old440 fixture error and CPU SDK-import reader error retained; no replay/threshold relaxation.

Actualpublication152 fourcases and latest collection/review determine pending/complete, not this snapshot. collect_route443_candidate_actual.py only actualcomplete/errorfree twohost8JSONbyteSHA/fullterrainNPZ/queryNPZ. review_route443_candidate_actual.py original50mm ten-wave2.406422727m/.4approach/both-wheel after200mm/80env1500control15s20260928white3/allroot30q parameters-staticrecipes-assignment/6000callbacks/actual float32trianglequery1e-6/groundcontactintegralCOMhardware/1N andposition separately; stand26 no traversingrequirement, allvalidfailedordinary-prefixes/declaration truncation exactoverlap coverage/no resetteleport/no shorterapproach or longerfrozenwindow.115129 fullsignedcircle alongcross-dedrift/two4pi/straight originalstrictfalse. Finalsensor dynamicbias vsstaticrecipe/.0075bound finite; feedbacklastreset actualwarmup-readyage schema. Ownfinite must107 realsavedCPU, no borrowedsource/discardfuturepass.

Fullsavedtrainingtrace144controls=1.44s/env alreadyread-only audited actualNPZ SHA/dynamic currentrootcellfamily4/staticassignment/maskdirection/two signedstanding/prereset-before/commands-beforephysics vs hist-afterupdate distinctphase. Rootcommandproxy is not actualwheelcontact/fullroute/causalproof. review_route443_direct151_prefix_actual.py only after allfour complete fullrawreviewed; compare full initial30q-parameters-staticrecipes-assignments and everyactual improvement/regression/validprefix against complete1519forward26reverse, retain alloriginalfalse/cost. Fullcandidate+own perenvexposure decide next bounded sameidentity route block or independentdiagnosis, no premature positive-forward repairclaim, no fixed27/27 or90/95/100promotionline. Source443 first300 actualonly; if next justified, newroot/sourcefreeze strictsame50entrydirectionroute CPUCUDA/episode+1/independentstorage and actualsourceownfullsave boundary, ≤2h/max2thenfullaudit/no thirdblinddurationblock/70. Futurelongwindow freshdurablefree vsactualownoutput resourceguard, no evidence/cache/env deletion/tmpfs/loweredguard. Evaluation/Git doesnot pause anotherexistingtrainer.

005canonical1188000/7extensions seventh100h alreadyonce; CPU/SDK/native/frozen/fresh0PPO nocharge, originalparent uniquelyloadlearnsaveexit/accountedtail; no ledgercopy/clearactive/tail/recharge/extension/autobudget. E0/accepted35/CURB20/SLOPEonlyobserved scopes frozen/gateuntrained/hardwareuncalibrated/S8specificapproval/93-94paused/WASD noGUIresetstoprestart. Original004005/master/RM/clockDRrewardLRhardwarehealthquerycontactCOMfullsignedcircle/families-commandranges andotherexpertgate min(18h,.13B) protection preserved. Allnew savedsource/errors/unusedprepared/reports/sync/monitor/workorder/Gitreceipt mustGit; newactualstage uniqueannotatedtrial actualremote main-tag-peeled, laterordinarysupplement, large originals actualpathsizeSHA only/preserve, credentials excluded. No oldMOD4/SCUT anyonce/GPUeval replay. Samehourlymod4-10ACTIVEtarget quiethealthy meaningfulonly; reviewready notmonitor deletion, only actualbudgetend/allfinalcomplete stop.
''',encoding='utf8')
    stamp=str(time.time_ns());files={
      'E1_WAVE50_ROUTE443_OWN_FORMAL_CPU_VERIFIED_'+stamp+'.json':cp,
      'E1_WAVE50_ROUTE443_FORMAL_FINAL_ACTUAL_REVIEW_'+stamp+'.json':R/'ROUTE443_FORMAL_FINAL_ACTUAL_REVIEW.json',
      'E1_WAVE50_ROUTE443_FORMAL_FINAL_CURRENT_ACTUAL_'+stamp+'.json':ap,
      'E1_WAVE50_ROUTE443_COMPLETE_TRAINING_TRACE_ACTUAL_'+stamp+'.json':tp,
      'E1_WAVE50_ROUTE443_CANDIDATE152_ACTUAL_COLLECTION_'+stamp+'.json':collection,
      'E1_WAVE50_ROUTE443_CANDIDATE152_PARTIAL_ACTUAL_REVIEW_'+stamp+'.json':review,
      'NEXT_E1_WAVE50_ROUTE443_CANDIDATE152_FULL_ACTUAL_REVIEW_WORK_ORDER_'+stamp+'.md':work}
    n,w=io.connect_both()
    try:
      with n.open_sftp() as f:
        for name,p in files.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
        raw=f.open(io.E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json','rb').read();old=H(raw);current=json.loads(raw)
      ref=lambda s:io.E+'/reports/'+next(k for k in files if s in k)
      rev=current['terrain_subexpert_revision004'];scope=rev['wave50_route_lifecycle_GPU_scope']
      scope.update(own_formal_pending=False,own_formal_complete=True,own_formal_CPU_ref=ref('OWN_FORMAL_CPU'),own_formal_final_review_ref=ref('FORMAL_FINAL_ACTUAL_REVIEW'),own_formal_current_ref=ref('FORMAL_FINAL_CURRENT'),full_training_trace_ref=ref('COMPLETE_TRAINING_TRACE'),own_checkpoint_SHA=own['own_checkpoint']['sha256'],own_actual_finite_tensors=107,actual_source_count=443,own_6updates144controls576callbacks=True,unique_loadlearnsaveexit_seconds=own['unique_loadlearnsaveexit_seconds'],actual_exit_two_fcntl_free_activeempty=True,big20kx4_own_PASSED=True,freshsame_scope_own_PASSED=True,phase=actual['reports']['E1_STATE.json']['phase'])
      rev['wave50_route_candidate152_actual_scope']=dict(own_source_count=443,own_checkpoint_SHA=own['own_checkpoint']['sha256'],actual_publication_152=True,actual_collection=ref('CANDIDATE152_ACTUAL_COLLECTION'),actual_review=ref('CANDIDATE152_PARTIAL_ACTUAL_REVIEW'),review_complete=r['review_complete'],pending=r['pending'],next_work_order=ref('NEXT_E1_WAVE50_ROUTE443'),no_more_PPO_before_full_candidate_and_trace_decision=True,no_qualified50_from_formal_save=True)
      rev['active_next_expert']='E1_WAVE';rev['active_next_phase']='WAVE50_route443_saved_candidate152_full_actual_review';rev['latest_actual_scope']='wave50_route_candidate152_actual_scope'
      nxt=io.E+'/reports/ROUTE443_FINAL_NEXT_CURRENT_'+stamp+'.json'
      with n.open_sftp() as f:io.put(f,nxt,json.dumps(current,ensure_ascii=False,indent=2).encode())
      synced=run(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(E_TOKEN)/'reports';p=R/'MOE_PLAN_EXECUTION_CURRENT.json';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=Path(B_TOKEN);before=h(B)
protected={k:(R/k).read_bytes() for k in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')};assert h(p)==OLD_TOKEN
tmp=p.with_name('ROUTE443_FINAL_CURRENT_'+str(time.time_ns())+'.tmp');tmp.write_bytes(Path(NEXT_TOKEN).read_bytes());assert h(p)==OLD_TOKEN;os.replace(tmp,p);assert all((R/k).read_bytes()==raw for k,raw in protected.items())
v=dict(epoch=time.time(),passed=True,current_SHA=h(p),master_approval_tracks_RM004_bytes_exact=True,canonical_SHA_before=before,canonical_SHA_after=h(B),canonical_not_written_by_sync=True,own443_formal_final_fulltrace_and_candidate152_actual_synced=True,no_GPU_or_oldonce_replay=True)
q=R/('E1_WAVE50_ROUTE443_FINAL_CLOSEOUT_METADATA_SYNCED_'+STAMP_TOKEN+'.json');assert not q.exists();q.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('E_TOKEN',repr(io.E)).replace('B_TOKEN',repr(io.B)).replace('OLD_TOKEN',repr(old)).replace('NEXT_TOKEN',repr(nxt)).replace('STAMP_TOKEN',repr(stamp)))
      save('ROUTE443_FINAL_CLOSEOUT_METADATA_SYNCED.json',synced)
    finally:io.cleanup(n,w)
    setting=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
    assert setting['status']=='ACTIVE' and setting['rrule']=='FREQ=HOURLY;INTERVAL=1'
    previous=D/'MONITOR_PREVIOUS_ROUTE443_BIG_ACTIVE_PROMPT.md';assert not previous.exists();previous.write_text(setting['prompt'],encoding='utf8')
    prefix=f'''最新source443首个route4m修复300s窗口已自然完整保存退出，旧big/fresh/formalactive均历史。ownmodel32264 SHA{own['own_checkpoint']['sha256']}/{own['checkpoint_bytes']}B/实际CPU107/source443/{own['actual_snapshot_file_count']}实际module snapshots+443ownfreeze/PID{own['own_PID']}/PASSED。6updates144controls2.88Msteps576callbacks，actor改变9/optimizerdelta120.0，ordinary-integrity-unknown0/nonfinitefalse/STOPnone/closure{h['max_closure_error_m']*1000}mm/mimic{h['max_mimic_error_rad']}rad；time_out1469/route1/unique1470，两coverageexact。unique{own['unique_loadlearnsaveexit_seconds']}s原parent一次结清，actual父guardian孩子exit/twofcntl-free/active-Sactive空/route_saved_review_ready合法单scope非故障或全课程finished，不复活任何oldmain/resume/once/budgettail。

先读中央E1_WAVE50_ROUTE443_OWN_FORMAL_CPU_VERIFIED/FORMAL_FINAL_ACTUAL_REVIEW/FORMAL_FINAL_CURRENT_ACTUAL/COMPLETE_TRAINING_TRACE_ACTUAL/CANDIDATE152_ACTUAL_COLLECTION/PARTIAL_ACTUAL_REVIEW/FINAL_CLOSEOUT_METADATA_SYNCED/NEXT_E1_WAVE50_ROUTE443_CANDIDATE152_FULL_ACTUAL_REVIEW_WORK_ORDER；本机{D}/reports最新ownCPU/final/trace/CANDIDATE数字actual。current.rev004.wave50_route_candidate152_actual_scope当前，wave50_route_lifecycle_GPU_scope已formalcomplete。所有newscopeSDK/native/smallbig/fresh真实once PASSED精确reuse，不重复预检/clockDR。

152四case已自己的实际publication，首readonlycollection全result_not_generated/attentionnull健康pending，以后来actualcomplete优先不假永久pending。积极collect_route443_candidate_actual.py/review_route443_candidate_actual.py仅actualcomplete/errorfree两host8JSONbyteSHA/fullNPZ/query原50protocol及115129signedcircle/原false/全validprefix。review_route443_direct151_prefix_actual.py只完整四case后直接配对complete151全初态参数staticrecipesassignment/逐env改善退化与prefix，不借fullsave/正actor或旧skill说地形合格。完整144controls训练NPZ原SHA已CPU审动态currentrootcellfamily4/two signedtowardstanding/prereset-before/beforephysicscommands vs afterupdatehist分列；每env1.44s/rootcommandproxy不是完整十波或contact/因果证书。完整新152+own perenvtrace后合理新sameidentity有界route块或独立诊断，≤2h/max2后fullaudit，不未审更多PPO/盲第三/70/qualified全RM-MoE/永久抗遗忘，也不造27/27或90/95/100机械晋级线。

初来源accepted35own369b026/CPU102/1293c97先全old35状态exact再显式50-entry-direction-route身份/CUDA磁盘roundtrip/sourceepisode+1，十startup实际通过。terrainexactfalse/newentry-newdirection-newroute true是新scope披露非漏恢复；samefresh107 geometry-command-entry-direction-route全strict/newflagsfalse，后sameidentity要求完全exact，非PhysXexactresume。仅训练Wave出生episode向内2→4m，outward/lateral/nonWave2m exact；DRrewardLRhardwareclockgeometryresetcommandRNG不混改，冻结.4approach15s1Nafter200mm不放松。新4m仅消除已测旧2m暴露上限，未证明正向改善。

0051188000/7extensions第七100h早once，本finalidle{own['remaining_snapshot_seconds']}s只是快照，actualactive/accounted尾段优先，不扩展复制clearactive-tail-recharge。future长窗资源guard依据真实自己的durablefree/output，不能删rawweights/source/env/cache/tmpfs/降guard。E0/CURB20/WAVE35/SLOPE ONLYobserved冻结/gate未训/hardware未标定/S8另批准/93-94paused/WASD不GUI干预。所有本轮ownfinal/candidatepending/fulltrace/newpreparedreaders/sync/monitor/Gitreceipt继续ordinarysupplement，actualtracked/remote工具优先不凭本文假补齐。sameheartbeatACTIVE1h同target/healthyDONT_NOTIFY/仅实质阶段真实修复重大退化完成人类动作NOTIFY，无5minSSH/ping/Rich额外监守自动预算，reviewready不删仅actualbudgetend/allfinal完停止。

旧完整prompt{previous} SHA{H(previous.read_bytes())}保留追溯。以下bigactive及此前快照仅历史，以上及之后actual优先：

'''+setting['prompt']
    save('ROUTE443_FINAL_HOURLY_MONITOR_UPDATE_REQUEST.json',dict(id='mod4-10',mode='update',kind='heartbeat',name=setting['name'],rrule=setting['rrule'],status='ACTIVE',targetThreadId=setting['target_thread_id'],prompt=prefix))
    print(json.dumps(dict(passed=True,ownfinal_synced=True,candidate_complete=r['review_complete'],monitor_request=str(R/'ROUTE443_FINAL_HOURLY_MONITOR_UPDATE_REQUEST.json'))))

if __name__=='__main__':
    try:main()
    except BaseException:save('ROUTE443_FINAL_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_oldonce_replay=True));raise
